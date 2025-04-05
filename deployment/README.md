# Nexobotics RAG Chatbot API

This is the backend API for the Nexobotics customer service chatbot, using Retrieval-Augmented Generation (RAG) with Google Gemini AI and ChromaDB.

## Deployment Options

### Option 1: Deploy on Vercel

1. **Setup Environment**:

   - Fork or clone this repository
   - Sign up for [Vercel](https://vercel.com) if you haven't already

2. **Deploy**:

   - Import your repository in Vercel
   - Set the following environment variables:
     - `GOOGLE_API_KEY`: Your Google API key
     - `CHROMA_PERSIST_DIR`: `./chromadb_data`
   - Deploy

3. **Initialize Knowledge Base**:
   - After deployment, use the Vercel CLI to run the knowledge base initialization:
     ```
     vercel env pull
     python api/persistent_add_docs.py
     vercel --prod
     ```

### Option 2: Deploy on Render.com

1. **Setup Environment**:

   - Fork or clone this repository
   - Sign up for [Render](https://render.com) if you haven't already

2. **Deploy**:

   - Create a new Web Service in Render
   - Link your repository
   - Specify the following settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn api.index:app`
   - Set the environment variables:
     - `GOOGLE_API_KEY`: Your Google API key
     - `CHROMA_PERSIST_DIR`: `./chromadb_data`
   - Deploy

3. **Initialize Knowledge Base**:
   - After deployment, connect to the Render shell and run:
     ```
     python api/persistent_add_docs.py
     ```

## Using the API

### API Endpoints

- **Chat API**: `POST /api/chat`

  - Request body: `{ "message": "User message", "session_id": "optional_session_id" }`
  - Response: `{ "response": "AI response" }`

- **Health Check**: `GET /api/health`

  - Response: `{ "status": "healthy", "service": "nexobotics-chatbot-api", "rag_initialized": true }`

- **Clear Session**: `POST /api/clear-session`
  - Request body: `{ "session_id": "session_id_to_clear" }`
  - Response: `{ "status": "success", "message": "Session cleared" }`

## Customizing the Knowledge Base

Edit the `DOCUMENTS` list in `api/persistent_add_docs.py` with your own business information, then run the script to rebuild the knowledge base.
