import streamlit as st
from config import ROOT, KNOWLEDGE_DIR, IMAGE_DIR, GROQ_API_KEY
from modules.module_registry import MODULES
from modules import home, ai_assistant, campus_explorer, campus_navigation, about
from src.vector_store import index, collection

st.set_page_config(page_title="Presidency University Campus Guide", page_icon="🏛️", layout="wide")
css=ROOT/"assets"/"styles.css"
if css.exists(): st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>",unsafe_allow_html=True)

PAGES={"home":home.render,"assistant":ai_assistant.render,"explorer":campus_explorer.render,"navigation":campus_navigation.render,"about":about.render}
with st.sidebar:
    st.markdown("## 🏛️ Campus Guide")
    selected=st.radio("Navigate",options=[m.id for m in MODULES if m.status=="Active"],format_func=lambda x: next(m.icon+"  "+m.title for m in MODULES if m.id==x),label_visibility="collapsed")
    st.divider()
    st.caption("Knowledge base")
    try:
        count=collection().count()
        st.write(f"Indexed · {count} chunks" if count else "Not indexed")
    except Exception: st.write("Not indexed")
    if st.button("Index / refresh campus files", use_container_width=True):
        with st.spinner("Building persistent semantic index…"):
            try: result=index(force=True)
            except Exception as exc: result={"ok":False,"message":f"Indexing failed: {type(exc).__name__}. Check dependencies and available memory."}
        (st.success if result["ok"] else st.error)(result["message"])
        st.rerun()
    if not GROQ_API_KEY: st.warning("Groq API key is not configured. Add GROQ_API_KEY to .env and restart the app.")

if not any(KNOWLEDGE_DIR.glob("*.txt")):
    st.warning("Add campus .txt source files to the knowledge_base folder, then index them.")
PAGES[selected]()
