"""
RAG Pipeline Module - Compatible with google-generativeai 0.8.4
This module provides a Retrieval-Augmented Generation pipeline 
using Google's Generative AI models and ChromaDB for vector storage.
"""

import os
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, Tuple
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions

class RAGPipeline:
    """Retrieval-Augmented Generation Pipeline using Google's Generative AI and ChromaDB"""
    
    def __init__(self, 
                 api_key: str,
                 collection_name: str = "knowledge_base",
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
        self.persist_directory = persist_directory
        
        # Configure Google Generative AI
        genai.configure(api_key=api_key)
        
        # Initialize ChromaDB
        self._init_chroma()
        
    def _init_chroma(self):
        """Initialize ChromaDB client and collection"""
        if self.persist_directory:
            self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        else:
            self.chroma_client = chromadb.Client()
        
        # Create or get the collection
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            # Collection doesn't exist, create a new one
            self.collection = self.chroma_client.create_collection(name=self.collection_name)
            print(f"Initialized collection with knowledge base data...")
            
            # Initialize with some basic documents if needed
            self._init_with_sample_data()
            
    def _init_with_sample_data(self):
        """Initialize the collection with sample data if needed"""
        # This is a placeholder for any initial data you want to add
        # For testing purposes, you might want to add some documents
        sample_docs = [
            "Nexobotics helps businesses improve customer service with AI.",
            "Customer satisfaction is critical for business success.",
            "AI chatbots can handle routine customer inquiries efficiently."
        ]
        
        sample_ids = [f"sample_{i}" for i in range(len(sample_docs))]
        sample_metadata = [{"source": "initial_data"} for _ in range(len(sample_docs))]
        
        try:
            # Generate embeddings for documents
            document_embeddings = []
            for doc in sample_docs:
                embedding_response = genai.embed_content(
                    model=self.embedding_model,
                    content=doc,
                    task_type="retrieval_document"
                )
                document_embeddings.append(embedding_response["embedding"])
            
            # Add documents to the collection
            self.collection.add(
                documents=sample_docs,
                embeddings=document_embeddings,
                ids=sample_ids,
                metadatas=sample_metadata
            )
            print(f"Successfully indexed {len(sample_docs)} documents")
        except Exception as e:
            print(f"Error initializing with sample data: {str(e)}")

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
            
    async def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG pipeline to get a response based on retrieved context.
        
        Args:
            query_text: The query text
            top_k: Number of top results to retrieve
            
        Returns:
            Dictionary containing the response and retrieved documents
        """
        try:
            # Generate embedding for the query using "retrieval_query" task type
            query_embedding_response = genai.embed_content(
                model=self.embedding_model,
                content=query_text,
                task_type="retrieval_query"
            )
            query_embedding = query_embedding_response["embedding"]
            
            # Query ChromaDB for similar documents - increased to get more context
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Extract the retrieved documents
            retrieved_documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            # Check if any documents were retrieved
            if not retrieved_documents or len(retrieved_documents) == 0:
                return {
                    "response": "I don't have specific information about that in my knowledge base. Would you like me to connect you with a customer service representative who can help?",
                    "documents": [],
                    "distances": []
                }
            
            # Format the prompt for customer service
            query_oneline = query_text.replace("\n", " ")
            prompt = f"""You are NOVA, a helpful customer service assistant for Nexobotics. Answer the user's question based on the information provided in the passages below.

If the information needed isn't in the passages, politely explain that you don't have that specific detail 
and suggest how the user could get help (e.g., 'For more details, please contact our support team').

Your responses should be:
- Friendly and conversational
- Clear and concise
- Helpful and solution-oriented
- Professional but approachable

QUESTION: {query_oneline}
"""
            
            # Add the retrieved documents to the prompt
            for i, passage in enumerate(retrieved_documents):
                passage_oneline = passage.replace("\n", " ")
                prompt += f"PASSAGE {i+1}: {passage_oneline}\n"
            
            print(f"Using model {self.generation_model} for customer service RAG response")
            
            try:
                # Generate the response with tuned parameters for customer service
                model = genai.GenerativeModel(model_name=self.generation_model)
                generation_config = {
                    "temperature": 0.4,     # Lower temperature for more factual responses
                    "top_p": 0.85,          # More focused on high probability tokens
                    "top_k": 40,            
                    "max_output_tokens": 1024,
                }
                response = model.generate_content(prompt, generation_config=generation_config)
                ai_response = response.text
            except Exception as e:
                print(f"Error in generate_content: {str(e)}")
                # Friendly error message
                ai_response = "I apologize, but I'm having trouble accessing that information right now. Is there something else I can help you with?"
            
            return {
                "response": ai_response,
                "documents": retrieved_documents,
                "distances": distances
            }
            
        except Exception as e:
            print(f"Error querying RAG pipeline: {str(e)}")
            return {
                "response": "I'm having technical difficulties at the moment. Please try again in a moment or reach out to our support team if this persists.",
                "documents": [],
                "distances": []
            }

# Singleton instance of the RAG pipeline
_rag_pipeline_instance = None

async def get_rag_pipeline(persist_directory: Optional[str] = None) -> RAGPipeline:
    """
    Get or create a RAG pipeline instance.
    
    Args:
        persist_directory: Optional directory to persist the ChromaDB database
        
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline_instance
    
    if _rag_pipeline_instance is None:
        # Get API key from environment
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Use the persistent directory we created
        persist_dir = "./chromadb_data"
        
        # Create RAG pipeline with our persistent collection
        _rag_pipeline_instance = RAGPipeline(
            api_key=api_key,
            collection_name="customer_service_best_practices",  # Use the collection we created
            persist_directory=persist_dir,  # Use our persistent directory
            generation_model="models/gemini-1.5-flash",  # Use confirmed working model
            embedding_model="models/embedding-001"
        )
    
    return _rag_pipeline_instance

async def query_rag(query_text: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Query the RAG pipeline.
    
    Args:
        query_text: The query text
        top_k: Number of top results to retrieve
        
    Returns:
        Dictionary containing the response and retrieved documents
    """
    rag_pipeline = await get_rag_pipeline()
    return await rag_pipeline.query(query_text, top_k) 