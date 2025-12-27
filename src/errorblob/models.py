"""Data models for errorblob."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ErrorEntry(BaseModel):
    """An error entry in the database."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    error_text: str = Field(..., description="The error message text")
    message: str = Field(..., description="Additional context/fix message")
    created_at: datetime = Field(default_factory=datetime.now)
    author: Optional[str] = Field(default=None, description="Who committed this error")
    tags: list[str] = Field(default_factory=list, description="Optional tags for categorization")

    def display(self) -> str:
        """Format the error entry for display."""
        lines = [
            f"📛 Error: {self.error_text}",
            f"💡 Fix: {self.message}",
            f"📅 Added: {self.created_at.strftime('%Y-%m-%d %H:%M')}",
        ]
        if self.author:
            lines.append(f"👤 Author: {self.author}")
        if self.tags:
            lines.append(f"🏷️  Tags: {', '.join(self.tags)}")
        return "\n".join(lines)


class SearchResult(BaseModel):
    """A search result with relevance score."""
    
    entry: ErrorEntry
    score: float = Field(..., description="Relevance score (higher is better)")

