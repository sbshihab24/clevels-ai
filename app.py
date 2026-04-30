# app.py
import streamlit as st
from clevels_ai.utils import detect_language
from clevels_ai import logger
from clevels_ai.rag import call_llm
from clevels_ai.agents import concierge as concierge_mod
from clevels_ai.agents import legal as legal_mod
from clevels_ai.agents import wellbeing as wellbeing_mod
from clevels_ai.config import settings

st.set_page_config(page_title="Monica — C-Levels AI", layout="wide")
st.title("Monica — Your C-Levels AI Assistant")

if "history" not in st.session_state:
    st.session_state.history = []

def route_and_respond(text: str):
    # quick heuristic router
    low = text.lower()
    if any(w in low for w in ["hotel","book","concierge","restaurant","cazare","hoteluri","bucuresti","bucharest"]):
        return concierge_mod.concierge_handle(text)
    if any(w in low for w in ["law","lege","legal","contract","drept","concediu","maternity","salariu"]):
        return {"type":"reply","message": legal_mod.legal_handle(text)}
    if any(w in low for w in ["feel","depress","sick","anxiet","panic","stres","sănătate","sinucide"]):
        return wellbeing_mod.wellbeing_handle(text)
    # fallback: ask clarifying question
    lang = detect_language(text)
    msg = {"en":"Do you need concierge, legal or wellbeing help?","ro":"Aveți nevoie de concierge, legal sau wellbeing?"}
    return {"type":"clarify","message": msg[lang]}

with st.form("msg"):
    user_input = st.text_input("Ask Monica anything...", key="user_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input:
        res = route_and_respond(user_input)
        st.session_state.history.append(("user", user_input))
        st.session_state.history.append(("monica", res))
        # display
        if isinstance(res, dict):
            if res.get("type") == "reply":
                st.markdown(f"**Monica:** {res['message']}")
            elif res.get("type") == "clarify":
                st.info(res["message"])
            elif res.get("type") == "crisis":
                st.error(res["message"])
            else:
                st.write(res)
        else:
            st.write(res)

st.markdown("### Conversation History")
for who, content in st.session_state.history[-20:]:
    if who == "user":
        st.markdown(f"**You:** {content}")
    else:
        # content might be dict
        if isinstance(content, dict):
            if content.get("type") == "reply":
                st.markdown(f"**Monica:** {content['message']}")
            else:
                st.write(content)
        else:
            st.markdown(f"**Monica:** {content}")
