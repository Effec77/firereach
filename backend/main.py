from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

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
    # Temporary mock response for testing
    return {
        "campaign_id": 1,
        "status": "awaiting_approval",
        "plan_tier": request.plan_tier,
        "max_companies": 3,
        "prospects": [
            {
                "id": 1,
                "company_name": "Example Corp",
                "business_summary": "A leading technology company",
                "website": "https://example.com",
                "signals": [
                    {
                        "type": "S2_FUNDING",
                        "signal": "Example Corp recently raised $50M in Series B funding",
                        "confidence": "HIGH",
                        "verified_by": "second_source",
                        "score": 30
                    }
                ],
                "high_confidence_count": 1,
                "target_designation": "CEO",
                "signal_score": 75,
                "approval_status": "pending"
            }
        ]
    }

@app.post("/approve")
def approve_endpoint(request: ApprovalRequest):
    status = "approved" if request.action == "approve" else "skipped"
    return {"prospect_id": request.prospect_id, "status": status}

@app.post("/outreach")
def outreach_endpoint(request: OutreachRequest):
    # Temporary mock response
    return {
        "prospect_id": request.prospect_id,
        "company": "Example Corp",
        "contact": {
            "name": "John Doe",
            "email": request.fallback_email,
            "title": "CEO",
            "source": "user_provided"
        },
        "account_brief": "Example Corp is in a growth phase with recent funding.",
        "subject": "Partnership Opportunity",
        "generated_email": "Hi John,\n\nI noticed Example Corp recently raised funding. We help companies like yours with cybersecurity training.\n\nWould you be open to a 15-minute call?\n\nBest regards",
        "pdf_generated": False,
        "status": "sent",
        "recipient": request.fallback_email
    }

@app.get("/campaign/{campaign_id}")
def get_campaign_endpoint(campaign_id: int):
    return {
        "campaign": {
            "id": campaign_id,
            "icp": "Test ICP",
            "plan_tier": "free",
            "status": "completed"
        },
        "prospects": []
    }

@app.get("/history")
def get_history():
    return {"campaigns": [], "total": 0}

@app.delete("/prospect/{prospect_id}")
def delete_prospect(prospect_id: int):
    return {"deleted": prospect_id}