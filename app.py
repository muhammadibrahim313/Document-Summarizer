import os
import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
from gtts import gTTS
import tempfile
import whisper
from streamlit.components.v1 import html

# Load Groq API key from environment variable
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# Load Whisper model
model = whisper.load_model("base")

def summarize_document(file):
    # Read file content
    if file.name.endswith('.pdf'):
        reader = PdfReader(file)
        text = ''.join([page.extract_text() for page in reader.pages])
    elif file.name.endswith('.docx'):
        doc = Document(file)
        text = ''.join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file format. Please upload a PDF or DOCX file.", None

    # Generate summary
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"Please summarize the following text: {text}"}
            ],
            model="llama3-8b-8192",
        )
        summary = chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {e}", None

    # Convert summary text to speech using gTTS
    try:
        tts = gTTS(text=summary, lang='en')
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(audio_file.name)
        audio_file.close()
    except Exception as e:
        return f"Error generating audio: {e}", None

    return summary, audio_file.name

# Enhanced CSS for 3D-like UI and modern styling
custom_css = """
<style>
body {
    font-family: 'Arial', sans-serif;
    color: #FFFFFF;
    background: linear-gradient(135deg, #222831, #393E46);
    background-attachment: fixed;
    overflow-x: hidden;
}

h1, h2, h3 {
    color: #EEEEEE;
    text-shadow: 2px 2px 4px #000000;
}

.stButton>button {
    background-color: #00ADB5;
    color: #FFFFFF;
    font-size: 18px;
    padding: 12px 24px;
    border-radius: 12px;
    border: none;
    box-shadow: 0px 5px 15px rgba(0, 173, 181, 0.4);
    transition: transform 0.3s ease, background-color 0.3s ease;
}

.stButton>button:hover {
    background-color: #00A5B5;
    transform: translateY(-3px);
}

.stButton>button:active {
    background-color: #009FA5;
    transform: translateY(1px);
    box-shadow: 0px 3px 12px rgba(0, 173, 181, 0.7);
}

.upload-btn-wrapper {
    position: relative;
    overflow: hidden;
    display: inline-block;
    border-radius: 12px;
    box-shadow: 0px 5px 15px rgba(0, 173, 181, 0.4);
    transition: transform 0.3s ease;
}

.upload-btn-wrapper:hover {
    transform: translateY(-3px);
}

.upload-btn-wrapper input[type=file] {
    font-size: 100px;
    position: absolute;
    left: 0;
    top: 0;
    opacity: 0;
    cursor: pointer;
}

.gradient-bg {
    background: linear-gradient(135deg, #00ADB5, #393E46);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0px 5px 20px rgba(0, 173, 181, 0.3);
    color: #EEEEEE;
    font-size: 16px;
}

.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #222831;
    color: #00ADB5;
    text-align: center;
    padding: 15px 0;
    box-shadow: 0px -2px 10px rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
    h1 {
        font-size: 28px;
    }
    .stButton>button {
        font-size: 16px;
        padding: 10px 20px;
    }
}
</style>
"""

# Inject custom CSS into Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

# Header with title
st.title("✨ Document Summarizer 3D UI ✨")
st.subheader("Upload a Word or PDF document and get an AI-generated summary with audio playback.")

# File uploader with enhanced styling
uploaded_file = st.file_uploader("Upload a Word or PDF Document", type=['pdf', 'docx'], help="Supports .pdf and .docx files")

if uploaded_file is not None:
    summary, audio_file_path = summarize_document(uploaded_file)
    
    if summary and audio_file_path:
        st.subheader("🔍 Summary")
        st.markdown(f"<div class='gradient-bg'>{summary}</div>", unsafe_allow_html=True)
        
        st.subheader("🎧 Audio Summary")
        st.audio(audio_file_path)
    else:
        st.error(summary)  # Display error message

# Footer with a modern touch
html("""
<div class="footer">
    <p>Developed with 💙 by Your Name</p>
</div>
""")
