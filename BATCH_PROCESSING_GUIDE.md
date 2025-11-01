# Batch PDF Processing Guide

This guide explains how to process all PDFs from the `data` folder using the new batch processing functionality.

## Overview

Three methods are available for batch processing PDFs:

1. **Simple Python Script** - Easiest way, just run one command
2. **Command-line Tool** - Flexible CLI with options
3. **FastAPI Endpoint** - REST API for integration

---

## Method 1: Simple Python Script (Recommended)

### Usage

Run the pre-configured script to process all PDFs in `data/papers`:

```bash
cd rag-groq-llm
python batch_process_pdfs.py
```

This will:
- Find all PDFs in `data/papers` (including subdirectories)
- Extract full text from each PDF
- Index them into the RAG system
- Display processing results

### Example Output

```
======================================================================
PDF Batch Processor for RAG System
======================================================================

Searching for PDFs in: /path/to/data/papers

Found 5 PDF file(s) in /path/to/data/papers
Processing: sample.pdf
Processing: research_paper.pdf
...
Indexing 5 document(s) into RAG system...
✓ Indexing complete!

======================================================================
PROCESSING RESULTS
======================================================================
Status:              success
Total PDFs found:    5
Successfully indexed: 5
Failed:              0
======================================================================

✓ All PDFs successfully indexed!
You can now query the RAG system with questions about your documents.
```

---

## Method 2: Command-line Tool

### Usage

For more control, use the batch processor module directly:

```bash
cd rag-groq-llm
python -m src.batch_pdf_processor data/papers
```

### Options

```bash
# Process only the specified directory (no subdirectories)
python -m src.batch_pdf_processor data/papers --no-recursive

# Extract only abstracts instead of full text
python -m src.batch_pdf_processor data/papers --extract-mode abstract

# Extract structured sections (abstract, intro, conclusion)
python -m src.batch_pdf_processor data/papers --extract-mode sections

# Use custom base ID for indexed documents
python -m src.batch_pdf_processor data/papers --base-id my_papers

# Combine options
python -m src.batch_pdf_processor data/papers --no-recursive --extract-mode abstract --base-id research_batch
```

### Available Extract Modes

- **`full`** (default) - Extract all text from PDF
- **`abstract`** - Extract abstract section only (falls back to full if not found)
- **`sections`** - Extract structured sections (abstract, introduction, conclusion)

---

## Method 3: FastAPI Endpoint

### Start the API Server

```bash
cd rag-groq-llm/src
uvicorn app:app --reload
```

### Call the Batch Processing Endpoint

**Endpoint:** `POST /batch-index-pdfs`

#### Example with curl

```bash
# Basic usage - process all PDFs in data/papers
curl -X POST "http://localhost:8000/batch-index-pdfs" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data/papers",
    "recursive": true,
    "extract_mode": "full",
    "base_id": "pdf_batch"
  }'
```

#### Example with Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/batch-index-pdfs",
    json={
        "directory": "data/papers",
        "recursive": True,
        "extract_mode": "full",
        "base_id": "pdf_batch"
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Indexed: {result['indexed']} documents")
```

#### Request Body Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `directory` | string | required | Path to directory containing PDFs |
| `recursive` | boolean | `true` | Search subdirectories |
| `extract_mode` | string | `"full"` | Extraction mode: `"full"`, `"abstract"`, or `"sections"` |
| `base_id` | string | `"pdf_batch"` | Base identifier for indexed documents |

#### Response Format

```json
{
  "status": "success",
  "total_found": 5,
  "processed": 5,
  "indexed": 5,
  "failed": 0,
  "failed_files": []
}
```

---

## Using the Batch Processor in Your Code

### Example: Custom Python Script

```python
from src.batch_pdf_processor import BatchPDFProcessor
from src.rag_pipeline import SimpleRAG

# Create RAG instance
rag = SimpleRAG()

# Create batch processor
processor = BatchPDFProcessor(rag_instance=rag)

# Process PDFs
result = processor.batch_process_and_index(
    directory="data/papers",
    recursive=True,
    extract_mode="full",
    base_id="my_batch"
)

print(f"Indexed {result['indexed']} documents")

# Now query the system
answer = rag.answer("What are the main findings?")
print(answer["answer"])
```

### Example: Find PDFs Only

```python
from src.batch_pdf_processor import BatchPDFProcessor

processor = BatchPDFProcessor()

# Just find PDFs without processing
pdf_files = processor.find_pdfs("data/papers", recursive=True)
print(f"Found {len(pdf_files)} PDFs:")
for pdf in pdf_files:
    print(f"  - {pdf}")
```

### Example: Process Single PDF

```python
from src.batch_pdf_processor import BatchPDFProcessor

processor = BatchPDFProcessor()

# Process one PDF
result = processor.process_pdf(
    "data/papers/sample.pdf",
    extract_mode="full"
)

if result:
    print(f"Extracted text: {result['text'][:200]}...")
    print(f"Metadata: {result['metadata']}")
```

---

## Directory Structure

Expected directory layout:

```
rag-groq-llm/
├── data/
│   ├── papers/              ← Put your PDFs here
│   │   ├── paper1.pdf
│   │   ├── paper2.pdf
│   │   └── subfolder/
│   │       └── paper3.pdf
│   └── web_pages/
├── src/
│   ├── batch_pdf_processor.py   ← New batch processor
│   ├── app.py                   ← FastAPI app (updated)
│   └── ...
└── batch_process_pdfs.py        ← Simple script to run
```

---

## After Processing

Once PDFs are indexed, query them using any of these methods:

### Command Line (interactive)

```bash
cd rag-groq-llm/src
python rag_pipeline.py
```

### FastAPI

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings in the research papers?",
    "k": 5
  }'
```

### Python Script

```python
from src.rag_pipeline import SimpleRAG

rag = SimpleRAG()
result = rag.answer("What are the main findings?", k=5)
print(result["answer"])
```

---

## Troubleshooting

### No PDFs Found

**Problem:** `No PDF files found in directory`

**Solutions:**
- Check that PDFs exist in the specified directory
- Verify the directory path is correct
- Use absolute paths if relative paths don't work

### Extraction Failed

**Problem:** `No text extracted from PDF`

**Solutions:**
- Ensure PDF is not encrypted or password-protected
- Try different `extract_mode` options
- Check PDF is not just scanned images (requires OCR)

### Indexing Failed

**Problem:** `Failed to index documents`

**Solutions:**
- Check GROQ_API_KEY is set in `.env` file
- Ensure ChromaDB is accessible
- Verify sufficient disk space for embeddings

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solutions:**
```bash
# Install dependencies
pip install -r requirements.txt

# Or install specific packages
pip install pdfplumber sentence-transformers chromadb
```

---

## Advanced Configuration

### Custom Data Directory

Edit `batch_process_pdfs.py` to change the default directory:

```python
# Change this line:
data_dir = os.path.join(os.path.dirname(__file__), "data", "papers")

# To your custom path:
data_dir = "/path/to/your/pdfs"
```

### Filter PDFs by Name Pattern

```python
import os
from src.batch_pdf_processor import BatchPDFProcessor

processor = BatchPDFProcessor()

# Find all PDFs
all_pdfs = processor.find_pdfs("data/papers")

# Filter by pattern (e.g., only PDFs starting with "research_")
filtered_pdfs = [p for p in all_pdfs if os.path.basename(p).startswith("research_")]

# Process filtered PDFs manually
for pdf_path in filtered_pdfs:
    result = processor.process_pdf(pdf_path)
    if result:
        # Index individually or collect and batch index
        pass
```

---

## Notes

- **First run**: The first PDF processed will download the sentence-transformers model (~90MB)
- **Re-indexing**: Running batch processing again will add documents, not replace existing ones
- **Performance**: Processing time depends on PDF size and count (~1-5 seconds per PDF)
- **Chunk size**: Now uses 2000 characters per chunk (improved from 1000) for better context
- **Text quality**: The improved text cleaning preserves paragraph structure

---

## Summary

**Quickest way to get started:**

```bash
cd rag-groq-llm
python batch_process_pdfs.py
```

That's it! Your PDFs are now indexed and ready to query.
