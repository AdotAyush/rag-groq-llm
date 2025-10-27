import re
from typing import List, Tuple

def clean_text(text: str) -> str:
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text: str, max_size: int = 1000, overlap: int = 200) -> List[str]:
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0:
            start = 0
        if end >= len(text):
            break
    return chunks
