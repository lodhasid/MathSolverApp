import streamlit as st
import requests
from dotenv import load_dotenv
import os
import base64
from PIL import Image
import io
from openai import OpenAI

# Load environment variables
load_dotenv()

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
    }
    .uploadedFile {
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        margin: 1rem 0;
        padding: 0.5rem;
    }
    .stTextInput>div>div>input {
        padding: 0.5rem;
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
            # Convert image to base64
            base64_image = encode_image_to_base64(image)
            
            # Prepare messages with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
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
            # Text-only messages
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        
        with st.status("Processing...", expanded=True) as status:
            st.write("Sending request to OpenAI API...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000
            )
            status.update(label="Done!", state="complete")
        return response.choices[0].message.content
    except Exception as e:
        if "OPENAI_API_KEY" not in st.secrets:
            raise Exception("OpenAI API key not found. Please add it to .streamlit/secrets.toml")
        raise Exception(f"API request failed: {str(e)}")

# Streamlit UI with improved mobile layout
st.title("📱 Math Problem Solver")

# Create two columns for the description
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    Upload a photo of your math problem and ask questions about it. 
    I'll help you solve it step by step! 📝
    """)

# Text input with clear placeholder
prompt = st.text_input(
    "Your question:",
    placeholder="Example: How do I solve this equation?",
    help="Type your question about the math problem here"
)

# Image upload with clear instructions
st.markdown("### 📸 Capture or Upload Image")

# Create tabs for camera and upload
tab1, tab2 = st.tabs(["📷 Camera", "📁 Upload"])

with tab1:
    st.markdown("""
    📱 **Using Camera on Mobile:**
    1. Connect your phone to the same WiFi network as this computer
    2. Access using the Network URL shown in the terminal when the app starts
       Example: http://192.168.x.x:8502
       Note: The exact IP address will be shown in the terminal
    3. If camera doesn't work:
       - Allow camera permissions in browser settings
       - Try Chrome or Firefox (some browsers may block camera)
       - Try clearing browser cache and refreshing
    """)
    
    try:
        camera_placeholder = st.empty()
        camera_image = camera_placeholder.camera_input(
            "Take a picture",
            help="Click to take a photo using your device's camera",
            key=None  # Remove the key to avoid caching issues
        )
        
        if camera_image is not None:
            try:
                image = Image.open(camera_image)
                # Use columns to make image display more responsive
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    st.image(image, caption="Your Math Problem", use_container_width=True)
                st.success("✅ Image captured successfully!")
            except Exception as e:
                st.error("❌ Error processing the image. Please try again.")
                st.info("💡 Tip: Make sure your camera is working and try refreshing the page if issues persist.")
    except Exception as e:
        st.error("❌ Camera access failed. Please check your camera permissions.")
        st.info("""
        💡 Troubleshooting Tips:
        - Allow camera access in your browser settings
        - Make sure you're using a secure (HTTPS) connection
        - Try using a different browser
        - Refresh the page and try again
        """)

with tab2:
    uploaded_file = st.file_uploader(
        "Upload an image of your math problem",
        type=["png", "jpg", "jpeg"],
        help="Supported formats: PNG, JPG, JPEG"
    )
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # Use columns to make image display more responsive
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(image, caption="Your Math Problem", use_column_width=True)

# Set image based on which input was used
if 'image' not in locals():
    image = None

# Add a prominent button to get response
if st.button("🔍 Solve Problem", type="primary", use_container_width=True):
    try:
        response = get_openai_response(prompt, image)
        st.markdown("### 💡 Solution:")
        # Create an expandable container for the response
        with st.expander("View detailed solution", expanded=True):
            st.markdown(response)
    except Exception as e:
        st.error("⚠️ " + str(e))
        st.info("💡 Tip: Make sure you have set up your OpenAI API key in the .env file.") 