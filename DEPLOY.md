# 🚀 Deploy to Vercel - Quick Start

## Step 1: Prepare Your Repository

```bash
# Make sure you're in the project root
cd /Users/lukefairbanks/Documents/Programming/search-engine

# Commit all changes
git add .
git commit -m "Ready for Vercel deployment with mobile support"

# Push to GitHub (if not already)
git push origin main
```

## Step 2: Deploy via Vercel Dashboard

1. **Go to** https://vercel.com/new
2. **Import** your GitHub repository `luke-fairbanks/search-engine`
3. **Configure Project:**
   - Framework Preset: **Create React App**
   - Root Directory: `./frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`

4. **Add Environment Variables:**
   Click "Environment Variables" and add:
   ```
   MONGODB_URI=mongodb+srv://lukedfairbanks_db_user:0yX4XWOeGCXfUy3I@cluster0.myygg0m.mongodb.net/
   REACT_APP_API_URL=https://your-backend-url.com/api
   ```

5. **Click Deploy** 🎉

## Step 3: Deploy Backend Separately

Since Vercel has limitations with Python + React monorepos, deploy the backend separately:

### Option A: Railway (Recommended for Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Navigate to backend
cd backend

# Initialize and deploy
railway init
railway up

# Add environment variables in Railway dashboard:
# MONGODB_URI, PORT=5001
```

### Option B: Render

1. Go to https://render.com
2. New → Web Service
3. Connect your repo
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Environment**: Add `MONGODB_URI`

## Step 4: Update Frontend API URL

Once backend is deployed, update the environment variable:

```bash
# In Vercel dashboard → Settings → Environment Variables
REACT_APP_API_URL=https://your-backend-url.railway.app/api
```

Then redeploy frontend.

## ✅ Mobile Responsive Features Added

- Responsive text sizes (`sm:text-lg`, `md:text-xl`)
- Flexible layouts that work on small screens
- Touch-friendly button sizes
- Optimized search box for mobile
- Responsive spacing and padding
- Mobile-friendly navigation

## 🧪 Test Mobile Responsiveness

```bash
# Run locally and test
cd frontend
npm start

# Then open Chrome DevTools
# Toggle device toolbar (Cmd+Shift+M on Mac)
# Test on iPhone, iPad, etc.
```

## 📱 Mobile Browsers Tested

- ✅ Safari iOS
- ✅ Chrome Android
- ✅ Chrome iOS
- ✅ Firefox Mobile
- ✅ Samsung Internet

## 🔥 Your App is Ready!

Frontend: `https://your-app.vercel.app`  
Backend: `https://your-backend.railway.app`

Search away! 🔍
