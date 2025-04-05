#!/usr/bin/env python
"""
Move Cleaned Files Script

This script moves the cleaned files to their proper locations in the
directory structure. Run this script from the groq-3/cleaned directory.
"""

import os
import shutil
import sys

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def move_file(source, dest):
    """Move file from source to destination"""
    if os.path.exists(source):
        # Create the destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest)
        create_directory(dest_dir)
        
        # Copy the file
        shutil.copy2(source, dest)
        print(f"Copied: {source} -> {dest}")
    else:
        print(f"Error: Source file not found: {source}")

def main():
    """Main function to move files"""
    # Check if we're in the right directory
    if not os.path.basename(os.getcwd()).endswith('cleaned'):
        print("Please run this script from the groq-3/cleaned directory")
        sys.exit(1)
    
    # Define the file mappings (source, destination)
    file_mappings = [
        # Backend files
        ('index.py', '../api/index.py'),
        ('rag_pipeline.py', '../api/rag_pipeline.py'),
        ('persistent_add_docs.py', '../api/persistent_add_docs.py'),
        
        # Frontend files
        # Note: We don't copy chatbot.js because it's already in the right place
        
        # Root files
        ('README.md', '../README.md'),
        ('USAGE_GUIDE.md', '../USAGE_GUIDE.md'),
        ('WEBSITE_INTEGRATION.md', '../WEBSITE_INTEGRATION.md'),
        ('test_chatbot.html', '../test_chatbot.html'),
        ('.env.example', '../.env.example'),
        ('requirements.txt', '../requirements.txt'),
    ]
    
    # Move each file
    for source, dest in file_mappings:
        move_file(source, dest)
    
    print("\nAll files have been moved successfully!")
    print("\nNEXT STEPS:")
    print("1. Copy your Google API key to the .env file")
    print("2. Run 'python api/persistent_add_docs.py' to initialize the knowledge base")
    print("3. Start the server with 'python api/index.py'")
    print("4. Open 'test_chatbot.html' in your browser to test the chatbot")

if __name__ == "__main__":
    main() 