"""
ChatGPT Export CLI Interface Module

This module provides a command-line interface to the ChatGPT export processing functionality.
It serves as one of multiple interfaces to the core functionality without modifying the existing codebase.
"""

__version__ = "1.0.0"
__author__ = "ChatGPT Export CLI"

from .cli_interface import main

__all__ = ["main"]