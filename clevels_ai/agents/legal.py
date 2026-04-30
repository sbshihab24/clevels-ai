# clevels_ai/agents/legal.py
from ..embeddings import embed_texts
from ..vectorstore import search
from ..config import settings
from ..logger import logger
from ..rag import call_llm, rag_search
from ..utils import detect_language

DISCLAIMER = {
    "en": "Disclaimer: This is general information and not legal advice. For specifics consult a qualified lawyer.",
    "ro": "Declinare de responsabilitate: Aceasta reprezintă informații generale și nu consultanță juridică. Pentru cazuri specifice consultați un avocat."
}

def legal_handle(query: str, lang: str = None):
    lang = lang or detect_language(query)
    # RAG retrieve
    ctx_items = rag_search(query, namespace="legal", top_k=6)
    context = "\n\n".join([i["text"] for i in ctx_items]) if ctx_items else ""
    system = {
        "en": "You are a precise legal assistant. Use the context to answer clearly and include citations (article numbers or document names) if present.",
        "ro": "Ești un asistent juridic precis. Folosește contextul pentru a răspunde clar și include citări dacă există."
    }[lang]
    user_prompt = f"User query: {query}\n\nContext:\n{context}\n\nAnswer in a friendly, understandable manner. Provide citations if available."
    try:
        reply = call_llm(system, user_prompt, max_tokens=700, temperature=0.2)
    except Exception as e:
        logger.exception("LLM legal failed: %s", e)
        reply = "Sorry, I couldn't generate a legal answer right now."
    return reply + "\n\n" + DISCLAIMER[lang]
