# ChatGPT Export Processor

A Python tool for processing and analyzing ChatGPT conversation exports. This tool provides a CLI interface to extract, analyze, and work with your ChatGPT conversation data locally.

## Features

- **Extract ChatGPT exports**: Unzip and organize exported conversation data
- **Metadata analysis**: Get detailed metadata about your conversation files
- **CLI Interface**: Easy-to-use command-line interface for all operations
- **Modular design**: Extensible architecture for adding new analysis capabilities
- **Privacy-focused**: All processing happens locally, no data leaves your machine

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/chatgpt-export.git
cd chatgpt-export
```

## Usage

### Process a ChatGPT export

```bash
python -m cli process your-export.zip
```

### List extracted datasets

```bash
python -m cli list
```

### Get metadata for extracted files

```bash
python -m cli metadata ./extracted_data/2025-07-20_Sunday_12-04-32
```

### Get detailed help

```bash
python -m cli --help
```

## Project Structure

```
chatgpt-export/
├── cli/                    # Command-line interface
│   ├── __init__.py
│   ├── __main__.py
│   └── cli_interface.py
├── uploading/             # Core extraction and metadata utilities
│   ├── __init__.py
│   ├── metadata.py
│   └── unzip_export.py
├── main.py               # Main processing logic
├── .gitignore            # Git ignore rules (protects personal data)
└── README.md             # This file
```

## Privacy & Security

This tool is designed with privacy in mind:

- All processing happens locally on your machine
- No data is sent to external servers
- The `.gitignore` file ensures personal conversation data is never committed
- Extracted data is stored in `extracted_data/` which is excluded from version control

## Future Plans

- Embedding generation for semantic search
- Vector database integration
- Advanced analysis capabilities
- API/MCP server interface
- Export to various formats

## Contributing

Contributions are welcome! Please ensure:
- No personal data is included in commits
- Code follows existing patterns
- Privacy-first design is maintained

## License

[Add your chosen license here]

## Warning

**Never commit your personal conversation data!** Always check `.gitignore` is properly configured before pushing to a repository.