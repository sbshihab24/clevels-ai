# clevels_ai/embeddings.py
import numpy as np
from openai import OpenAI
from .config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def embed_texts(texts):
    """
    texts: list[str]
    returns: list[np.array]
    """
    if not texts:
        return []

    response = client.embeddings.create(
        model=settings.OPENAI_EMBEDDING_MODEL,
        input=texts
    )

    embeddings = []
    for item in response.data:
        embeddings.append(np.array(item.embedding, dtype="float32"))

    return embeddings
