from tools.signal_harvester import tool_signal_harvester
from tools.research_analyst import tool_research_analyst
from tools.email_sender import tool_outreach_automated_sender
from database import (
    init_db,
    get_cached_signals,
    save_signal_cache,
    save_outreach_run
)

init_db()

def run_agent(icp: str, company: str, recipient_email: str) -> dict:
    # Step 1: Check 24hr cache first
    cached = get_cached_signals(company, max_age_hours=24)
    if cached:
        harvested = cached
        cache_hit = True
    else:
        harvested = tool_signal_harvester(company)
        save_signal_cache(company, harvested)
        cache_hit = False
    
    # Step 2: Resolve contact
    # Apollo/Hunter result takes priority; fall back to user-provided email
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
    
    # Step 5: Persist run to SQLite
    save_outreach_run(
        company=company,
        icp=icp,
        recipient_email=email_result.get("recipient", recipient_email),
        contact=contact,
        signals=harvested["signals"],
        high_confidence_count=harvested.get("high_confidence_count", 0),
        account_brief=research["account_brief"],
        email_subject=email_result.get("subject", ""),
        generated_email=email_result.get("generated_email", ""),
        send_status=email_result.get("status", "failed")
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
        "cache_hit": cache_hit
    }
