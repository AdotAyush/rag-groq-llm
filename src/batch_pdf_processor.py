import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from .tools.pdf_scraper import PDFScraper
from .rag_pipeline import SimpleRAG

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BatchPDFProcessor:
    """
    Batch processor for indexing multiple PDF files from a directory.
    """

    def __init__(self, rag_instance: Optional[SimpleRAG] = None):
        """
        Initialize the batch processor.

        Args:
            rag_instance: Optional SimpleRAG instance. Creates new one if not provided.
        """
        self.rag = rag_instance or SimpleRAG()
        self.pdf_scraper = PDFScraper("")  # Initialize with empty path

    def find_pdfs(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Find all PDF files in a directory.

        Args:
            directory: Path to directory to search
            recursive: If True, search subdirectories as well

        Returns:
            List of absolute paths to PDF files
        """
        pdf_files = []
        directory_path = Path(directory)

        if not directory_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return []

        if not directory_path.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return []

        if recursive:
            # Search recursively
            pdf_files = list(directory_path.rglob("*.pdf"))
        else:
            # Search only in the specified directory
            pdf_files = list(directory_path.glob("*.pdf"))

        # Convert to absolute paths and strings
        pdf_files = [str(p.absolute()) for p in pdf_files]

        logger.info(f"Found {len(pdf_files)} PDF file(s) in {directory}")
        return pdf_files

    def process_pdf(self, pdf_path: str, extract_mode: str = "full") -> Optional[Dict[str, str]]:
        """
        Process a single PDF file.

        Args:
            pdf_path: Path to PDF file
            extract_mode: "full", "abstract", or "sections" (default: "full")

        Returns:
            Dictionary with extracted text and metadata, or None if extraction failed
        """
        try:
            logger.info(f"Processing: {pdf_path}")

            # Extract sections from PDF
            sections = self.pdf_scraper.extract_sections(pdf_path)

            # Determine what text to use
            if extract_mode == "full":
                text = sections.get("full", "")
            elif extract_mode == "abstract":
                text = sections.get("abstract", "") or sections.get("full", "")
            elif extract_mode == "sections":
                # Combine all sections
                text = "\n\n".join([
                    f"=== {key.upper()} ===\n{value}"
                    for key, value in sections.items()
                    if value and key != "full"
                ])
                if not text:
                    text = sections.get("full", "")
            else:
                logger.warning(f"Unknown extract_mode '{extract_mode}', using 'full'")
                text = sections.get("full", "")

            if not text or not text.strip():
                logger.warning(f"No text extracted from {pdf_path}")
                return None

            # Create metadata
            filename = os.path.basename(pdf_path)
            file_id = os.path.splitext(filename)[0]

            return {
                "text": text,
                "metadata": {
                    "filename": filename,
                    "file_path": pdf_path,
                    "file_id": file_id,
                    "extract_mode": extract_mode
                }
            }

        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
            return None

    def batch_process_and_index(
        self,
        directory: str,
        recursive: bool = True,
        extract_mode: str = "full",
        base_id: str = "pdf_batch"
    ) -> Dict[str, any]:
        """
        Find all PDFs in a directory, extract text, and index them in the RAG system.

        Args:
            directory: Path to directory containing PDFs
            recursive: If True, search subdirectories (default: True)
            extract_mode: "full", "abstract", or "sections" (default: "full")
            base_id: Base identifier for indexed documents (default: "pdf_batch")

        Returns:
            Dictionary with processing results
        """
        # Find all PDFs
        pdf_files = self.find_pdfs(directory, recursive=recursive)

        if not pdf_files:
            logger.warning(f"No PDF files found in {directory}")
            return {
                "status": "no_files",
                "total_found": 0,
                "processed": 0,
                "indexed": 0,
                "failed": 0
            }

        # Process each PDF
        documents = []
        metadatas = []
        ids = []
        failed_files = []

        for pdf_path in pdf_files:
            result = self.process_pdf(pdf_path, extract_mode=extract_mode)

            if result:
                documents.append(result["text"])
                metadatas.append(result["metadata"])
                ids.append(f"{base_id}_{result['metadata']['file_id']}")
            else:
                failed_files.append(pdf_path)

        # Index all successfully processed documents
        if documents:
            logger.info(f"Indexing {len(documents)} document(s) into RAG system...")
            try:
                self.rag.index_documents(documents, metadatas, ids)
                logger.info("✓ Indexing complete!")
            except Exception as e:
                logger.error(f"Failed to index documents: {e}")
                return {
                    "status": "indexing_failed",
                    "error": str(e),
                    "total_found": len(pdf_files),
                    "processed": len(documents),
                    "indexed": 0,
                    "failed": len(failed_files) + len(documents)
                }

        result = {
            "status": "success",
            "total_found": len(pdf_files),
            "processed": len(documents),
            "indexed": len(documents),
            "failed": len(failed_files),
            "failed_files": failed_files
        }

        logger.info(f"Batch processing complete: {result}")
        return result


# Standalone script functionality
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch process and index PDF files into RAG system"
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing PDF files to process"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not search subdirectories"
    )
    parser.add_argument(
        "--extract-mode",
        type=str,
        choices=["full", "abstract", "sections"],
        default="full",
        help="Extraction mode: full (default), abstract, or sections"
    )
    parser.add_argument(
        "--base-id",
        type=str,
        default="pdf_batch",
        help="Base identifier for indexed documents (default: pdf_batch)"
    )

    args = parser.parse_args()

    # Create processor and run
    processor = BatchPDFProcessor()
    result = processor.batch_process_and_index(
        directory=args.directory,
        recursive=not args.no_recursive,
        extract_mode=args.extract_mode,
        base_id=args.base_id
    )

    # Print results
    print("\n" + "="*60)
    print("BATCH PROCESSING RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Total PDFs found: {result['total_found']}")
    print(f"Successfully processed: {result['processed']}")
    print(f"Successfully indexed: {result['indexed']}")
    print(f"Failed: {result['failed']}")

    if result.get('failed_files'):
        print(f"\nFailed files:")
        for f in result['failed_files']:
            print(f"  - {f}")

    print("="*60)

    # Exit with appropriate code
    sys.exit(0 if result['status'] == 'success' else 1)
