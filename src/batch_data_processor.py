import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from .tools.pdf_scraper import PDFScraper
from .rag_pipeline import SimpleRAG

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BatchDataProcessor:
    """
    Batch processor for indexing PDFs and text files from directories.
    Handles both PDF extraction and pre-scraped web content.
    """

    def __init__(self, rag_instance: Optional[SimpleRAG] = None):
        """
        Initialize the batch processor.

        Args:
            rag_instance: Optional SimpleRAG instance. Creates new one if not provided.
        """
        self.rag = rag_instance or SimpleRAG()
        self.pdf_scraper = PDFScraper("")

    def find_data_files(self, directory: str, recursive: bool = True) -> Dict[str, List[str]]:
        """
        Find all PDF and text files in a directory.

        Args:
            directory: Path to directory to search
            recursive: If True, search subdirectories as well

        Returns:
            Dictionary with 'pdfs' and 'texts' lists of file paths
        """
        directory_path = Path(directory)

        if not directory_path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return {"pdfs": [], "texts": []}

        if not directory_path.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return {"pdfs": [], "texts": []}

        if recursive:
            pdf_files = list(directory_path.rglob("*.pdf"))
            txt_files = list(directory_path.rglob("*.txt"))
        else:
            pdf_files = list(directory_path.glob("*.pdf"))
            txt_files = list(directory_path.glob("*.txt"))

        # Convert to absolute paths
        pdfs = [str(p.absolute()) for p in pdf_files]
        texts = [str(p.absolute()) for p in txt_files]

        logger.info(f"Found {len(pdfs)} PDF(s) and {len(texts)} text file(s) in {directory}")

        return {"pdfs": pdfs, "texts": texts}

    def process_pdf(self, pdf_path: str, extract_mode: str = "full") -> Optional[Dict[str, str]]:
        """
        Process a single PDF file.

        Args:
            pdf_path: Path to PDF file
            extract_mode: "full", "abstract", or "sections"

        Returns:
            Dictionary with extracted text and metadata, or None if extraction failed
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")

            sections = self.pdf_scraper.extract_sections(pdf_path)

            if extract_mode == "full":
                text = sections.get("full", "")
            elif extract_mode == "abstract":
                text = sections.get("abstract", "") or sections.get("full", "")
            elif extract_mode == "sections":
                text = "\n\n".join([
                    f"=== {key.upper()} ===\n{value}"
                    for key, value in sections.items()
                    if value and key != "full"
                ])
                if not text:
                    text = sections.get("full", "")
            else:
                text = sections.get("full", "")

            if not text or not text.strip():
                logger.warning(f"No text extracted from {pdf_path}")
                return None

            filename = os.path.basename(pdf_path)
            file_id = os.path.splitext(filename)[0]

            return {
                "text": text,
                "metadata": {
                    "filename": filename,
                    "file_path": pdf_path,
                    "file_id": file_id,
                    "file_type": "pdf",
                    "extract_mode": extract_mode
                }
            }

        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            return None

    def process_text_file(self, text_path: str) -> Optional[Dict[str, str]]:
        """
        Process a single text file (e.g., from web scraper).

        Args:
            text_path: Path to text file

        Returns:
            Dictionary with text content and metadata, or None if reading failed
        """
        try:
            logger.info(f"Processing text file: {text_path}")

            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text or not text.strip():
                logger.warning(f"No content in {text_path}")
                return None

            filename = os.path.basename(text_path)
            file_id = os.path.splitext(filename)[0]

            return {
                "text": text,
                "metadata": {
                    "filename": filename,
                    "file_path": text_path,
                    "file_id": file_id,
                    "file_type": "text"
                }
            }

        except Exception as e:
            logger.error(f"Failed to process text file {text_path}: {e}")
            return None

    def batch_process_and_index(
        self,
        directory: str,
        recursive: bool = True,
        extract_mode: str = "full",
        base_id: str = "doc_batch",
        process_pdfs: bool = True,
        process_texts: bool = True
    ) -> Dict[str, any]:
        """
        Find all data files in a directory, extract content, and index in RAG system.

        Args:
            directory: Path to directory containing data files
            recursive: If True, search subdirectories (default: True)
            extract_mode: "full", "abstract", or "sections" for PDFs (default: "full")
            base_id: Base identifier for indexed documents (default: "doc_batch")
            process_pdfs: Process PDF files (default: True)
            process_texts: Process text files (default: True)

        Returns:
            Dictionary with processing results
        """
        # Find all data files
        files = self.find_data_files(directory, recursive=recursive)

        total_found = len(files["pdfs"]) + len(files["texts"])

        if total_found == 0:
            logger.warning(f"No data files found in {directory}")
            return {
                "status": "no_files",
                "total_found": 0,
                "pdfs_found": 0,
                "texts_found": 0,
                "processed": 0,
                "indexed": 0,
                "failed": 0
            }

        # Process files
        documents = []
        metadatas = []
        ids = []
        failed_files = []

        # Process PDFs
        if process_pdfs:
            for pdf_path in files["pdfs"]:
                result = self.process_pdf(pdf_path, extract_mode=extract_mode)
                if result:
                    documents.append(result["text"])
                    metadatas.append(result["metadata"])
                    ids.append(f"{base_id}_{result['metadata']['file_id']}")
                else:
                    failed_files.append(pdf_path)

        # Process text files
        if process_texts:
            for text_path in files["texts"]:
                result = self.process_text_file(text_path)
                if result:
                    documents.append(result["text"])
                    metadatas.append(result["metadata"])
                    ids.append(f"{base_id}_{result['metadata']['file_id']}")
                else:
                    failed_files.append(text_path)

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
                    "total_found": total_found,
                    "pdfs_found": len(files["pdfs"]),
                    "texts_found": len(files["texts"]),
                    "processed": len(documents),
                    "indexed": 0,
                    "failed": len(failed_files) + len(documents)
                }

        result = {
            "status": "success",
            "total_found": total_found,
            "pdfs_found": len(files["pdfs"]),
            "texts_found": len(files["texts"]),
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
        description="Batch process and index PDF and text files into RAG system"
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing data files to process"
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
        help="Extraction mode for PDFs: full (default), abstract, or sections"
    )
    parser.add_argument(
        "--base-id",
        type=str,
        default="doc_batch",
        help="Base identifier for indexed documents (default: doc_batch)"
    )
    parser.add_argument(
        "--pdfs-only",
        action="store_true",
        help="Process only PDF files, skip text files"
    )
    parser.add_argument(
        "--texts-only",
        action="store_true",
        help="Process only text files, skip PDFs"
    )

    args = parser.parse_args()

    # Determine what to process
    process_pdfs = not args.texts_only
    process_texts = not args.pdfs_only

    # Create processor and run
    processor = BatchDataProcessor()
    result = processor.batch_process_and_index(
        directory=args.directory,
        recursive=not args.no_recursive,
        extract_mode=args.extract_mode,
        base_id=args.base_id,
        process_pdfs=process_pdfs,
        process_texts=process_texts
    )

    # Print results
    print("\n" + "="*60)
    print("BATCH PROCESSING RESULTS")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Total files found: {result['total_found']} (PDFs: {result['pdfs_found']}, Texts: {result['texts_found']})")
    print(f"Successfully processed: {result['processed']}")
    print(f"Successfully indexed: {result['indexed']}")
    print(f"Failed: {result['failed']}")

    if result.get('failed_files'):
        print(f"\nFailed files:")
        for f in result['failed_files']:
            print(f"  - {f}")

    print("="*60)

    sys.exit(0 if result['status'] == 'success' else 1)
