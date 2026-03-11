# 🔥 FireReach - Autonomous Outreach Engine

Autonomous AI agent that automates the complete SDR workflow: Signal Discovery → Research → Personalized Outreach

## ✅ System Status

**All components operational:**
- ✅ Signal Harvester (DDGS)
- ✅ Research Analyst (Groq LLM)
- ✅ Email Generator (Groq LLM)
- ✅ Email Sender (Resend API)
- ✅ FastAPI Backend
- ✅ Frontend UI

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
RESEND_API_KEY=your_resend_api_key_here
FROM_EMAIL=your_verified_email@domain.com
```

### 3. Start Backend

```bash
cd backend
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### 4. Open Frontend

Open `frontend/index.html` in your browser or serve it:

```bash
cd frontend
python -m http.server 3000
```

Frontend runs on `http://localhost:3000`

## 🧪 Test the Pipeline

Run the test script:

```bash
cd backend
python test_agent.py
```

Expected output:
- 5 company signals captured
- 2-paragraph account brief generated
- Personalized email created

## 📋 API Endpoints

### Health Check
```bash
GET http://localhost:8000/
```

Response:
```json
{
  "status": "FireReach API running"
}
```

### Run Agent
```bash
POST http://localhost:8000/run-agent
```

Request body:
```json
{
  "icp": "We sell cybersecurity training to Series B startups",
  "company": "Stripe",
  "recipient_email": "john@stripe.com"
}
```

Response:
```json
{
  "signals": ["signal1", "signal2", ...],
  "account_brief": "Two paragraph analysis...",
  "email_status": "sent",
  "email_subject": "Subject line",
  "email_body": "Email content"
}
```

## 🏗️ Architecture

```
Frontend (HTML/JS)
    ↓
FastAPI Backend
    ↓
Agent Controller
    ↓
┌─────────────────┬──────────────────┬─────────────────┐
│ Signal Harvester│ Research Analyst │  Email Sender   │
│    (DDGS)       │   (Groq LLM)     │ (Groq + Resend) │
└─────────────────┴──────────────────┴─────────────────┘
```

## 📦 Tech Stack

- **Backend**: FastAPI + Python
- **LLM**: Groq (llama-3.3-70b-versatile)
- **Search**: DDGS (DuckDuckGo)
- **Email**: Resend API
- **Frontend**: Vanilla HTML/CSS/JS

## 🔧 Troubleshooting

### Environment Variables Not Loading
Make sure `.env` is in the `backend/` directory and contains all required keys.

### Email Status "simulated_sent"
This means Resend API call failed (usually domain not verified). Email generation still works - check the output.

### Model Errors
Current model: `llama-3.3-70b-versatile`. If decommissioned, check [Groq docs](https://console.groq.com/docs/models) for alternatives.

## 🚢 Deployment

### Backend (Render)
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard
5. Deploy from `backend/` directory

### Frontend (Vercel)
1. Deploy `frontend/` directory
2. Update API URL in `index.html` to your Render backend URL
3. Deploy

## 📝 Example Output

**Input:**
- ICP: "We sell cybersecurity training to Series B startups"
- Company: "Stripe"
- Email: "test@example.com"

**Output:**
- 5 signals about Stripe's funding and expansion
- Account brief connecting signals to ICP
- Personalized email referencing specific signals

## 📄 License

MIT
