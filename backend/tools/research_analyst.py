import os
from groq import Groq

def tool_research_analyst(company: str, signals: list, icp: str) -> dict:
    """
    Analyze signals and generate contextual account brief using Groq LLM.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    signals_text = "\n".join([f"- {signal}" for signal in signals])
    
    prompt = f"""You are a B2B sales analyst. Analyze the following company signals and create an account brief.

Company: {company}

Signals:
{signals_text}

Ideal Customer Profile (ICP):
{icp}

Write EXACTLY two concise paragraphs. No more, no less.

Paragraph 1 (maximum 5 sentences):
Explain the company's recent growth signals and what they indicate about the company's strategic direction. Reference specific signals.

Paragraph 2 (maximum 5 sentences):
Explain how those signals align with the Ideal Customer Profile and identify potential business pain points the ICP solution could address.

Requirements:
- EXACTLY two paragraphs
- Maximum 5 sentences per paragraph
- Professional GTM analysis tone
- No bullet points
- No extra commentary
- Reference signals directly"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        account_brief = response.choices[0].message.content
        
        return {
            "company": company,
            "account_brief": account_brief
        }
    except Exception as e:
        return {
            "company": company,
            "account_brief": f"Error generating brief: {str(e)}"
        }
