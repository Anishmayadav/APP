import streamlit as st
import cv2
from deepface import DeepFace
import json
import base64
import time
from st_clickable_images import clickable_images

if "current_section" not in st.session_state:
    st.session_state.current_section = None


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
    ["🏠 Home"] + SECTIONS,   # 👈 list + list works fine
    index=0
)









if menu == "🏠 Home":
    st.title("🏠 Welcome to Autistic Support Dashboard")
    st.success("This dashboard provides real-time emotion detection, gaze tracking, heart rate monitoring, and interactive therapy tools.")

    
    # ------------------------------
 
elif menu == "🧘 Color Tracker":
    st.title("🖍️ Color Preference Tracker")
    st.info("Track color attention using predefined gaze-based games.")

    

    script_paths = {
        "Tracker 1": "pages/color1.py",
        "Tracker 2": "D:/Streamlite/color2.py",
        "Tracker 3": "D:/Streamlite/color3.py",
        "Tracker 4": "D:/Streamlite/color4.py",
    }

    def show_tracker_controls(tracker_name):
        st.subheader(f"{tracker_name}")

        if st.button(f"▶️ Start {tracker_name}"):
            if os.path.exists(script_paths[tracker_name]):
                os.system(f'python "{script_paths[tracker_name]}" &')

                st.success(f"{tracker_name} started. Complete the session.")
            else:
                st.error(f"{tracker_name} script not found.")

        if st.button(f"📄 Show {tracker_name} Report"):
            result_path = result_paths[tracker_name]
            if os.path.exists(result_path):
                with open(result_path, "r", encoding="utf-8") as f:
                    report_lines = f.readlines()

                # Debug: show raw content
                st.text("📝 Raw Report Content:")
                st.code("".join(report_lines))

                # Parse float values with "sec"
                color_scores = {}
                for line in report_lines:
                    line = line.strip()

                    # Skip empty or non-data lines
                    if not line or "Summary" in line:
                        continue

                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            color = parts[0].strip()
                            value_str = parts[1].strip().replace("sec", "").strip()
                            try:
                                score = float(value_str)
                                color_scores[color] = score
                            except ValueError:
                                continue  # skip invalid numbers

                if color_scores:
                    st.subheader("🎯 Color-wise Attention Summary (Seconds)")
                    df = pd.DataFrame.from_dict(color_scores, orient='index', columns=['Time (sec)'])
                    df = df.round(2)
                    st.bar_chart(df)
                    st.table(df)
                else:
                    st.warning("Report is empty or incorrectly formatted.")
            else:
                st.warning(f"No report found for {tracker_name}.")


# 1. Set the page layout to 'wide' for a full-screen-like experience
    # Create 5 tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 colorTracker 1",
        "🎨 colorTracker 2", 
        "🎨 colorTracker 3",
        "🎨 colorTracker 4"
    ])

    with tab1:
        show_tracker_controls("Tracker 1")
   
    with tab2:
        show_tracker_controls("Tracker 2")

    with tab3:
        show_tracker_controls("Tracker 3")

    with tab4:
        show_tracker_controls("Tracker 4")
