#!/usr/bin/env python

"""
Knowledge Base Manager for Nexobotics RAG Chatbot

This script manages the knowledge base for the Nexobotics RAG Chatbot by creating
and populating a ChromaDB collection with document embeddings. This allows the 
chatbot to retrieve relevant information when answering customer queries.

Usage:
    python persistent_add_docs.py

Environment Variables:
    GOOGLE_API_KEY: Your Google API key for accessing embedding models
    CHROMA_PERSIST_DIR: (Optional) Directory to store the ChromaDB database
"""

import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
import chromadb

# Load environment variables
load_dotenv()

# Set Google API Key
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Get the ChromaDB persistence directory
CHROMA_PERSIST_DIR = os.environ.get('CHROMA_PERSIST_DIR', "./chromadb_data")

# Collection name
COLLECTION_NAME = "nexobotics_knowledge_base"

# Define documents to add to the knowledge base
# Replace these examples with your actual business information
DOCUMENTS = [
    # Company Information - Replace with your actual company description
    "Nexobotics is a cutting-edge robotics company specializing in industrial automation solutions. Our mission is to transform manufacturing through innovative robotic systems that increase efficiency and productivity.",
    "Founded in 2018, Nexobotics has grown to become a leader in custom robotic solutions for the manufacturing industry. We serve clients across automotive, electronics, and consumer goods sectors.",
    "Nexobotics headquarters is located in Boston, Massachusetts, with additional offices in Austin, Texas and San Jose, California. Our team consists of over 100 engineers and robotics specialists.",
    
    # Products and Services - Replace with your actual product information
    "The Nexobotics RoboArm Pro is our flagship robotic arm solution, featuring 6-axis precision movement with a reach of 1.8 meters and payload capacity of 25kg. It's ideal for pick-and-place, assembly, and material handling applications.",
    "Our Vision AI System uses advanced computer vision algorithms to enable robots to identify, sort, and handle objects with 99.8% accuracy regardless of orientation or lighting conditions.",
    "Nexobotics offers comprehensive maintenance packages including quarterly inspections, software updates, and 24/7 emergency support to ensure minimal downtime for our clients' robotic systems.",
    
    # Support Information - Replace with your actual support information
    "For technical support, customers can contact our support team at support@nexobotics.com or call our 24/7 support line at (800) 555-0123. Our average response time is under 2 hours.",
    "The Nexobotics customer portal at support.nexobotics.com provides access to documentation, troubleshooting guides, software updates, and the ability to log and track support tickets.",
    "Our standard warranty covers all hardware for 24 months and software for 36 months from the date of installation. Extended warranty options are available for up to 5 years.",
    
    # Customer Service Policies - Replace with your actual policies
    "Nexobotics offers a 30-day satisfaction guarantee for all software products. If you're not completely satisfied, we'll provide a full refund or work with you to find a better solution.",
    "Our project implementation follows a 5-phase approach: requirements gathering, solution design, development, installation, and post-deployment support to ensure successful integration.",
    "Training services include initial operator training, advanced maintenance training, and custom curriculum development for your technical team to ensure maximum ROI on your robotics investment."
]

def main():
    """Add documents to a persistent ChromaDB collection"""
    try:
        # Create persistent directory if it doesn't exist
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Create ChromaDB client
        print(f"Initializing persistent ChromaDB client in {CHROMA_PERSIST_DIR}...")
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # Get or create collection
        try:
            collection = chroma_client.get_collection(name=COLLECTION_NAME)
            print(f"Using existing collection: {COLLECTION_NAME}")
            
            # Delete existing collection to start fresh
            print(f"Deleting existing collection to start fresh...")
            chroma_client.delete_collection(name=COLLECTION_NAME)
            collection = chroma_client.create_collection(name=COLLECTION_NAME)
            print(f"Created new collection: {COLLECTION_NAME}")
        except Exception:
            collection = chroma_client.create_collection(name=COLLECTION_NAME)
            print(f"Created new collection: {COLLECTION_NAME}")
        
        # Generate document IDs and metadata
        doc_ids = [f"doc_{i+1}" for i in range(len(DOCUMENTS))]
        
        # Create more detailed metadata for better filtering capabilities
        metadata = []
        for i, doc in enumerate(DOCUMENTS):
            if i < 3:
                category = "company_info"
            elif i < 6:
                category = "products_services"
            elif i < 9:
                category = "support_info"
            else:
                category = "policies"
                
            metadata.append({
                "source": "nexobotics_knowledge_base",
                "category": category,
                "doc_id": doc_ids[i]
            })
        
        # Generate embeddings
        print("Generating embeddings for documents...")
        embeddings = []
        embedding_model = "models/embedding-001"
        
        for doc in DOCUMENTS:
            try:
                embedding_response = genai.embed_content(
                    model=embedding_model,
                    content=doc,
                    task_type="retrieval_document"
                )
                embeddings.append(embedding_response["embedding"])
            except Exception as e:
                print(f"Error generating embedding: {str(e)}")
                return
        
        # Add documents to collection
        print(f"Adding {len(DOCUMENTS)} documents to the collection...")
        collection.add(
            documents=DOCUMENTS,
            embeddings=embeddings,
            ids=doc_ids,
            metadatas=metadata
        )
        
        print("Documents added successfully!")
        
        # Test a query to verify
        test_query = "What products does Nexobotics offer?"
        print(f"\nTesting query: {test_query}")
        
        # Generate query embedding
        query_embedding_response = genai.embed_content(
            model=embedding_model,
            content=test_query,
            task_type="retrieval_query"
        )
        query_embedding = query_embedding_response["embedding"]
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        # Print retrieved documents
        retrieved_documents = results["documents"][0]
        print("\nRetrieved documents:")
        for i, doc in enumerate(retrieved_documents):
            print(f"{i+1}. {doc}")
        
        print("\nKnowledge base is now ready for the RAG pipeline to use!")
        print(f"Location: {os.path.abspath(CHROMA_PERSIST_DIR)}")
        print(f"Collection name: {COLLECTION_NAME}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 