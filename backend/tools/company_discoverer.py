"""
Discovers companies matching the user ICP using Tavily.
NO LLM. Pure search + extraction.
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def discover_companies(icp: str, max_companies: int = 3) -> list:
    """Search for companies that match the ICP description.
    Returns list of dicts: {company_name, business_summary, website}
    """
    print(f"🔍 Starting company discovery for ICP: {icp}")
    print(f"📊 Max companies: {max_companies}")
    print(f"🔑 Tavily API Key present: {bool(TAVILY_API_KEY)}")
    
    # If no Tavily API key, return mock data for testing
    if not TAVILY_API_KEY:
        print("⚠️ No Tavily API key found, returning mock data")
        return get_mock_companies(icp, max_companies)
    
    try:
        from tavily import TavilyClient
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
                print(f"🔍 Searching: {query}")
                results = client.search(query,
                                      max_results=5,
                                      search_depth="advanced")
                
                print(f"📊 Found {len(results.get('results', []))} results")
                
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
                    
                    print(f"✅ Added company: {company_name}")
                    
                    if len(discovered) >= max_companies * 2:
                        break
            except Exception as e:
                print(f"❌ Search query failed: {e}")
                continue
        
        companies = list(discovered.values())[:max_companies]
        print(f"🎯 Final result: {len(companies)} companies discovered")
        
        # If no companies found via API, return mock data
        if not companies:
            print("⚠️ No companies found via API, returning mock data")
            return get_mock_companies(icp, max_companies)
        
        return companies
        
    except Exception as e:
        print(f"❌ Tavily client error: {e}")
        print("⚠️ Falling back to mock data")
        return get_mock_companies(icp, max_companies)

def get_mock_companies(icp: str, max_companies: int = 3) -> list:
    """Return mock companies for testing when Tavily is not available"""
    
    # Determine company type based on ICP keywords
    if "cybersecurity" in icp.lower() or "security" in icp.lower():
        mock_companies = [
            {
                "company_name": "SecureFlow Technologies",
                "business_summary": "A Series B cybersecurity startup that recently raised $25M and is rapidly scaling their engineering team across multiple offices.",
                "website": "https://secureflow.com"
            },
            {
                "company_name": "DataShield Systems", 
                "business_summary": "Fast-growing data security company that recently expanded to 3 new markets and is building out their security infrastructure.",
                "website": "https://datashield.com"
            },
            {
                "company_name": "CyberGuard Solutions",
                "business_summary": "Enterprise security platform that raised Series B funding and is actively hiring security engineers and compliance specialists.",
                "website": "https://cyberguard.com"
            }
        ]
    elif "fintech" in icp.lower() or "financial" in icp.lower():
        mock_companies = [
            {
                "company_name": "PayFlow Innovations",
                "business_summary": "Series B fintech startup revolutionizing payment processing with recent $30M funding round and rapid team expansion.",
                "website": "https://payflow.com"
            },
            {
                "company_name": "CreditTech Solutions",
                "business_summary": "AI-powered lending platform that recently raised funding and is scaling their engineering and compliance teams.",
                "website": "https://credittech.com"
            },
            {
                "company_name": "BlockChain Finance",
                "business_summary": "Cryptocurrency trading platform expanding internationally with focus on regulatory compliance and security.",
                "website": "https://blockchainfinance.com"
            }
        ]
    else:
        # Generic tech companies
        mock_companies = [
            {
                "company_name": "TechCorp Solutions",
                "business_summary": "A Series B technology startup that recently raised funding and is rapidly scaling their engineering team.",
                "website": "https://techcorp.com"
            },
            {
                "company_name": "DataFlow Systems",
                "business_summary": "Fast-growing data analytics company that recently expanded to new markets and is building out their infrastructure.",
                "website": "https://dataflow.com"
            },
            {
                "company_name": "CloudScale Inc",
                "business_summary": "Cloud infrastructure provider that raised Series B funding and is actively hiring engineers and specialists.",
                "website": "https://cloudscale.com"
            }
        ]
    
    return mock_companies[:max_companies]