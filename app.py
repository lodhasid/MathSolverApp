import streamlit as st
import base64
from PIL import Image
import io
from openai import OpenAI

# Custom CSS for mobile-first design
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide header */
    header {
        display: none !important;
    }

    /* Tabs */
    .stTabs {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        margin: 0;
        background: white;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1f77b4;
        color: rgba(255, 255, 255, 0.7);
        border-radius: 0;
        gap: 0;
        padding: 10px;
        flex: 1;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 18px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }

    /* Camera container */
    .stCamera {
        margin-top: 50px;  /* Height of tabs */
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 70px;  /* Leave space for retake button */
        background: black;
    }
    .stCamera > label {
        display: none;
    }
    .stCamera > div[data-testid="stCameraInput"] {
        border: none;
        padding: 0;
        height: 100%;
        width: 100%;
        cursor: pointer;
    }
    .stCamera video {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
    }

    /* Image display */
    .element-container:has(>.stImage) {
        margin-top: 50px;  /* Height of tabs */
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 70px;  /* Leave space for retake button */
        background: black;
    }
    .stImage {
        margin: 0;
        height: 100%;
        display: flex;
        align-items: center;
    }
    .stImage img {
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important;
    }

    /* Question input and button - fixed at bottom */
    .stTextInput, .stButton {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 10px;
        z-index: 1000;
    }
    .stTextInput {
        bottom: 60px;  /* Height of button + padding */
    }
    .stTextInput > div {
        padding: 0;
    }
    .stTextInput input {
        font-size: 16px;
    }
    .stButton > button {
        width: 100%;
        padding: 0.5rem;
        font-size: 16px;
        margin: 0;
    }

    /* Retake button - fixed at bottom */
    .stButton:has(button:contains("↺")) {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: white !important;
        padding: 10px !important;
        z-index: 9999 !important;
        margin: 0 !important;
    }
    .stButton:has(button:contains("↺")) button {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
        width: 100% !important;
        padding: 0.75rem !important;
        font-size: 18px !important;
        margin: 0 !important;
        font-weight: bold !important;
    }

    /* Click instruction */
    .camera-instruction {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        font-size: 16px;
        z-index: 1000;
        pointer-events: none;
    }

    /* File uploader */
    .stFileUploader {
        margin-top: 50px;  /* Height of tabs */
    }
    .stFileUploader > div {
        padding: 0;
    }
    .stFileUploader > div > div {
        padding: 0.5rem;
    }
    .stFileUploader label {
        color: #000000 !important;
        font-size: 16px;
        font-weight: 500;
    }
    .stFileUploader span {
        color: #000000 !important;
    }
    .stFileUploader p {
        color: #000000 !important;
    }
    .uploadedFile {
        color: #000000 !important;
    }
    .stFileUploader [data-testid="stFileUploadDropzone"] {
        color: #000000 !important;
    }

    /* Solution text */
    .stMarkdown {
        margin-bottom: 140px;  /* Space for input and button */
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

def encode_image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_openai_response(prompt, image=None):
    """Get response from OpenAI API"""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        if not api_key:
            raise Exception("OpenAI API key not found in secrets")
        client = OpenAI(api_key=api_key)
        
        if image:
            base64_image = encode_image_to_base64(image)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        else:
            messages = [{"role": "user", "content": prompt}]
        
        with st.status("Processing...", expanded=False) as status:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000
            )
            status.update(label="✓", state="complete")
        return response.choices[0].message.content
    except Exception as e:
        if "OPENAI_API_KEY" not in st.secrets:
            raise Exception("OpenAI API key not found")
        raise Exception(f"Error: {str(e)}")

# Streamlit UI
st.title("📱 Math Solver")

# Create tabs for camera and upload
tab1, tab2 = st.tabs(["📷 Camera", "📁 Upload"])

with tab1:
    if 'camera_image' not in st.session_state:
        st.session_state.camera_image = None

    # Show retake button if we have an image
    if st.session_state.camera_image is not None:
        image = Image.open(st.session_state.camera_image)
        st.image(image, use_container_width=True)
        
        if st.button("↺ Retake Photo", key="retake_button"):
            st.session_state.camera_image = None
            st.rerun()
    else:
        # Show camera input with click instruction
        st.markdown('<div class="camera-instruction">Tap to capture</div>', unsafe_allow_html=True)
        camera_image = st.camera_input("", label_visibility="collapsed")
        if camera_image:
            st.session_state.camera_image = camera_image
            st.rerun()

with tab2:
    uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

# Set image based on which input was used
if 'image' not in locals():
    if st.session_state.camera_image is not None:
        image = Image.open(st.session_state.camera_image)
    else:
        image = None

if image:
    prompt = st.text_input("", placeholder="Ask about the math problem...")
    
    if st.button("Solve 🔍"):
        try:
            response = get_openai_response(prompt, image)
            st.markdown(f"### Solution\n{response}")
        except Exception as e:
            st.error(str(e)) 