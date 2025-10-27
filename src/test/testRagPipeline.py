import pytest
from src.rag_pipeline import SimpleRAG

def test_index_and_query(tmp_path):
    rag = SimpleRAG(chroma_collection_name="test_collection")
    texts = [
        "Transformer models introduced self-attention and have become core to NLP.",
        "Recent work improves transformers with sparse attention and better normalization."
    ]
    rag.index_texts_with_auto_ids(texts, base_id="unittest")
    res = rag.answer("What improved transformer architectures?", k=2, use_cache=False)
    assert "transformer" in res["answer"].lower() or "attention" in res["answer"].lower()
    assert isinstance(res["sources"], list)
