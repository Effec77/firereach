import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def tool_research_analyst(company: str, signals: list, icp: str, contact: dict) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    signals_text = ""
    for s in signals:
        signals_text += (
            f"[{s['confidence']}] {s['signal']} "
            f"(verified: {s.get('verified_by', 'single source')})\n"
        )
    
    contact_context = (
        f"{contact.get('name', 'the team')} "
        f"({contact.get('title', '')})"
        if contact.get("name")
        else "the leadership team"
    )
    
    prompt = f"""You are a B2B GTM analyst. Generate a precise account brief.

Company: {company}
Decision Maker: {contact_context}

VERIFIED SIGNALS (HIGH/MEDIUM confidence only):
{signals_text}

ICP: {icp}

Write EXACTLY two paragraphs:

Paragraph 1: Describe the company's current growth phase using the verified signals. Reference signal types specifically (hiring activity, funding, training needs etc). Be specific, not generic. Max 5 sentences.

Paragraph 2: Connect those signals directly to the ICP value proposition. Name the specific pain points these signals create and why the ICP solution addresses them right now. Max 5 sentences.

Rules:
- EXACTLY two paragraphs, no headers, no bullets
- Only reference signals from the verified list above
- Do not invent or assume signals not listed
- Professional GTM analyst tone"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )
        
        return {
            "company": company,
            "account_brief": response.choices[0].message.content,
            "contact": contact
        }
    except Exception as e:
        return {
            "company": company,
            "account_brief": f"Error generating brief: {str(e)}",
            "contact": contact
        }
