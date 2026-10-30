import streamlit as st
from src.chatbot import answer

def render():
    st.title("💬 AI Campus Assistant")
    if "history" not in st.session_state: st.session_state.history=[]
    for item in st.session_state.history:
        with st.chat_message(item["role"]): st.markdown(item["content"])
    q=st.chat_input("Ask about campus locations or directions")
    if q:
        st.session_state.history.append({"role":"user","content":q})
        with st.chat_message("user"): st.write(q)
        with st.chat_message("assistant"):
            with st.spinner("Searching campus files…"): response, docs=answer(q,st.session_state.history[:-1])
            st.markdown(response)
            if docs:
                with st.expander("Retrieved sources"):
                    for d in docs: st.caption(f"{d['source']} · chunk {d['chunk']} · cosine distance {d['distance']:.3f}"); st.write(d["text"])
        st.session_state.history.append({"role":"assistant","content":response})
