# 🚀 FireReach Deployment Guide

## Overview
- **Backend**: Deploy to Render
- **Frontend**: Deploy to Vercel

---

## 🔧 Backend Deployment (Render)

### Step 1: Prepare Repository
Push your code to GitHub (if not already done).

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Connect your GitHub account

### Step 3: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `firereach-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables
In Render dashboard, add these environment variables:

```
GROQ_API_KEY=your_groq_api_key_here
RESEND_API_KEY=your_resend_api_key_here
FROM_EMAIL=your_verified_email@domain.com
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment (3-5 minutes)
3. Copy your backend URL (e.g., `https://firereach-backend.onrender.com`)

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Update API URL
Before deploying, update the frontend to use your Render backend URL.

Open `frontend/index.html` and replace:
```javascript
const response = await fetch('http://localhost:8000/run-agent', {
```

With:
```javascript
const response = await fetch('https://YOUR-RENDER-URL.onrender.com/run-agent', {
```

### Step 2: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up or log in with GitHub

### Step 3: Deploy Frontend
1. Click "Add New..." → "Project"
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
4. Click "Deploy"

### Step 4: Access Your App
1. Vercel will provide a URL (e.g., `https://firereach.vercel.app`)
2. Visit the URL to use FireReach

---

## 🔍 Testing Deployment

### Test Backend
```bash
curl https://YOUR-RENDER-URL.onrender.com/
```

Expected response:
```json
{"status":"FireReach API running"}
```

### Test Frontend
1. Open your Vercel URL
2. Fill in the form:
   - ICP: "We sell cybersecurity training to Series B startups"
   - Company: "Stripe"
   - Email: "test@example.com"
3. Click "Launch FireReach"
4. Verify results display

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: "Application failed to start"
- Check environment variables are set correctly
- Verify `requirements.txt` is in backend directory
- Check Render logs for errors

**Problem**: CORS errors
- Backend already has CORS enabled for all origins
- If issues persist, check Render logs

### Frontend Issues

**Problem**: "Failed to fetch"
- Verify backend URL is correct in `index.html`
- Check backend is running (visit backend URL)
- Check browser console for errors

**Problem**: "Email status: ERROR"
- This is normal if Resend domain isn't verified
- Email generation still works, check the output

---

## 📝 Environment Variables Reference

### Required for Backend (Render)
```
GROQ_API_KEY     - Get from console.groq.com
RESEND_API_KEY   - Get from resend.com/api-keys
FROM_EMAIL       - Must be verified in Resend
```

---

## 🎯 Quick Deploy Checklist

- [ ] Push code to GitHub
- [ ] Deploy backend to Render
- [ ] Add environment variables in Render
- [ ] Copy Render backend URL
- [ ] Update frontend API URL
- [ ] Deploy frontend to Vercel
- [ ] Test the deployed app

---

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Groq API Console](https://console.groq.com)
- [Resend Dashboard](https://resend.com/overview)
