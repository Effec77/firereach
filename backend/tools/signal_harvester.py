import os
import httpx
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

SIGNAL_KEYWORDS = {
    "HIRING": ["hiring", "engineer", "recruiting", "talent", "headcount", "job opening", "positions", "roles"],
    "FUNDING": ["raised", "funding", "series", "investment", "million", "billion", "capital", "round"],
    "TRAINING": ["training", "enablement", "learning", "L&D", "upskilling", "certification", "program"],
    "AI_AGENTS": ["AI agent", "LLM", "automation", "copilot", "generative AI", "agentic", "artificial intelligence"],
    "LEADERSHIP": ["appointed", "joins as", "new CTO", "new CISO", "new VP", "named chief", "promoted to"]
}

def harvest_and_verify_signals(company_name: str) -> list:
    client = TavilyClient(api_key=TAVILY_API_KEY)
    
    queries = [
        f"{company_name} hiring engineers security AI 2025",
        f"{company_name} funding raised series 2025",
        f"{company_name} training program requirements jobs 2025",
        f"{company_name} AI agents automation requirements 2025",
        f"{company_name} leadership change CTO CISO appointed 2025"
    ]
    
    raw_signals = []
    for query in queries:
        try:
            result = client.search(query, max_results=3, search_depth="advanced")
            for item in result.get("results", []):
                snippet = item.get("content", "")[:300]
                url = item.get("url", "")
                
                if not snippet:
                    continue
                
                snippet_lower = snippet.lower()
                matched_type = None
                for signal_type, keywords in SIGNAL_KEYWORDS.items():
                    if any(kw.lower() in snippet_lower for kw in keywords):
                        matched_type = signal_type
                        break
                
                if not matched_type:
                    continue
                
                # Clean signal text: take first sentence, max 150 chars
                first_sentence = snippet.split(".")[0].strip()
                if len(first_sentence) > 150:
                    first_sentence = first_sentence[:150] + "..."
                
                raw_signals.append({
                    "type": matched_type,
                    "signal": first_sentence,
                    "source_url": url,
                    "confidence": "UNVERIFIED"
                })
        except Exception:
            continue
    
    # Deduplicate by type, keep first occurrence per type
    seen_types = set()
    deduped = []
    for s in raw_signals:
        if s["type"] not in seen_types:
            seen_types.add(s["type"])
            deduped.append(s)
    
    # Verification pass: second Tavily search per signal
    verified = []
    for signal in deduped:
        try:
            verify_query = (
                f"{company_name} {signal['type'].lower()} "
                f"{signal['signal'][:50]}"
            )
            verify_result = client.search(
                verify_query,
                max_results=2,
                search_depth="basic"
            )
            verify_urls = [r.get("url", "") for r in verify_result.get("results", [])]
            
            # Check if second source is from a different domain
            source_domain = signal["source_url"].split("/")[2] if signal["source_url"] else ""
            corroborated = any(
                source_domain not in url and url != signal["source_url"]
                for url in verify_urls
                if url
            )
            
            if corroborated:
                signal["confidence"] = "HIGH"
                signal["verified_by"] = next(
                    (u for u in verify_urls if source_domain not in u),
                    "second_source"
                )
            else:
                signal["confidence"] = "MEDIUM"
                signal["verified_by"] = "single_source"
            
            verified.append(signal)
        except Exception:
            signal["confidence"] = "MEDIUM"
            signal["verified_by"] = "single_source"
            verified.append(signal)
    
    # Filter: only HIGH and MEDIUM, sort HIGH first, max 5
    filtered = [s for s in verified if s["confidence"] in ["HIGH", "MEDIUM"]]
    filtered.sort(key=lambda x: 0 if x["confidence"] == "HIGH" else 1)
    return filtered[:5]

def discover_contact(company_name: str) -> dict:
    # STEP A: Apollo.io
    try:
        url = "https://api.apollo.io/v1/mixed_people/search"
        headers = {
            "x-api-key": APOLLO_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q_organization_name": company_name,
            "person_titles": [
                "CTO", "CISO", "VP Engineering",
                "Head of Engineering", "CEO", "VP of Security"
            ],
            "contact_email_status": ["verified", "guessed"],
            "per_page": 1
        }
        
        response = httpx.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        people = data.get("people", [])
        
        if people and people[0].get("email"):
            person = people[0]
            return {
                "name": person.get("name", ""),
                "email": person.get("email", ""),
                "title": person.get("title", ""),
                "linkedin_url": person.get("linkedin_url", ""),
                "company_domain": person.get("organization", {}).get("primary_domain", ""),
                "source": "apollo"
            }
    except Exception:
        pass
    
    # STEP B: Hunter.io fallback
    try:
        # Derive domain from company name
        domain_guess = company_name.lower().replace(" ", "") + ".com"
        
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            "domain": domain_guess,
            "api_key": HUNTER_API_KEY,
            "limit": 1,
            "seniority": "executive"
        }
        
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()
        emails = data.get("data", {}).get("emails", [])
        
        if emails:
            contact = emails[0]
            return {
                "name": f"{contact.get('first_name','')} {contact.get('last_name','')}".strip(),
                "email": contact.get("value", ""),
                "title": contact.get("position", ""),
                "linkedin_url": "",
                "company_domain": domain_guess,
                "source": "hunter"
            }
    except Exception:
        pass
    
    # STEP C: Not found
    return {
        "name": "",
        "email": "",
        "title": "",
        "linkedin_url": "",
        "company_domain": "",
        "source": "not_found"
    }

def tool_signal_harvester(company_name: str) -> dict:
    signals = harvest_and_verify_signals(company_name)
    contact = discover_contact(company_name)
    
    return {
        "company": company_name,
        "signals": signals,
        "contact": contact,
        "high_confidence_count": len([s for s in signals if s["confidence"] == "HIGH"]),
        "signal_summary": [s["signal"] for s in signals]
    }
