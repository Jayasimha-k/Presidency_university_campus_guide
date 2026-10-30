import streamlit as st
from config import IMAGE_DIR, KNOWLEDGE_DIR, GROQ_API_KEY
from src.vector_store import collection
from modules.module_registry import MODULES

def render():
    st.title("🏛️ Presidency University Campus Guide")
    st.write("Find campus information using the supplied route documents. Answers and navigation remain grounded in those sources.")
    try: indexed=collection().count()>0
    except Exception: indexed=False
    images=sum(1 for p in IMAGE_DIR.iterdir() if p.suffix.lower() in {".jpg",".jpeg",".png",".webp"}) if IMAGE_DIR.exists() else 0
    kb=any(p.suffix.lower()==".txt" and p.read_text(encoding="utf-8-sig").strip() for p in KNOWLEDGE_DIR.glob("*.txt"))
    a,b,c=st.columns(3)
    a.metric("Knowledge base", "Indexed" if indexed else ("Ready to index" if kb else "Missing"))
    b.metric("Image library", f"{images} image(s) found")
    c.metric("AI service", "Configured" if GROQ_API_KEY else "API key missing")
    st.info("Navigation uses directions explicitly present in your files. Some source routes are marked ‘Verify’; those caveats are retained.")
    st.subheader("Modules")
    cols=st.columns(2)
    for i,m in enumerate(MODULES):
        with cols[i%2]:
            st.markdown(f"### {m.icon} {m.title}")
            st.write(m.description)
            st.caption(m.status)
