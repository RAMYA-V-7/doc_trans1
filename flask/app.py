from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from transformers import MarianMTModel, MarianTokenizer
import os
import io
from PIL import Image
import pdfplumber
from docx import Document
import torch

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

UPLOAD_FOLDER = 'uploads'
TRANSLATED_FOLDER = 'translated'

# Create folders if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSLATED_FOLDER, exist_ok=True)

# Load MarianMT model and tokenizer
model_name = 'Helsinki-NLP/opus-mt-ar-en'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Translate the document
        translated_file_path = translate_document(file_path, TRANSLATED_FOLDER)

        # Send the translated file back to the client
        return send_file(translated_file_path, as_attachment=True)

def translate_document(file_path, output_folder):
    file_extension = os.path.splitext(file_path)[1].lower()
    translated_file_path = os.path.join(output_folder, f"translated_{os.path.basename(file_path)}")

    if file_extension == '.pdf':
        translated_text = translate_text_from_pdf(file_path)
    elif file_extension == '.docx':
        translated_text = translate_text_from_docx(file_path)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    with open(translated_file_path, 'w') as output_file:
        output_file.write(translated_text)
    
    return translated_file_path

def translate_text_from_pdf(file_path):
    translated_text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                translated_text += translate_text(text) + '\n'
    return translated_text

def translate_text_from_docx(file_path):
    translated_text = ''
    doc = Document(file_path)
    for para in doc.paragraphs:
        translated_text += translate_text(para.text) + '\n'
    return translated_text

def translate_text(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model.generate(**inputs)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text

if __name__ == "__main__":
      app.run(debug=False, use_reloader=False, port=5001)
