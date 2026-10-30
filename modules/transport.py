import streamlit as st

from src.chatbot import answer_with_context
from src.knowledge_ingestion import source_name, sources
from src.vector_store import search

TRANSPORT_SOURCE = "transport_information.txt"
TRANSPORT_INSTRUCTIONS = (
    "You are the Presidency University Transport Assistant. Answer only from the provided "
    "transport source. Identify the source's dates and snapshot limitations when relevant. "
    "Do not guess drop-off times, holiday bus service, live seat availability, or contact details. "
    "The source intentionally omits driver personal information. Direct students to the official "
    "university website or student portal for current contact details and confirmation."
)


def transport_sources():
    return [
        source_name(path)
        for path in sources()
        if path.name.casefold() == TRANSPORT_SOURCE
        or "transport" in path.stem.casefold()
    ]


def answer(question, history=None):
    docs = search(question, top_k=6, source=transport_sources())
    return answer_with_context(
        question,
        docs,
        history=history,
        system_instruction=TRANSPORT_INSTRUCTIONS,
    )


def render():
    st.title("🚌 University Transport")
    st.write(
        "Ask about bus routes, boarding points, pickup times, annual fees, registration, "
        "route changes, and the academic calendar."
    )
    st.warning(
        "Transport details are a dated snapshot, not live information. Confirm current routes, "
        "fees, seat availability, dates, and policies with the university."
    )
    if "transport_history" not in st.session_state:
        st.session_state["transport_history"] = []

    if st.button("Clear conversation", key="clear_transport_conversation"):
        st.session_state["transport_history"] = []
        st.rerun()

    for item in st.session_state["transport_history"]:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item["role"] == "assistant" and item.get("sources"):
                with st.expander("Retrieved transport sources"):
                    for doc in item["sources"]:
                        st.caption(f"{doc['source']} · chunk {doc['chunk']}")
                        st.write(doc["text"])

    question = st.chat_input("Ask a transport question")
    if question and question.strip():
        question = question.strip()
        history = st.session_state["transport_history"]
        history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching transport information and preparing an answer…"):
                response, docs = answer(question, history[:-1])
            st.markdown(response)
            if docs:
                with st.expander("Retrieved transport sources"):
                    for doc in docs:
                        st.caption(f"{doc['source']} · chunk {doc['chunk']}")
                        st.write(doc["text"])
        history.append({"role": "assistant", "content": response, "sources": docs})
