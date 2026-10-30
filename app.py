import streamlit as st
from config import ROOT, GROQ_API_KEY
from modules.module_registry import MODULES
from modules import home, ai_assistant, campus_explorer, campus_navigation, library, transport, about
from src.knowledge_ingestion import sources
from src.uploaded_documents import SUPPORTED_EXTENSIONS, UploadError, save_uploaded_file
from src.vector_store import index, collection

st.set_page_config(page_title="Presidency University Campus Guide", page_icon="🏛️", layout="wide")
css=ROOT/"assets"/"styles.css"
if css.exists(): st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>",unsafe_allow_html=True)

PAGES={"home":home.render,"assistant":ai_assistant.render,"explorer":campus_explorer.render,"navigation":campus_navigation.render,"library":library.render,"transport":transport.render,"about":about.render}
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
    with st.form("knowledge_upload_form", clear_on_submit=True):
        uploaded_files=st.file_uploader(
            "Upload knowledge files",
            type=list(SUPPORTED_EXTENSIONS),
            accept_multiple_files=True,
            help="Supported: TXT, Markdown, CSV, JSON, PDF, DOCX, and XLSX. Maximum 10 MB per file.",
        )
        upload_category=st.selectbox(
            "Content category",
            options=("General", "Library", "Transport"),
            help="Library and Transport uploads are also included in their matching assistant.",
        )
        upload_submitted=st.form_submit_button("Upload and index")
    if upload_submitted:
        saved_files=[]
        for uploaded_file in uploaded_files or []:
            try:
                saved_files.append(
                    save_uploaded_file(
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        category=upload_category,
                    )
                )
            except (UploadError, OSError) as exc:
                st.error(f"{uploaded_file.name}: upload failed ({type(exc).__name__}: {exc})")
        if saved_files:
            with st.spinner("Indexing uploaded files with the campus knowledge base…"):
                try:
                    result=index(force=True)
                except Exception as exc:
                    result={"ok":False,"message":f"Files were saved, but indexing failed: {type(exc).__name__}. Use Index / refresh campus files to retry."}
            (st.success if result["ok"] else st.error)(
                f"{len(saved_files)} file(s) saved. {result['message']}"
            )
        else:
            st.warning("Choose at least one supported file to upload.")
    if not GROQ_API_KEY: st.warning("Groq API key is not configured. Add GROQ_API_KEY to .env and restart the app.")

if not sources():
    st.warning("Upload knowledge files from the sidebar or add .txt source files to the knowledge base, then index them.")
PAGES[selected]()
