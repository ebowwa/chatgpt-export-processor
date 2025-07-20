#!/usr/bin/env python3
"""
Entry point for running the CLI as a module.

This allows the CLI to be run using: python -m cli
"""

from .cli_interface import main

if __name__ == "__main__":
    main()