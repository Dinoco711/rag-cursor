# Nexobotics RAG Chatbot (Cleaned Version)

A customer service chatbot powered by Retrieval-Augmented Generation (RAG) using Google Gemini AI and ChromaDB. This is a clean, well-structured version of the original codebase.

## Project Structure

```
groq-3/cleaned/
├── api/                     # Backend API directory
│   ├── index.py             # Main Flask application
│   ├── rag_pipeline.py      # RAG implementation
│   └── persistent_add_docs.py # Knowledge base management
│
├── website/                  # Frontend directory
│   └── chatbot.js            # Chat widget implementation
│
├── test_chatbot.html         # Test page for the chat widget
├── .env.example              # Template for environment variables
├── requirements.txt          # Python dependencies
├── README.md                 # This README file
├── USAGE_GUIDE.md            # Guide for using and updating the system
└── WEBSITE_INTEGRATION.md    # Guide for website integration
```

## Quick Start

1. **Set up the environment**:

   ```bash
   cd groq-3/cleaned
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Add your API key**:
   Edit the `.env` file and add your Google API key:

   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. **Initialize the knowledge base**:

   ```bash
   python api/persistent_add_docs.py
   ```

4. **Start the server**:

   ```bash
   python api/index.py
   ```

5. **Test the chatbot**:
   Open `test_chatbot.html` in your browser to test the chatbot functionality.

## Features

- **RAG-Powered Responses**: Answers based on your knowledge base
- **Persistent Sessions**: Conversation continuity for users
- **User-Friendly Interface**: Clean, modern chat widget
- **Customizable**: Easy to configure and brand
- **Well-Documented**: Clear guides for usage and integration

## Customizing the Knowledge Base

To add or update information in the chatbot's knowledge base:

1. Edit the `DOCUMENTS` list in `api/persistent_add_docs.py`
2. Add your business information, categorized by type
3. Run the script to rebuild the knowledge base

## Documentation

The project includes detailed documentation:

- **USAGE_GUIDE.md**: How to use, manage, and maintain the system
- **WEBSITE_INTEGRATION.md**: How to integrate the chatbot into your website

## Architecture Overview

### Backend

- **Flask Server**: Provides the chat API endpoint
- **RAG Pipeline**: Retrieves relevant information and generates responses
- **ChromaDB**: Stores document embeddings for semantic search

### Frontend

- **Chat Widget**: JavaScript widget that can be embedded in any website
- **Test Page**: Simple HTML page to test the chatbot functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created by Nexobotics for customer service automation.
