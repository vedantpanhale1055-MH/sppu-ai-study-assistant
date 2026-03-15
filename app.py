import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import PyPDF2
import io

app = Flask(__name__)
CORS(app)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF using PyPDF2"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None

def extract_text_from_image(file_bytes, mime_type):
    """Send image to Groq vision model"""
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

def build_prompt(topic, task_type):
    topic_line = f"Topic requested: {topic}" if topic else "Topic: Entire syllabus"

    prompts = {
        "summary": f"""You are an expert academic assistant for SPPU (Savitribai Phule Pune University) students.
{topic_line}

Generate a COMPREHENSIVE SUMMARY that includes:
1. 📋 **Overview** - Brief introduction to the topic
2. 🔑 **Key Concepts** - Main ideas and theories (bullet points)
3. 📚 **Unit Breakdown** - Sub-topics covered under each section
4. 🔗 **Connections** - How concepts relate to each other
5. 💡 **Real-world Applications** - Practical use cases

Format in clear markdown with headers and bullet points. Tailor it for SPPU exam preparation.""",

        "questions": f"""You are an expert exam preparation assistant for SPPU (Savitribai Phule Pune University) students.
{topic_line}

Generate IMPORTANT QUESTIONS for exam preparation:

## 🎯 2-Mark Questions (Short Answer)
- List 8-10 short definition/concept questions

## 📝 5-Mark Questions (Medium Answer)
- List 6-8 questions requiring detailed explanations

## 📖 10-Mark Questions (Long Answer / Essay Type)
- List 4-5 comprehensive questions

## 🔥 Most Likely to Come in Exam (Star Questions ⭐)
- List 5 questions that are highly probable

For each question, indicate difficulty: [Easy] [Medium] [Hard]
Focus on SPPU exam pattern.""",

        "notes": f"""You are an expert note-maker for SPPU (Savitribai Phule Pune University) students.
{topic_line}

Create DETAILED STUDY NOTES:

## 📖 Study Notes

### 🧠 Core Theory
- Explain each concept in simple language with examples

### 📌 Important Definitions
- Key terms with clear definitions

### 📊 Diagrams/Flowcharts (Text-based)
- ASCII or text-based representations of processes

### ⚡ Quick Revision Points
- Must-remember facts in bullet points

### 🧪 Examples & Case Studies
- Practical examples to understand better

### 🎓 Exam Tips
- What to focus on, common mistakes to avoid

Make notes comprehensive enough to score well in SPPU exams."""
    }
    return prompts.get(task_type, prompts["summary"])


def process_with_groq_text(text, topic, task_type):
    """Process extracted text with Groq LLaMA"""
    prompt = build_prompt(topic, task_type)

    full_prompt = f"""{prompt}

Here is the syllabus content to analyze:
---
{text[:12000]}
---
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert SPPU exam preparation assistant. Generate detailed, well-formatted markdown responses."},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=4096,
        temperature=0.7
    )
    return response.choices[0].message.content


def process_with_groq_vision(file_bytes, mime_type, topic, task_type):
    """Process image with Groq Vision model"""
    prompt = build_prompt(topic, task_type)
    b64 = base64.b64encode(file_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        max_tokens=4096,
        temperature=0.7
    )
    return response.choices[0].message.content


@app.route('/api/process', methods=['POST'])
def process_syllabus():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        topic = request.form.get('topic', '').strip()
        task_type = request.form.get('task_type', 'summary')

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        file_bytes = file.read()
        filename = file.filename.lower()

        # Determine MIME type
        if filename.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif filename.endswith('.png'):
            mime_type = 'image/png'
        elif filename.endswith('.webp'):
            mime_type = 'image/webp'
        elif filename.endswith('.gif'):
            mime_type = 'image/gif'
        else:
            mime_type = 'image/jpeg'

        file_size_mb = len(file_bytes) / (1024 * 1024)
        print(f"Processing: {file.filename} ({file_size_mb:.1f} MB) | Task: {task_type}")

        result_text = None

        if mime_type == 'application/pdf':
            # Extract text from PDF then use LLaMA text model
            extracted_text = extract_text_from_pdf(file_bytes)
            if extracted_text and len(extracted_text) > 50:
                print(f"Extracted {len(extracted_text)} characters from PDF")
                result_text = process_with_groq_text(extracted_text, topic, task_type)
            else:
                return jsonify({"error": "Could not extract text from PDF. Please ensure the PDF is not scanned/image-based."}), 400
        else:
            # Use vision model for images
            print("Using Groq vision model for image...")
            result_text = process_with_groq_vision(file_bytes, mime_type, topic, task_type)

        return jsonify({
            "success": True,
            "result": result_text,
            "task_type": task_type,
            "topic": topic,
            "extraction_method": "groq-llama"
        })

    except Exception as e:
        print(f"Error: {e}")
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            error_msg = "Invalid or missing Groq API key. Please check your GROQ_API_KEY."
        elif "rate_limit" in error_msg.lower() or "429" in error_msg:
            error_msg = "Rate limit exceeded. Please wait a minute and try again."
        return jsonify({"error": error_msg}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "SPPU AI Study Assistant (Groq LLaMA) is running!"})


if __name__ == '__main__':
    print("🎓 SPPU AI Study Assistant (Groq LLaMA) Starting...")
    print("📡 Running on http://localhost:5000")
    app.run(debug=True, port=5000)