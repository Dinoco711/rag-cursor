# Nexobotics RAG Chatbot Usage Guide

This guide provides instructions for managing and updating your Nexobotics customer service chatbot, which uses Retrieval-Augmented Generation (RAG) to provide accurate responses based on your company's knowledge base.

## Table of Contents

1. [Setting Up](#setting-up)
2. [Managing the Knowledge Base](#managing-the-knowledge-base)
3. [Customizing the Chatbot](#customizing-the-chatbot)
4. [Monitoring and Maintenance](#monitoring-and-maintenance)
5. [Troubleshooting](#troubleshooting)

## Setting Up

### Prerequisites

- Python 3.8 or higher
- A Google API key for Gemini models
- Basic knowledge of command line operations

### Installation

1. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

2. Configure your environment:

   - Create a `.env` file based on `.env.example`
   - Add your Google API key to the `.env` file

   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

3. Start the server:

   ```
   python groq-3/api/index.py
   ```

4. Test the chatbot by opening `test_chatbot.html` in a web browser

## Managing the Knowledge Base

The chatbot's ability to provide accurate information depends on the quality of its knowledge base. Here's how to manage it:

### Viewing the Current Knowledge Base

To see what information is currently in the knowledge base:

1. Run the server
2. Use the test page to ask questions like "What services does Nexobotics offer?"
3. Observe the responses to understand what information is available

### Updating the Knowledge Base

To update the knowledge base with your company's information:

1. Edit the `persistent_add_docs.py` file
2. Modify the `DOCUMENTS` list with your information, organized by category
3. Run the script to update the database:
   ```
   python groq-3/api/persistent_add_docs.py
   ```

### Knowledge Base Best Practices

- **Keep documents concise**: 1-3 sentences per document works best
- **Organize information by category**: Use the metadata system to organize information
- **Include specific details**: Product specs, contact information, policies, etc.
- **Update regularly**: Keep information current for accurate responses
- **Test after updates**: Ask relevant questions to ensure proper retrieval

## Customizing the Chatbot

### System Prompt

The system prompt defines the chatbot's personality and behavior. To modify it:

1. Edit the `SYSTEM_PROMPT` variable in `index.py`
2. Restart the server for changes to take effect

### Response Generation Parameters

To adjust how the chatbot generates responses:

1. Edit the `generation_config` parameters in `rag_pipeline.py`:
   - `temperature`: Higher (0.7+) for more creative responses, lower (0.2-0.4) for more factual responses
   - `max_output_tokens`: Adjust the maximum response length
2. Restart the server for changes to take effect

### Appearance

To customize the chatbot's appearance on your website:

1. Edit the CSS styles in `chatbot.js`
2. Modify the colors, fonts, and other visual elements to match your brand
3. Update the logo by replacing the image URL

## Monitoring and Maintenance

### Logging

The server logs important information to the console:

- Initialization status
- Retrieved documents for each query
- Error messages

For production environments, consider setting up more advanced logging.

### Performance Optimization

If the chatbot becomes slow:

1. Reduce the `top_k` parameter in `query_rag()` function calls
2. Ensure the ChromaDB collection isn't too large (< 1000 documents)
3. Consider using a faster server or adding more RAM

### Regular Maintenance

1. **Update the knowledge base** when company information changes
2. **Check for package updates** periodically:
   ```
   pip list --outdated
   ```
3. **Backup the ChromaDB database** regularly by copying the `chromadb_data` directory

## Troubleshooting

### Common Issues

1. **Chatbot returns "I don't have information about that"**

   - Add relevant information to the knowledge base
   - Check that the RAG pipeline is initialized correctly

2. **Server fails to start**

   - Check that the Google API key is valid
   - Ensure all required packages are installed
   - Verify port 5000 is available (or set a different port in .env)

3. **Slow response times**

   - Check network connection
   - Reduce the number of documents being retrieved
   - Verify server resources are adequate

4. **Error connecting to the API**
   - Ensure CORS is configured correctly
   - Check that the server URL in `chatbot.js` matches your deployment

### Getting Help

For additional assistance:

1. Check the Google Generative AI documentation
2. Review the ChromaDB documentation
3. Contact the development team for critical issues
