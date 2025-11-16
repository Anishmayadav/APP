import streamlit as st

# Page config
st.set_page_config(page_title="Simple Color Display", layout="centered")

# Target color
color = (100, 150, 255)  # Light Blue

st.title("Simple Color Display (Streamlit Version)")

# Convert RGB to CSS hex
hex_color = '#%02x%02x%02x' % color

# Display color block
st.markdown(
    f"""
    <div style='
         width: 600px;
         height: 400px;
         background-color: {hex_color};
         border: 3px solid black;
         border-radius: 10px;
         margin-top: 20px;'>
    </div>
    """,
    unsafe_allow_html=True
)

# Exit button
if st.button("Close Window"):
    st.write("Window closed (simulation).")
    st.stop()
