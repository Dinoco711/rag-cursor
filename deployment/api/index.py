"""
Nexobotics Customer Service Chatbot API Server

This module provides the Flask server implementation for the Nexobotics
customer service chatbot API. It handles chat requests, manages sessions,
and integrates with the RAG pipeline for knowledge-based responses.
"""

import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import RAG pipeline
from .rag_pipeline import query_rag, get_rag_pipeline

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set Google API Key from environment variable
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Define the chatbot's system prompt
SYSTEM_PROMPT = """You are NOVA, a helpful customer service assistant for Nexobotics. Your goal is to provide accurate, 
helpful responses to customer inquiries based on the information in our knowledge base.

Your communication style should be:
- Warm and professional
- Clear and concise
- Solution-oriented
- Friendly but not overly casual

When greeting users, keep introductions brief and focus on addressing their needs.
"""

# Initialize chat history for each session
chat_histories = {}

# Flag to track if RAG is initialized
rag_initialized = False

# Function to initialize RAG pipeline
async def initialize_rag():
    """Initialize the RAG pipeline with the persistent directory."""
    global rag_initialized
    if rag_initialized:
        return
        
    try:
        # Get the persistence directory from environment or use default
        persist_dir = os.environ.get('CHROMA_PERSIST_DIR', "./chromadb_data")
        await get_rag_pipeline()
        rag_initialized = True
        print(f"RAG pipeline initialized successfully with persistence directory: {persist_dir}")
    except Exception as e:
        print(f"Error initializing RAG pipeline: {str(e)}")
        raise

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Chat endpoint to process user messages and generate responses.
    
    Request JSON format:
    {
        "message": "User's message",
        "session_id": "unique_session_id" (optional)
    }
    
    Response JSON format:
    {
        "response": "AI's response"
    }
    """
    # Initialize RAG before processing the first request
    global rag_initialized
    if not rag_initialized:
        try:
            # Use asyncio.run to call the async function from sync code
            asyncio.run(initialize_rag())
        except Exception as e:
            return jsonify({
                'error': f'Failed to initialize RAG pipeline: {str(e)}',
                'response': 'I apologize, but I am having trouble connecting to my knowledge base. Please try again in a moment.'
            }), 500
        
    # Validate request
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    # Extract request data
    message = request.json.get('message')
    session_id = request.json.get('session_id', str(datetime.now().timestamp()))
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        # Initialize or retrieve chat history for the session
        if session_id not in chat_histories:
            chat_histories[session_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
            print(f"New session created: {session_id}")

        # Add user message to chat history
        chat_histories[session_id].append({"role": "user", "content": message})

        # Use RAG pipeline to generate response
        try:
            # Run the async RAG query in synchronous context
            rag_result = asyncio.run(query_rag(message))
            ai_response = rag_result["response"]
            
            # Debugging info
            retrieved_docs = rag_result.get("documents", [])
            if retrieved_docs:
                print(f"Retrieved {len(retrieved_docs)} documents for query: '{message}'")
                
                # Store retrieved documents in history for context (optional)
                # This can be useful for debugging but might not be needed in production
                if os.environ.get('DEBUG', 'false').lower() == 'true':
                    retrieved_context = "\n---\nRetrieved knowledge:\n" + "\n".join(retrieved_docs)
                    chat_histories[session_id].append({
                        "role": "system", 
                        "content": retrieved_context
                    })
            else:
                print(f"No documents retrieved for query: '{message}'")
                
        except Exception as e:
            print(f"RAG error: {str(e)}")
            ai_response = "I'm having trouble accessing my knowledge base right now. Is there something else I can help with?"
        
        # Add AI response to chat history
        chat_histories[session_id].append({"role": "assistant", "content": ai_response})

        # Limit chat history size to prevent memory issues
        if len(chat_histories[session_id]) > 20:  # Keep last 20 messages
            chat_histories[session_id] = chat_histories[session_id][-20:]
            
        return jsonify({'response': ai_response})
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your request',
            'response': 'I apologize for the inconvenience, but I encountered an error. Please try again.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'healthy', 
        'service': 'nexobotics-chatbot-api',
        'rag_initialized': rag_initialized
    })

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear a specific chat session."""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400
        
    if session_id in chat_histories:
        # Keep only the system prompt
        chat_histories[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        return jsonify({'status': 'success', 'message': 'Session cleared'})
    else:
        return jsonify({'status': 'success', 'message': 'Session not found'})

# Default route for Vercel serverless
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'running',
        'service': 'nexobotics-chatbot-api',
        'version': '1.0.0'
    })

# For local development
if __name__ == '__main__':
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment variable or use default True for development
    debug_mode = os.environ.get('DEBUG', 'true').lower() == 'true'
    
    print(f"Starting Nexobotics Customer Service Chatbot API on port {port}")
    print(f"Debug mode: {debug_mode}")
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 