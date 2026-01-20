# 🚀 Complete Migration Guide to Railway

**Your data is ready to migrate!**

## 📦 What's Been Prepared

✅ **Database exported:** 1,544 items, 86 allocations, 43 images  
✅ **Backup created:** `railway_export/inventory_backup_*.db`  
✅ **SQL export:** `railway_export/database_export.sql`  
✅ **Migration scripts:** All ready in `railway_export/`

## 🎯 3-Step Migration Process

### Step 1: Upload Images to Cloudinary (5 min)

**Why Cloudinary?**
- Free tier: 25GB storage + bandwidth
- Your 43 images = ~2MB total
- Permanent, fast URLs
- No Railway storage fees

**Steps:**

1. **Sign up (1 min):**
   - Go to: https://cloudinary.com
   - Click "Sign up for free"
   - Verify email

2. **Get credentials (1 min):**
   - Dashboard: https://console.cloudinary.com/
   - You'll see:
     - **Cloud Name:** (copy this)
     - **API Key:** (copy this)
     - **API Secret:** (click "Show" and copy)

3. **Prepare upload script (1 min):**
   ```bash
   cd railway_export
   pip install cloudinary
   
   # Edit upload script
   nano upload_to_cloudinary.py
   # (or use any text editor)
   ```
   
   Replace these 3 lines at the top:
   ```python
   CLOUDINARY_CLOUD_NAME = "your_cloud_name"      # ← Paste yours
   CLOUDINARY_API_KEY = "your_api_key"            # ← Paste yours
   CLOUDINARY_API_SECRET = "your_api_secret"      # ← Paste yours
   ```
   
   Save and exit.

4. **Upload images (2 min):**
   ```bash
   python3 upload_to_cloudinary.py
   ```
   
   You'll see:
   ```
   ✅ [1/43] Phantasmal Flames Booster Bundle.jpg
      URL: https://res.cloudinary.com/...
   ✅ [2/43] Prismatic Evolutions Elite Trainer Box.jpg
      URL: https://res.cloudinary.com/...
   ...
   ✅ Uploaded 43 images
   ✅ URL mapping saved: cloudinary_urls.json
   ```

### Step 2: Update Database with Cloud URLs (1 min)

```bash
# Still in railway_export/
python3 update_image_urls.py
```

This replaces local paths with Cloudinary URLs in your database.

You'll see:
```
✅ Updated: phantasmal flames booster bundle
✅ Updated: prismatic evolutions elite trainer box
...
✅ Updated 43 image URLs
✅ Database ready for Railway!
```

### Step 3: Deploy to Railway (3 min)

**Option A: Via Railway CLI (Recommended)**

```bash
# Install Railway CLI (one-time)
npm i -g @railway/cli

# Login to Railway
railway login

# Go back to project root
cd /Users/sahcihansahin/KantoCollectInventory

# Link to your Railway project
railway link
# (Select your project from list)

# Copy the updated database to Railway
railway run cp data/inventory.db /app/data/inventory.db

# Deploy
railway up

# Done! Get your URL
railway status
```

**Option B: Manual Upload**

If CLI doesn't work:

1. Go to Railway dashboard
2. Your project → Settings → Variables
3. Add variable: `DATABASE_SEED=true`
4. Restart service
5. The database will be created

Then use the Railway web shell to import:
1. Settings → Shell
2. Upload your `database_export.sql`
3. Run: `sqlite3 data/inventory.db < database_export.sql`

## ✅ Verification

Visit your Railway URL. You should see:

- ✅ **Total Inventory:** 1,544 items
- ✅ **Allocated:** Your 86 allocations
- ✅ **Images:** All 43 images loading from Cloudinary
- ✅ **Cihan/Askar/Nima/Kanto:** All assignments visible

## 🔐 Lock Admin Before Sharing

**Important!** Lock admin mode for team viewing:

1. Visit Railway URL
2. Click **🔓 Admin Enabled** button
3. It becomes **🔒 Admin Locked**
4. Now team sees view-only interface

**Unlock later:**
- Click **🔒 Admin Locked**
- Enter PIN: `1453`
- Full edit access restored

## 📋 Files in railway_export/

| File | Purpose |
|------|---------|
| `IMPORT_TO_RAILWAY.md` | Detailed instructions |
| `upload_to_cloudinary.py` | Upload images to cloud |
| `update_image_urls.py` | Update DB with cloud URLs |
| `database_export.sql` | SQL dump for import |
| `inventory_backup_*.db` | Your database backup |
| `cloudinary_urls.json` | URL mapping (after upload) |

## 🆘 Troubleshooting

### Images not showing?
- Make sure you ran both scripts:
  1. `upload_to_cloudinary.py`
  2. `update_image_urls.py`
- Check `cloudinary_urls.json` exists

### Database empty on Railway?
- Make sure you copied the database:
  ```bash
  railway run cp data/inventory.db /app/data/inventory.db
  ```
- Or imported the SQL:
  ```bash
  railway run sqlite3 data/inventory.db < railway_export/database_export.sql
  ```

### Railway CLI not working?
- Install Node.js first: https://nodejs.org
- Then: `npm i -g @railway/cli`
- Login: `railway login`

## 🎉 You're Done!

After migration:
- **Local:** Keep your local version (1,544 items)
- **Railway:** Team access (same 1,544 items)
- **Images:** Hosted on Cloudinary (free)
- **Backups:** Safe in `railway_export/`

**Share Railway URL with team! 🚀**

---

**Need help?** Read `railway_export/IMPORT_TO_RAILWAY.md` for more details.
