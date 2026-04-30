# umbrella.py

from clevels_ai.utils import clean_text
from clevels_ai.logger import logger
from clevels_ai.agents import concierge as concierge_mod
from clevels_ai.agents import legal as legal_mod
from clevels_ai.agents import wellbeing as wellbeing_mod
from openai import OpenAI
from clevels_ai.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ---------------- LANGUAGE DETECT ----------------
def detect_language(text: str) -> str:
    ro_chars = ["ă", "â", "î", "ș", "ț"]
    if any(c in text.lower() for c in ro_chars):
        return "ro"
    return "en"


# ---------------- INTENT DETECT ----------------
def detect_intent(text: str) -> str:
    t = clean_text(text.lower())

    # Greeting only
    if t in ["hi", "hello", "hey", "bună", "salut"]:
        return "greeting"

    # Concierge-related
    concierge_kw = ["hotel", "restaurant", "stay", "romania", "trip", "booking", "travel"]
    if any(k in t for k in concierge_kw):
        return "concierge"

    # Legal
    legal_kw = ["article", "law", "legal", "cod", "lege", "procedura"]
    if any(k in t for k in legal_kw):
        return "legal"

    # Wellbeing
    well_kw = ["stress", "burnout", "sad", "anxiety", "depressed", "stres", "obosit"]
    if any(k in t for k in well_kw):
        return "wellbeing"

    # Everything else → general assistant Monica
    return "general"


# ---------------- ROUTER ----------------
def route_to_agent(text: str):
    lang = detect_language(text)
    intent = detect_intent(text)

    greeting_msg = {
        "en": "Hi! I’m Monica, your C-Levels AI assistant. How can I support you today?",
        "ro": "Salut! Sunt Monica, asistentul tău AI C-Levels. Cu ce te pot ajuta astăzi?"
    }

    try:
        # Greeting
        if intent == "greeting":
            return "monica", greeting_msg[lang]

        # Concierge
        if intent == "concierge":
            return "concierge", concierge_mod.concierge_handle(text, lang=lang)

        # Legal
        if intent == "legal":
            return "legal", legal_mod.legal_handle(text, lang=lang)

        # Wellbeing
        if intent == "wellbeing":
            return "wellbeing", wellbeing_mod.wellbeing_handle(text, lang=lang)

        # General Monica assistant mode
        response = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are Monica, a helpful, kind and intelligent AI assistant."},
                {"role": "user", "content": text}
            ]
        )
        return "monica", response.choices[0].message.content

    except Exception as e:
        logger.exception(e)
        return "monica", greeting_msg[lang]
