import os
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def tool_outreach_automated_sender(account_brief: str, signals: list, recipient_email: str, company: str) -> dict:
    """
    Generate personalized outreach email and send it automatically using SMTP.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    signals_text = "\n".join([f"- {signal}" for signal in signals[:3]])
    
    prompt = f"""You are writing a personalized B2B outreach email.

Company: {company}
Recipient: {recipient_email}

Account Brief:
{account_brief}

Key Signals:
{signals_text}

Write a professional outreach email that:
- References at least TWO specific signals
- Connects those signals to potential challenges
- Offers clear value
- Includes a specific call to action

Format:
Subject: [write subject line]
---
[write email body]

Keep it concise and professional."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )
        
        email_content = response.choices[0].message.content
        
        parts = email_content.split("---")
        subject = parts[0].replace("Subject:", "").strip()
        body = parts[1].strip() if len(parts) > 1 else email_content
        
        # Attempt real email delivery via SMTP
        try:
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")
            from_email = os.getenv("FROM_EMAIL", smtp_user)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {
                "status": "sent",
                "recipient": recipient_email,
                "subject": subject,
                "generated_email": body
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "recipient": recipient_email,
                "subject": subject,
                "generated_email": body
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "recipient": recipient_email,
            "subject": "",
            "generated_email": ""
        }
