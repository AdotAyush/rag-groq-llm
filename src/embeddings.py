from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from .config import SENTENCE_TRANSFORMER_MODEL

class LocalEmbedder:
    def __init__(self, model_name: str = SENTENCE_TRANSFORMER_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return [list(map(float, v)) for v in embeddings]
    
if __name__ == "__main__":
    e = LocalEmbedder()
    print(e.embed(["Hello world", "How are you?"]))