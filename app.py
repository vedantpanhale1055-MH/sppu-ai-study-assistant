import os
import time
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


def process_with_gemini(file_bytes, mime_type, topic, task_type, filename):
    """
    Smart upload strategy:
    - Small files (< 20MB): inline upload (faster)
    - Large files (>= 20MB): File API upload (supports up to 2GB)
    """
    prompt = build_prompt(topic, task_type)
    file_size_mb = len(file_bytes) / (1024 * 1024)

    if file_size_mb < 20:
        # ── Inline upload (fast, no storage needed) ──
        print(f"Using inline upload ({file_size_mb:.1f} MB)")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                prompt
            ]
        )
    else:
        # ── File API upload (for large files up to 2GB) ──
        print(f"Using File API upload ({file_size_mb:.1f} MB)")

        # Save temporarily to disk for upload
        temp_path = f"temp_{filename}"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        try:
            # Upload file to Gemini File API
            print("Uploading file to Gemini File API...")
            uploaded_file = client.files.upload(
                file=temp_path,
                config=types.UploadFileConfig(
                    mime_type=mime_type,
                    display_name=filename
                )
            )

            # Wait for file to be processed
            print("Waiting for file to be ready...")
            max_wait = 60  # seconds
            waited = 0
            while uploaded_file.state.name == "PROCESSING" and waited < max_wait:
                time.sleep(3)
                waited += 3
                uploaded_file = client.files.get(name=uploaded_file.name)
                print(f"File state: {uploaded_file.state.name}")

            if uploaded_file.state.name == "FAILED":
                raise Exception("File processing failed on Gemini servers.")

            # Generate content using uploaded file
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=mime_type
                    ),
                    prompt
                ]
            )

            # Clean up uploaded file from Gemini servers
            client.files.delete(name=uploaded_file.name)
            print("File deleted from Gemini servers.")

        finally:
            # Always clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

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
        filename = file.filename
        filename_lower = filename.lower()

        # Determine correct MIME type
        if filename_lower.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif filename_lower.endswith('.png'):
            mime_type = 'image/png'
        elif filename_lower.endswith('.webp'):
            mime_type = 'image/webp'
        elif filename_lower.endswith('.gif'):
            mime_type = 'image/gif'
        else:
            mime_type = 'image/jpeg'

        # Max 2GB limit
        if len(file_bytes) > 2 * 1024 * 1024 * 1024:
            return jsonify({"error": "File too large. Maximum size is 2GB."}), 400

        file_size_mb = len(file_bytes) / (1024 * 1024)
        print(f"Processing: {filename} ({file_size_mb:.1f} MB) | Task: {task_type}")

        result_text = process_with_gemini(file_bytes, mime_type, topic, task_type, filename)

        return jsonify({
            "success": True,
            "result": result_text,
            "task_type": task_type,
            "topic": topic,
            "file_size_mb": round(file_size_mb, 1),
            "extraction_method": "gemini-file-api" if file_size_mb >= 20 else "gemini-inline"
        })

    except Exception as e:
        print(f"Error: {e}")
        error_msg = str(e)
        if "API_KEY" in error_msg or "api key" in error_msg.lower():
            error_msg = "Invalid or missing Gemini API key. Please check your GEMINI_API_KEY."
        elif "quota" in error_msg.lower() or "429" in error_msg:
            error_msg = "Free quota exceeded. Please wait a minute and try again."
        elif "too large" in error_msg.lower():
            error_msg = "File too large. Please use a file under 2GB."
        return jsonify({"error": error_msg}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "SPPU AI Study Assistant (Gemini) is running!"})


if __name__ == '__main__':
    print("🎓 SPPU AI Study Assistant (Google Gemini) Starting...")
    print("📡 Running on http://localhost:5000")
    print("📁 Supports files up to 2GB via Gemini File API")
    app.run(debug=True, port=5000)