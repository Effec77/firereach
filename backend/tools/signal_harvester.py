"""
Harvests and verifies S1-S6 signals per company.
Discovers contact via Apollo then Hunter fallback.
NO LLM. Pure API calls.
"""
import os
import httpx
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

# Signal definitions
SIGNALS = {
    "S1_HIRING": {
        "keywords": ["hiring", "engineer", "recruiting", "talent",
                    "headcount", "job opening", "positions", "roles"],
        "score": 25,
        "designations": ["VP Engineering", "CTO", "Head of Engineering"]
    },
    "S2_FUNDING": {
        "keywords": ["raised", "funding", "series", "investment",
                    "million", "billion", "capital", "round"],
        "score": 30,
        "designations": ["CEO", "CFO", "COO"]
    },
    "S3_TRAINING": {
        "keywords": ["training", "enablement", "learning", "L&D",
                    "upskilling", "certification", "program"],
        "score": 35,
        "designations": ["CHRO", "Head of L&D", "Chief People Officer"]
    },
    "S4_AI_AGENTS": {
        "keywords": ["AI agent", "LLM", "automation", "copilot",
                    "generative AI", "agentic", "artificial intelligence"],
        "score": 20,
        "designations": ["CTO", "Head of AI", "VP Technology"]
    },
    "S5_PRODUCT_LEAD": {
        "keywords": ["product lead", "CPO", "VP product", "product manager",
                    "product director", "head of product"],
        "score": 15,
        "designations": ["CPO", "VP Product", "Chief Product Officer"]
    },
    "S6_EXPANSION": {
        "keywords": ["expansion", "new market", "international",
                    "scaling", "growth", "launch"],
        "score": 20,
        "designations": ["CEO", "VP Sales", "Chief Revenue Officer"]
    }
}

def harvest_and_verify_signals(company_name: str) -> dict:
    client = TavilyClient(api_key=TAVILY_API_KEY)
    
    queries = [
        f"{company_name} hiring engineers security AI 2025",
        f"{company_name} funding raised series 2025",
        f"{company_name} training program requirements 2025",
        f"{company_name} AI agents automation 2025",
        f"{company_name} product lead expansion launch 2025"
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
                
                for signal_type, config in SIGNALS.items():
                    if any(kw.lower() in snippet_lower for kw in config["keywords"]):
                        matched_type = signal_type
                        break
                
                if not matched_type:
                    continue
                
                first_sentence = snippet.split(".")[0].strip()
                if len(first_sentence) > 150:
                    first_sentence = first_sentence[:150] + "..."
                
                raw_signals.append({
                    "type": matched_type,
                    "signal": first_sentence,
                    "source_url": url,
                    "confidence": "UNVERIFIED",
                    "score": SIGNALS[matched_type]["score"]
                })
        except Exception:
            continue
    
    # Deduplicate by type
    seen_types = set()
    deduped = []
    for s in raw_signals:
        if s["type"] not in seen_types:
            seen_types.add(s["type"])
            deduped.append(s)
    
    # Verify each signal with second Tavily search
    verified = []
    for signal in deduped:
        try:
            verify_query = f"{company_name} {signal['type']} {signal['signal'][:50]}"
            verify_result = client.search(verify_query, max_results=2, search_depth="basic")
            verify_urls = [r.get("url", "") for r in verify_result.get("results", [])]
            
            source_domain = signal["source_url"].split("/")[2] if signal["source_url"] else ""
            corroborated = any(source_domain not in u and u != signal["source_url"]
                             for u in verify_urls if u)
            
            if corroborated:
                signal["confidence"] = "HIGH"
                signal["verified_by"] = next((u for u in verify_urls if source_domain not in u),
                                           "second_source")
            else:
                signal["confidence"] = "MEDIUM"
                signal["verified_by"] = "single_source"
            
            verified.append(signal)
        except Exception:
            signal["confidence"] = "MEDIUM"
            signal["verified_by"] = "single_source"
            verified.append(signal)
    
    # Filter HIGH + MEDIUM, sort HIGH first
    filtered = [s for s in verified if s["confidence"] in ["HIGH", "MEDIUM"]]
    filtered.sort(key=lambda x: 0 if x["confidence"] == "HIGH" else 1)
    filtered = filtered[:5]
    
    # Calculate total score
    total_score = sum(s["score"] for s in filtered)
    total_score = min(total_score, 100)
    
    # Determine primary designation from highest-scored signal
    primary_designation = ""
    if filtered:
        top_signal_type = filtered[0]["type"]
        primary_designation = SIGNALS[top_signal_type]["designations"][0]
    
    return {
        "signals": filtered,
        "high_confidence_count": len([s for s in filtered if s["confidence"] == "HIGH"]),
        "signal_summary": [s["signal"] for s in filtered],
        "signal_score": total_score,
        "target_designation": primary_designation
    }

def discover_contact(company_name: str, designation: str) -> dict:
    # STEP A: Apollo
    try:
        titles = SIGNALS.get(next((k for k in SIGNALS if SIGNALS[k]["designations"][0] == designation), "S2_FUNDING"),
                           {}).get("designations", [designation])
        
        response = httpx.post("https://api.apollo.io/v1/mixed_people/search",
                            json={
                                "q_organization_name": company_name,
                                "person_titles": titles,
                                "contact_email_status": ["verified", "guessed"],
                                "per_page": 1
                            },
                            headers={"x-api-key": APOLLO_API_KEY, "Content-Type": "application/json"},
                            timeout=10)
        
        data = response.json()
        people = data.get("people", [])
        
        if people and people[0].get("email"):
            p = people[0]
            return {
                "name": p.get("name", ""),
                "email": p.get("email", ""),
                "title": p.get("title", ""),
                "linkedin_url": p.get("linkedin_url", ""),
                "company_domain": p.get("organization", {}).get("primary_domain", ""),
                "source": "apollo"
            }
    except Exception:
        pass
    
    # STEP B: Hunter fallback
    try:
        domain = company_name.lower().replace(" ", "") + ".com"
        response = httpx.get("https://api.hunter.io/v2/domain-search",
                           params={
                               "domain": domain,
                               "api_key": HUNTER_API_KEY,
                               "limit": 1,
                               "seniority": "executive"
                           },
                           timeout=10)
        
        data = response.json()
        emails = data.get("data", {}).get("emails", [])
        
        if emails:
            c = emails[0]
            return {
                "name": f"{c.get('first_name','')} {c.get('last_name','')}".strip(),
                "email": c.get("value", ""),
                "title": c.get("position", ""),
                "linkedin_url": "",
                "company_domain": domain,
                "source": "hunter"
            }
    except Exception:
        pass
    
    return {
        "name": "", "email": "", "title": "",
        "linkedin_url": "", "company_domain": "",
        "source": "not_found"
    }

def tool_signal_harvester(company_name: str, designation: str = "") -> dict:
    cached = None
    try:
        from database import get_cached_signals, save_signal_cache
        cached = get_cached_signals(company_name)
        if cached:
            return {
                "company": company_name,
                "signals": cached["signals"],
                "contact": cached["contact"],
                "high_confidence_count": cached["high_confidence_count"],
                "signal_summary": cached["signal_summary"],
                "signal_score": 0,
                "target_designation": designation,
                "from_cache": True
            }
    except Exception:
        pass
    
    harvested = harvest_and_verify_signals(company_name)
    contact = discover_contact(company_name,
                             designation or harvested.get("target_designation", ""))
    
    result = {
        "company": company_name,
        "signals": harvested["signals"],
        "contact": contact,
        "high_confidence_count": harvested["high_confidence_count"],
        "signal_summary": harvested["signal_summary"],
        "signal_score": harvested["signal_score"],
        "target_designation": harvested["target_designation"],
        "from_cache": False
    }
    
    try:
        save_signal_cache(company_name, result)
    except Exception:
        pass
    
    return result