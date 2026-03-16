from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.email_sender import tool_outreach_automated_sender

def run_agent(icp: str, company: str, recipient_email: str) -> dict:
    try:
        # Step 1: Get signals (no caching for now)
        harvested = tool_signal_harvester(company)
        
        # Step 2: Resolve contact
        contact = harvested["contact"]
        if not contact.get("email") and recipient_email:
            contact["email"] = recipient_email
            contact["source"] = "user_provided"
        
        # Step 3: Generate account brief
        research = tool_research_analyst(
            company=company,
            signals=harvested["signals"],
            icp=icp,
            contact=contact
        )
        
        # Step 4: Generate + send email
        email_result = tool_outreach_automated_sender(
            account_brief=research["account_brief"],
            signals=harvested["signals"],
            contact=contact,
            company=company
        )
        
        return {
            "signals": harvested["signals"],
            "signal_summary": harvested["signal_summary"],
            "high_confidence_count": harvested["high_confidence_count"],
            "contact_discovered": contact,
            "account_brief": research["account_brief"],
            "generated_email": email_result.get("generated_email", ""),
            "subject": email_result.get("subject", ""),
            "status": email_result.get("status", "failed"),
            "recipient": email_result.get("recipient", ""),
            "recipient_name": email_result.get("recipient_name", ""),
            "cache_hit": False
        }
    except Exception as e:
        return {
            "error": str(e),
            "signals": [],
            "signal_summary": [],
            "high_confidence_count": 0,
            "contact_discovered": {},
            "account_brief": f"Error: {str(e)}",
            "generated_email": "",
            "subject": "",
            "status": "failed",
            "recipient": "",
            "recipient_name": "",
            "cache_hit": False
        }
