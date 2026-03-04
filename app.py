import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def build_prompt(topic, task_type):
    topic_line = f"Topic requested: {topic}" if topic else "Topic: Entire syllabus"
    prompts = {
        "summary": f"""You are an expert academic assistant for SPPU (Savitribai Phule Pune University) students.
{topic_line}
Analyze the uploaded syllabus file and generate a COMPREHENSIVE SUMMARY that includes:
1. 📋 **Overview** - Brief introduction to the topic
2. 🔑 **Key Concepts** - Main ideas and theories (bullet points)
3. 📚 **Unit Breakdown** - Sub-topics covered under each section
4. 🔗 **Connections** - How concepts relate to each other
5. 💡 **Real-world Applications** - Practical use cases
Format in clear markdown with headers and bullet points. Tailor it for SPPU exam preparation.""",

        "questions": f"""You are an expert exam preparation assistant for SPPU (Savitribai Phule Pune University) students.
{topic_line}
Analyze the uploaded syllabus and generate IMPORTANT QUESTIONS for exam preparation:
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
Analyze the uploaded syllabus and create DETAILED STUDY NOTES:
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

def process_with_gemini(file_bytes, mime_type, topic, task_type):
    prompt = build_prompt(topic, task_type)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt
        ]
    )
    return response.text

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
        if len(file_bytes) > 20 * 1024 * 1024:
            return jsonify({"error": "File too large. Please use a file under 20MB."}), 400
        result_text = process_with_gemini(file_bytes, mime_type, topic, task_type)
        return jsonify({"success": True, "result": result_text, "task_type": task_type, "topic": topic, "extraction_method": "gemini-vision"})
    except Exception as e:
        print(f"Error: {e}")
        error_msg = str(e)
        if "API_KEY" in error_msg or "api key" in error_msg.lower():
            error_msg = "Invalid or missing Gemini API key. Please check your GEMINI_API_KEY."
        elif "quota" in error_msg.lower():
            error_msg = "Free quota exceeded. Please wait a minute and try again."
        return jsonify({"error": error_msg}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "SPPU AI Study Assistant (Gemini) is running!"})

if __name__ == '__main__':
    print("🎓 SPPU AI Study Assistant (Google Gemini) Starting...")
    print("📡 Running on http://localhost:5000")
    app.run(debug=True, port=5000)
