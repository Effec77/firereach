from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from agent import run_discovery, run_outreach_for_prospect
from database import (
    init_db, get_campaign, get_campaign_prospects,
    get_recent_campaigns, update_prospect, get_connection
)

load_dotenv()
init_db()

app = FastAPI(title="FireReach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiscoverRequest(BaseModel):
    icp: str
    plan_tier: str = "free"

class OutreachRequest(BaseModel):
    prospect_id: int
    icp: str
    fallback_email: Optional[str] = ""

class ApprovalRequest(BaseModel):
    prospect_id: int
    action: str  # "approve" or "skip"

@app.get("/")
def health_check():
    return {"status": "FireReach API running", "version": "v2.0-rebuild"}

@app.post("/discover")
def discover_endpoint(request: DiscoverRequest):
    result = run_discovery(
        icp=request.icp,
        plan_tier=request.plan_tier
    )
    return result

@app.post("/approve")
def approve_endpoint(request: ApprovalRequest):
    status = "approved" if request.action == "approve" else "skipped"
    update_prospect(request.prospect_id, {"approval_status": status})
    return {"prospect_id": request.prospect_id, "status": status}

@app.post("/outreach")
def outreach_endpoint(request: OutreachRequest):
    result = run_outreach_for_prospect(
        prospect_id=request.prospect_id,
        icp=request.icp,
        fallback_email=request.fallback_email or ""
    )
    return result

@app.get("/campaign/{campaign_id}")
def get_campaign_endpoint(campaign_id: int):
    campaign = get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    prospects = get_campaign_prospects(campaign_id)
    return {"campaign": campaign, "prospects": prospects}

@app.get("/history")
def get_history():
    campaigns = get_recent_campaigns(limit=10)
    return {"campaigns": campaigns, "total": len(campaigns)}

@app.delete("/prospect/{prospect_id}")
def delete_prospect(prospect_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM company_prospects WHERE id = ?", (prospect_id,))
    conn.commit()
    conn.close()
    return {"deleted": prospect_id}