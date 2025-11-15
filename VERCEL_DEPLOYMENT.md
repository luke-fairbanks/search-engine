# Vercel Deployment Guide

## Quick Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (sign up at vercel.com)
- MongoDB Atlas database (already configured)

### Step 1: Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for Vercel deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/search-engine.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Vercel

#### Option A: Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? search-engine
# - In which directory is your code located? ./
# - Want to override settings? No

# Deploy to production
vercel --prod
```

#### Option B: Vercel Dashboard
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: frontend/build
   - **Install Command**: `cd backend && pip install -r requirements-vercel.txt`

### Step 3: Configure Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

Add these variables:
- `MONGODB_URI`: Your MongoDB Atlas connection string
  ```
  mongodb+srv://username:password@cluster.mongodb.net/
  ```
- `USE_MONGODB`: `true`
- `PORT`: `5001` (optional)

### Step 4: Redeploy
After adding environment variables, trigger a new deployment:
```bash
vercel --prod
```

Or click "Redeploy" in the Vercel dashboard.

## Important Notes

### API Routes
- All API endpoints are available at: `https://your-app.vercel.app/api/*`
- WebSocket endpoints: `wss://your-app.vercel.app/ws/*`

### MongoDB Connection
- Ensure MongoDB Atlas allows connections from `0.0.0.0/0` (all IPs)
- Or add Vercel's IP ranges to your MongoDB whitelist

### Known Limitations on Vercel
1. **WebSocket support is limited** - The crawler WebSocket may not work on Vercel's serverless functions
2. **Background tasks** - Crawler jobs run synchronously and may timeout (10s limit on hobby plan)

### Alternatives for Production

If you need full WebSocket/background task support:

#### Option 1: Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Option 2: Render.com
1. Create Web Service
2. Connect GitHub repo
3. Build Command: `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
4. Start Command: `cd backend && python server.py`

#### Option 3: DigitalOcean App Platform
1. Create App
2. Connect GitHub
3. Add environment variables
4. Deploy

## Testing Your Deployment

1. Visit your Vercel URL
2. Test search functionality
3. Check MongoDB connection in browser console
4. Try searching for indexed content

## Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements-vercel.txt`
- Verify `package.json` has all frontend dependencies

### MongoDB Connection Error
- Verify `MONGODB_URI` is correctly set
- Check MongoDB Atlas network access settings
- Ensure database user has read/write permissions

### Frontend Not Loading
- Check that `frontend/build` directory was created
- Verify `vercel.json` routing is correct

### API Not Working
- Check Vercel function logs
- Verify environment variables are set
- Test endpoints directly: `https://your-app.vercel.app/api/stats`

## Performance Tips

1. **Enable Caching**: MongoDB index cache reduces rebuild time
2. **Optimize Images**: None currently, but consider for future enhancements
3. **CDN**: Vercel automatically uses CDN for static assets
4. **Monitoring**: Use Vercel Analytics for performance insights

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS:
   - Type: `CNAME`
   - Name: `@` or `www`
   - Value: `cname.vercel-dns.com`

## Continuous Deployment

Once connected to GitHub, Vercel will:
- Automatically deploy on every push to `main`
- Create preview deployments for pull requests
- Show deployment status in GitHub

Your search engine is now live! 🚀
