from functools import lru_cache
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(EMBEDDING_MODEL)

def embed_texts(texts):
    return get_model().encode(texts, normalize_embeddings=True).tolist()
