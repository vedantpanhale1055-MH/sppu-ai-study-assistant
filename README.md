# 🎓 SPPU AI Study Assistant

An AI-powered web app for SPPU students to upload their syllabus (PDF/Image) and get:
- 📋 Smart Summaries
- 🎯 Important Questions (2, 5, 10 marks — SPPU pattern)
- 📖 Detailed Notes with definitions, examples & exam tips

---

## 🌍 Live Demo
- **Frontend:** https://vedantpanhale1055-mh.github.io/sppu-ai-study-assistant
- **Backend:** https://sppu-ai-study-assistant.onrender.com

---

## 🏗️ Architecture

```
index.html          ← Frontend (GitHub Pages)
    │
    │  HTTP POST /api/process (FormData)
    ▼
app.py (Flask)      ← Python backend (Render.com)
    │
    │  Groq API (Free - LLaMA 3.3 70B)
    ▼
Groq LLaMA AI       ← Processes syllabus content
```

---

## ⚡ Local Setup (Run on Your PC)

### Step 1 — Get FREE Groq API Key
1. Go to https://console.groq.com
2. Sign up with Google account
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)
5. No credit card needed — completely free!

### Step 2 — Install Python dependencies

```bash
pip install flask flask-cors groq PyPDF2 gunicorn
```

### Step 3 — Run Backend

```bash
# Windows CMD
cd F:\APP
set GROQ_API_KEY=gsk_your-key-here
python app.py

# Windows PowerShell / VS Code Terminal
cd F:\APP
$env:GROQ_API_KEY="gsk_your-key-here"
python app.py
```

You should see:
```
🎓 SPPU AI Study Assistant (Groq LLaMA) Starting...
📡 Running on http://localhost:5000
```

### Step 4 — Open Frontend
Simply open `index.html` in your browser. That's it! 🎉

---

## 🚀 Easy Start Every Time (Windows)

Create `start.bat` in your APP folder:

```batch
cd F:\APP
set GROQ_API_KEY=gsk_your-key-here
python app.py
```

Just **double-click `start.bat`** to start the server!

---

## ☁️ Deployment

### Backend — Render.com (Free)
1. Go to **render.com** → Sign up with GitHub
2. Click **New +** → **Web Service**
3. Connect your GitHub repo
4. Add environment variable:
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your-key-here`
5. Click **Deploy**
6. Your backend URL: `https://sppu-ai-study-assistant.onrender.com`

### Frontend — GitHub Pages (Free)
1. Go to your GitHub repo → **Settings** → **Pages**
2. Source: **Deploy from branch** → **main** → **/ (root)**
3. Click **Save**
4. Your frontend URL: `https://vedantpanhale1055-mh.github.io/sppu-ai-study-assistant`

---

## 🎮 How to Use

1. **Upload** your SPPU syllabus PDF or photo
2. **Type a topic** (optional) — e.g., "Operating Systems", "TCP/IP", "IoT"
3. **Select what you need**: Summary / Important Questions / Detailed Notes
4. Click **Generate with AI** and wait 10-20 seconds
5. **Copy or Download** the output as Markdown

---

## 📁 File Structure

```
APP/
├── index.html       ← Frontend (open in browser / GitHub Pages)
├── app.py           ← Python Flask backend (Groq AI)
├── requirements.txt ← Python dependencies
├── render.yaml      ← Render.com deployment config
├── start.bat        ← Double-click to start locally (Windows)
└── README.md        ← This file
```

---

## 🆓 Groq Free Tier Limits

| Limit | Value |
|---|---|
| Requests per minute | 30 |
| Requests per day | 14,400 |
| Cost | FREE |

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to backend` | Make sure `python app.py` is running |
| `Rate limit exceeded` | Wait 1 minute and try again |
| `Invalid API key` | Check GROQ_API_KEY is set correctly |
| PowerShell key not working | Use `$env:GROQ_API_KEY="gsk_..."` instead of `set` |
| File not processing | Use PDF or clear image under 20MB |
| Git push rejected | Run `git pull origin main --no-rebase` then `git push` |

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| AI Model | Groq LLaMA 3.3 70B |
| PDF Processing | PyPDF2 |
| Hosting (Backend) | Render.com (Free) |
| Hosting (Frontend) | GitHub Pages (Free) |

---

*Made for SPPU Students in Pune 🙏*
*GitHub: https://github.com/vedantpanhale1055-MH/sppu-ai-study-assistant*
