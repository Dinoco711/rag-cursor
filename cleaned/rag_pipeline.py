"""
RAG Pipeline Module for Nexobotics Customer Service Chatbot

This module provides a Retrieval-Augmented Generation pipeline 
using Google's Generative AI models and ChromaDB for vector storage.
It is optimized for customer service applications, with friendly,
helpful responses based on the company's knowledge base.

Compatible with google-generativeai 0.8.4+
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import chromadb

class RAGPipeline:
    """
    Retrieval-Augmented Generation Pipeline for customer service applications
    
    This class provides methods to:
    1. Initialize and manage a knowledge base using ChromaDB
    2. Query the knowledge base using embeddings
    3. Generate contextual responses using Google's Generative AI
    """
    
    def __init__(self, 
                 api_key: str,
                 collection_name: str = "nexobotics_knowledge_base",
                 embedding_model: str = "models/embedding-001",
                 generation_model: str = "models/gemini-1.5-flash",
                 persist_directory: Optional[str] = None):
        """
        Initialize the RAG pipeline.
        
        Args:
            api_key: Google API key
            collection_name: Name of the ChromaDB collection
            embedding_model: Model to use for embeddings
            generation_model: Model to use for text generation
            persist_directory: Directory to persist the ChromaDB database
        """
        self.api_key = api_key
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.generation_model = generation_model
        self.persist_directory = persist_directory or "./chromadb_data"
        
        # Configure Google Generative AI
        genai.configure(api_key=api_key)
        
        # Initialize ChromaDB
        self._init_chroma()
        
    def _init_chroma(self):
        """Initialize ChromaDB client and collection"""
        # Create directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize persistent client
        self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Create or get the collection
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            # Collection doesn't exist, create a new one
            self.collection = self.chroma_client.create_collection(name=self.collection_name)
            print(f"Created new collection: {self.collection_name}")

    async def add_documents(self, documents: List[str], ids: List[str], 
                          metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of text documents to add
            ids: Unique IDs for each document
            metadatas: Optional metadata for each document
        """
        try:
            if len(documents) != len(ids):
                raise ValueError("Number of documents and ids must match")
                
            if metadatas and len(metadatas) != len(documents):
                raise ValueError("Number of metadata items must match number of documents")
            
            # Generate embeddings for documents
            document_embeddings = []
            for doc in documents:
                embedding_response = genai.embed_content(
                    model=self.embedding_model,
                    content=doc,
                    task_type="retrieval_document"
                )
                document_embeddings.append(embedding_response["embedding"])
                
            # Add documents to the collection
            self.collection.add(
                documents=documents,
                embeddings=document_embeddings,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"Successfully added {len(documents)} documents to the collection")
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            raise
            
    async def query(self, query_text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query the RAG pipeline to get a response based on retrieved context.
        
        Args:
            query_text: The query text
            top_k: Number of top results to retrieve
            
        Returns:
            Dictionary containing the response and retrieved documents
        """
        try:
            # Generate embedding for the query
            query_embedding_response = genai.embed_content(
                model=self.embedding_model,
                content=query_text,
                task_type="retrieval_query"
            )
            query_embedding = query_embedding_response["embedding"]
            
            # Query ChromaDB for similar documents
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Extract the retrieved documents
            retrieved_documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            
            # Check if any documents were retrieved
            if not retrieved_documents or len(retrieved_documents) == 0:
                return {
                    "response": "I don't have specific information about that in my knowledge base. Is there something else I can help with, or would you like me to connect you with a representative?",
                    "documents": [],
                    "distances": [],
                    "metadatas": []
                }
            
            # Format the prompt with clear instructions for customer service
            sanitized_query = query_text.replace("\n", " ")
            prompt = self._build_customer_service_prompt(sanitized_query, retrieved_documents, metadatas)
            
            try:
                # Generate the response with optimized parameters for customer service
                model = genai.GenerativeModel(model_name=self.generation_model)
                generation_config = {
                    "temperature": 0.3,     # Lower temperature for more consistent responses
                    "top_p": 0.85,          # More focused on high probability tokens
                    "top_k": 40,            
                    "max_output_tokens": 800,  # Limited length for concise responses
                }
                
                response = model.generate_content(prompt, generation_config=generation_config)
                ai_response = response.text
            except Exception as e:
                print(f"Error in generate_content: {str(e)}")
                ai_response = "I'm experiencing a brief technical difficulty retrieving that information. Is there something else I can help you with in the meantime?"
            
            return {
                "response": ai_response,
                "documents": retrieved_documents,
                "distances": distances,
                "metadatas": metadatas
            }
            
        except Exception as e:
            print(f"Error querying RAG pipeline: {str(e)}")
            return {
                "response": "I apologize for the inconvenience, but I'm having trouble accessing our knowledge base right now. Please try again shortly or contact our support team for immediate assistance.",
                "documents": [],
                "distances": [],
                "metadatas": []
            }

    def _build_customer_service_prompt(self, query: str, documents: List[str], metadatas: List[Dict]) -> str:
        """
        Build a prompt optimized for customer service responses.
        
        Args:
            query: The user's query
            documents: Retrieved relevant documents
            metadatas: Metadata for the documents
            
        Returns:
            Formatted prompt for the generative model
        """
        prompt = f"""You are NOVA, Nexobotics' helpful customer service AI assistant. Your goal is to provide accurate, 
helpful responses to customer inquiries based on the information in our knowledge base.

Guidelines for your responses:
1. Be warm, friendly, and professional
2. Answer directly and concisely from the provided information
3. If the knowledge base doesn't contain the answer, politely say so and offer to help in other ways
4. Never make up information that isn't in the knowledge base
5. Format your responses clearly, using short paragraphs and bullet points when appropriate
6. Always maintain a helpful, customer-first tone

CUSTOMER QUESTION: {query}

RELEVANT INFORMATION FROM KNOWLEDGE BASE:
"""
        
        # Add each document with its category if available
        for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
            category = metadata.get("category", "general information")
            prompt += f"[{category.upper()}] {doc}\n\n"
            
        prompt += "YOUR RESPONSE:"
        return prompt

# Singleton instance of the RAG pipeline
_rag_pipeline_instance = None

async def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create a singleton RAG pipeline instance.
    
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline_instance
    
    if _rag_pipeline_instance is None:
        # Get API key from environment
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Get persistence directory from environment or use default
        persist_dir = os.environ.get('CHROMA_PERSIST_DIR', "./chromadb_data")
        
        # Create RAG pipeline
        _rag_pipeline_instance = RAGPipeline(
            api_key=api_key,
            collection_name="nexobotics_knowledge_base",
            persist_directory=persist_dir,
            generation_model="models/gemini-1.5-flash",
            embedding_model="models/embedding-001"
        )
    
    return _rag_pipeline_instance

async def query_rag(query_text: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Query the RAG pipeline with a user question.
    
    Args:
        query_text: The query text from the user
        top_k: Number of top results to retrieve
        
    Returns:
        Dictionary containing the response and retrieved documents
    """
    rag_pipeline = await get_rag_pipeline()
    return await rag_pipeline.query(query_text, top_k) 