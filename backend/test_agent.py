"""
Quick test script to verify FireReach pipeline
"""
import os
from dotenv import load_dotenv

load_dotenv()

from agent import run_agent

# Test inputs
icp = "We sell high-end cybersecurity training to Series B startups"
company = "Stripe"
recipient_email = "aaaditya169@gmail.com"

print("🔥 Testing FireReach Pipeline...\n")
print(f"ICP: {icp}")
print(f"Company: {company}")
print(f"Recipient: {recipient_email}\n")
print("=" * 60)

result = run_agent(icp=icp, company=company, recipient_email=recipient_email)

print("\n📊 SIGNALS CAPTURED:")
for i, signal in enumerate(result["signals"], 1):
    print(f"{i}. {signal}")

print("\n📝 ACCOUNT BRIEF:")
print(result["account_brief"])

print("\n✉️ EMAIL STATUS:", result["status"].upper())
print("📧 RECIPIENT:", result["recipient"])

print("\n📧 GENERATED EMAIL:")
print(f"Subject: {result['subject']}")
print(f"\n{result['generated_email']}")

print("\n" + "=" * 60)
print("✅ Pipeline completed successfully!")
