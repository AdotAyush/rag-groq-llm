# How to Fix: RAG Not Finding Your Data

## Problem

When you run `python src/rag_pipeline.py` and ask "What is RAG?", it doesn't find the information even though you have data about RAG in your `data/web_pages/` folder.

## Root Cause

The `rag_pipeline.py` script only indexes **3 demo sample texts** (about Groq, LangChain, and Chroma) when you run it. It does NOT automatically index your PDF files or web scraper text files from the `data/` folder.

Your actual data files are sitting in:
- `data/web_pages/www.ibm.com_topics_what-is-rag.txt` ← **Has info about RAG!**
- `data/web_pages/en.wikipedia.org_wiki_Large_language_model.txt`
- `data/web_pages/arxiv.org_.txt`
- `data/papers/sample.pdf`
- And more...

But they're **not indexed**, so the RAG system can't retrieve them.

## Solution: Index Your Data First

You need to **index your data files BEFORE** querying the system.

---

## ✅ RECOMMENDED: Use the Complete Workflow Script

### Simple One-Command Solution

```bash
cd rag-groq-llm
python run_rag_with_pdfs.py
```

This script will:
1. **Automatically find and index ALL data files** (both PDFs and text files) from your `data/` folder
2. **Start an interactive Q&A session** where you can ask questions

### Example Output

```
======================================================================
RAG System - Complete Data Indexing
======================================================================

Step 1: Indexing all data files (PDFs and text files)...
Searching in: /path/to/data

Found 2 PDF(s) and 6 text file(s) in /path/to/data
Processing PDF: sample.pdf
Processing PDF: neurips_paper.pdf
Processing text file: www.ibm.com_topics_what-is-rag.txt
Processing text file: en.wikipedia.org_wiki_Large_language_model.txt
...
Indexing 8 document(s) into RAG system...
✓ Indexing complete!

----------------------------------------------------------------------
Status: success
Total files found: 8
  - PDFs: 2
  - Text files: 6
Successfully indexed: 8
Failed: 0
----------------------------------------------------------------------

✓ Successfully indexed 8 document(s)!

======================================================================
Interactive Q&A Mode
======================================================================
You can now ask questions about your documents.
Type 'exit' or 'quit' to stop.


Enter your query: What is RAG
```

Now when you ask "What is RAG?", it will retrieve information from the IBM article and other sources!

---

## Alternative Methods

### Method 1: Manual Two-Step Process

If you prefer to index and query separately:

#### Step 1: Index your data

```bash
cd rag-groq-llm
python -m src.batch_data_processor data
```

This will index all PDFs and text files in the `data/` folder.

#### Step 2: Query (using Python)

```python
from src.rag_pipeline import SimpleRAG

rag = SimpleRAG()
result = rag.answer("What is RAG?", k=5)
print(result["answer"])
```

### Method 2: Using the Batch Processor Directly

```python
from src.batch_data_processor import BatchDataProcessor
from src.rag_pipeline import SimpleRAG

# Create RAG instance
rag = SimpleRAG()

# Create processor
processor = BatchDataProcessor(rag_instance=rag)

# Index all data
result = processor.batch_process_and_index(
    directory="data",
    recursive=True,
    process_pdfs=True,
    process_texts=True
)

print(f"Indexed {result['indexed']} documents")

# Now query
answer = rag.answer("What is RAG?")
print(answer["answer"])
```

### Method 3: Using FastAPI

Start the server:
```bash
cd src
uvicorn app:app --reload
```

Index your data:
```bash
curl -X POST "http://localhost:8000/batch-index-pdfs" \
  -H "Content-Type: application/json" \
  -d '{"directory": "data", "recursive": true}'
```

Query:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "k": 5}'
```

---

## What Gets Indexed?

The new `BatchDataProcessor` indexes:

✓ **PDF files** - Extracts text from PDFs using pdfplumber
✓ **Text files (.txt)** - Reads pre-scraped web content from your web crawler

**From your data folder:**
- ✓ `data/papers/*.pdf` - Research papers
- ✓ `data/web_pages/*.txt` - Web scraper output (includes RAG info!)
- ✓ `data/web_pages/*.pdf` - Any PDFs downloaded by web scraper
- ✓ All subdirectories (recursive search)

---

## Why This Fixes the Problem

### Before

```
User runs: python src/rag_pipeline.py
↓
Indexes: 3 demo texts (Groq, LangChain, Chroma)
↓
User asks: "What is RAG?"
↓
System searches: Only demo texts
↓
Result: "Context does not mention RAG" ❌
```

### After

```
User runs: python run_rag_with_pdfs.py
↓
Indexes: All PDFs + text files (including IBM RAG article!)
↓
User asks: "What is RAG?"
↓
System searches: All indexed documents
↓
Result: Detailed answer about RAG from IBM article ✅
```

---

## Understanding the Files

### New Files Created

1. **`src/batch_data_processor.py`**
   - Complete batch processor for PDFs and text files
   - Handles both file types automatically
   - Replaces and improves upon `batch_pdf_processor.py`

2. **`run_rag_with_pdfs.py`**
   - One-command solution script
   - Indexes all data, then starts Q&A
   - **Use this for easiest experience**

### Modified Files

3. **`src/rag_pipeline.py`**
   - Now warns when running with demo data only
   - Suggests using `run_rag_with_pdfs.py` instead

---

## Quick Comparison

| Method | Command | Indexes | Interactive |
|--------|---------|---------|-------------|
| **Recommended** | `python run_rag_with_pdfs.py` | All PDFs + texts | Yes |
| Old way (broken) | `python src/rag_pipeline.py` | Demo data only | Yes |
| Manual batch | `python -m src.batch_data_processor data` | All PDFs + texts | No |
| FastAPI | `/batch-index-pdfs` endpoint | All PDFs + texts | No |

---

## Testing the Fix

### Test 1: Ask about RAG

```bash
python run_rag_with_pdfs.py
# Wait for indexing to complete
# Then type:
What is RAG?
```

**Expected:** Should get detailed answer from IBM article about RAG (Retrieval-Augmented Generation)

### Test 2: Ask about LLMs

```bash
# In the same session:
What are large language models?
```

**Expected:** Should get answer from Wikipedia article about LLMs

### Test 3: Check sources

The answer should include source citations like:
- `[doc_www.ibm.com_topics_what-is-rag_chunk_0]`
- `[doc_en.wikipedia.org_wiki_Large_language_model_chunk_1]`

This proves it's retrieving from your actual data files!

---

## Troubleshooting

### Still not finding data?

1. **Check data folder structure:**
   ```bash
   ls -R data/
   ```
   Should show PDF and txt files.

2. **Check indexing output:**
   Look for "Successfully indexed: X documents" where X > 0

3. **Check file permissions:**
   ```bash
   chmod 644 data/papers/*.pdf
   chmod 644 data/web_pages/*.txt
   ```

4. **Verify files have content:**
   ```bash
   head data/web_pages/www.ibm.com_topics_what-is-rag.txt
   ```

### Database issues?

If you want to start fresh, delete the Chroma database:
```bash
rm -rf chroma_db/
```

Then run the indexing script again.

---

## Summary

**The fix:**
1. Use `python run_rag_with_pdfs.py` instead of `python src/rag_pipeline.py`
2. This indexes your actual data files (PDFs + texts) before querying
3. Now "What is RAG?" will find the IBM article about RAG

**Key files:**
- `run_rag_with_pdfs.py` - Complete workflow script ← **Use this!**
- `src/batch_data_processor.py` - Batch processor for all file types
- `src/rag_pipeline.py` - Core RAG logic (modified to warn about demo mode)

**Your data:**
- `data/web_pages/www.ibm.com_topics_what-is-rag.txt` - Contains RAG info!
- All other files in `data/` folder

---

## Quick Reference

**Single command to fix everything:**
```bash
cd rag-groq-llm && python run_rag_with_pdfs.py
```

That's it! Your RAG system will now work correctly with all your data.
