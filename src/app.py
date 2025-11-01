import os
import tempfile
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from .rag_pipeline import SimpleRAG
from .tools.pdf_scraper import PDFScraper
from .batch_pdf_processor import BatchPDFProcessor

logger = logging.getLogger("rag_app")
logger.setLevel(logging.INFO)

app = FastAPI(title="RAG Groq Capstone API")
rag = SimpleRAG()
pdf_scraper = PDFScraper("../data/papers/sample.pdf")  # Dummy path for initialization
batch_processor = BatchPDFProcessor(rag_instance=rag)  # Batch processor using same RAG instance


class IndexRequest(BaseModel):
    texts: Optional[List[str]] = None
    base_id: Optional[str] = "batch"


class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 5
    use_cache: Optional[bool] = True


class BatchPDFRequest(BaseModel):
    directory: str
    recursive: Optional[bool] = True
    extract_mode: Optional[str] = "full"  # "full", "abstract", or "sections"
    base_id: Optional[str] = "pdf_batch"


@app.post("/index")
async def index_payload(req: IndexRequest):
    if not req.texts:
        raise HTTPException(status_code=400, detail="No texts provided to index.")
    rag.index_texts_with_auto_ids(req.texts, base_id=req.base_id)
    return {"status": "ok", "indexed": len(req.texts)}


@app.post("/upload-pdfs")
async def upload_and_index(files: List[UploadFile] = File(...)):
    saved_texts = []
    saved_paths = []
    for f in files:
        contents = await f.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp.flush()
            tmp_path = tmp.name
            saved_paths.append(tmp_path)
            sec = pdf_scraper.extract_sections(tmp_path)
            txt = sec.get("full") or sec.get("abstract") or ""
            if txt.strip():
                saved_texts.append(txt)

    if not saved_texts:
        raise HTTPException(status_code=400, detail="No extractable text from uploaded PDFs.")
    rag.index_texts_with_auto_ids(saved_texts, base_id="uploaded_pdf")
    return {"status": "ok", "indexed": len(saved_texts), "temp_paths": saved_paths}


@app.post("/query")
async def query_endpoint(req: QueryRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty.")
    result = rag.answer(req.question, k=req.k, use_cache=req.use_cache)
    return {"answer": result["answer"], "sources": result["sources"]}


@app.post("/batch-index-pdfs")
async def batch_index_pdfs(req: BatchPDFRequest):
    """
    Batch process and index all PDF files from a specified directory.

    Args:
        directory: Path to directory containing PDF files
        recursive: Search subdirectories (default: True)
        extract_mode: "full" (default), "abstract", or "sections"
        base_id: Base identifier for indexed documents (default: "pdf_batch")

    Returns:
        Processing results with status and statistics
    """
    if not req.directory or not req.directory.strip():
        raise HTTPException(status_code=400, detail="Directory path is required.")

    # Validate extract_mode
    if req.extract_mode not in ["full", "abstract", "sections"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid extract_mode '{req.extract_mode}'. Must be 'full', 'abstract', or 'sections'."
        )

    try:
        result = batch_processor.batch_process_and_index(
            directory=req.directory,
            recursive=req.recursive,
            extract_mode=req.extract_mode,
            base_id=req.base_id
        )

        if result["status"] == "no_files":
            raise HTTPException(status_code=404, detail=f"No PDF files found in {req.directory}")

        if result["status"] == "indexing_failed":
            raise HTTPException(status_code=500, detail=f"Indexing failed: {result.get('error', 'Unknown error')}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy"}