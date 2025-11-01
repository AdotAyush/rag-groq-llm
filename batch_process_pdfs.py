#!/usr/bin/env python3
"""
Simple script to batch process all PDFs in the data folder and index them.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.batch_pdf_processor import BatchPDFProcessor


def main():
    """
    Batch process all PDFs from the data/papers directory.
    """
    # Set the data directory path
    data_dir = os.path.join(os.path.dirname(__file__), "data", "papers")

    print("="*70)
    print("PDF Batch Processor for RAG System")
    print("="*70)
    print(f"\nSearching for PDFs in: {data_dir}")
    print()

    # Create processor
    processor = BatchPDFProcessor()

    # Process and index all PDFs
    result = processor.batch_process_and_index(
        directory=data_dir,
        recursive=True,          # Search subdirectories
        extract_mode="full",     # Extract full text ("full", "abstract", or "sections")
        base_id="pdf_batch"      # Base ID for indexed documents
    )

    # Display results
    print("\n" + "="*70)
    print("PROCESSING RESULTS")
    print("="*70)
    print(f"Status:              {result['status']}")
    print(f"Total PDFs found:    {result['total_found']}")
    print(f"Successfully indexed: {result['indexed']}")
    print(f"Failed:              {result['failed']}")

    if result.get('failed_files'):
        print(f"\nFailed files:")
        for f in result['failed_files']:
            print(f"  - {os.path.basename(f)}")

    print("="*70)

    if result['status'] == 'success' and result['indexed'] > 0:
        print("\n✓ All PDFs successfully indexed!")
        print("You can now query the RAG system with questions about your documents.")
    elif result['status'] == 'no_files':
        print(f"\n⚠ No PDF files found in {data_dir}")
        print("Please add PDF files to the data/papers directory.")
    else:
        print("\n⚠ Some errors occurred during processing.")

    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    sys.exit(main())
