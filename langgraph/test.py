import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import os

# Initialize client (NEW OpenAI SDK)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit Page Settings
st.set_page_config(page_title="Car Damage Detector", layout="wide")
st.title("🚗 AI Car Damage Detector")
st.write("Upload a car image and let an OpenAI vision model detect damages.")

uploaded_file = st.file_uploader("Upload a car photo", type=["jpg", "jpeg", "png"])

def to_base64(image: Image.Image):
    """Convert PIL image to base64."""
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Car Image", use_column_width=True)

    base64_img = to_base64(image)
    
    if st.button("Analyze Damage"):
        with st.spinner("Analyzing image using OpenAI Vision Model..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",   # you can upgrade to "gpt-4o" or "gpt-5" if needed
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": 
                                    "Analyze this car image and list all visible damages. "
                                    "Provide:\n"
                                    "- Damaged parts\n"
                                    "- Type of damage (scratch, dent, crack, etc.)\n"
                                    "- Severity (minor/moderate/severe)\n"
                                    "- Suggested repair actions\n"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_img}"
                                    }
                                }
                            ]
                        }
                    ]
                )

                result = response.choices[0].message.content

                st.subheader("🔍 Damage Analysis")
                st.write(result)

            except Exception as e:
                st.error(f"Error: {e}")
