from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

app = FastAPI(title="FireReach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    icp: str
    company: str
    recipient_email: str

@app.get("/")
def health_check():
    return {"status": "FireReach API running"}

@app.get("/test-env")
def test_environment():
    import os
    return {
        "groq_key_exists": bool(os.getenv("GROQ_API_KEY")),
        "smtp_user_exists": bool(os.getenv("SMTP_USER")),
        "smtp_password_exists": bool(os.getenv("SMTP_PASSWORD")),
        "from_email_exists": bool(os.getenv("FROM_EMAIL")),
        "apollo_key_exists": bool(os.getenv("APOLLO_API_KEY")),
        "hunter_key_exists": bool(os.getenv("HUNTER_API_KEY"))
    }

@app.post("/run-agent")
def run_agent_endpoint(request: AgentRequest):
    result = run_agent(
        icp=request.icp,
        company=request.company,
        recipient_email=request.recipient_email
    )
    return result
