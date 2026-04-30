# clevels_ai/rag.py
from openai import OpenAI
from .config import settings
from .embeddings import embed_texts
from .vectorstore import search
from .logger import logger

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def call_llm(system_msg: str, user_msg: str, max_tokens=400, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.exception("LLM Error: %s", e)
        return "Sorry, something went wrong while generating the AI response."

def rag_search(query: str, namespace: str, top_k=5):
    embeddings = embed_texts([query])
    if not embeddings:
        return []

    q_emb = embeddings[0]
    results = search(q_emb, top_k=top_k, namespace=namespace)
    return results
