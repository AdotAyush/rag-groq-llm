import os
import tempfile
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from .rag_pipeline import SimpleRAG
from .tools.pdf_scraper import PDFScraper

logger = logging.getLogger("rag_app")
logger.setLevel(logging.INFO)

app = FastAPI(title="RAG Groq Capstone API")
rag = SimpleRAG()
pdf_scraper = PDFScraper("../data/papers/sample.pdf")  # Dummy path for initialization


class IndexRequest(BaseModel):
    texts: Optional[List[str]] = None
    base_id: Optional[str] = "batch"


class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 5
    use_cache: Optional[bool] = True


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


@app.get("/health")
async def health():
    return {"status": "healthy"}