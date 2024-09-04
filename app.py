from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import tempfile
from gtts import gTTS
from PyPDF2 import PdfReader
from docx import Document
from groq import Groq
import whisper

app = Flask(__name__)

# Load Groq API key from environment variable
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
groq_client = Groq(api_key=groq_api_key)

# Load Whisper model
model = whisper.load_model("base")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['document']
        model_selection = request.form['model_selection']
        summary, audio_file = summarize_document(file, model_selection)
        return render_template('index.html', summary=summary, audio_file=audio_file, model_selection=model_selection)
    return render_template('index.html')

def summarize_document(file, model_selection):
    # Read file content
    if file.filename.endswith('.pdf'):
        # Read PDF file
        reader = PdfReader(file)
        text = ''.join([page.extract_text() for page in reader.pages])
    elif file.filename.endswith('.docx'):
        # Read DOCX file
        doc = Document(file)
        text = ''.join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file format. Please upload a PDF or DOCX file.", None

    # Generate summary based on the selected model
    try:
        if model_selection == 'llama3-8b-8192':
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": f"Please summarize the following text: {text}"}
                ],
                model="llama3-8b-8192",
            )
            summary = chat_completion.choices[0].message['content']
        else:
            # Placeholder for another model
            summary = "This model is not implemented yet. Please select 'llama3-8b-8192'."
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

if __name__ == '__main__':
    app.run(debug=True)
