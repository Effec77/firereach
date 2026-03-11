from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

app = FastAPI()

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

@app.post("/run-agent")
def run_agent_endpoint(request: AgentRequest):
    result = run_agent(
        icp=request.icp,
        company=request.company,
        recipient_email=request.recipient_email
    )
    return result
