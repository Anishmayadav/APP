import os
import streamlit as st
import pandas as pd

# ----------------------- Must be First -----------------------
st.set_page_config(page_title="Autistic Support Dashboard", layout="wide")

# Import Pygame Color Trackers
from pages import color1, color2, color3, color4

# ----------------------- Sidebar -----------------------
SECTIONS = [
    "🧘 Color Tracker",
    "🎮 Games",
    "🎨 Cartoon Therapy",
    "🎮 LifeQuest Game",
]

st.sidebar.title("📋 Dashboard Menu")

menu = st.sidebar.radio(
    "Go to",
    ["🏠 Home"] + SECTIONS,
    index=0
)


# ---------------------------------------------------------------
#                          HOME PAGE
# ---------------------------------------------------------------
if menu == "🏠 Home":
    st.title("🏠 Welcome to Autistic Support Dashboard")
    st.success(
        "This dashboard provides real-time emotion detection, gaze tracking, "
        "heart rate monitoring, and interactive therapy tools."
    )


# ---------------------------------------------------------------
#                     COLOR TRACKER SECTION
# ---------------------------------------------------------------
elif menu == "🧘 Color Tracker":

    st.title("🖍️ Color Preference Tracker")
    st.info("Track color attention using predefined gaze-based games.")

    st.write("Select a Color Tracker tab below to begin 👇")

    # Tabs for 4 color trackers
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 ColorTracker 1",
        "🎨 ColorTracker 2",
        "🎨 ColorTracker 3",
        "🎨 ColorTracker 4"
    ])

    with tab1:
        st.subheader("Tracker 1")
        color1.run()

    with tab2:
        st.subheader("Tracker 2")
        color2.run()

    with tab3:
        st.subheader("Tracker 3")
        color3.run()

    with tab4:
        st.subheader("Tracker 4")
        color4.run()


# ---------------------------------------------------------------
#                   OTHER SECTIONS (FUTURE PAGES)
# ---------------------------------------------------------------
elif menu == "🎮 Games":
    st.title("🎮 Games (Coming Soon)")
    st.info("Add your games here.")


elif menu == "🎨 Cartoon Therapy":
    st.title("🎨 Cartoon Therapy (Coming Soon)")
    st.info("Therapeutic animated content will appear here.")


elif menu == "🎮 LifeQuest Game":
    st.title("🎮 LifeQuest Game (Coming Soon)")
    st.info("Interactive emotional learning game will appear here.")
