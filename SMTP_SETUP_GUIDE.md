# 📧 SMTP Email Setup Guide (Gmail)

FireReach now uses SMTP for email sending - no domain verification needed!

---

## 🚀 Quick Setup with Gmail

### Step 1: Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the steps to enable it

### Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Enter "FireReach" as the name
4. Click "Generate"
5. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### Step 3: Update .env File

Open `backend/.env` and update these lines:

```env
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="abcdefghijklmnop"
FROM_EMAIL="your-email@gmail.com"
```

**Important**: 
- Use your actual Gmail address for `SMTP_USER` and `FROM_EMAIL`
- Use the 16-character app password (remove spaces) for `SMTP_PASSWORD`

---

## ✅ Test Email Sending

```bash
cd backend
python test_agent.py
```

You should see:
```
✉️ EMAIL STATUS: SENT
```

The email will be sent from your Gmail account!

---

## 🔧 Other SMTP Providers

### Outlook/Hotmail
```env
SMTP_SERVER="smtp-mail.outlook.com"
SMTP_PORT="587"
SMTP_USER="your-email@outlook.com"
SMTP_PASSWORD="your-password"
```

### Yahoo Mail
```env
SMTP_SERVER="smtp.mail.yahoo.com"
SMTP_PORT="587"
SMTP_USER="your-email@yahoo.com"
SMTP_PASSWORD="your-app-password"
```

### Custom SMTP
```env
SMTP_SERVER="your-smtp-server.com"
SMTP_PORT="587"
SMTP_USER="your-username"
SMTP_PASSWORD="your-password"
```

---

## 🐛 Troubleshooting

### "Authentication failed"
- Make sure 2FA is enabled
- Use app password, not your regular Gmail password
- Remove spaces from the app password

### "Connection refused"
- Check SMTP_SERVER and SMTP_PORT are correct
- Make sure port 587 is not blocked by firewall

### "Sender address rejected"
- Make sure FROM_EMAIL matches SMTP_USER
- Use your actual Gmail address

---

## ✨ Advantages of SMTP

- ✅ No domain verification needed
- ✅ Works immediately
- ✅ Free with Gmail
- ✅ Reliable delivery
- ✅ Perfect for testing and production

---

## 🎯 Ready to Deploy

Once SMTP is configured, FireReach will send real emails!

Follow `DEPLOY_INSTRUCTIONS.txt` to deploy to Render + Vercel.
