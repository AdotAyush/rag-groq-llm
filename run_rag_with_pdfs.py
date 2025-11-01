#!/usr/bin/env python3
"""
Complete RAG workflow: Index all data (PDFs and text files) and start interactive Q&A.
This script will:
1. Find and index all PDFs and text files from data folder
2. Start an interactive Q&A session
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.batch_data_processor import BatchDataProcessor
from src.rag_pipeline import SimpleRAG


def main():
    """
    Index all data files (PDFs and text files) and start interactive Q&A.
    """
    print("="*70)
    print("RAG System - Complete Data Indexing")
    print("="*70)
    print()

    # Set the data directory path
    data_dir = os.path.join(os.path.dirname(__file__), "data")

    # Create RAG instance (will be shared)
    rag = SimpleRAG()

    # Create batch processor with the same RAG instance
    processor = BatchDataProcessor(rag_instance=rag)

    # Step 1: Index all data from data folder
    print("Step 1: Indexing all data files (PDFs and text files)...")
    print(f"Searching in: {data_dir}")
    print()

    result = processor.batch_process_and_index(
        directory=data_dir,
        recursive=True,
        extract_mode="full",
        base_id="doc",
        process_pdfs=True,
        process_texts=True
    )

    print()
    print("-"*70)
    print(f"Status: {result['status']}")
    print(f"Total files found: {result['total_found']}")
    print(f"  - PDFs: {result['pdfs_found']}")
    print(f"  - Text files: {result['texts_found']}")
    print(f"Successfully indexed: {result['indexed']}")
    print(f"Failed: {result['failed']}")
    print("-"*70)
    print()

    if result['indexed'] == 0:
        print("⚠ No documents were indexed!")
        print()
        print("To use this system:")
        print("1. Add PDF files to the 'data/papers' directory")
        print("2. Or add URLs to scrape to 'data/web_pages'")
        print("3. Run this script again")
        print()
        return 1

    print(f"✓ Successfully indexed {result['indexed']} document(s)!")
    print()

    # Step 2: Start interactive Q&A
    print("="*70)
    print("Interactive Q&A Mode")
    print("="*70)
    print("You can now ask questions about your documents.")
    print("Type 'exit' or 'quit' to stop.")
    print()

    while True:
        try:
            query = input("\nEnter your query: ").strip()

            if query.lower() in ["exit", "quit", "q"]:
                print("\nExiting RAG system...")
                break

            if not query:
                continue

            print("\nRetrieving and generating answer...\n")

            # Query the system
            result = rag.answer(query, k=5)

            # Display answer
            print("-"*70)
            print("ANSWER:")
            print("-"*70)
            print(result["answer"])
            print()

            # Display sources
            if result.get("sources"):
                print("-"*70)
                print("SOURCES:")
                print("-"*70)
                for i, source in enumerate(result["sources"], 1):
                    source_id = source.get("id", "Unknown")
                    print(f"{i}. {source_id}")
                print()

        except KeyboardInterrupt:
            print("\n\nExiting RAG system...")
            break
        except Exception as e:
            print(f"\n⚠ Error: {e}")
            print("Please try again.\n")

    print("="*70)
    print("Thank you for using the RAG system!")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
