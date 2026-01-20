# Import Database and Images to Railway

**Date:** 2026-01-20 02:27:52

## 📊 Your Database Stats

- **Transactions:** {1070}
- **Allocations:** {86}
- **Product Images:** {59}
- **Total Items:** {1544}

## 🎯 Migration Steps

### Step 1: Upload Images to Cloudinary (5 minutes)

1. **Sign up for Cloudinary (free):**
   - Go to: https://cloudinary.com
   - Create free account
   - Verify email

2. **Get credentials:**
   - Go to Dashboard: https://console.cloudinary.com/
   - Copy these values:
     - Cloud Name
     - API Key
     - API Secret

3. **Install Cloudinary:**
   ```bash
   pip install cloudinary
   ```

4. **Edit upload script:**
   - Open: `upload_to_cloudinary.py`
   - Replace placeholder credentials with yours
   - Save

5. **Upload images:**
   ```bash
   python3 upload_to_cloudinary.py
   ```
   
   This will:
   - Upload all 41 images to Cloudinary
   - Save URL mapping to `cloudinary_urls.json`

### Step 2: Update Database with Cloud URLs (1 minute)

```bash
python3 update_image_urls.py
```

This updates your database to use Cloudinary URLs instead of local paths.

### Step 3: Import Database to Railway (2 minutes)

**Option A: Copy Database File (Easiest)**

1. **Via Railway CLI:**
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Link to your project
   railway link
   
   # Copy database to Railway
   railway run cp ../data/inventory.db /app/data/inventory.db
   ```

**Option B: Import SQL (Alternative)**

1. **SSH into Railway:**
   ```bash
   railway shell
   ```

2. **Import SQL:**
   ```bash
   sqlite3 data/inventory.db < database_export.sql
   exit
   ```

### Step 4: Restart Railway Service

```bash
railway up
```

Or click "Restart" in Railway dashboard.

### Step 5: Verify

1. Visit your Railway URL
2. You should see:
   - ✅ All {1544} items
   - ✅ All allocations
   - ✅ All images (from Cloudinary)

## 📝 Exported Files

- `inventory_backup_*.db` - Database backup
- `database_export.sql` - SQL export
- `upload_to_cloudinary.py` - Image upload script
- `update_image_urls.py` - Database update script
- `cloudinary_urls.json` - URL mapping (created after upload)

## 🔐 Important

**Lock admin before sharing:**
1. Visit Railway URL
2. Click 🔓 Admin Enabled
3. Lock it (🔒 Admin Locked)
4. Share URL with team

Team will see view-only interface with all your data!

## ⚠️ Troubleshooting

### Images not showing on Railway?
- Make sure you ran `update_image_urls.py`
- Check `cloudinary_urls.json` exists
- Verify URLs start with `https://res.cloudinary.com`

### Database empty on Railway?
- Make sure you copied the database file
- Check Railway logs: `railway logs`
- Verify data/ directory exists

### Need help?
Check Railway logs:
```bash
railway logs
```

---

**Ready to migrate!** Start with Step 1 (Cloudinary). 🚀
