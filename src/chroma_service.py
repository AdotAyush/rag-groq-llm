# src/chroma_service.py
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
from .config import CHROMA_SETTINGS


class ChromaService:
    def __init__(self, persist_directory: str = None, embedding_function=None):
        """
        Modern ChromaDB client initialization.
        Supports both local persistent and remote (HTTP) setups.
        """
        self.persist_directory = persist_directory or CHROMA_SETTINGS.get("persist_directory", "./chroma_db")
        self.embedding_function = embedding_function

        # ✅ Use PersistentClient (replaces deprecated chromadb.Client + Settings)
        self.client = chromadb.PersistentClient(path=self.persist_directory)

    def get_or_create_collection(self, name: str):
        """
        Retrieve or create a Chroma collection.
        """
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(
                name,
                metadata={"source": "RAG system"},
            )

    def add_documents(self, collection_name: str, texts: list, embeddings: list, metadatas: list, ids: list):
        collection = self.get_or_create_collection(collection_name)
        collection.add(documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids)


    def query(self, collection_name: str, query_embedding: list, n_results: int = 5):
        """
        Query Chroma collection for semantically similar documents using a precomputed embedding.
        """
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        return results


    def persist(self):
        """
        Chroma’s new PersistentClient automatically persists data to disk.
        Explicit persist() is unnecessary, but retained for compatibility.
        """
        print(f"ChromaDB data persisted at: {self.persist_directory}")
