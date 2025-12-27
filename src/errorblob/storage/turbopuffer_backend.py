"""Turbopuffer storage backend for cloud-based error storage."""

from datetime import datetime
from typing import Optional

import turbopuffer

from .base import StorageBackend
from ..models import ErrorEntry, SearchResult


class TurbopufferStorage(StorageBackend):
    """Store errors in Turbopuffer for cloud-based semantic search."""

    def __init__(
        self,
        api_key: str,
        namespace: str = "errorblob",
        region: str = "gcp-us-central1",
    ):
        self.tpuf = turbopuffer.Turbopuffer(
            api_key=api_key,
            region=region,
        )
        self.ns = self.tpuf.namespace(namespace)
        self._namespace_name = namespace
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure the namespace is initialized with the correct schema."""
        if self._initialized:
            return
        self._initialized = True

    def commit(self, entry: ErrorEntry) -> None:
        """Store an error entry using full-text search indexing."""
        self._ensure_initialized()
        
        # Combine error_text and message for better searchability
        combined_text = f"{entry.error_text} {entry.message}"
        
        self.ns.write(
            upsert_rows=[
                {
                    "id": entry.id,
                    "error_text": entry.error_text,
                    "message": entry.message,
                    "combined_text": combined_text,
                    "created_at": entry.created_at.isoformat(),
                    "author": entry.author or "",
                    "tags": ",".join(entry.tags) if entry.tags else "",
                }
            ],
            schema={
                "error_text": {
                    "type": "string",
                    "full_text_search": {
                        "language": "english",
                        "stemming": True,
                        "remove_stopwords": True,
                        "case_sensitive": False,
                    },
                },
                "message": {
                    "type": "string",
                    "full_text_search": {
                        "language": "english",
                        "stemming": True,
                        "remove_stopwords": True,
                        "case_sensitive": False,
                    },
                },
                "combined_text": {
                    "type": "string",
                    "full_text_search": {
                        "language": "english",
                        "stemming": True,
                        "remove_stopwords": True,
                        "case_sensitive": False,
                    },
                },
            },
        )

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Search for errors using BM25 full-text search."""
        self._ensure_initialized()
        
        try:
            results = self.ns.query(
                rank_by=("combined_text", "BM25", query),
                top_k=limit,
                include_attributes=["error_text", "message", "created_at", "author", "tags"],
            )
            
            search_results: list[SearchResult] = []
            for row in results:
                # Parse the result back into an ErrorEntry
                tags_str = getattr(row, "tags", "") or ""
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                
                created_at_str = getattr(row, "created_at", None)
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                else:
                    created_at = datetime.now()
                
                author = getattr(row, "author", None)
                if author == "":
                    author = None
                
                entry = ErrorEntry(
                    id=str(row.id),
                    error_text=getattr(row, "error_text", ""),
                    message=getattr(row, "message", ""),
                    created_at=created_at,
                    author=author,
                    tags=tags,
                )
                
                # $dist is the BM25 score (higher is better for BM25)
                score = getattr(row, "$dist", 0.0) if hasattr(row, "$dist") else 0.0
                search_results.append(SearchResult(entry=entry, score=float(score)))
            
            return search_results
            
        except Exception:
            # If namespace is empty or doesn't exist yet, return empty
            return []

    def get_all(self) -> list[ErrorEntry]:
        """Get all stored errors by exporting the namespace."""
        self._ensure_initialized()
        
        try:
            entries: list[ErrorEntry] = []
            
            # Use export to get all rows
            for row in self.ns.export():
                tags_str = getattr(row, "tags", "") or ""
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                
                created_at_str = getattr(row, "created_at", None)
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                else:
                    created_at = datetime.now()
                
                author = getattr(row, "author", None)
                if author == "":
                    author = None
                
                entry = ErrorEntry(
                    id=str(row.id),
                    error_text=getattr(row, "error_text", ""),
                    message=getattr(row, "message", ""),
                    created_at=created_at,
                    author=author,
                    tags=tags,
                )
                entries.append(entry)
            
            return entries
            
        except Exception:
            return []

    def delete(self, error_id: str) -> bool:
        """Delete an error by ID."""
        self._ensure_initialized()
        
        try:
            self.ns.write(deletes=[error_id])
            return True
        except Exception:
            return False

    def count(self) -> int:
        """Return the number of stored errors."""
        return len(self.get_all())

