import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Import RAG pipeline
from rag_pipeline import query_rag, get_rag_pipeline

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set Google Gemini API Key from environment variable
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Define the model to use for standard chat (non-RAG)
DEFAULT_MODEL = "models/gemini-1.5-flash"  # Using a model that's confirmed to be available

# Define the chatbot's context
CONTEXT = """You are NOVA, a proactive and adaptable customer service agent for Nexobotics. Your role is to guide users, particularly business owners, on how Nexobotics can transform their customer service by handling all customer interactions efficiently and attentively while maximizing customer satisfaction. You also act as a consultant, offering actionable insights to enhance customer satisfaction and loyalty.

Adapt your communication style to match the user's tone—casual if they're laid-back (e.g., "Hey, what's up?") or professional if they're formal but stay formal in the beginning of the conversation. Always ensure clarity and relevance in your responses while minimizing unnecessary explanations unless requested. Use unique, engaging opening and closing lines but keep them short maximum 1 to 2 sentences. Keep greetings short and dynamic. End conversations with motivational and engaging lines. Stay concise, focused, and results-oriented, delivering valuable insights quickly without overwhelming the user. Don't provide too much or too long explanation or even greetings, keep them short and sweet. You can use bold, italic formats to highlight the important parts, or any types of list that makes the user reading easy. Maintain a friendly and approachable tone while ensuring your responses are practical and impactful.

When '/start' will be prompted then that means that user has arrived so, you have to greet them uniquely but in a very short sentence. Avoid long introductions and explanations.
"""

# Initialize chat history for each session
chat_histories = {}
# Flag to track if RAG is initialized
rag_initialized = False

# Function to initialize RAG pipeline
async def initialize_rag():
    """Initialize the RAG pipeline."""
    global rag_initialized
    if rag_initialized:
        return
        
    try:
        # Determine if we should use persistent storage
        persist_dir = os.environ.get('CHROMA_PERSIST_DIR', None)
        await get_rag_pipeline(persist_directory=persist_dir)
        rag_initialized = True
        print("RAG pipeline initialized successfully")
    except Exception as e:
        print(f"Error initializing RAG pipeline: {str(e)}")

# Make the route non-async for compatibility with Flask's standard server
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    # Initialize RAG before processing the first request
    if not rag_initialized:
        # Use asyncio.run to call the async function from sync code
        asyncio.run(initialize_rag())
        
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    message = request.json.get('message')
    session_id = request.json.get('session_id', str(datetime.now()))  # Default session ID
    
    # Always use RAG regardless of what's in the request
    use_rag = True

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        # Initialize or retrieve chat history for the session
        if session_id not in chat_histories:
            chat_histories[session_id] = [
                {"role": "system", "content": CONTEXT}
            ]

        # Add user prompt to history
        chat_histories[session_id].append({"role": "user", "content": message})

        # Use RAG pipeline to generate response - use asyncio.run to call async from sync
        try:
            rag_result = asyncio.run(query_rag(message))
            ai_response = rag_result["response"]
            
            # Store retrieved documents in the chat history for context
            documents = rag_result.get("documents", [])
            if documents:
                retrieved_context = "\n---\nRetrieved knowledge:\n" + "\n".join(documents)
                chat_histories[session_id].append({
                    "role": "system", 
                    "content": retrieved_context
                })
        except Exception as e:
            print(f"RAG error: {str(e)}")
            # Fallback to a friendly error message
            ai_response = "I'm currently having trouble accessing my knowledge base. Please try asking a different question or try again later."
        
        # Add AI response to history
        if ai_response:
            chat_histories[session_id].append({"role": "assistant", "content": ai_response})

        return jsonify({'response': ai_response})
    except Exception as e:
        print(f"Error processing message: {str(e)}")  # For debugging
        return jsonify({'error': 'An error occurred processing your request'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({'status': 'healthy', 'service': 'nexobotics-chatbot-api'})

import threading
import time
import requests

def keep_awake():
    url = "https://rag-cursor.onrender.com/health"  # Use your actual Render URL and a lightweight endpoint
    while True:
        try:
            requests.get(url, timeout=5)
        except Exception:
            pass
        time.sleep(15)

# Start the self-ping in a background thread
threading.Thread(target=keep_awake, daemon=True).start()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Render uses the PORT environment variable
    
    # Use Flask's built-in development server instead of Hypercorn
    app.run(host='0.0.0.0', port=port, debug=True)
    
    # Remove Hypercorn server code
    # config = HyperConfig()
    # config.bind = [f"0.0.0.0:{port}"]
    # asyncio.run(serve(app, config))
