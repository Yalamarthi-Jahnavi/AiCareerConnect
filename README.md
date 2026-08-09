# AI Career Connect 🚀

An AI-powered job board, career consulting, and analytics platform built with Flask, SQLite, and Mistral AI, featuring voice control, speech synthesis, and an interactive premium dashboard.

---

## 🌟 Key Features

1. **AI Career Advisor**: Conversational AI assistant powered by the Mistral Chat Completions API.
2. **AI Resume Parser**: Uploads resumes, extracts text, and generates structured analytical JSON (skills, strengths, education).
3. **Voice Commands (Speech-to-Text)**: Audio commands support voice job searching (e.g., *"search for Python jobs"*).
4. **Text-to-Speech (TTS)**: Synthesizes text recommendations into natural-sounding voice output.
5. **Modern Interactive Dashboard**: Premium glassmorphic analytics interface for both Job Seekers and Employers.
6. **Authentication & Profile Management**: Secure stateless authorization powered by JSON Web Tokens (JWT).
7. **Job Search Engine**: Advanced listing search and filtering by roles, skills, and types.

---

## 📂 Project Architecture

```
Ai Career Connect/
├── app/
│   ├── __init__.py          # Flask app factory & template router
│   ├── config.py            # Development, Test, and Production settings
│   ├── extensions.py        # Centralized extensions (DB, JWT, Migrate)
│   ├── models/              # SQLAlchemy database schemas
│   │   ├── user.py          # User & Profile model
│   │   ├── job.py           # Job Listing model
│   │   ├── application.py   # Job Application model
│   │   └── resume.py        # Resume model
│   ├── routes/              # RESTful API Blueprints
│   │   ├── auth.py          # Auth flows (JWT)
│   │   ├── jobs.py          # Job Board CRUD
│   │   ├── applications.py  # Application tracking
│   │   ├── ai.py            # Mistral AI integrations
│   │   ├── speech.py        # STT & TTS flows
│   │   └── dashboard.py     # Analytics & feeds
│   ├── services/            # Core business logic (AI, speech processing)
│   ├── utils/               # Decorators, validators, helpers
│   └── templates/
│       └── index.html       # Premium single-page Glassmorphism UI
├── instance/                # SQLite database container
├── tests/                   # Pytest automated test suites
├── uploads/                 # Storage for resumes and audio recordings
├── .env.example             # Template for API secret keys
├── requirements.txt         # Core dependencies
└── run.py                   # Dev-server entry point
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher
- Mistral AI API Key

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```
Ensure to insert your secret key and Mistral AI API key:
```ini
SECRET_KEY=your-secret-key
MISTRAL_API_KEY=your-mistral-api-key-here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Running the Application
Always run the app using the virtual environment interpreter to ensure all imports load correctly:
```powershell
# Windows
.\env\Scripts\python run.py
```

Open `http://127.0.0.1:5000/` in your browser to view the interactive dashboard.

---

## 🧪 Testing

The project includes unit and integration tests covering the authentication layer, job creation rules, and applications lifecycle.

Run the test suite using pytest inside the virtual environment:
```powershell
# Windows
.\env\Scripts\pytest
```
