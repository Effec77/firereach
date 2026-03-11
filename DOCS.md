# FireReach - Autonomous Outreach Engine

## Quick Start

### Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### Frontend Setup

1. Open `frontend/index.html` in a browser
2. Or use a local server:
```bash
cd frontend
python -m http.server 3000
```

Frontend runs on `http://localhost:3000`

## Environment Variables

Create `.env` in the backend directory:

```
GROQ_API_KEY=your_groq_api_key
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=your_verified_email@domain.com
```

## API Endpoints

### GET /
Health check

### POST /run-agent
Execute the full pipeline

Request:
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
  "signals": ["..."],
  "account_brief": "...",
  "email_status": "sent",
  "email_subject": "...",
  "email_body": "..."
}
```

## Architecture

```
Signal Harvester (DuckDuckGo) 
    ↓
Research Analyst (Groq LLM)
    ↓
Email Sender (Groq + Resend)
```

## Deployment

### Backend (Render)
- Connect GitHub repo
- Set environment variables
- Deploy from `backend/` directory

### Frontend (Vercel)
- Deploy `frontend/` directory
- Update API URL in `index.html`
