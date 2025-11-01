import re
from typing import List, Tuple

def clean_text(text: str) -> str:
    # Replace Windows line endings with Unix
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')

    # Preserve paragraph breaks (2+ consecutive newlines)
    text = re.sub(r'\n{2,}', '|||PARA|||', text)

    # Convert single newlines to spaces (handles line-wrapped text)
    text = text.replace('\n', ' ')

    # Restore paragraph breaks
    text = text.replace('|||PARA|||', '\n\n')

    # Normalize spaces (collapse multiple spaces to single)
    text = re.sub(r' +', ' ', text)

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
