from tools.company_discoverer import discover_companies
from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.email_sender import tool_outreach_automated_sender
from pdf_generator import generate_prospect_pdf
from database import (
    init_db, create_campaign, update_campaign_status,
    save_prospect, update_prospect,
    get_campaign, get_campaign_prospects
)

init_db()

def run_discovery(icp: str, plan_tier: str) -> dict:
    """Stage 1-3: Discover companies, harvest signals, score them.
    Returns campaign_id + list of prospects for user approval."""
    from database import get_plan_limit
    
    print(f"🚀 Starting discovery for ICP: {icp}")
    print(f"📊 Plan tier: {plan_tier}")
    
    max_companies = get_plan_limit(plan_tier)
    print(f"🎯 Max companies: {max_companies}")
    
    # Create campaign
    campaign_id = create_campaign(icp, plan_tier)
    print(f"📝 Created campaign ID: {campaign_id}")
    
    try:
        # Stage 1: Find companies matching ICP
        print("🔍 Stage 1: Discovering companies...")
        companies = discover_companies(icp, max_companies=max_companies)
        print(f"✅ Found {len(companies)} companies")
        
        if not companies:
            print("❌ No companies found")
            update_campaign_status(campaign_id, "failed")
            return {
                "campaign_id": campaign_id,
                "status": "failed",
                "error": "No companies found for this ICP",
                "prospects": []
            }
        
        # Stage 2+3: Signals + scoring per company
        print("📡 Stage 2+3: Harvesting signals and scoring...")
        prospect_ids = []
        for i, company_data in enumerate(companies):
            company_name = company_data["company_name"]
            print(f"🏢 Processing company {i+1}/{len(companies)}: {company_name}")
            
            try:
                harvested = tool_signal_harvester(company_name)
                print(f"📊 Harvested {len(harvested.get('signals', []))} signals")
                
                prospect_data = {
                    "company_name": company_name,
                    "business_summary": company_data.get("business_summary", ""),
                    "website": company_data.get("website", ""),
                    "signals": harvested["signals"],
                    "high_confidence_count": harvested["high_confidence_count"],
                    "target_designation": harvested["target_designation"],
                    "signal_score": harvested["signal_score"]
                }
                
                prospect_id = save_prospect(campaign_id, prospect_data)
                prospect_ids.append(prospect_id)
                print(f"✅ Saved prospect ID: {prospect_id}")
                
            except Exception as e:
                print(f"❌ Error processing {company_name}: {e}")
                continue
        
        if not prospect_ids:
            print("❌ No prospects created")
            update_campaign_status(campaign_id, "failed")
            return {
                "campaign_id": campaign_id,
                "status": "failed",
                "error": "Failed to process any companies",
                "prospects": []
            }
        
        update_campaign_status(campaign_id,
                              "awaiting_approval",
                              companies_found=len(companies))
        
        prospects = get_campaign_prospects(campaign_id)
        print(f"🎯 Discovery complete: {len(prospects)} prospects ready for approval")
        
        return {
            "campaign_id": campaign_id,
            "status": "awaiting_approval",
            "plan_tier": plan_tier,
            "max_companies": max_companies,
            "prospects": prospects
        }
        
    except Exception as e:
        print(f"❌ Discovery failed with error: {e}")
        update_campaign_status(campaign_id, "failed")
        return {
            "campaign_id": campaign_id,
            "status": "failed",
            "error": f"Discovery failed: {str(e)}",
            "prospects": []
        }

def run_outreach_for_prospect(prospect_id: int,
                             icp: str,
                             fallback_email: str = "") -> dict:
    """Stage 4-6: For one approved prospect:
    find contact → generate brief → generate email + PDF → send"""
    from database import get_prospect
    
    prospect = get_prospect(prospect_id)
    if not prospect:
        return {"status": "failed", "error": "Prospect not found"}
    
    company = prospect["company_name"]
    signals = prospect["signals"]
    designation = prospect["target_designation"]
    
    # Stage 4: Contact discovery
    harvested = tool_signal_harvester(company, designation)
    contact = harvested["contact"]
    
    if not contact.get("email") and fallback_email:
        contact["email"] = fallback_email
        contact["source"] = "user_provided"
    
    # Stage 5a: Account brief
    research = tool_research_analyst(
        company=company,
        signals=signals,
        icp=icp,
        contact=contact
    )
    
    # Stage 5b: Generate PDF one-pager
    pdf_path = ""
    try:
        pdf_path = generate_prospect_pdf(
            company=company,
            contact=contact,
            signals=signals,
            account_brief=research["account_brief"],
            icp=icp
        )
    except Exception:
        pdf_path = ""
    
    # Stage 6: Generate email + send with PDF attached
    email_result = tool_outreach_automated_sender(
        account_brief=research["account_brief"],
        signals=signals,
        contact=contact,
        company=company,
        pdf_path=pdf_path
    )
    
    # Update prospect in DB
    update_prospect(prospect_id, {
        "approval_status": "approved",
        "contact_name": contact.get("name", ""),
        "contact_email": contact.get("email", ""),
        "contact_title": contact.get("title", ""),
        "contact_source": contact.get("source", ""),
        "account_brief": research["account_brief"],
        "email_subject": email_result.get("subject", ""),
        "generated_email": email_result.get("generated_email", ""),
        "pdf_path": pdf_path,
        "send_status": email_result.get("status", "failed")
    })
    
    return {
        "prospect_id": prospect_id,
        "company": company,
        "contact": contact,
        "account_brief": research["account_brief"],
        "subject": email_result.get("subject", ""),
        "generated_email": email_result.get("generated_email", ""),
        "pdf_generated": bool(pdf_path),
        "status": email_result.get("status", "failed"),
        "recipient": email_result.get("recipient", "")
    }