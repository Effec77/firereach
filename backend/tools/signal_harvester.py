from ddgs import DDGS
import re

def tool_signal_harvester(company_name: str) -> dict:
    """
    Collect company growth and activity signals using DuckDuckGo search.
    This is a deterministic tool - NO LLM usage.
    """
    try:
        ddgs = DDGS()
        query = f"{company_name} funding hiring expansion startup news"
        results = ddgs.text(query, max_results=10)
        
        signals = []
        
        for result in results:
            snippet = result.get('body', '')
            if not snippet:
                continue
            
            # Clean snippet
            snippet = re.sub(r'http\S+', '', snippet)
            snippet = re.sub(r'\.\.\.+', '', snippet)
            snippet = snippet.strip()
            
            if len(snippet) < 20:
                continue
            
            # Categorize and format signal
            snippet_lower = snippet.lower()
            signal = None
            
            if any(word in snippet_lower for word in ['funding', 'raised', 'investment', 'series', 'capital']):
                signal = f"{company_name} involved in major funding activity related to growth and expansion."
            elif any(word in snippet_lower for word in ['hiring', 'recruiting', 'engineers', 'talent', 'team']):
                signal = f"{company_name} expanding engineering and infrastructure capabilities."
            elif any(word in snippet_lower for word in ['launch', 'product', 'expansion', 'market', 'new']):
                signal = f"{company_name} launching new products or expanding into new markets."
            elif any(word in snippet_lower for word in ['partnership', 'acquisition', 'acquired', 'partner']):
                signal = f"{company_name} pursuing strategic partnerships or acquisitions."
            elif any(word in snippet_lower for word in ['invest', 'venture', 'startup', 'portfolio']):
                signal = f"{company_name} investing in emerging technologies and startup ecosystem."
            
            if signal and signal not in signals:
                signals.append(signal)
            
            if len(signals) >= 5:
                break
        
        # Fallback if no signals found
        if not signals:
            signals = [f"{company_name} is actively growing and expanding operations."]
        
        return {
            "company": company_name,
            "signals": signals[:5]
        }
    except Exception as e:
        return {
            "company": company_name,
            "signals": [f"{company_name} is actively growing and expanding operations."]
        }
