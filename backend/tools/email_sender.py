import os
import resend
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def tool_outreach_automated_sender(account_brief: str,
                                   signals: list,
                                   contact: dict,
                                   company: str,
                                   pdf_path: str = "") -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    first_name = (contact.get("name") or "there").split()[0]
    recipient_email = contact.get("email", "")
    recipient_title = contact.get("title", "")
    
    verified_signals = [s["signal"] for s in signals
                       if s["confidence"] in ["HIGH", "MEDIUM"]]
    signals_text = "\n".join([f"- {s}" for s in verified_signals[:3]])
    
    prompt = f"""Write a personalized B2B outreach email.

Recipient: {first_name}, {recipient_title} at {company}

Account Brief:
{account_brief}

Verified Signals (reference AT LEAST 2):
{signals_text}

Rules:
- Address by first name
- Reference minimum 2 specific verified signals
- Connect signals to a specific pain point
- One CTA: 15-minute call
- Max 150 words in body
- No generic openers
- Zero-template: every sentence is specific to this company

Format EXACTLY as:
Subject: [subject line]
---
[email body]"""
    
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
        
        if recipient_email:
            try:
                html_body = ("<div style='font-family:sans-serif;max-width:600px;"
                           "line-height:1.6;color:#333'>"
                           + body.replace("\n", "<br>")
                           + "</div>")
                
                email_params = {
                    "from": os.getenv("FROM_EMAIL", "onboarding@resend.dev"),
                    "to": [recipient_email],
                    "subject": subject,
                    "html": html_body
                }
                
                # Attach PDF if exists
                if pdf_path and os.path.exists(pdf_path):
                    import base64
                    with open(pdf_path, "rb") as f:
                        pdf_data = base64.b64encode(f.read()).decode()
                    email_params["attachments"] = [{
                        "filename": f"FireReach_{company.replace(' ','_')}.pdf",
                        "content": pdf_data
                    }]
                
                result = resend.Emails.send(email_params)
                
                return {
                    "status": "sent",
                    "recipient": recipient_email,
                    "recipient_name": contact.get("name", ""),
                    "subject": subject,
                    "generated_email": body,
                    "email_id": result.get("id", "")
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e),
                    "recipient": recipient_email,
                    "recipient_name": contact.get("name", ""),
                    "subject": subject,
                    "generated_email": body
                }
        else:
            return {
                "status": "no_email_found",
                "recipient": "",
                "recipient_name": contact.get("name", ""),
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