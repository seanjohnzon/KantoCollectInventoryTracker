# Railway Deployment Troubleshooting

## Check Logs

**In Railway Dashboard:**
1. Click on your project
2. Click "**Deployments**" tab
3. Click on the latest deployment
4. Click "**View Logs**"
5. Look for error messages

## Common Issues & Fixes

### Issue 1: Port Binding Error

**Error:** `Address already in use` or `Cannot bind to port`

**Fix:** Make sure app uses Railway's PORT variable (already configured)

### Issue 2: Database Path Error

**Error:** `No such file or directory: data/inventory.db`

**Fix:** Railway needs database to be created on startup

Add this to `app/ui.py` before starting server:

```python
# In main() function, before creating server:
from pathlib import Path
db_path = Path("data")
db_path.mkdir(exist_ok=True)
```

### Issue 3: Missing Dependencies

**Error:** `ModuleNotFoundError`

**Fix:** Check `requirements.txt` has all dependencies

### Issue 4: Server Not Starting

**Error:** Various startup errors

**Most likely cause:** Database directory doesn't exist on Railway

## Quick Fix for Database

The app tries to use `data/inventory.db` but this directory might not exist on Railway.

**Two Solutions:**

### A. Use Current Directory (Quick Fix)
Change database path to use current directory instead of `data/`

### B. Create Directory on Startup (Better)
Ensure `data/` directory is created before accessing database

## Which Error Are You Seeing?

**Please share the logs from Railway and I'll fix it immediately.**

Look for lines like:
- `FileNotFoundError`
- `Address already in use`  
- `ModuleNotFoundError`
- `Cannot connect to database`

## Railway Environment Check

Railway sets these automatically:
- `PORT` - Dynamic port (not 5173)
- `RAILWAY_ENVIRONMENT` - Set to "production"

Our code already handles these! ✅
