import streamlit as st

st.set_page_config(page_title="Color Tracker 1", layout="wide")

color = (100, 150, 255)  # Light Blue
hex_color = '#%02x%02x%02x' % color

st.title("🎨 Color Tracker 1")

st.markdown(
    f"""
    <div style="
         width: 100vw;
         height: 90vh;
         background-color: {hex_color};
         border: 5px solid black;
         border-radius: 10px;
         position: fixed;
         top: 60px;
         left: 0px;
         ">
    </div>
    """,
    unsafe_allow_html=True
)
