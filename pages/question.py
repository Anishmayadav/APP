import streamlit as st
import time
import json
import base64
from datetime import datetime

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="User Profile Questionnaire",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------- BACKGROUND IMAGE -------------------
def add_bg_from_local(image_file):
    # Fallback CSS: Gentle blue/white gradient for a calming effect if the file is missing
    fallback_css = """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e6f7ff 0%, #f0f8ff 100%);
        background-size: cover;
        background-attachment: fixed;
    }
    </style>
    """
    try:
        # Attempt to load and apply local image
        with open(image_file, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        
        page_bg_img = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        # Use fallback if image is missing
        st.markdown(fallback_css, unsafe_allow_html=True)
        # Updated info message to confirm the file couldn't be found
        st.info(f"Note: The file '{image_file}' was not found in the current directory. Using a default calming gradient background.")
    except Exception as e:
        # Handle other errors (e.g., permission issues)
        st.markdown(fallback_css, unsafe_allow_html=True)
        st.error(f"Error loading background image: {e}. Using a fallback gradient.")

# Apply the background image (requires 'question.jpg' in the same folder)
add_bg_from_local("question.jpg")

# ------------------- HEADER -------------------
st.title("📋 User Profile Questionnaire")
st.markdown("### Help us understand you better to personalize your experience!")

# ------------------- SESSION STATE -------------------
if 'questionnaire_completed' not in st.session_state:
    st.session_state.questionnaire_completed = False
if 'user_responses' not in st.session_state:
    st.session_state.user_responses = {}

# ------------------- CUSTOM CSS -------------------
st.markdown("""
<style>
/* Ensure form elements are readable against the background */
.stForm {
    background-color: rgba(255, 255, 255, 0.9); /* Slightly transparent white background for readability */
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.question-card {
    background-color: #f8f9fa;
    padding: 25px;
    border-radius: 15px;
    border-left: 6px solid #4ECDC4;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.result-card {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

# ------------------- QUESTIONNAIRE FORM -------------------
if not st.session_state.questionnaire_completed:
    with st.form("user_questionnaire"):

        # 1. Age Group
        st.markdown('<div class="question-card"><h3>🧒 1. Age Group</h3>', unsafe_allow_html=True)
        age_group = st.radio(
            "Select your age group:",
            ["Toddler (3-5 years)", "Early Learner (5-7 years)",
             "School-Age Child (7-10 years)", "Adolescent (10-12 years)"],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Autism in Family
        st.markdown('<div class="question-card"><h3>👨‍👩‍👧‍👦 2. Autism in Family</h3>', unsafe_allow_html=True)
        family_member = st.radio(
            "Does anyone in the child’s family have autism or display autistic traits?",
            ["Mother", "Father", "Sister", "Brother", "No one"],
            index=4
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. Technology Experience
        st.markdown('<div class="question-card"><h3>🎯 3. Experience Level with Technology</h3>', unsafe_allow_html=True)
        tech_level = st.radio(
            "How comfortable are you with technology?",
            ["Beginner (New to apps/games)", "Intermediate (Some experience)",
             "Advanced (Comfortable with tech)", "Expert (Tech enthusiast)"],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. Favorite Color
        st.markdown('<div class="question-card"><h3>🎨 4. Favorite Color</h3>', unsafe_allow_html=True)
        st.write("Select your favorite color(s):")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            red = st.checkbox("🔴 Red")
        with col2:
            blue = st.checkbox("🔵 Blue")
        with col3:
            green = st.checkbox("🟢 Green")
        with col4:
            yellow = st.checkbox("🟡 Yellow")

        selected_colors = []
        color_mapping = {"red": red, "blue": blue, "green": green, "yellow": yellow}
        for color, selected in color_mapping.items():
            if selected:
                selected_colors.append(color)
        st.markdown('</div>', unsafe_allow_html=True)

        # 5. Activity Preference
        st.markdown('<div class="question-card"><h3>🎮 5. Preferred Activity Type</h3>', unsafe_allow_html=True)
        activity_preference = st.selectbox(
            "What type of activities do you enjoy most?",
            ["Creative (Drawing, Music, Stories)", "Active (Movement, Sports, Games)",
             "Calming (Meditation, Puzzles, Reading)", "Social (Talking, Sharing, Group activities)",
             "Learning (Educational games, Quizzes)"]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 6. Support Preferences
        st.markdown('<div class="question-card"><h3>🌟 6. Support Preferences</h3>', unsafe_allow_html=True)
        support_preferences = st.multiselect(
            "What kind of support would be most helpful for you?",
            ["Visual aids and colors", "Step-by-step instructions",
             "Voice guidance", "Simple interfaces", "Reward systems",
             "Social interaction", "Quiet activities", "Movement breaks"]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Submit Button
        submitted = st.form_submit_button("🚀 Submit Questionnaire", use_container_width=True)

        if submitted:
            if not selected_colors:
                st.error("Please select at least one favorite color!")
            elif not support_preferences:
                st.error("Please select at least one support preference!")
            else:
                st.session_state.user_responses = {
                    "age_group": age_group,
                    "family_member": family_member,
                    "tech_level": tech_level,
                    "favorite_colors": selected_colors,
                    "activity_preference": activity_preference,
                    "support_preferences": support_preferences,
                    "completion_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.questionnaire_completed = True
                st.success("✅ Questionnaire submitted successfully!")
                st.balloons()
                time.sleep(2)
                st.rerun()

# ------------------- DISPLAY RESULTS -------------------
else:
    responses = st.session_state.user_responses

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.header("🎉 Questionnaire Completed!")
    st.subheader("Thank you for sharing your preferences!")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Left Column: Profile Summary
    with col1:
        st.subheader("📊 Your Profile Summary")
        st.metric("Age Group", responses["age_group"])
        st.metric("Tech Level", responses["tech_level"])
        st.metric("Activity Preference", responses["activity_preference"])
        st.metric("Family Member", responses["family_member"])

        st.subheader("🎨 Favorite Colors")
        color_display = ""
        color_emoji = {
            "red": "🔴", "blue": "🔵", "green": "🟢", "yellow": "🟡"
        }
        for color in responses["favorite_colors"]:
            color_display += f'{color_emoji.get(color, "⚪")} {color.capitalize()}  '
        st.write(color_display)

    # Right Column: Recommendations
    with col2:
        st.subheader("💡 Recommended Support")
        recommendations = []

        if "Child" in responses["age_group"]:
            recommendations += [
                "🎈 Simple, colorful interfaces with big buttons",
                "🎮 Game-based learning activities",
                "📚 Visual stories and animated content"
            ]
        elif "Adolescent" in responses["age_group"]:
            recommendations += [
                "🎵 Music and creative expression tools",
                "🎯 Challenge-based games with rewards",
                "👥 Social sharing features"
            ]

        if "Beginner" in responses["tech_level"]:
            recommendations += [
                "🔄 Step-by-step tutorials",
                "🎯 One-tap simple interactions",
                "📱 Minimal interface options"
            ]
        elif "Expert" in responses["tech_level"]:
            recommendations += [
                "⚙️ Customizable settings",
                "📊 Detailed progress tracking",
                "🔧 Advanced features access"
            ]

        if "Creative" in responses["activity_preference"]:
            recommendations += [
                "🎨 Drawing and coloring activities",
                "🎵 Music and sound exploration",
                "📖 Interactive storytelling"
            ]
        elif "Active" in responses["activity_preference"]:
            recommendations += [
                "💪 Movement-based games",
                "🏃 Physical activity tracking",
                "🎯 Action-oriented challenges"
            ]
        elif "Calming" in responses["activity_preference"]:
            recommendations += [
                "🧘 Meditation and breathing exercises",
                "🧩 Relaxing puzzles",
                "🌊 Soothing visual experiences"
            ]

        if "Visual aids and colors" in responses["support_preferences"]:
            recommendations += ["🌈 Color-coded instructions", "📸 Picture-based guidance"]
        if "Voice guidance" in responses["support_preferences"]:
            recommendations += ["🔊 Audio instructions available", "🎵 Sound feedback for actions"]
        if "Reward systems" in responses["support_preferences"]:
            recommendations += ["⭐ Points and achievement system", "🏆 Badges and progress tracking"]

        for rec in set(recommendations):
            st.write(f"• {rec}")

    # Color visualization
    st.markdown("---")
    st.subheader("🎨 Your Color Preferences Visualization")
    colors_hex = {
        "red": "#FF6B6B", "blue": "#4ECDC4", "green": "#6BCF7F",
        "yellow": "#FFD166"
    }
    color_html = "<div style='display: flex; height: 50px; border-radius: 10px; overflow: hidden; margin: 20px 0;'>"
    for color in responses["favorite_colors"]:
        hex_color = colors_hex.get(color, "#CCCCCC")
        color_html += f"<div style='flex: 1; background-color: {hex_color};'></div>"
    color_html += "</div>"
    st.markdown(color_html, unsafe_allow_html=True)

    # Personalized dashboard info
    st.markdown("---")
    st.subheader("🚀 Personalized Dashboard Setup")
    st.info("""
    Based on your questionnaire, we've optimized your dashboard with:
    - **Interface**: Adjusted for your age group and tech level  
    - **Activities**: Prioritized your preferred activity types  
    - **Support**: Incorporated your chosen support methods  
    - **Colors**: Used your favorite colors throughout the interface
    """)

    # Reset Questionnaire Button
    st.markdown("---")
    if st.button("🔄 Take Questionnaire Again", use_container_width=True):
        st.session_state.questionnaire_completed = False
        st.session_state.user_responses = {}
        st.rerun()

    # Download Results
    st.download_button(
        label="📥 Download Your Profile",
        data=json.dumps(responses, indent=2),
        file_name=f"user_profile_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )
