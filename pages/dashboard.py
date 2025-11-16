import streamlit as st
import pandas as pd

# ----------------------- Must be First -----------------------
st.set_page_config(page_title="Autistic Support Dashboard", layout="wide")

SECTIONS = [
    "🧘 Color Tracker",
    "🎮 Games",
    "🎨 Cartoon Therapy",
    "🎮 LifeQuest Game",
]

# ----------------------- Sidebar -----------------------
st.sidebar.title("📋 Dashboard Menu")
menu = st.sidebar.radio(
    "Go to",
    ["🏠 Home"] + SECTIONS,
    index=0
)

# ----------------------- Home Page -----------------------
if menu == "🏠 Home":
    st.title("🏠 Welcome to Autistic Support Dashboard")
    st.success(
        "This dashboard provides basic interactive tools for therapy and learning.\n\n"
        "Cloud-compatible version: tracking & games run inside Streamlit."
    )

# ----------------------- Color Tracker -----------------------
elif menu == "🧘 Color Tracker":
    st.title("🖍️ Color Preference Tracker")
    st.info("This cloud version shows color blocks directly in Streamlit.")

    # ------------------ Tracker UI Function ------------------
    def show_color_block(r, g, b):
        """Displays a color block in Streamlit."""
        hex_color = '#%02x%02x%02x' % (r, g, b)
        st.markdown(
            f"""
            <div style='
                width: 600px;
                height: 350px;
                background-color: {hex_color};
                border-radius: 12px;
                border: 3px solid black;
                margin-top: 20px;'>
            </div>
            """,
            unsafe_allow_html=True
        )

    def tracker_ui(title, default_color):
        st.subheader(title)
        st.write("Color displayed below:")

        show_color_block(*default_color)

        if st.button(f"Record {title} Data"):
            st.success("In cloud version, recording is simulated.")
            st.code(f"Color viewed: RGB {default_color}")

    # ------------------ Tabs ------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 ColorTracker 1",
        "🎨 ColorTracker 2",
        "🎨 ColorTracker 3",
        "🎨 ColorTracker 4"
    ])

    with tab1:
        tracker_ui("Tracker 1", (100, 150, 255))

    with tab2:
        tracker_ui("Tracker 2", (255, 200, 100))

    with tab3:
        tracker_ui("Tracker 3", (150, 255, 140))

    with tab4:
        tracker_ui("Tracker 4", (240, 120, 120))
