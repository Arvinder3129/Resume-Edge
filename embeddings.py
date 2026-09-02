from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )


def encode_texts(texts):
    return get_model().encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
