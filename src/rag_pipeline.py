from typing import Any, Dict, List, Optional, Tuple

from functools import lru_cache
import logging
import uuid

from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from .groq_llm import GroqLLM
from .embeddings import LocalEmbedder
from .chroma_service import ChromaService
from .utils import chunk_text
from .config import MAX_CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_PROMPT = """You are a research assistant. Use the provided context to answer the question in detail and comprehensively.
Provide thorough explanations with relevant examples and supporting information from the context.
Cite the source chunk ids in square brackets after each fact where appropriate.

Context:
{context}

Question: {question}

Answer (detailed and comprehensive, with citations): """

class SimpleRAG: 
    def __init__(self, chroma_collection_name:str = "research_papers", embedder: Optional[LocalEmbedder] = None):
        self.embedder = embedder or LocalEmbedder()
        self.chroma = ChromaService()
        self.collection = chroma_collection_name
        self.llm = GroqLLM()
        self.prompt_template = PromptTemplate.from_template(DEFAULT_PROMPT)
        
    def index_documents(self, documents: List[str], metadatas: List[dict], ids: List[str]) -> None:
        if not (len(documents) == len(metadatas) == len(ids)):
            raise ValueError("Documents, metadatas, and ids must have the same length.")
        
        all_chunks, all_meta, all_ids = [], [], []
        for d, md, id_ in zip(documents, metadatas, ids):
            # chunks = chunk_text(d, max_chunk_size=MAX_CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            chunks = chunk_text(d, max_size=MAX_CHUNK_SIZE, overlap=CHUNK_OVERLAP)

            for i, chunk in enumerate(chunks):
                chunk_id = f"{id_}_chunk_{i}"
                meta = md.copy()
                meta.update({"source_id": id_, "chunk_id": i})
                all_chunks.append(chunk)
                all_meta.append(meta)
                all_ids.append(chunk_id)
        
        logger.info("Embedding %d chunks", len(all_chunks))
        embeddings = self.embedder.embed(all_chunks)

        self.chroma.add_documents(self.collection, all_chunks, embeddings, all_meta, all_ids)
        try:
            self.chroma.persist()
        except Exception as e:
            logger.warning("Failed to persist Chroma database: %s", e)

    def _parse_chroma_results(self, results: dict) -> List[Tuple[str, dict]]:
        docs_out = []
        docs = results.get("documents") or results.get("documents_texts") or []
        metas = results.get("metadatas") or []
        ids = results.get("ids") or []

        if isinstance(docs, list) and len(docs) > 0 and isinstance(docs[0], list):
            doc_list = docs[0]
        elif isinstance(docs, list):
            doc_list = docs
        else:
            doc_list = []

        meta_list = metas[0] if (isinstance(metas, list) and len(metas) > 0 and isinstance(metas[0], list)) else metas
        id_list = ids[0] if (isinstance(ids, list) and len(ids) > 0 and isinstance(ids[0], list)) else ids

        for i, d in enumerate(doc_list):
            meta = {}
            if i < len(meta_list) and isinstance(meta_list[i], list):
                meta = meta_list[i] or {}

            if i < len(id_list) and isinstance(id_list, list):
                meta = meta.copy()
                meta["id"] = id_list[i]
            docs_out.append((d, meta))
        return docs_out
    
    def retrieve(self, query: str, top_k: int = 2) -> List[Document]:
        query_embedding = self.embedder.embed([query])[0]
        try:
            raw = self.chroma.query(self.collection, query_embedding, n_results=top_k)
        except Exception as e:
            logger.error("Chroma query failed: %s", e)
            return []
        
        pairs = self._parse_chroma_results(raw)
        docs = []
        for text, meta in pairs:
            docs.append(Document(page_content=text, metadata=meta or {}))

        return docs
    
    def _build_context(self, documents: List[Document]) -> str:
        parts = []
        for doc in documents:
            meta = doc.metadata or {}
            chunk_id = meta.get("id") or meta.get("source_doc", "") + f"_chunk_{meta.get('chunk_id', '')}"
            meta_info = f"[{chunk_id}]" if chunk_id else ""
            snippet = doc.page_content.strip()

            parts.append(f"{meta_info}\n{snippet}")
        return "\n\n --- \n\n".join(parts) if parts else ""
    
    def answer(self, question: str, k: int = 2, use_cache: bool = False) -> dict:
        docs = self.retrieve(question, top_k=k)

        context = self._build_context(docs)
        prompt = self.prompt_template.format(context=context, question=question)

        try:
            generated = self.llm.generate([prompt])
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            generated = f"LLM error: {e}"

        sources = [d.metadata for d in docs]
        return {
            "answer": generated,
            "sources": sources,
            "raw_retrieved_documents": docs
        }
    
    def index_texts_with_auto_ids(self, texts: List[str], base_id: str = "doc"):
        metas, ids = [], []
        docs = []
        for i, text in enumerate(texts):
            doc_id = f"{base_id}_{i}_{str(uuid.uuid4())[:8]}"
            docs.append(text)
            metas.append({"base_id": base_id})
            ids.append(doc_id)
        self.index_documents(docs, metas, ids)

if __name__ == "__main__":
    rag = SimpleRAG()

    # 🔹 Step 1: Index some text
    print("Indexing example documents into Chroma...")
    sample_texts = [
        "Large Language Models like Groq LLM can process text efficiently and support retrieval-augmented generation.",
        "LangChain provides modular components for building LLM-powered applications.",
        "Chroma is a vector database used to store and retrieve document embeddings."
    ]
    rag.index_texts_with_auto_ids(sample_texts, base_id="sample")

    print("Indexing complete.\n")

    # 🔹 Step 2: Interactive Q&A loop
    print("=== Retrieval-Augmented Generation (RAG) System ===")
    print("Type your research question below (or 'exit' to quit)\n")

    while True:
        query = input("Enter your query: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Exiting RAG system...")
            break

        print("\nRetrieving and generating answer...\n")
        result = rag.answer(query)

        answer = result.get("answer", "")
        sources = result.get("sources", [])
        docs = result.get("raw_retrieved_documents", [])

        print("\n" + "="*70)
        print("🧠  Final Answer:\n")
        print(answer.strip())
        print("\n" + "="*70)
        print("📚  Sources Used:")
        for i, src in enumerate(sources):
            src_id = src.get("id", "unknown")
            print(f"  [{i+1}] Chunk ID: {src_id}")
        print("="*70 + "\n")
