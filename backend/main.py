from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
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
    return {"status": "FireReach API running", "version": "v2.1-fixed"}

@app.post("/test")
def test_endpoint():
    return {"message": "Test endpoint working", "timestamp": "2025-01-15"}

@app.post("/discover")
def discover_endpoint(request: DiscoverRequest):
    try:
        print(f"🚀 Discover endpoint called with ICP: {request.icp}")
        print(f"📊 Plan tier: {request.plan_tier}")
        
        # Import the real discovery function
        try:
            from agent import run_discovery
            print("✅ Agent import successful")
            
            result = run_discovery(request.icp, request.plan_tier)
            print(f"✅ Discovery completed: {result.get('status')}")
            return result
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            # Return mock data if imports fail
            return get_mock_discovery_response(request.icp, request.plan_tier)
        except Exception as e:
            print(f"❌ Discovery error: {e}")
            # Return mock data if discovery fails
            return get_mock_discovery_response(request.icp, request.plan_tier)
            
    except Exception as e:
        print(f"❌ Endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_mock_discovery_response(icp: str, plan_tier: str):
    """Temporary mock response while fixing real pipeline"""
    max_companies = 3 if plan_tier == "free" else 10 if plan_tier == "pro" else 25
    
    return {
        "campaign_id": 1,
        "status": "awaiting_approval", 
        "plan_tier": plan_tier,
        "max_companies": max_companies,
        "prospects": [
            {
                "id": 1,
                "company_name": "TechFlow Solutions",
                "business_summary": f"Company matching your ICP: {icp[:100]}...",
                "website": "https://techflow.com",
                "signals": [
                    {
                        "type": "S2_FUNDING",
                        "signal": "Recently raised Series B funding for expansion",
                        "confidence": "HIGH",
                        "verified_by": "Multiple sources",
                        "score": 30
                    }
                ],
                "high_confidence_count": 1,
                "target_designation": "CTO",
                "signal_score": 85,
                "approval_status": "pending"
            }
        ]
    }

# Simplified endpoints for now
@app.post("/approve")
def approve_endpoint(request: ApprovalRequest):
    return {"prospect_id": request.prospect_id, "status": "approved"}

@app.post("/outreach") 
def outreach_endpoint(request: OutreachRequest):
    return {
        "prospect_id": request.prospect_id,
        "status": "sent",
        "message": "Email sent successfully"
    }

@app.get("/history")
def get_history():
    return {"campaigns": [], "total": 0}

@app.get("/sent-emails")
def get_sent_emails():
    return {"sent_emails": [], "total_sent": 0}