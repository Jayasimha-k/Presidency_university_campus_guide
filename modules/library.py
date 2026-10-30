import streamlit as st

from src.chatbot import answer_with_context
from src.knowledge_ingestion import source_name, sources
from src.vector_store import search

LIBRARY_INSTRUCTIONS = (
    "You are the Presidency University Library Assistant. Answer only from the retrieved "
    "library-related campus documents. Distinguish the Law Library from the Technical Library. "
    "Do not invent opening hours, borrowing rules, membership details, or services that are "
    "not stated in the sources. Preserve any route verification caveats."
)


def library_sources():
    return [
        source_name(path)
        for path in sources()
        if path.name.casefold().startswith("campus_directions")
        or "library" in path.stem.casefold()
    ]


def answer(question, history=None):
    docs = search(question, top_k=6, source=library_sources())
    return answer_with_context(
        question,
        docs,
        history=history,
        system_instruction=LIBRARY_INSTRUCTIONS,
    )


def render():
    st.title("📚 Library Assistant")
    st.write(
        "Ask about the Law Library, Technical Library, their listed facilities, or source-listed "
        "directions. Library documents can be added from the sidebar upload form."
    )
    if "library_history" not in st.session_state:
        st.session_state["library_history"] = []

    if st.button("Clear conversation", key="clear_library_conversation"):
        st.session_state["library_history"] = []
        st.rerun()

    for item in st.session_state["library_history"]:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item["role"] == "assistant" and item.get("sources"):
                with st.expander("Retrieved library sources"):
                    for doc in item["sources"]:
                        st.caption(f"{doc['source']} · chunk {doc['chunk']}")
                        st.write(doc["text"])

    question = st.chat_input("Ask a library question")
    if question and question.strip():
        question = question.strip()
        history = st.session_state["library_history"]
        history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching library information…"):
                response, docs = answer(question, history[:-1])
            st.markdown(response)
            if docs:
                with st.expander("Retrieved library sources"):
                    for doc in docs:
                        st.caption(f"{doc['source']} · chunk {doc['chunk']}")
                        st.write(doc["text"])
        history.append({"role": "assistant", "content": response, "sources": docs})
