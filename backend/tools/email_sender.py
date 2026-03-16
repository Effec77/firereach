import os
import resend
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def tool_outreach_automated_sender(account_brief: str,
                                   signals: list,
                                   contact: dict,
                                   company: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    recipient_name = contact.get("name", "") or "there"
    first_name = recipient_name.split()[0] if recipient_name != "there" else "there"
    recipient_email = contact.get("email", "")
    recipient_title = contact.get("title", "")
    
    # Only HIGH + MEDIUM verified signals in email
    verified_signals = [s["signal"] for s in signals if s["confidence"] in ["HIGH", "MEDIUM"]]
    signals_text = "\n".join([f"- {s}" for s in verified_signals[:3]])
    
    prompt = f"""Write a personalized B2B outreach email.

Recipient: {first_name}, {recipient_title} at {company}

Account Brief:
{account_brief}

Verified Signals (reference AT LEAST 2 specifically):
{signals_text}

Rules:
- Address recipient by first name only
- Reference minimum 2 specific verified signals by name in the body
- Connect those signals to a specific operational pain point
- One clear CTA: 15-minute call
- Max 150 words total in the body
- No generic phrases like "I wanted to reach out" or "Hope this finds you well"
- Professional but conversational tone
- Zero-template policy: every sentence must reference this specific company

Format EXACTLY as:
Subject: [subject line here]
---
[email body here]"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=350
        )
        
        content = response.choices[0].message.content
        parts = content.split("---")
        subject = parts[0].replace("Subject:", "").strip()
        body = parts[1].strip() if len(parts) > 1 else content
        
        # Send via Resend if email exists
        if recipient_email:
            try:
                html_body = (
                    "<div style='font-family:sans-serif;"
                    "max-width:600px;line-height:1.6;color:#333'>"
                    + body.replace("\n", "<br>")
                    + "</div>"
                )
                
                result = resend.Emails.send({
                    "from": os.getenv("FROM_EMAIL", "onboarding@resend.dev"),
                    "to": [recipient_email],
                    "subject": subject,
                    "html": html_body
                })
                
                return {
                    "status": "sent",
                    "recipient": recipient_email,
                    "recipient_name": recipient_name,
                    "subject": subject,
                    "generated_email": body,
                    "email_id": result.get("id", "")
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e),
                    "recipient": recipient_email,
                    "recipient_name": recipient_name,
                    "subject": subject,
                    "generated_email": body
                }
        else:
            return {
                "status": "no_email_found",
                "recipient": "",
                "recipient_name": recipient_name,
                "subject": subject,
                "generated_email": body
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "recipient": recipient_email,
            "recipient_name": "",
            "subject": "",
            "generated_email": ""
        }
