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
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    st.error("GROQ_API_KEY environment variable is not set.")
    st.stop()

groq_client = Groq(api_key=groq_api_key)

# Load Whisper model
model = whisper.load_model("base")

def summarize_document(file):
    # Read file content
    if file.name.endswith('.pdf'):
        # Read PDF file
        reader = PdfReader(file)
        text = ''.join([page.extract_text() for page in reader.pages])
    elif file.name.endswith('.docx'):
        # Read DOCX file
        doc = Document(file)
        text = ''.join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file format. Please upload a PDF or DOCX file.", None

    # Generate summary
    try:
        chat_completion = groq_client.chat.completions.create(
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

# Custom CSS for styling
custom_css = """
<style>
body {
    font-family: 'Helvetica Neue', sans-serif;
    color: #FFFFFF;
    background: linear-gradient(135deg, #6d5dfc, #3dd5f3);
    background-attachment: fixed;
}

h1, h2, h3 {
    color: #FFFFFF;
    text-shadow: 2px 2px #3dd5f3;
}

.stButton>button {
    background-color: #3dd5f3;
    color: white;
    font-size: 18px;
    padding: 10px 20px;
    border-radius: 10px;
    border: none;
    transition: background-color 0.3s ease;
}

.stButton>button:hover {
    background-color: #6d5dfc;
}

.upload-btn-wrapper {
    position: relative;
    overflow: hidden;
    display: inline-block;
}

.upload-btn-wrapper input[type=file] {
    font-size: 100px;
    position: absolute;
    left: 0;
    top: 0;
    opacity: 0;
    cursor: pointer;
}

.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #3dd5f3;
    color: white;
    text-align: center;
    padding: 10px;
}

.gradient-bg {
    background: linear-gradient(135deg, #6d5dfc, #3dd5f3);
    border-radius: 10px;
    padding: 20px;
}

.dark-mode body {
    background: linear-gradient(135deg, #2c2c54, #24243e);
}

.dark-mode h1, .dark-mode h2, .dark-mode h3 {
    color: #e3e3e3;
}

.dark-mode .stButton>button {
    background-color: #24243e;
    color: #FFFFFF;
}

.dark-mode .footer {
    background-color: #2c2c54;
    color: #e3e3e3;
}

@media (max-width: 768px) {
    h1 {
        font-size: 24px;
    }
    .stButton>button {
        font-size: 16px;
        padding: 8px 16px;
    }
}
</style>
"""

# Inject custom CSS into Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

# Header with title
st.title("🌟 Document Summarizer 🌟")
st.subheader("Upload a Word or PDF document and get an AI-generated summary with audio playback.")

# File uploader
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

# Footer
html("""
<div class="footer">
    <p>Developed with 💙 by Your Name</p>
</div>
""")
