# 🎓 SPPU AI Study Assistant

An AI-powered web app for SPPU students to upload their syllabus (PDF/Image) and get:
- 📋 Smart Summaries
- 🎯 Important Questions (2, 5, 10 marks — SPPU pattern)
- 📖 Detailed Notes with definitions, examples & exam tips

---

## 🏗️ Architecture

```
index.html          ← Frontend (just open in browser)
    │
    │  HTTP POST /api/process (FormData)
    ▼
app.py (Flask)      ← Python backend on port 5000
    │
    │  Anthropic Claude API (Vision + Text)
    ▼
Claude AI           ← Processes syllabus content
```

---

## ⚡ Quick Setup (5 Minutes)

### Step 1 — Get Gemeni API Key
1. Go to aistudio.google.com
2. Create an account → API Keys → Create Key
3. Copy the key (starts with `Alza.....)

### Step 2 — Install Python dependencies

```bash
# Make sure Python 3.9+ is installed
pip install -r requirements.txt

# Also install tesseract for OCR (fallback for images)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Step 3 — Set API Key & Run Backend

```bash
# Linux/macOS
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
python app.py

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-ant-your-key-here
python app.py

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
python app.py
```

You should see:
```
🎓 SPPU AI Study Assistant Backend Starting...
📡 Running on http://localhost:5000
```

### Step 4 — Open Frontend
Simply open `index.html` in your browser (double-click or drag into Chrome/Firefox).

---

## 🎮 How to Use

1. **Upload** your SPPU syllabus PDF or photo
2. **Type a topic** (optional) — e.g., "Operating Systems", "TCP/IP", "B-Trees"
3. **Select what you need**: Summary / Important Questions / Detailed Notes
4. Click **Generate with AI** and wait 15-30 seconds
5. **Copy or Download** the output as Markdown

---

## 📁 File Structure

```
sppu-ai-assistant/
├── index.html          ← Frontend (open in browser)
├── app.py              ← Python Flask backend
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🧠 How the AI Logic Works

The app uses a **chain-style prompt engineering** approach (inspired by LangChain):

1. **Extract** — Claude Vision reads the PDF/image directly
2. **Identify** — Determines what topic and content is relevant
3. **Generate** — Uses a specific prompt template per task type:
   - `summary` prompt → structured overview
   - `questions` prompt → SPPU exam-pattern questions
   - `notes` prompt → detailed study notes

No LangChain dependency needed — the same pattern implemented directly with the Anthropic SDK for simplicity and reliability.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to backend` | Make sure `python app.py` is running |
| `API Key error` | Check `ANTHROPIC_API_KEY` is set correctly |
| `File not readable` | Use clearer image, or use PDF instead |
| CORS error in browser | Backend CORS is enabled, try refreshing |
| Tesseract not found | Install tesseract (see Step 2) — optional, app works without it |

---

## 💰 Cost Estimate

- ~1000-3000 tokens per request
- Claude API: ~$0.003-0.015 per request (very cheap)
- Free tier available on Anthropic console

---

*Made for SPPU Students in Pune 🙏*
