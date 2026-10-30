import streamlit as st
from src.navigation import directions_answer
from src.image_retrieval import route_images
from config import IMAGE_DIR

def render():
    st.title("🧭 Campus Navigation")
    st.info("Destination discovery and source-listed directions are available. The files contain no verified campus graph or walking distances; some routes explicitly require verification. The app will not combine routes or calculate shortest paths.")
    start=st.text_input("Starting location", value="Main Gate")
    destination=st.text_input("Destination")
    if st.button("Find directions", type="primary"):
        if not start.strip() or not destination.strip():
            st.warning("Enter both a starting location and a destination.")
            return
        with st.spinner("Checking campus routes and preparing directions…"):
            response,hits=directions_answer(start,destination)
        if not hits:
            st.warning("No source record explicitly matched both the starting location and destination. Try a known location name or check the route files.")
        else:
            st.markdown(response)
            imgs=route_images(hits,start,destination)
            if imgs:
                st.subheader("Photos along this route")
                for offset in range(0,len(imgs),3):
                    route_images_row=imgs[offset:offset+3]
                    cols=st.columns(len(route_images_row))
                    for index,(col,img) in enumerate(zip(cols,route_images_row),start=offset+1):
                        with col:
                            st.image(str(IMAGE_DIR/img["filename"]),caption=f"{index}. {img.get('title') or img.get('location') or img['filename']}")
            with st.expander("Retrieved route sources"):
                for h in hits:
                    st.caption(f"{h['source']} · chunk {h['chunk']}")
                    st.write(h["text"])
