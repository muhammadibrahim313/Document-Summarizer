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

def transcribe_audio(file):
    # Transcribe audio using Whisper model
    try:
        result = model.transcribe(file.name)
        return result["text"]
    except Exception as e:
        return f"Error transcribing audio: {e}"

def analyze_text(text):
    # Analyze text content using Groq model
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"Please analyze the following text: {text}"}
            ],
            model="llama3-8b-8192",
        )
        analysis = chat_completion.choices[0].message.content
        return analysis
    except Exception as e:
        return f"Error analyzing text: {e}"

# Enhanced CSS with background image and modern design
custom_css = """
<style>
body {
    font-family: 'Poppins', sans-serif;
    color: var(--text-color);
    background: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS0QJce7Y5aqHz8Se2WjlBnqClnluoKHZ9jCg&s') no-repeat center center fixed;
    background-size: cover;
    transition: background-color 0.3s ease, color 0.3s ease;
}

:root {
    --background: rgba(255, 255, 255, 0.8);
    --text-color: #333;
    --primary-color: #6200ea;
    --secondary-color: #03dac6;
    --highlight-color: #bb86fc;
    --button-bg: #6200ea;
    --button-hover-bg: #3700b3;
}

@media (prefers-color-scheme: dark) {
    :root {
        --background: rgba(18, 18, 18, 0.8);
        --text-color: #e0e0e0;
        --primary-color: #bb86fc;
        --secondary-color: #03dac6;
        --highlight-color: #3700b3;
        --button-bg: #bb86fc;
        --button-hover-bg: #3700b3;
    }
}

h1, h2, h3 {
    color: var(--primary-color);
    text-align: center;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
    margin-bottom: 1.5rem;
}

.stButton>button {
    background-color: var(--button-bg);
    color: #ffffff;
    font-size: 18px;
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease, background-color 0.3s ease;
}

.stButton>button:hover {
    background-color: var(--button-hover-bg);
    transform: translateY(-3px);
    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
}

.upload-btn-wrapper {
    position: relative;
    overflow: hidden;
    display: inline-block;
    border-radius: 12px;
    background: var(--primary-color);
    color: #fff;
    padding: 10px 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
}

.upload-btn-wrapper:hover {
    background: var(--highlight-color);
    transform: translateY(-3px);
    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
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
    background: var(--secondary-color);
    color: var(--text-color);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
    transition: background 0.3s ease, box-shadow 0.3s ease;
}

.gradient-bg:hover {
    background: var(--highlight-color);
    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2);
}

.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: var(--primary-color);
    color: #fff;
    text-align: center;
    padding: 15px 0;
    box-shadow: 0px -2px 10px rgba(0, 0, 0, 0.5);
    font-size: 14px;
    transition: background-color 0.3s ease;
}

.footer p {
    margin: 0;
    padding: 0;
}

.footer a {
    color: var(--secondary-color);
    text-decoration: none;
    font-weight: bold;
    transition: color 0.3s ease;
}

.footer a:hover {
    color: var(--highlight-color);
    text-decoration: underline;
}

@media (max-width: 768px) {
    h1 {
        font-size: 26px;
    }
    .stButton>button {
        font-size: 16px;
        padding: 10px 20px;
    }
    .footer {
        padding: 10px 0;
    }
}
</style>
"""

# Inject custom CSS into Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

# Header with title and links
st.title("✨ Document Summarizer & Audio Generator ✨")
st.markdown("#### Made By Me ✨ Connect with me on  | [GitHub](https://github.com/muhammadibrahim313) | [LinkedIn](https://www.linkedin.com/in/muhammad-ibrahim-qasmi-9876a1297/)")

# File uploader with enhanced styling
uploaded_file = st.file_uploader("Upload a Word, PDF Document, or Audio File", type=['pdf', 'docx', 'mp3', 'wav'], help="Supports .pdf, .docx, .mp3, and .wav files")

if uploaded_file is not None:
    if uploaded_file.name.endswith(('.mp3', '.wav')):
        # Transcribe audio if an audio file is uploaded
        transcription = transcribe_audio(uploaded_file)
        st.subheader("🔊 Transcription")
        st.markdown(f"<div class='gradient-bg'>{transcription}</div>", unsafe_allow_html=True)
    else:
        # Summarize document if a PDF or DOCX file is uploaded
        summary, audio_file_path = summarize_document(uploaded_file)
        
        if summary and audio_file_path:
            st.subheader("🔍 Summary")
            st.markdown(f"<div class='gradient-bg'>{summary}</div>", unsafe_allow_html=True)
            
            st.subheader("🎧 Audio Summary")
            st.audio(audio_file_path)
        else:
            st.error(summary)  # Display error message

    # Analyze text input
    st.subheader("📄 Analyze Text")
    input_text = st.text_area("Enter text for analysis", height=150)
    if st.button("Analyze Text"):
        if input_text:
            analysis_result = analyze_text(input_text)
            st.markdown(f"<div class='gradient-bg'>{analysis_result}</div>", unsafe_allow_html=True)

# Footer section
st.markdown("""
<div class="footer">
    <p>&copy; 2024 Document Summarizer | All Rights Reserved</p>
    <p>Connect with us: <a href="https://github.com/muhammadibrahim313" target="_blank">GitHub</a> | <a href="https://www.linkedin.com/in/muhammad-ibrahim-qasmi-9876a1297/" target="_blank">LinkedIn</a></p>
</div>
""", unsafe_allow_html=True)
