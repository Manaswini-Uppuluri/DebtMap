#  DebtMap — AI-Powered Migration Advisor

> Detect deprecated APIs. Understand why. Get fixes. Instantly.

**Team:** GitHappens
**Hackathon:** Clash of the Claws — The OpenClaw Hackathon 2026 | PRISM, SRI-B
**Live Demo:** 🔗 [https://debtmap.onrender.com/](https://debtmap.onrender.com/)

---

##  Problem Statement

Modern software projects accumulate **technical debt** silently. Developers use APIs that get deprecated over time — leading to security vulnerabilities, broken builds, and hours of painful debugging.

There is no easy way to:
- Know *which* APIs in your code are deprecated
- Understand *why* they are dangerous or outdated
- Get *actionable* migration steps without digging through documentation

---

##  Our Solution

**DebtMap** is an AI-powered code analysis tool that:

1. **Scans** your code for deprecated or risky API patterns
2. **Explains** why each pattern is problematic
3. **Generates** step-by-step migration guidance using an LLM
4. **Provides** updated, corrected code snippets — ready to use

Paste a code snippet or drop in a GitHub repo URL. DebtMap does the rest.

---

##  Key Features

| Feature | Description |
|---|---|
|  Deprecated API Detection | Rule-based regex scanner catches known bad patterns |
|  AI-Powered Explanations | Groq LLM explains issues in plain English |
|  Migration Steps | 3 clear steps to fix each issue |
|  Updated Code | Corrected code snippet generated automatically |
|  Repo URL Support | Analyze entire GitHub repositories |
|  Agent Memory | HEARTBEAT.md logs every migration run |

---

##  Deprecated Patterns Detected

| Pattern | Why It's a Problem |
|---|---|
| `openai.api_key` | Deprecated OpenAI authentication method |
| `eval()` | Major security vulnerability |
| `os.system()` | Should use `subprocess` for safety |
| `import cgi` | Deprecated since Python 3.11 |
| `import imp` | Deprecated since Python 3.4 |

---

##  Architecture
User Input (code / repo URL)
↓
Frontend (HTML/CSS/JS)
↓
Flask Backend (main.py)
↓
scanner.py — regex pattern detection
↓
agent.py — Groq LLM (llama3-8b-8192)
↓
Structured JSON Report → Frontend
↓
HEARTBEAT.md — memory log updated

### Agent Design — Inspired by OpenClaw Pattern

DebtMap's agent is **designed following the OpenClaw SOUL/SKILL/HEARTBEAT pattern** as an architectural inspiration:

| File | Purpose |
|---|---|
| `SOUL.md` | Defines the agent's identity and mission |
| `SKILL.md` | Defines what the agent knows how to do |
| `HEARTBEAT.md` | Memory log — updated after each migration run |

> Note: This is not a direct OpenClaw integration. We have mimicked the pattern to structure our agent's identity, skills, and memory in a meaningful way.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3, Flask, Flask-CORS |
| AI Model | `llama3-8b-8192` via Groq API |
| Detection | Regex-based rule engine |
| Deployment | Render (free tier) |

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Manaswini-Uppuluri/DebtMap.git
cd DebtMap
```
### 2. Install dependencies

```bash
pip install flask flask-cors openai python-dotenv
```

### 3. Add your Groq API key

Create a file called `.env` inside the `backend/` folder:
GROQ_API_KEY=your_groq_api_key_here

> Get a free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run the backend server

```bash
python backend/main.py
```

### 5. Open the frontend

Visit `http://localhost:5000` in your browser,  
or open `index.html` using **Live Server** in VS Code.

---

## 🧪 Try It Out — Test Snippets

Paste any of these into the live demo to trigger detection:

**Snippet 1:**
```python
import os
os.system("ls")
```

**Snippet 2:**
```python
import cgi
```

**Snippet 3:**
```python
import imp
```

---

## 📡 API Reference

**Endpoint:** `POST /analyze`

**Option 1 — Code snippet:**
```json
{
  "code": "import cgi\nprint('hello')"
}
```

**Option 2 — GitHub repo URL:**
```json
{
  "repo_url": "https://github.com/your/repo"
}
```

**Sample Response:**
```json
{
  "status": "success",
  "scan_result": { "..." },
  "all_results": ["..."],
  "ai_result": {
    "explanation": "...",
    "migration_steps": ["...", "...", "..."],
    "updated_code": "..."
  }
}
```

---

## ⚠️ Known Limitations

- AI explanation is generated in backend but not yet rendered on frontend UI
- File persistence not implemented in this version
- `dependency_scanner.py` exists but not yet connected to main API endpoint
- Currently detects 5 deprecated patterns (expandable)

---

## 🔮 Future Scope

- Expand detection to 20+ deprecated patterns across multiple languages
- Display full AI explanation on frontend
- Auto-generate pull requests with fixes
- Support for JavaScript, Java, and Go codebases
- VS Code extension integration

---

## 👥 Team GitHappens

- Manaswini Uppuluri
- Sanjana K R 
- Shreshth Agarwal
- Varnit Pal

---

## 📄 License

MIT License — built for Clash of the Claws, The OpenClaw Hackathon 2026, organized by PRISM | Tech Management, SRI-B.
