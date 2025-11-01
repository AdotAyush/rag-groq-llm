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

def chunk_text(text: str, max_size: int = 2000, overlap: int = 200) -> List[str]:
    if len(text) <= max_size:
        return [text]

    chunks = []
    start = 0
    sentence_search_window = 300  # How far back to look for sentence boundary

    while start < len(text):
        target_end = start + max_size

        # If we're at or past the end, take remaining text
        if target_end >= len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Search for sentence boundary within window
        search_start = max(start, target_end - sentence_search_window)
        best_split = target_end

        # Look for sentence endings: ". ", "! ", "? ", ".\n", "!\n", "?\n"
        sentence_pattern = r'[.!?][\s\n]'
        matches = list(re.finditer(sentence_pattern, text[search_start:target_end]))

        if matches:
            # Use the last sentence boundary found
            last_match = matches[-1]
            # Split after the punctuation mark and the space/newline (include full sentence)
            best_split = search_start + last_match.end()
        else:
            # No sentence boundary found, look for word boundary
            word_pattern = r'[\s\n\-]'
            matches = list(re.finditer(word_pattern, text[search_start:target_end]))

            if matches:
                # Use the last word boundary found
                last_match = matches[-1]
                best_split = search_start + last_match.start()
            # else: no word boundary either, force split at target_end (best_split already set)

        # Extract chunk and add to list
        chunk = text[start:best_split].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position with overlap
        start = best_split - overlap
        if start < 0:
            start = 0

    return chunks
