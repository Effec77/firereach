from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from agent import run_discovery, run_outreach_for_prospect
from database import (
    get_recent_campaigns, get_campaign_prospects, 
    get_campaign, update_prospect, get_prospect
)

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

@app.post("/test")
def test_endpoint():
    return {"message": "Test endpoint working", "timestamp": "2025-01-15"}

@app.post("/discover")
def discover_endpoint(request: DiscoverRequest):
    try:
        print(f"🚀 Discover endpoint called with ICP: {request.icp}")
        print(f"📊 Plan tier: {request.plan_tier}")
        
        # Test if imports work
        try:
            from agent import run_discovery
            print("✅ Agent import successful")
        except Exception as e:
            print(f"❌ Agent import failed: {e}")
            return {
                "campaign_id": 0,
                "status": "failed", 
                "error": f"Import error: {str(e)}",
                "prospects": []
            }
        
        result = run_discovery(request.icp, request.plan_tier)
        print(f"✅ Discovery completed: {result.get('status')}")
        return result
    except Exception as e:
        print(f"❌ Discovery endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/approve")
def approve_endpoint(request: ApprovalRequest):
    try:
        prospect = get_prospect(request.prospect_id)
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        status = "approved" if request.action == "approve" else "skipped"
        update_prospect(request.prospect_id, {"approval_status": status})
        
        return {"prospect_id": request.prospect_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/outreach")
def outreach_endpoint(request: OutreachRequest):
    try:
        result = run_outreach_for_prospect(
            request.prospect_id, 
            request.icp, 
            request.fallback_email
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaign/{campaign_id}")
def get_campaign_endpoint(campaign_id: int):
    try:
        campaign = get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        prospects = get_campaign_prospects(campaign_id)
        
        return {
            "campaign": campaign,
            "prospects": prospects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    try:
        campaigns = get_recent_campaigns(limit=20)
        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sent-emails")
def get_sent_emails():
    """Get all sent emails across all campaigns"""
    try:
        from database import get_connection
        conn = get_connection()
        
        rows = conn.execute("""
            SELECT p.*, c.icp, c.created_at as campaign_date
            FROM company_prospects p
            JOIN icp_campaigns c ON p.campaign_id = c.id
            WHERE p.send_status = 'sent' AND p.contact_email IS NOT NULL
            ORDER BY p.created_at DESC
        """).fetchall()
        
        conn.close()
        
        sent_emails = []
        for row in rows:
            sent_emails.append({
                "id": row["id"],
                "campaign_id": row["campaign_id"],
                "company_name": row["company_name"],
                "contact_name": row["contact_name"],
                "contact_email": row["contact_email"],
                "contact_title": row["contact_title"],
                "email_subject": row["email_subject"],
                "generated_email": row["generated_email"],
                "pdf_path": row["pdf_path"],
                "sent_at": row["created_at"],
                "campaign_icp": row["icp"],
                "campaign_date": row["campaign_date"]
            })
        
        return {
            "sent_emails": sent_emails,
            "total_sent": len(sent_emails)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/prospect/{prospect_id}")
def delete_prospect(prospect_id: int):
    return {"deleted": prospect_id}