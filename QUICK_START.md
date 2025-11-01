# Quick Start: Process All PDFs in Data Folder

## Simple One-Command Solution

Process all PDFs in your `data/papers` folder with a single command:

```bash
cd rag-groq-llm
python batch_process_pdfs.py
```

That's it! This will:
1. Find all PDFs in `data/papers` directory (and subdirectories)
2. Extract text from each PDF
3. Index them into the RAG system with improved chunking and text processing
4. Show you the results

## Example Output

```
======================================================================
PDF Batch Processor for RAG System
======================================================================

Searching for PDFs in: /path/to/rag-groq-llm/data/papers

Found 2 PDF file(s) in /path/to/rag-groq-llm/data/papers
Processing: /path/to/data/papers/sample.pdf
Processing: /path/to/data/web_pages/neurips_paper.pdf
Indexing 2 document(s) into RAG system...
✓ Indexing complete!

======================================================================
PROCESSING RESULTS
======================================================================
Status:              success
Total PDFs found:    2
Successfully indexed: 2
Failed:              0
======================================================================

✓ All PDFs successfully indexed!
You can now query the RAG system with questions about your documents.
```

## What Changed?

The recent fixes ensure you get **better results**:

✓ **Text structure preserved** - No more words running together
✓ **Smart chunking** - Respects sentence boundaries (2000 chars per chunk)
✓ **No truncation** - Full context available to the LLM
✓ **Detailed responses** - Prompts encourage comprehensive answers

## Query Your Documents

After processing, query your documents:

### Method 1: Python Script

```python
from src.rag_pipeline import SimpleRAG

rag = SimpleRAG()
result = rag.answer("What are the main findings in the papers?", k=5)
print(result["answer"])
```

### Method 2: FastAPI Server

Start server:
```bash
cd src
uvicorn app:app --reload
```

Query via curl:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "k": 5
  }'
```

### Method 3: Interactive Mode

```bash
cd src
python rag_pipeline.py
# Then type your questions interactively
```

## More Options?

See `BATCH_PROCESSING_GUIDE.md` for:
- Command-line options
- Custom directories
- Different extraction modes (full/abstract/sections)
- API endpoints
- Advanced usage

## Troubleshooting

**No PDFs found?**
- Make sure PDFs are in `rag-groq-llm/data/papers/` directory
- Check file extensions are `.pdf` (lowercase)

**Extraction errors?**
- Ensure PDFs are not encrypted
- Try opening PDFs manually to verify they're readable

**Need help?**
- Check `BATCH_PROCESSING_GUIDE.md` for detailed documentation
- Review error messages in the output

---

**That's all you need to get started!** 🚀
