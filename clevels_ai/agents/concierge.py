# clevels_ai/agents/concierge.py
import os
import pandas as pd
from urllib.parse import quote_plus
from ..google_api import fetch_place_search, static_map_url
from ..rag import call_llm, rag_search
from ..config import settings
from ..logger import logger
from ..embeddings import embed_texts
from ..vectorstore import search
from ..utils import clean_text, detect_language
from difflib import get_close_matches

PARTNERS_CSV = settings.PARTNERS_CSV_PATH

def load_partners():
    if os.path.exists(PARTNERS_CSV):
        df = pd.read_csv(PARTNERS_CSV).fillna("")
        for c in df.columns:
            df[c] = df[c].astype(str)
        return df
    return pd.DataFrame(columns=["name","address","lat","lng","curated_category","quality_tags","perks","notes","rating"])

def simple_match(df, query, city=None, top_k=5):
    q = clean_text(query).lower()
    if df.empty:
        return pd.DataFrame()
    dfc = df if city is None else df[df["address"].str.lower().str.contains(city.lower())]
    if dfc.empty:
        dfc = df
    mask = dfc["name"].str.lower().str.contains(q) | dfc["curated_category"].str.lower().str.contains(q)
    matched = dfc[mask]
    if not matched.empty:
        return matched.head(top_k)
    # fuzzy
    names = dfc["name"].tolist()
    close = get_close_matches(query, names, n=top_k, cutoff=0.4)
    return dfc[dfc["name"].isin(close)].head(top_k)

def format_partner_row(row):
    lat = row.get("lat","")
    lng = row.get("lng","")
    static = static_map_url(lat, lng) if lat and lng else None
    maps_link = f"https://www.google.com/maps/search/?api=1&query={quote_plus(str(row.get('name',''))+' '+str(row.get('address','')))}"
    return {
        "name": row.get("name"),
        "address": row.get("address"),
        "rating": row.get("rating") if "rating" in row else None,
        "quality_tags": [x.strip() for x in str(row.get("quality_tags","")).split(",") if x.strip()],
        "perks": [x.strip() for x in str(row.get("perks","")).split(",") if x.strip()],
        "partner_status": True,
        "static_map": static,
        "maps_link": maps_link
    }

def format_google_place(place):
    name = place.get("name")
    address = place.get("formatted_address")
    rating = place.get("rating")
    return {
        "name": name,
        "address": address,
        "rating": rating,
        "quality_tags": [],
        "perks": [],
        "partner_status": False,
        "maps_link": f"https://www.google.com/maps/search/?api=1&query={quote_plus(name + ' ' + (address or ''))}",
        "static_map": None,
        "reason_to_pick": f"Highly rated place nearby ({rating})."
    }

def detect_city_in_query(query):
    # naive; expand list as you need
    cities = ["bucharest","bucuresti","brasov","cluj","iasi","constanta","sibiu"]
    low = query.lower()
    for c in cities:
        if c in low:
            return c
    return None

def generate_reason(meta, lang="en"):
    sys = {
        "en": "You are a premium concierge copywriter. Provide a short elegant reason why someone should pick this hotel.",
        "ro": "Ești un copywriter concierge premium. Oferă un motiv scurt și elegant pentru a alege acest hotel."
    }[lang]
    prompt = f"Name: {meta.get('name')}\nTags: {', '.join(meta.get('quality_tags',[]))}\nPerks: {', '.join(meta.get('perks',[]))}"
    try:
        return call_llm(sys, prompt, max_tokens=80)
    except Exception as e:
        logger.exception("LLM reason generation failed %s", e)
        return ""

def concierge_handle(query: str, lang: str = None, top_k: int = 5):
    lang = lang or detect_language(query)
    city = detect_city_in_query(query)
    # check partners first
    df = load_partners()
    hotels = []
    if not df.empty:
        matched = simple_match(df, query, city=city, top_k=top_k)
        for _, row in matched.iterrows():
            hotels.append(format_partner_row(row))
    # if not enough, RAG search within concierge namespace
    if len(hotels) < top_k:
        rag_items = rag_search(query, namespace="concierge", top_k=top_k)
        for i in rag_items:
            # rag item text may include partner info; we keep as context, but not convert to partner cards
            pass
    # fallback to Google
    if len(hotels) < top_k:
        try:
            need = top_k - len(hotels)
            g = fetch_place_search(f"hotels {city or ''}", limit=need, language=lang)
            for p in g:
                hotels.append(format_google_place(p))
        except Exception as e:
            logger.exception("Google fallback error: %s", e)
    hotels = hotels[:top_k]
    # create human-friendly reply
    if not hotels:
        empty_msg = {"en": "I couldn't find any hotels. Would you like me to search on the web?", "ro":"Nu am găsit hoteluri. Vrei să caut pe web?"}
        return {"type":"clarify","message": empty_msg[lang]}
    # Compose friendly reply using LLM
    sys = {
        "en": "You are a warm, helpful concierge. Given the list of hotels and context, produce a friendly recommendation message. Ask one clarifying question if necessary.",
        "ro": "Ești un concierge prietenos. Folosește lista de hoteluri și oferă o recomandare prietenoasă. Pune o întrebare dacă e necesar."
    }[lang]
    hotels_text = ""
    for h in hotels:
        hotels_text += f"**{h['name']}**\n• Rating: {h.get('rating','N/A')}\n• Address: {h.get('address')}\n• Maps: {h.get('maps_link')}\n\n"
    user_prompt = f"User query: {query}\n\nHotels:\n{hotels_text}\n\nWrite a concise friendly message recommending the top picks and explain why."
    try:
        reply = call_llm(sys, user_prompt, max_tokens=450, temperature=0.8)
    except Exception as e:
        logger.exception("LLM reply failed: %s", e)
        # fallback quick formatting
        lines = ["Here are some options:" if lang=="en" else "Iată câteva opțiuni:"]
        for h in hotels:
            lines.append(f"- {h['name']} — {h.get('address')} (rating: {h.get('rating')})")
        reply = "\n".join(lines)
    return {"type":"reply","message": reply}
