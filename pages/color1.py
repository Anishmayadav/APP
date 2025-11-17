import streamlit as st
import streamlit.components.v1 as components
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av
import cv2
import numpy as np
from deepface import DeepFace
import threading

st.set_page_config(layout="wide")
st.title("Color Tracker 1  —  Live Emotion Detection (DeepFace)")

# -------------------------
# Left: color canvas (your original)
# -------------------------
with st.container():
    st.subheader("Color Canvas")
    # Set color here (R, G, B)
    color = (135, 206, 250)  # Light sky blue

    html_template = """
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

            ctx.fillStyle = 'rgb(%d, %d, %d)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = 'white';
            ctx.font = '30px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Color: RGB(%d, %d, %d)', canvas.width/2, canvas.height/2);
        </script>
    </body>
    </html>
    """ % (color[0], color[1], color[2], color[0], color[1], color[2])

    components.html(html_template, height=450)

# Color picker sliders
st.subheader("Change Color")
col1, col2, col3 = st.columns(3)
with col1:
    r = st.slider("Red", 0, 255, color[0])
with col2:
    g = st.slider("Green", 0, 255, color[1])
with col3:
    b = st.slider("Blue", 0, 255, color[2])

if (r, g, b) != color:
    new_html = """
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

            ctx.fillStyle = 'rgb(%d, %d, %d)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = 'white';
            ctx.font = '30px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Color: RGB(%d, %d, %d)', canvas.width/2, canvas.height/2);
        </script>
    </body>
    </html>
    """ % (r, g, b, r, g, b)
    components.html(new_html, height=450)

# -------------------------
# Right: live webcam + DeepFace emotion detection
# -------------------------
st.subheader("Live Emotion Detection (DeepFace)")

# Options
model_action = st.selectbox("DeepFace actions", ("emotion",), index=0)
enforce_detection = st.checkbox("Enforce face detection (may drop frames if False)", value=False)
detector_backend = st.selectbox("Detector backend", ("opencv", "mtcnn", "retinaface", "ssd", "dlib"), index=0)

# We use webrtc_streamer to show live webcam and process frames
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Transformer that runs DeepFace on each frame and draws overlay
class EmotionTransformer(VideoTransformerBase):
    def __init__(self):
        # run heavy model loading lazily to avoid blocking Streamlit UI thread
        self.model_loaded = False
        self.lock = threading.Lock()

    def _ensure_model(self):
        # DeepFace loads models lazily inside analyze; we use a simple flag
        with self.lock:
            if not self.model_loaded:
                # Running a dummy call to force model downloads/caching (small image)
                try:
                    DeepFace.build_model("Emotion")
                except Exception:
                    # If building fails, ignore here; analyze will attempt later
                    pass
                self.model_loaded = True

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        self._ensure_model()
        img = frame.to_ndarray(format="bgr24")  # OpenCV BGR

        try:
            # convert to RGB for DeepFace
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # analyze emotion only
            result = DeepFace.analyze(
                rgb_img,
                actions=["emotion"],
                enforce_detection=enforce_detection,
                detector_backend=detector_backend,
                prog_bar=False,
            )
            # DeepFace may return a list (if multiple faces) or a single dict
            if isinstance(result, list) and len(result) > 0:
                face_data = result[0]
            else:
                face_data = result

            # extract dominant emotion + scores
            dominant = face_data.get("dominant_emotion", None)
            scores = face_data.get("emotion", {})

            # Draw overlay: text and simple bar for emotion scores
            if dominant:
                text = f"Dominant: {dominant}"
                cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            1.0, (255, 255, 255), 2, cv2.LINE_AA)

            # Draw small bars for top emotions
            if isinstance(scores, dict):
                start_y = 60
                max_bar_w = 200
                for i, (emo, val) in enumerate(sorted(scores.items(), key=lambda x: -x[1])[:5]):
                    y = start_y + i * 22
                    bar_w = int((val / 100.0) * max_bar_w)
                    cv2.rectangle(img, (10, y), (10 + bar_w, y + 16), (0, 128, 0), -1)
                    cv2.putText(img, f"{emo}: {int(val)}%", (220, y + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255), 1, cv2.LINE_AA)

        except Exception as e:
            # If DeepFace fails (no face, model, etc.), write a small message
            cv2.putText(img, f"No face / error: {str(e)[:60]}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Start the webcam streamer
webrtc_ctx = webrtc_streamer(
    key="deepface-emotion",
    video_transformer_factory=EmotionTransformer,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    async_transform=True,
    desired_playing=True,
)

st.caption("Notes: DeepFace analyzes frames and returns the dominant emotion. Use 'enforce detection' carefully — on low-powered devices it may drop frames.")
