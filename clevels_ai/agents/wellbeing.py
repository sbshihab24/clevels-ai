# clevels_ai/agents/wellbeing.py
from ..embeddings import embed_texts
from ..vectorstore import search
from ..rag import call_llm, rag_search
from ..utils import detect_language
from ..logger import logger

CRISIS_KEYWORDS = ["suicide","kill myself","hurt myself","panic","self-harm","sinucide","sinucidere"]

SAFE_MESSAGE = {
    "en": "If you are in immediate danger, contact local emergency services. I can provide general well-being tips but I'm not a healthcare professional.",
    "ro": "Dacă ești în pericol imediat contactează serviciile de urgență. Pot oferi sfaturi generale, dar nu sunt profesionist medical."
}

def detects_crisis(text: str):
    t = text.lower()
    return any(k in t for k in CRISIS_KEYWORDS)

def wellbeing_handle(query: str, lang: str = None):
    lang = lang or detect_language(query)
    if detects_crisis(query):
        return {"type":"crisis","message": SAFE_MESSAGE[lang]}
    ctx_items = rag_search(query, namespace="wellbeing", top_k=6)
    context = "\n\n".join([i["text"] for i in ctx_items]) if ctx_items else ""
    system = {
        "en": "You are a compassionate wellbeing coach. Use context to suggest practical, empathetic support, exercises, and resources. Always include a brief safety note.",
        "ro": "Ești un coach empatic. Folosește contextul pentru a oferi suport practic și exerciții. Include un scurt mesaj de siguranță."
    }[lang]
    prompt = f"User: {query}\n\nContext:\n{context}\n\nProvide an empathetic helpful response and short exercises if relevant."
    try:
        reply = call_llm(system, prompt, max_tokens=450, temperature=0.7)
    except Exception as e:
        logger.exception("LLM wellbeing failed: %s", e)
        reply = SAFE_MESSAGE[lang]
    return {"type":"reply","message": reply + "\n\n" + SAFE_MESSAGE[lang]}
