import streamlit as st
from src.campus_explorer import explore
from config import IMAGE_DIR

def render():
    st.title("🔎 Campus Explorer")
    q=st.text_input("Search campus locations, facilities, or route landmarks")
    if q:
        with st.spinner("Searching campus files and preparing an answer…"):
            response,docs,imgs=explore(q)
        st.markdown(response)
        if imgs:
            cols=st.columns(min(3,len(imgs)))
            for col,img in zip(cols,imgs):
                with col: st.image(str(IMAGE_DIR/img["filename"]),caption=img.get("title") or img.get("location"))
        if docs:
            with st.expander("Retrieved campus sources"):
                for d in docs:
                    st.caption(f"{d['source']} · chunk {d['chunk']} · cosine distance {d['distance']:.3f}")
                    st.write(d["text"])
