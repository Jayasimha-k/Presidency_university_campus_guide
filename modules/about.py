import streamlit as st
from src.chatbot import answer_with_context

SYSTEM_CONTEXT = """This is the Presidency University Campus Guide. It uses Streamlit for the interface, Sentence Transformers to embed campus text, and persistent ChromaDB to retrieve relevant campus sources. Campus Explorer retrieves relevant chunks and asks Groq to summarize them. Campus Navigation looks for a source record that explicitly includes both requested endpoints, then asks Groq to explain that route without inventing missing directions. The AI Campus Assistant uses the same source-grounded Groq answering flow. Groq API credentials are stored in the local .env file. The campus images are matched using editable metadata; images are not analyzed by a vision model. The route documents may contain verification caveats or conflicting details, and the guide does not calculate distances or find routes by combining route fragments."""

def render():
    st.title("ℹ️ About the System")
    st.write("The guide retrieves information from the supplied campus documents and uses Groq to turn relevant source text into a clear answer. Campus-specific answers remain grounded in those documents.")
    st.code("User → Streamlit → Sentence Transformer → ChromaDB → Retrieved campus context → Groq API → Answer + metadata-matched images")
    st.write("Navigation only uses source records that explicitly mention both endpoints; it does not combine route fragments, infer missing turns, calculate distances, or run shortest-path routing. Route files can disagree or contain verification caveats, which should be checked against the campus before use.")
    question = st.text_input("Ask how the campus guide works")
    if st.button("Ask about the system", type="primary"):
        if not question.strip():
            st.warning("Enter a question about the campus guide.")
            return
        with st.spinner("Preparing an answer…"):
            response, _ = answer_with_context(
                question,
                [{"source": "Campus guide documentation", "chunk": 1, "text": SYSTEM_CONTEXT}],
                system_instruction="Answer questions about this application using only the supplied system description. Do not claim features that are not described.",
            )
        st.markdown(response)
