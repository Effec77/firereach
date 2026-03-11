from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.email_sender import tool_outreach_automated_sender

def run_agent(icp: str, company: str, recipient_email: str) -> dict:
    """
    Execute the full FireReach pipeline:
    Signal Capture → Contextual Research → Automated Outreach
    
    Deterministic sequential pipeline (no dynamic routing):
    tool_signal_harvester → tool_research_analyst → tool_outreach_automated_sender
    """
    
    # Step 1: Harvest signals
    signals = tool_signal_harvester(company)
    
    # Step 2: Generate account brief
    research = tool_research_analyst(
        company=company,
        signals=signals["signals"],
        icp=icp
    )
    
    # Step 3: Generate and send email
    email_result = tool_outreach_automated_sender(
        account_brief=research["account_brief"],
        signals=signals["signals"],
        recipient_email=recipient_email,
        company=company
    )
    
    return {
        "signals": signals["signals"],
        "account_brief": research["account_brief"],
        "generated_email": email_result.get("generated_email", ""),
        "subject": email_result.get("subject", ""),
        "status": email_result.get("status", "failed"),
        "recipient": email_result.get("recipient", recipient_email)
    }
