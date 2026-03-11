# 🚀 Push FireReach to GitHub

## Step 1: Create GitHub Repository

1. Go to: **https://github.com/new**
2. Repository name: `firereach`
3. Description: `Autonomous Outreach Engine - AI-powered sales outreach automation`
4. Choose: **Private** or **Public**
5. **DO NOT** initialize with README, .gitignore, or license
6. Click **"Create repository"**

## Step 2: Push Your Code

After creating the repository, run these commands:

```bash
git remote add origin https://github.com/YOUR-USERNAME/firereach.git
git branch -M main
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username.

## Step 3: Verify

Go to your GitHub repository URL to see your code!

---

## 🔒 Important: Protect Your Secrets

Your `.env` file is already in `.gitignore`, so your API keys are safe and won't be pushed to GitHub.

Files that are NOT pushed (protected):
- `backend/.env` (contains your API keys)

---

## 📝 Repository Structure

```
firereach/
├── backend/          # FastAPI backend
├── frontend/         # HTML/CSS/JS frontend
├── README.md         # Project documentation
├── DEPLOYMENT.md     # Deployment guide
└── .gitignore        # Protected files
```

---

## ✅ Next Steps After Pushing

1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Follow `DEPLOY_INSTRUCTIONS.txt` for deployment

---

## 🔗 Quick Links

- Create repo: https://github.com/new
- Your repos: https://github.com/YOUR-USERNAME?tab=repositories
