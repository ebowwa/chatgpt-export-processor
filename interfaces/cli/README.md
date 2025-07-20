# ChatGPT Export CLI

This directory contains the Command Line Interface (CLI) for the ChatGPT export processing tool. The CLI serves as one of multiple interfaces to the core functionality, providing a structured way to interact with the existing codebase without modifying it.

## Design Principles

1. **Non-invasive**: The CLI acts as a wrapper around existing functionality
2. **Modular**: Can be used independently or alongside other interfaces
3. **Preserves existing code**: No modifications to the core codebase
4. **Extensible**: Easy to add new commands and features

## Usage

The CLI can be run in several ways:

```bash
# From the project root
python -m cli process export.zip

# Or using the direct script
python cli/cli_interface.py process export.zip

# With custom output directory
python -m cli process export.zip --output /custom/path

# List available datasets
python -m cli list

# Analyze extracted data (integrates with v001 modules)
python -m cli analyze ./user-data/2025-07-20_Monday_10-30-00 --type cognitive
```

## Available Commands

- `process`: Process a ChatGPT export ZIP file
- `analyze`: Run analysis on previously extracted data
- `list`: List available extracted datasets

## Integration

The CLI integrates with:
- `main.py`: Core processing functionality
- `uploading/`: Extraction and metadata modules
- `v001/`: Analysis modules (when using analyze command)

This ensures all existing functionality remains available while providing a clean command-line interface.