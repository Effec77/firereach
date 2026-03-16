"""
Discovers companies matching the user ICP using Tavily.
NO LLM. Pure search + extraction.
"""
import os
import httpx
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def discover_companies(icp: str, max_companies: int = 3) -> list:
    """Search for companies that match the ICP description.
    Returns list of dicts: {company_name, business_summary, website}
    """
    client = TavilyClient(api_key=TAVILY_API_KEY)
    
    # Extract key terms from ICP for search
    search_queries = [
        f"companies {icp} recently funded startup 2025",
        f"{icp} Series B startup hiring 2025",
        f"top startups {icp} expanding 2025"
    ]
    
    discovered = {}
    
    for query in search_queries:
        try:
            results = client.search(query,
                                  max_results=5,
                                  search_depth="advanced")
            
            for item in results.get("results", []):
                title = item.get("title", "")
                content = item.get("content", "")[:200]
                url = item.get("url", "")
                
                # Extract company name from title
                # Usually "CompanyName - description" or "CompanyName | ..."
                company_name = title.split(" - ")[0].split(" | ")[0].split(":")[0].strip()
                
                # Skip if too short, too long, or already found
                if len(company_name) < 2 or len(company_name) > 40:
                    continue
                if company_name.lower() in discovered:
                    continue
                
                # Skip generic results
                skip_words = ["google", "linkedin", "crunchbase", "techcrunch",
                             "forbes", "bloomberg", "news", "article", "blog"]
                if any(w in company_name.lower() for w in skip_words):
                    continue
                
                discovered[company_name.lower()] = {
                    "company_name": company_name,
                    "business_summary": content.strip(),
                    "website": url
                }
                
                if len(discovered) >= max_companies * 2:
                    break
        except Exception:
            continue
    
    companies = list(discovered.values())[:max_companies]
    return companies