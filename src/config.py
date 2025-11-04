from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "groq-mini-1")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")

CHROMA_SETTINGS = {
    "persist_directory": CHROMA_PERSIST_DIR
}

MAX_CHUNK_SIZE = 2000  # Increased from 1000 for better context
CHUNK_OVERLAP = 200     # Unchanged