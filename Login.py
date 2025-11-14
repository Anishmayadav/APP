# -*- coding: utf-8 -*-
import streamlit as st
from supabase import create_client, Client
from streamlit_extras.switch_page_button import switch_page

import hashlib
import base64
import time

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🔐 Therapy App — Login / Signup", layout="centered")

# ------------------- ADD BACKGROUND IMAGE -------------------
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
    except FileNotFoundError:
        st.error(f"Background image file '{image_file}' not found. Please ensure it is in the same directory.")
        encoded = ""
        
    page_bg = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# ✅ Add your background image file here
add_bg_from_local("HD-wallpaper-smile-color-hand-paint.jpg")

# ------------------- CLEAN UI STYLING -------------------
st.markdown("""
    <style>
    .block-container {
        max-width: 550px !important;
        padding-top: 2rem !important;
        margin: auto;
        background: rgba(255, 255, 255, 0.75);
        border-radius: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        padding: 2rem 2.5rem;
        backdrop-filter: blur(6px);
    }

    div[data-testid="stTextInput"] > label {
        font-weight: 600 !important;
        color: #004080 !important;
        margin-bottom: 6px !important;
        display: block !important;
        text-align: left !important;
    }

    input[type="text"], input[type="password"] {
        width: 100% !important;
        height: 38px !important;
        background-color: rgba(232, 244, 255, 0.95) !important;
        border: 1.5px solid #0078d7 !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        font-size: 15px !important;
        color: #000 !important;
        outline: none !important;
        box-shadow: none !important;
        transition: 0.3s;
    }

    input[type="text"]:focus, input[type="password"]:focus {
        border-color: #004080 !important;
        box-shadow: 0 0 5px #0078d7 !important;
    }

    div.stButton > button:first-child {
        width: 100% !important;
        background-color: #0078d7 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 42px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        transition: 0.3s ease-in-out;
    }

    div.stButton > button:first-child:hover {
        background-color: #005a9e !important;
    }

    div[role="radiogroup"] {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: -10px !important;
        margin-top: 0.5rem !important;
    }

    h2 {
        margin-top: -10px !important;
        margin-bottom: 0.75rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------- CONNECT TO SUPABASE -------------------
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except KeyError:
    st.error("Missing SUPABASE_URL or SUPABASE_KEY in st.secrets.")
    supabase = None
except Exception as e:
    st.error(f"Failed to connect to Supabase: {e}")
    supabase = None

# ------------------- PASSWORD HASHING -------------------
def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------- SIGNUP FUNCTION (Fixed for Supabase API errors) -------------------
def signup_user(username, password):
    if not supabase: return False
    
    hashed_pw = make_hash(password)
    try:
        data = {"username": username, "password": hashed_pw}
        response = supabase.table("User").insert(data).execute()
        
        if response.data:
            return True
        return False
        
    except Exception as e:
        error_message = str(e)
        
        if "duplicate key" in error_message.lower() or "unique constraint" in error_message.lower():
            st.error("⚠️ Failed to create account. That **Username already exists**. Please choose another.")
        else:
            st.error(f"⚠️ An unexpected error occurred during sign up: {error_message}")
        
        return False

# ------------------- LOGIN FUNCTION -------------------
def login_user(username, password):
    if not supabase: return False
    
    hashed_pw = make_hash(password)
    try:
        response = supabase.table("User").select("id, password").eq("username", username).limit(1).execute()
        
        if response.data:
            st.session_state.user_id = response.data[0].get("id")
            return response.data[0]["password"] == hashed_pw
        return False
    except Exception as e:
        st.error(f"⚠️ Error during login: {e}")
        return False

# ------------------- MAIN UI -------------------
st.title("🔐 Therapy App — Login / Signup")

choice = st.radio("Select Option", ["Login", "Sign Up"], horizontal=True)
st.markdown("<div style='margin-top:-15px;'></div>", unsafe_allow_html=True)

# ------------------- SIGNUP SECTION -------------------
if choice == "Sign Up":
    st.subheader("Create Account")
    new_user = st.text_input("Username", key="new_user")
    new_pass = st.text_input("Password", type="password", key="new_pass")

    if st.button("Sign Up"):
        if new_user and new_pass:
            if signup_user(new_user, new_pass):
                st.success("✅ Account created successfully! Redirecting...")
                
                # --- FIX APPLIED: Using the canonical page name (assuming question.py is in pages/) ---
                # The file structure suggests it's a multi-page app file, so this is the correct format.
                time.sleep(1) 
                st.switch_page("pages/question.py")

 
                
            else:
                pass  
        else:
            st.warning("Please fill all fields.")

# ------------------- LOGIN SECTION -------------------
elif choice == "Login":
    st.subheader("Login to Your Account")
    user = st.text_input("Username", key="login_user")
    pw = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        if login_user(user, pw):
            st.session_state.logged_in = True
            st.session_state.username = user
            st.success(f"🎉 Welcome back, {user}! Redirecting...")
            
            # --- Using canonical page name (assuming dashboard.py is in pages/) ---
            time.sleep(1) 
            st.switch_page("pages/dashboard.py") 
            
        else:
            st.error("❌ Invalid username or password.")

