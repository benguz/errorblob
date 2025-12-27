"""Configuration management for errorblob."""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class StorageMode(str, Enum):
    """Storage mode options."""
    LOCAL = "local"
    TURBOPUFFER = "turbopuffer"


class TeamMode(str, Enum):
    """Team sharing mode options."""
    NONE = "none"
    GIT = "git"  # Shared via git (for local mode)
    SHARED_NAMESPACE = "shared_namespace"  # Shared turbopuffer namespace


class ErrorBlobConfig(BaseModel):
    """Configuration for errorblob."""
    
    storage_mode: StorageMode = Field(default=StorageMode.LOCAL)
    
    # Local storage settings
    local_file_path: Path = Field(
        default_factory=lambda: Path.home() / ".errorblob" / "errors.json"
    )
    
    # Turbopuffer settings
    turbopuffer_api_key: Optional[str] = Field(default=None)
    turbopuffer_namespace: str = Field(default="errorblob")
    turbopuffer_region: str = Field(default="gcp-us-central1")
    
    # Team settings
    team_mode: TeamMode = Field(default=TeamMode.NONE)
    team_name: Optional[str] = Field(default=None)
    
    # User settings
    author_name: Optional[str] = Field(default=None)


def get_config_path() -> Path:
    """Get the configuration file path."""
    config_dir = Path.home() / ".errorblob"
    return config_dir / "config.json"


def load_config() -> ErrorBlobConfig:
    """Load configuration from file or return defaults."""
    config_path = get_config_path()
    
    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
            return ErrorBlobConfig.model_validate(data)
    
    return ErrorBlobConfig()


def save_config(config: ErrorBlobConfig) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    with open(config_path, "w") as f:
        # Convert to dict and handle Path serialization
        data = config.model_dump(mode="json")
        json.dump(data, f, indent=2, default=str)
    
    # Restrict config file permissions (contains API key)
    config_path.chmod(0o600)


def get_turbopuffer_api_key(config: ErrorBlobConfig) -> Optional[str]:
    """Get turbopuffer API key from config or environment."""
    return config.turbopuffer_api_key or os.environ.get("TURBOPUFFER_API_KEY")

