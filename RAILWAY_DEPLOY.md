# Railway Deployment Guide

**Date:** January 20, 2026  
**Repository:** https://github.com/seanjohnzon/KantoCollectInventoryTracker

## Prerequisites

1. Railway account (free tier available)
2. GitHub repository already set up ✅
3. Code pushed to GitHub ✅

## Deployment Steps

### Option 1: Deploy via Railway Dashboard (Recommended)

1. **Go to Railway:**
   - Visit https://railway.app/
   - Sign in with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `seanjohnzon/KantoCollectInventoryTracker`

3. **Configure:**
   - Railway will auto-detect Python
   - Will use `Procfile` and `railway.json`
   - Database will be created automatically

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)

5. **Get URL:**
   - Click "Settings" → "Domains"
   - Railway will provide a URL like:
     `https://your-app.railway.app`

### Option 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
cd /Users/sahcihansahin/KantoCollectInventory
railway init

# Deploy
railway up

# Get URL
railway domain
```

## Important Notes

### Database Persistence

⚠️ **Your local database won't be deployed!**

Railway will create a fresh database. You have two options:

**Option A: Start Fresh**
- New empty database on Railway
- Team members can ingest CSVs via UI
- Each deployment is independent

**Option B: Seed Data** (if needed later)
- Export your local data
- Create seed script
- Run on Railway startup

For now, **Option A** is recommended - team can view structure and you maintain local data.

### Admin Lock

✅ **PIN protection works on Railway**
- PIN: 1453 (same as local)
- Team members need PIN to edit
- They can view without PIN
- Lock it by default for view-only access

### Environment Variables

Railway automatically sets:
- `PORT` - Server port (dynamic)
- `RAILWAY_ENVIRONMENT` - Enables 0.0.0.0 binding

No manual configuration needed!

## Access for Team

### Share with Team:
1. Deploy to Railway (get URL)
2. **Lock admin mode** before sharing
3. Share URL: `https://your-app.railway.app`
4. Team can view inventory (view-only)

### If Team Needs to Edit:
- Share PIN: 1453
- They can unlock admin mode
- Full control available

## Configuration Files

✅ `Procfile` - Tells Railway how to start app  
✅ `railway.json` - Railway build configuration  
✅ `requirements.txt` - Python dependencies  
✅ `.gitignore` - Excludes database files  

## Cost

**Railway Free Tier:**
- $5 credit/month
- Should be sufficient for small team
- Automatic scaling

**If you need more:**
- Upgrade to Pro ($20/month)
- More resources
- Better performance

## Deployment Checklist

- [x] Code pushed to GitHub
- [x] Procfile created
- [x] railway.json created
- [x] requirements.txt up to date
- [x] .gitignore excludes database
- [x] Port configuration dynamic
- [ ] Deploy on Railway dashboard
- [ ] Get deployment URL
- [ ] Lock admin mode
- [ ] Share with team

## Next Steps

1. **Go to:** https://railway.app/
2. **Sign in** with GitHub
3. **Click "New Project"**
4. **Select your repo:** `KantoCollectInventoryTracker`
5. **Wait for deployment** (2-3 min)
6. **Get URL** and share with team!

---

**Ready to deploy! Just go to Railway and connect your GitHub repo.** 🚀
