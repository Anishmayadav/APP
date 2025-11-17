import streamlit as st
import streamlit.components.v1 as components

st.title("Color Tracker 1")

# Set color here (R, G, B)
color = (135, 206, 250)  # Light sky blue

# Create interactive HTML canvas
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
        }}
        canvas {{
            border: 2px solid #333;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <canvas id="myCanvas" width="600" height="400"></canvas>
    
    <script>
        const canvas = document.getElementById('myCanvas');
        const ctx = canvas.getContext('2d');
        
        // Set the background color
        ctx.fillStyle = 'rgb({color[0]}, {color[1]}, {color[2]})';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Optional: Add some text
        ctx.fillStyle = 'white';
        ctx.font = '30px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Color: RGB({color[0]}, {color[1]}, {color[2]})', 
                     canvas.width/2, canvas.height/2);
    </script>
</body>
</html>
"""

# Display the HTML canvas
components.html(html_code, height=450)

# Color picker
st.subheader("Change Color")
col1, col2, col3 = st.columns(3)
with col1:
    r = st.slider("Red", 0, 255, color[0])
with col2:
    g = st.slider("Green", 0, 255, color[1])
with col3:
    b = st.slider("Blue", 0, 255, color[2])

if (r, g, b) != color:
    new_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #f0f0f0;
            }}
            canvas {{
                border: 2px solid #333;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <canvas id="myCanvas" width="600" height="400"></canvas>
        
        <script>
            const canvas = document.getElementById('myCanvas');
            const ctx = canvas.getContext('2d');
            
            ctx.fillStyle = 'rgb({r}, {g}, {b})';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = 'white';
            ctx.font = '30px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Color: RGB({r}, {g}, {b})', 
                         canvas.width/2, canvas.height/2);
        </script>
    </body>
    </html>
    """
    components.html(new_html, height=450)
