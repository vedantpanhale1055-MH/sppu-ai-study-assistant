import os
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import PyPDF2
import io
from PIL import Image
import pytesseract

app = Flask(__name__)
CORS(app)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF using PyPDF2"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return None

def extract_text_from_image(file_bytes):
    """Extract text from image using OCR (pytesseract)"""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return None

def get_file_as_base64(file_bytes):
    """Convert file bytes to base64"""
    return base64.standard_b64encode(file_bytes).decode("utf-8")

def build_prompt(syllabus_text, topic, task_type):
    """Build the prompt for AI based on task type - LangChain-style prompt templates"""
    
    prompts = {
        "summary": f"""You are an expert academic assistant for SPPU (Savitribai Phule Pune University) students.

Given the following syllabus content:
---
{syllabus_text}
---

Topic requested: {topic if topic else "entire syllabus"}

Generate a COMPREHENSIVE SUMMARY that includes:
1. 📋 **Overview** - Brief introduction to the topic
2. 🔑 **Key Concepts** - Main ideas and theories (bullet points)
3. 📚 **Unit Breakdown** - Sub-topics covered under each section
4. 🔗 **Connections** - How concepts relate to each other
5. 💡 **Real-world Applications** - Practical use cases

Format the output in clear markdown with headers and bullet points. Be concise but thorough. Tailor it for SPPU exam preparation.""",

        "questions": f"""You are an expert exam preparation assistant for SPPU (Savitribai Phule Pune University) students.

Given the following syllabus content:
---
{syllabus_text}
---

Topic requested: {topic if topic else "entire syllabus"}

Generate IMPORTANT QUESTIONS for exam preparation. Include:

## 🎯 2-Mark Questions (Short Answer)
- List 8-10 short definition/concept questions

## 📝 5-Mark Questions (Medium Answer)
- List 6-8 questions requiring detailed explanations

## 📖 10-Mark Questions (Long Answer / Essay Type)
- List 4-5 comprehensive questions

## 🔥 Most Likely to Come in Exam (Star Questions)
- List 5 questions that are highly probable based on the syllabus

For each question, indicate the difficulty level: [Easy] [Medium] [Hard]
Format nicely in markdown. Focus on SPPU exam pattern.""",

        "notes": f"""You are an expert note-maker for SPPU (Savitribai Phule Pune University) students.

Given the following syllabus content:
---
{syllabus_text}
---

Topic requested: {topic if topic else "entire syllabus"}

Create DETAILED STUDY NOTES that include:

## 📖 Topic: {topic if topic else "Complete Syllabus Notes"}

### 🧠 Core Theory
- Explain each concept in simple, easy-to-understand language
- Use examples wherever possible

### 📌 Important Definitions
- Key terms with clear definitions

### 📊 Diagrams/Flowcharts (Text-based)
- Create ASCII or text-based representations of processes/architectures

### ⚡ Quick Revision Points
- Bullet-point summary of must-remember facts

### 🧪 Examples & Case Studies
- Practical examples to solidify understanding

### 🎓 Exam Tips
- What to focus on, common mistakes to avoid

Make the notes comprehensive enough that a student can study ONLY from these notes and still score well in SPPU exams. Use clear markdown formatting."""
    }
    
    return prompts.get(task_type, prompts["summary"])

def process_with_claude_vision(file_bytes, mime_type, topic, task_type):
    """Process image/PDF directly with Claude Vision API"""
    b64_data = get_file_as_base64(file_bytes)
    
    prompt = build_prompt("[Analyze the uploaded file which contains syllabus/academic content]", topic, task_type)
    
    # For vision, we send the file directly
    if mime_type == "application/pdf":
        content = [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": b64_data
                }
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
    else:
        # Normalize mime type
        if mime_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
            mime_type = "image/jpeg"
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": b64_data
                }
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": content}]
    )
    
    return response.content[0].text

def process_with_claude_text(syllabus_text, topic, task_type):
    """Process extracted text with Claude"""
    prompt = build_prompt(syllabus_text, topic, task_type)
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

@app.route('/api/process', methods=['POST'])
def process_syllabus():
    """Main endpoint to process syllabus"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        topic = request.form.get('topic', '').strip()
        task_type = request.form.get('task_type', 'summary')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file
        file_bytes = file.read()
        mime_type = file.content_type
        filename = file.filename.lower()
        
        result_text = None
        extraction_method = "vision"

        # Determine correct mime type from filename
        if filename.endswith('.pdf') or mime_type == 'application/pdf':
            img_mime = 'application/pdf'
        elif filename.endswith('.png'):
            img_mime = 'image/png'
        elif filename.endswith('.webp'):
            img_mime = 'image/webp'
        elif filename.endswith('.gif'):
            img_mime = 'image/gif'
        else:
            img_mime = 'image/jpeg'  # default for jpg/jpeg and unknown

        # Always use Claude Vision — it handles both PDFs and images directly
        try:
            result_text = process_with_claude_vision(file_bytes, img_mime, topic, task_type)
            extraction_method = "vision"
        except Exception as vision_error:
            print(f"Vision API failed: {vision_error}")
            # Fallback: extract text and process
            if img_mime == 'application/pdf':
                extracted_text = extract_text_from_pdf(file_bytes)
            else:
                extracted_text = extract_text_from_image(file_bytes)

            if extracted_text and len(extracted_text) > 50:
                result_text = process_with_claude_text(extracted_text, topic, task_type)
                extraction_method = "ocr+text"
            else:
                return jsonify({"error": f"AI processing failed: {str(vision_error)}"}), 400
        
        if not result_text:
            return jsonify({"error": "Failed to process the syllabus. Please try again."}), 500
        
        return jsonify({
            "success": True,
            "result": result_text,
            "task_type": task_type,
            "topic": topic,
            "extraction_method": extraction_method
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "SPPU AI Study Assistant is running!"})

if __name__ == '__main__':
    print("🎓 SPPU AI Study Assistant Backend Starting...")
    print("📡 Running on http://localhost:5000")
    app.run(debug=True, port=5000)
