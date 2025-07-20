# ChatGPT Export Processing - Uploading Module

## Module Structure

```
chatgpt-export/
├── main.py                  # Main orchestrator
├── uploading/              # Core processing modules
│   ├── unzip_export.py     # ZIP extraction and initial processing
│   ├── metadata.py         # File metadata analysis functions
│   └── README.md           # This file
└── extracted_data/         # Timestamped extraction folders
```

## Data Flow

1. **Initial Input**: User provides ChatGPT export ZIP file
2. **Extraction** (`unzip_export.py`): 
   - Unzips files to timestamped folder
   - Returns list of extracted files
3. **Metadata Analysis** (`metadata.py`):
   - Analyzes file sizes and structure
   - Counts lines and JSON items
   - Provides formatted output
4. **Orchestration** (`main.py`):
   - Coordinates the entire process
   - Manages data flow between modules
   - Provides summary statistics

## Module Details

### metadata.py
- `format_file_size()`: Human-readable file sizes
- `count_lines()`: Accurate line counting
- `analyze_json_structure()`: JSON type and item counting
- `get_file_metadata()`: Comprehensive file analysis
- `format_metadata_display()`: Formatted output strings

### unzip_export.py
- `unzip_file()`: Extract ZIP and analyze contents
- Returns structured data about extracted files
- Integrates with metadata module for analysis

## Usage

```bash
# Use default ZIP file
python main.py

# Specify custom ZIP file
python main.py /path/to/chatgpt-export.zip
```

## Future Integration Points

- **Embeddings**: Generate vector embeddings for conversations
- **Storage**: Vector database integration
- **Search**: Semantic search capabilities
- **Export**: Additional export formats