# 🚀 DEPLOY TO RAILWAY - Step by Step

**Your data is backed up and safe!**

## ✅ Your Data (Verified)

- ✅ **1,070 transactions**
- ✅ **86 allocations** (Cihan, Askar, Nima, Kanto)
- ✅ **59 product images** (on ImageKit)
- ✅ **1,544 total items**

**Backup created:** `data/inventory.db.FINAL_BACKUP_20260120_023647`

---

## 📋 Deployment Steps

### Step 1: Login to Railway

```bash
railway login
```

**What happens:**
- Browser window opens
- Click "Authorize"
- Come back to terminal
- You'll see: "✅ Logged in"

---

### Step 2: Link to Your Project

```bash
railway link
```

**What happens:**
- Shows list of your Railway projects
- Select your project (use arrow keys + Enter)
- You'll see: "✅ Linked to project"

---

### Step 3: Run Safe Deployment Script

```bash
./deploy_safe.sh
```

**What happens:**
- ✅ Verifies local data (1,544 items)
- ✅ Creates backup
- ✅ Copies database to Railway
- ✅ Verifies data on Railway
- ✅ Deploys code
- ✅ Shows your URL

**Takes:** 2-3 minutes

**Output example:**
```
✅ Local database verified:
   Transactions: 1070
   Allocations: 86
   Images: 59
   Total Items: 1544

✅ Railway database verified:
   Transactions: 1070
   Allocations: 86
   Images: 59
   Total Items: 1544

✅ VERIFICATION PASSED: All data matches!

✅ DEPLOYMENT COMPLETE!
```

---

## 🔍 Verify Deployment

After deployment, visit your Railway URL:

### Check Total Items
- Should show: **1,544 items**

### Check Allocations
- **Cihan:** Should have items assigned
- **Askar:** Should have items assigned
- **Nima:** Should have items assigned
- **Kanto:** Should have items assigned

### Check Images
- All images should load from ImageKit
- Example: Prismatic Evolutions, Phantasmal Flames, etc.

### Check Unallocated
- Should show remaining inventory

---

## 🔒 Lock Admin (Important!)

Before sharing with team:

1. Visit your Railway URL
2. Click: **🔓 Admin Enabled**
3. It becomes: **🔒 Admin Locked**
4. Now team can only VIEW (no edits)

**To unlock later:**
- Click **🔒 Admin Locked**
- Enter PIN: **1453**
- Full access restored

---

## ⚠️ If Something Goes Wrong

### Database not copied?

```bash
# Try manual copy
railway run mkdir -p /app/data
railway run cp data/inventory.db /app/data/inventory.db
```

### Need to restore local backup?

```bash
# Your data is safe!
cp data/inventory.db.FINAL_BACKUP_20260120_023647 data/inventory.db
```

### Images not loading?

- They're on ImageKit: https://ik.imagekit.io/homecraft/Item%20Pics/
- Test one: https://ik.imagekit.io/homecraft/Item%20Pics/Prismatic%20Evolutions%20Booster%20Pack.jpg
- Should load instantly

---

## 💾 Your Backups

Multiple backups created:

1. **FINAL_BACKUP_20260120_023647** - Before deployment
2. **BEFORE_RAILWAY_[timestamp]** - Created by script
3. **with_imagekit_urls** - With cloud URLs
4. **GitHub** - Full code backup

**Your data is 100% safe!**

---

## 🎯 Summary

Run these 3 commands:

```bash
railway login        # Step 1: Authorize
railway link         # Step 2: Select project
./deploy_safe.sh     # Step 3: Deploy safely
```

**That's it!** Script handles verification and deployment. 🚀

---

## ✅ After Deployment

1. Visit Railway URL
2. Verify: 1,544 items ✅
3. Verify: All images load ✅
4. Verify: Allocations show ✅
5. Lock admin 🔒
6. Share with team! 🎉

**PIN: 1453**
