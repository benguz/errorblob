"""Local JSON file storage backend."""

import json
from pathlib import Path
from difflib import SequenceMatcher

from .base import StorageBackend
from ..models import ErrorEntry, SearchResult


class LocalStorage(StorageBackend):
    """Store errors in a local JSON file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the storage file and parent directories exist."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save_entries([])

    def _load_entries(self) -> list[ErrorEntry]:
        """Load all entries from file."""
        with open(self.file_path) as f:
            data = json.load(f)
            return [ErrorEntry.model_validate(entry) for entry in data]

    def _save_entries(self, entries: list[ErrorEntry]) -> None:
        """Save all entries to file."""
        with open(self.file_path, "w") as f:
            data = [entry.model_dump(mode="json") for entry in entries]
            json.dump(data, f, indent=2, default=str)

    def commit(self, entry: ErrorEntry) -> None:
        """Store an error entry."""
        entries = self._load_entries()
        entries.append(entry)
        self._save_entries(entries)

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Search for errors matching the query using fuzzy matching."""
        entries = self._load_entries()
        results: list[SearchResult] = []
        
        query_lower = query.lower()
        
        for entry in entries:
            # Calculate similarity score based on error text
            error_lower = entry.error_text.lower()
            
            # Check for substring match first (high score)
            if query_lower in error_lower or error_lower in query_lower:
                score = 0.9
            else:
                # Use SequenceMatcher for fuzzy matching
                score = SequenceMatcher(None, query_lower, error_lower).ratio()
            
            # Also check the message for context
            message_score = SequenceMatcher(
                None, query_lower, entry.message.lower()
            ).ratio() * 0.3  # Weight message matches lower
            
            combined_score = max(score, score + message_score)
            
            if combined_score > 0.2:  # Threshold for relevance
                results.append(SearchResult(entry=entry, score=combined_score))
        
        # Sort by score descending and limit results
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def get_all(self) -> list[ErrorEntry]:
        """Get all stored errors."""
        return self._load_entries()

    def delete(self, error_id: str) -> bool:
        """Delete an error by ID."""
        entries = self._load_entries()
        original_count = len(entries)
        entries = [e for e in entries if e.id != error_id]
        
        if len(entries) < original_count:
            self._save_entries(entries)
            return True
        return False

    def count(self) -> int:
        """Return the number of stored errors."""
        return len(self._load_entries())

