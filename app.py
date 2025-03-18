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
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1f77b4;
        border-radius: 4px;
        gap: 1px;
        padding: 10px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }

    /* Camera input */
    .stCamera > label {
        display: none;
    }
    .stCamera > div[data-testid="stCameraInput"] {
        border: none;
        padding: 0;
    }
    button.step-up, button.step-down {
        display: none;
    }

    /* Image display */
    .stImage {
        margin-top: 0.5rem;
    }

    /* Question input */
    .stTextInput > div {
        padding: 5px;
    }
    .stTextInput input {
        font-size: 16px;
    }

    /* Submit button */
    .stButton > button {
        width: 100%;
        padding: 0.5rem;
        font-size: 16px;
        margin: 0.5rem 0;
    }

    /* File uploader */
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
    /* Make drag and drop text visible */
    .stFileUploader [data-testid="stFileUploadDropzone"] {
        color: #000000 !important;
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
        if st.button("↺ Retake"):
            st.session_state.camera_image = None
            st.rerun()
        
        image = Image.open(st.session_state.camera_image)
        st.image(image, use_container_width=True)
    else:
        # Show camera input if we don't have an image
        camera_image = st.camera_input("")
        if camera_image:
            st.session_state.camera_image = camera_image
            st.rerun()

with tab2:
    uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])
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