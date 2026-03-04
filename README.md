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
    │  Google Gemini API (Free)
    ▼
Gemini 2.0 Flash    ← Processes syllabus content
```

---

## ⚡ Quick Setup (5 Minutes)

### Step 1 — Get FREE Gemini API Key
1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click **Get API Key** → **Create API Key**
4. Copy the key (starts with `AIza...`)
5. No credit card needed — completely free!

### Step 2 — Install Python dependencies

```bash
pip install flask flask-cors google-genai
```

### Step 3 — Set API Key & Run Backend

```bash
# Windows (Command Prompt)
cd F:\APP
set GEMINI_API_KEY=AIza-your-key-here
python app.py
```

You should see:
```
🎓 SPPU AI Study Assistant (Google Gemini) Starting...
📡 Running on http://localhost:5000
```

### Step 4 — Open Frontend
Simply open `index.html` in your browser (double-click it). That's it! 🎉

---

## 🚀 Easy Start (Every Time)

Create a file called `start.bat` in your APP folder with this content:

```batch
cd F:\APP
set GEMINI_API_KEY=AIza-your-key-here
python app.py
```

Just **double-click `start.bat`** every time you want to run the app!

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
APP/
├── index.html       ← Frontend (open in browser)
├── app.py           ← Python Flask backend
├── requirements.txt ← Python dependencies
├── start.bat        ← Double-click to start (Windows)
└── README.md        ← This file
```

---

## 🆓 Free Tier Limits (Gemini)

| Limit | Value |
|---|---|
| Requests per minute | 15 |
| Requests per day | 1500 |
| Cost | FREE |

If you see "quota exceeded", just wait 1 minute and try again.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to backend` | Make sure `python app.py` is running |
| `Free quota exceeded` | Wait 1 minute and try again |
| `Invalid API key` | Check GEMINI_API_KEY is set correctly |
| File not processing | Use PDF or clear image under 20MB |

---

*Made for SPPU Students in Pune 🙏*
