import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def tool_research_analyst(company: str,
                         signals: list,
                         icp: str,
                         contact: dict) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    signals_text = "\n".join([f"[{s['confidence']}] {s['type']}: {s['signal']}"
                             for s in signals])
    
    contact_context = (f"{contact.get('name','the team')} ({contact.get('title','')})"
                      if contact.get("name") else "the leadership team")
    
    prompt = f"""You are a B2B GTM analyst. Generate a precise account brief.

Company: {company}
Decision Maker: {contact_context}

VERIFIED SIGNALS:
{signals_text}

ICP: {icp}

Write EXACTLY two paragraphs:

Paragraph 1 (max 5 sentences):
Describe the company's current growth phase using the verified signals.
Reference specific signal types. Be precise, not generic.

Paragraph 2 (max 5 sentences):
Connect those signals to the ICP value proposition.
Name specific pain points these signals create and why the ICP
solution addresses them right now.

Rules:
- EXACTLY two paragraphs, no headers, no bullets
- Only reference signals listed above
- Professional GTM analyst tone
- Never invent signals not in the list"""
    
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