# ChatGPT Export Processor 🤖

**Extract, analyze, and search your ChatGPT conversations locally with complete privacy**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Privacy](https://img.shields.io/badge/privacy-first-orange.svg)](https://github.com/ebowwa/chatgpt-export-processor)

A powerful Python CLI tool for processing ChatGPT data exports from OpenAI. Extract your conversations, analyze metadata, generate embeddings, and search through your AI chat history - all while keeping your data 100% private and local.

## 🚀 Key Features

- **🗂️ ChatGPT Export Processing**: Seamlessly extract and organize your ChatGPT conversation exports
- **📊 Metadata Analysis**: Analyze conversation statistics, message counts, and file sizes
- **🔍 Local Search** (coming soon): Search through your conversations with embeddings
- **🔒 100% Private**: All processing happens on your machine - no data ever leaves your device
- **⚡ Fast CLI**: Efficient command-line interface for batch processing
- **🧩 Extensible**: Modular architecture ready for custom analysis plugins
- **🤝 OpenAI Compatible**: Works with official ChatGPT data exports

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/ebowwa/chatgpt-export-processor.git
cd chatgpt-export-processor

# Install dependencies (optional, for future features)
pip install -r requirements.txt  # Coming soon
```

## 🎯 Quick Start

### 1️⃣ Export your ChatGPT data
Go to [ChatGPT Settings](https://chat.openai.com/settings) → Data Controls → Export data

### 2️⃣ Process your export
```bash
python -m interfaces.cli process your-chatgpt-export.zip
```

### 3️⃣ Explore your data
```bash
# List all extracted conversations
python -m interfaces.cli list

# Analyze metadata for specific dataset
python -m interfaces.cli metadata ./user-data/2025-07-20_Sunday_12-04-32

# Get help
python -m interfaces.cli --help
```

## 📁 Project Structure

```
chatgpt-export-processor/
├── interfaces/            # User interfaces (CLI, API, etc.)
│   └── cli/              # Command-line interface
├── src/                  # Core functionality
│   └── uploading/        # Extraction and metadata utilities
├── main.py              # Main processing engine
├── .gitignore           # Protects your personal data
└── README.md            # Documentation
```

## 🔐 Privacy & Security

**Your conversations never leave your machine:**

- ✅ 100% local processing - no cloud, no external APIs
- ✅ Your data stays in `user-data/` (automatically gitignored)
- ✅ No telemetry, no tracking, no data collection
- ✅ Open source - inspect every line of code

## 🗺️ Roadmap

- [ ] **Embeddings Generation** - Semantic search through conversations
- [ ] **Vector Database** - Efficient similarity search with FAISS/ChromaDB
- [ ] **Advanced Analytics** - Conversation insights and patterns
- [ ] **Export Formats** - JSON, CSV, Markdown exports
- [ ] **Web UI** - Browser-based interface
- [ ] **API Server** - REST API for integrations
- [ ] **LLM Fine-tuning** - Prepare data for model training

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Important**: Never commit personal conversation data. Check `.gitignore` before pushing.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [ChatGPT](https://chat.openai.com) - OpenAI's conversational AI
- [OpenAI API](https://platform.openai.com) - Build with GPT models
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework

## 📞 Support

- 🐛 [Report bugs](https://github.com/ebowwa/chatgpt-export-processor/issues)
- 💡 [Request features](https://github.com/ebowwa/chatgpt-export-processor/issues)
- 📖 [Documentation](https://github.com/ebowwa/chatgpt-export-processor/wiki)

---

**Keywords**: ChatGPT export, OpenAI data export, conversation analysis, ChatGPT backup, AI chat history, local ChatGPT search, privacy-first AI tools, ChatGPT data processing, conversation embeddings, ChatGPT analytics