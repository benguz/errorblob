#!/usr/bin/env python3
"""Entry point for PyInstaller binary."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from errorblob.cli import cli

if __name__ == "__main__":
    cli()

