import streamlit as st
import pandas as pd

# ----------------------- Must be First -----------------------
st.set_page_config(page_title="Autistic Support Dashboard", layout="wide")


# ----------------------- Color Tracker Components -----------------------

def color_tracker_page(rgb_color, title="Color Tracker"):
    """Renders a full-screen color block inside Streamlit."""
    
    st.title(title)

    hex_color = '#%02x%02x%02x' % rgb_color

    st.markdown(
        f"""
        <div style="
            width: 95vw;
            height: 85vh;
            background-color: {hex_color};
            border-radius: 15px;
            border: 5px solid black;
        ">
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("⬅️ Back to Dashboard"):
        st.session_state["page"] = "home"
        st.rerun()


# ----------------------- Sidebar -----------------------

if "page" not in st.session_state:
    st.session_state.page = "home"

st.sidebar.title("📋 Dashboard Menu")

menu = st.sidebar.radio(
    "Go to",
    ["🏠 Home", "🧘 Color Tracker"],
    index=0
)


# ----------------------- Home Page -----------------------

if menu == "🏠 Home":
    st.session_state.page = "home"

    st.title("🏠 Welcome to Autistic Support Dashboard")
    st.success("Real-time therapy tools including color tracking, games, and emotion detection.")


# ----------------------- Color Tracker -----------------------

elif menu == "🧘 Color Tracker":

    st.title("🖍️ Color Preference Trackers")
    st.info("Choose a color tracker. Each opens full screen.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 Tracker 1",
        "🎨 Tracker 2",
        "🎨 Tracker 3",
        "🎨 Tracker 4",
    ])

    with tab1:
        if st.button("Start Tracker 1"):
            st.session_state.page = "c1"
            st.rerun()

    with tab2:
        if st.button("Start Tracker 2"):
            st.session_state.page = "c2"
            st.rerun()

    with tab3:
        if st.button("Start Tracker 3"):
            st.session_state.page = "c3"
            st.rerun()

    with tab4:
        if st.button("Start Tracker 4"):
            st.session_state.page = "c4"
            st.rerun()


# ----------------------- Full Screen Color Pages -----------------------

if st.session_state.page == "c1":
    color_tracker_page((100, 150, 255), "🎨 Color Tracker 1 (Light Blue)")

if st.session_state.page == "c2":
    color_tracker_page((255, 100, 120), "🎨 Color Tracker 2 (Pink Shade)")

if st.session_state.page == "c3":
    color_tracker_page((120, 255, 140), "🎨 Color Tracker 3 (Green Shade)")

if st.session_state.page == "c4":
    color_tracker_page((255, 220, 90), "🎨 Color Tracker 4 (Yellow Shade)")
