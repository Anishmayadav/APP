import streamlit as st
import os

st.set_page_config(page_title="Autistic Support Dashboard", layout="wide")

st.title("🏠 Autistic Support Dashboard")

st.subheader("🧘 Color Tracker")

st.markdown("### Tracker Pages")

st.markdown("""
- <a href="https://anishmayadav.github.io/color1.py/" target="_blank">🟦 Open Color Tracker 1</a>
- <a href="https://yourname.github.io/color2/" target="_blank">🟩 Open Color Tracker 2</a>
- <a href="https://yourname.github.io/color3/" target="_blank">🟧 Open Color Tracker 3</a>
- <a href="https://yourname.github.io/color4/" target="_blank">🟥 Open Color Tracker 4</a>
""", unsafe_allow_html=True)
