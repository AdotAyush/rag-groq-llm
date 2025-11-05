# embed_store.py
import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


DATA_DIR = "data"
WEB_DIR = os.path.join(DATA_DIR, "web_pages")
PDF_DIR = os.path.join(DATA_DIR, "papers")
CHROMA_DIR = os.path.join(DATA_DIR, "embeddings")

def load_all_text():
    docs = []
    for folder in [WEB_DIR, PDF_DIR]:
        if not os.path.exists(folder):
            print(f"⚠️ Directory not found: {folder}")
            continue

        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            if path.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if text:  # ✅ skip empty files
                        docs.append(Document(page_content=text, metadata={"source": fname}))
                    else:
                        print(f"Skipping empty file: {fname}")
    return docs


def create_embeddings():
    print("Loading documents...")
    docs = load_all_text()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    print("Generating embeddings...")
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Creating ChromaDB vector store...")
    vectordb = Chroma.from_documents(chunks, embedding=embedder, persist_directory=CHROMA_DIR)
    vectordb.persist()
    print(f"Stored {len(chunks)} chunks in ChromaDB at {CHROMA_DIR}")

if __name__ == "__main__":
    create_embeddings()
