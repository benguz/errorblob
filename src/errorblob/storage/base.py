"""Base storage backend interface."""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import ErrorEntry, SearchResult


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def commit(self, entry: ErrorEntry) -> None:
        """Store an error entry."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Search for errors matching the query."""
        pass

    @abstractmethod
    def get_all(self) -> list[ErrorEntry]:
        """Get all stored errors."""
        pass

    @abstractmethod
    def delete(self, error_id: str) -> bool:
        """Delete an error by ID. Returns True if deleted."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored errors."""
        pass

