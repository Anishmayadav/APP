import streamlit as st

st.set_page_config(page_title="Autistic Support Dashboard", layout="wide")

st.title("🏠 Autistic Support Dashboard")

st.subheader("🧘 Color Tracker")

st.markdown("### Tracker Pages")

st.markdown("""
- <a href="/color1" target="_blank">🟦 Open Color Tracker 1</a>
- <a href="/color2" target="_blank">🟩 Open Color Tracker 2</a>
- <a href="/color3" target="_blank">🟧 Open Color Tracker 3</a>
- <a href="/color4" target="_blank">🟥 Open Color Tracker 4</a>
""", unsafe_allow_html=True)
