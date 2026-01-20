#!/usr/bin/env python3
"""
Migration script to prepare database and images for Railway deployment.

This script:
1. Exports your local database to SQL format
2. Uploads images to Cloudinary (free cloud storage)
3. Updates database with Cloudinary URLs
4. Creates a backup for Railway import

Prerequisites:
- pip install cloudinary

Usage:
- Set Cloudinary credentials (get from cloudinary.com)
- Run: python3 migrate_to_railway.py
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict
import shutil
from datetime import datetime

# Paths
LOCAL_DB = Path("data/inventory.db")
LOCAL_IMAGES = Path("/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics")
EXPORT_DIR = Path("railway_export")
BACKUP_DB = EXPORT_DIR / f"inventory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
SQL_EXPORT = EXPORT_DIR / "database_export.sql"


def create_export_directory():
    """Create export directory for migration files."""
    EXPORT_DIR.mkdir(exist_ok=True)
    print(f"✅ Export directory: {EXPORT_DIR.absolute()}")


def backup_database():
    """Create a backup of the current database."""
    if not LOCAL_DB.exists():
        print(f"❌ Database not found: {LOCAL_DB}")
        return False
    
    shutil.copy2(LOCAL_DB, BACKUP_DB)
    print(f"✅ Database backed up: {BACKUP_DB}")
    return True


def export_database_to_sql():
    """Export database to SQL format for easy import on Railway."""
    conn = sqlite3.connect(LOCAL_DB)
    
    with open(SQL_EXPORT, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    
    conn.close()
    print(f"✅ SQL export created: {SQL_EXPORT}")
    print(f"   Size: {SQL_EXPORT.stat().st_size / 1024:.2f} KB")


def get_database_stats():
    """Get statistics about the database."""
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()
    
    stats = {}
    
    # Count transactions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    stats['transactions'] = cursor.fetchone()[0]
    
    # Count allocations
    cursor.execute("SELECT COUNT(*) FROM allocations")
    stats['allocations'] = cursor.fetchone()[0]
    
    # Count product images
    cursor.execute("SELECT COUNT(*) FROM product_images")
    stats['product_images'] = cursor.fetchone()[0]
    
    # Total inventory
    cursor.execute("SELECT SUM(quantity_sold) FROM transactions")
    stats['total_items'] = cursor.fetchone()[0] or 0
    
    conn.close()
    return stats


def list_images() -> List[Path]:
    """List all images to be uploaded."""
    if not LOCAL_IMAGES.exists():
        print(f"❌ Images directory not found: {LOCAL_IMAGES}")
        return []
    
    images = list(LOCAL_IMAGES.glob("*.jpg")) + list(LOCAL_IMAGES.glob("*.png"))
    print(f"✅ Found {len(images)} images")
    return images


def create_cloudinary_upload_script(images: List[Path]):
    """Create a script to upload images to Cloudinary."""
    script_path = EXPORT_DIR / "upload_to_cloudinary.py"
    
    # Format images list for script
    images_list = "[\n"
    for img in images:
        images_list += f'    r"{img}",\n'
    images_list += "]"
    
    script_content = f'''#!/usr/bin/env python3
"""
Upload images to Cloudinary.

Prerequisites:
1. Sign up at https://cloudinary.com (free tier)
2. Get your credentials from dashboard
3. pip install cloudinary
4. Run this script

Usage:
    python3 upload_to_cloudinary.py
"""

import cloudinary
import cloudinary.uploader
from pathlib import Path

# TODO: Replace with your Cloudinary credentials
# Get these from: https://console.cloudinary.com/
CLOUDINARY_CLOUD_NAME = "your_cloud_name"
CLOUDINARY_API_KEY = "your_api_key"
CLOUDINARY_API_SECRET = "your_api_secret"

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# Images to upload
IMAGES = {images_list}

def upload_images():
    """Upload all images to Cloudinary."""
    url_mapping = {{}}
    
    print("🚀 Starting upload to Cloudinary...")
    print()
    
    for i, image_path in enumerate(IMAGES, 1):
        try:
            path = Path(image_path)
            if not path.exists():
                print(f"⚠️  Skipping (not found): {{path.name}}")
                continue
            
            # Upload to Cloudinary
            # Use folder "kanto-inventory" to organize
            result = cloudinary.uploader.upload(
                str(path),
                folder="kanto-inventory",
                public_id=path.stem,  # Use filename without extension
                overwrite=True,
                resource_type="image"
            )
            
            url_mapping[str(path)] = result['secure_url']
            print(f"✅ [{{i}}/{{len(IMAGES)}}] {{path.name}}")
            print(f"   URL: {{result['secure_url']}}")
            
        except Exception as e:
            print(f"❌ Failed: {{path.name}} - {{e}}")
    
    print()
    print(f"✅ Uploaded {{len(url_mapping)}} images")
    
    # Save URL mapping
    import json
    mapping_file = Path("cloudinary_urls.json")
    with open(mapping_file, 'w') as f:
        json.dump(url_mapping, f, indent=2)
    
    print(f"✅ URL mapping saved: {{mapping_file}}")
    return url_mapping

if __name__ == "__main__":
    if CLOUDINARY_CLOUD_NAME == "your_cloud_name":
        print("❌ Please update Cloudinary credentials in this script first!")
        print()
        print("Steps:")
        print("1. Go to https://cloudinary.com")
        print("2. Sign up (free)")
        print("3. Go to Dashboard")
        print("4. Copy: Cloud Name, API Key, API Secret")
        print("5. Update this script with your credentials")
        print("6. Run again")
        exit(1)
    
    upload_images()
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(0o755)
    
    print(f"✅ Cloudinary upload script created: {script_path}")


def create_database_update_script():
    """Create script to update database with Cloudinary URLs."""
    script_path = EXPORT_DIR / "update_image_urls.py"
    
    script_content = '''#!/usr/bin/env python3
"""
Update database with Cloudinary URLs after upload.

Run this AFTER uploading images to Cloudinary.

Usage:
    python3 update_image_urls.py
"""

import sqlite3
import json
from pathlib import Path
import unicodedata

def normalize_path(path_str: str) -> str:
    """Normalize Unicode characters in path."""
    return unicodedata.normalize('NFC', str(path_str))

def update_database():
    """Update product_images table with Cloudinary URLs."""
    
    # Load URL mapping
    mapping_file = Path("cloudinary_urls.json")
    if not mapping_file.exists():
        print("❌ cloudinary_urls.json not found!")
        print("   Run upload_to_cloudinary.py first")
        return
    
    with open(mapping_file, 'r') as f:
        url_mapping = json.load(f)
    
    # Connect to database
    db_path = Path("../data/inventory.db")
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current product images
    cursor.execute("SELECT id, normalized_item_name, image_url FROM product_images")
    rows = cursor.fetchall()
    
    updated = 0
    for row_id, normalized_name, old_url in rows:
        if not old_url or not old_url.startswith('/Users/'):
            continue  # Skip if not local path
        
        # Normalize old URL for matching
        old_url_normalized = normalize_path(old_url)
        
        # Find matching Cloudinary URL
        new_url = None
        for local_path, cloud_url in url_mapping.items():
            local_path_normalized = normalize_path(local_path)
            if local_path_normalized == old_url_normalized:
                new_url = cloud_url
                break
        
        if new_url:
            cursor.execute(
                "UPDATE product_images SET image_url = ? WHERE id = ?",
                (new_url, row_id)
            )
            updated += 1
            print(f"✅ Updated: {normalized_name}")
    
    conn.commit()
    conn.close()
    
    print()
    print(f"✅ Updated {updated} image URLs")
    print("✅ Database ready for Railway!")

if __name__ == "__main__":
    update_database()
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    script_path.chmod(0o755)
    
    print(f"✅ Database update script created: {script_path}")


def create_railway_import_instructions():
    """Create instructions for importing to Railway."""
    instructions_path = EXPORT_DIR / "IMPORT_TO_RAILWAY.md"
    
    content = f'''# Import Database and Images to Railway

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Your Database Stats

- **Transactions:** {{{{transactions}}}}
- **Allocations:** {{{{allocations}}}}
- **Product Images:** {{{{product_images}}}}
- **Total Items:** {{{{total_items}}}}

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
   - ✅ All {{{{total_items}}}} items
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
'''
    
    with open(instructions_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Import instructions created: {instructions_path}")
    
    return instructions_path


def main():
    """Main migration preparation."""
    print("=" * 60)
    print("🚀 Railway Migration Preparation")
    print("=" * 60)
    print()
    
    # Create export directory
    create_export_directory()
    print()
    
    # Get database stats
    print("📊 Database Statistics:")
    stats = get_database_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Backup database
    print("💾 Creating Backup:")
    if not backup_database():
        return
    print()
    
    # Export to SQL
    print("📤 Exporting to SQL:")
    export_database_to_sql()
    print()
    
    # List images
    print("🖼️  Scanning Images:")
    images = list_images()
    if not images:
        print("⚠️  No images found!")
        return
    print()
    
    # Create upload scripts
    print("📝 Creating Migration Scripts:")
    create_cloudinary_upload_script(images)
    create_database_update_script()
    instructions_path = create_railway_import_instructions()
    print()
    
    # Update instructions with stats
    with open(instructions_path, 'r') as f:
        content = f.read()
    
    for key, value in stats.items():
        content = content.replace(f"{{{key}}}", str(value))
    
    with open(instructions_path, 'w') as f:
        f.write(content)
    
    print("=" * 60)
    print("✅ MIGRATION PREPARATION COMPLETE!")
    print("=" * 60)
    print()
    print(f"📁 All files exported to: {EXPORT_DIR.absolute()}")
    print()
    print("📖 Next Steps:")
    print(f"   1. cd {EXPORT_DIR}")
    print(f"   2. Read IMPORT_TO_RAILWAY.md")
    print(f"   3. Follow the steps!")
    print()
    print("🎯 Summary:")
    print(f"   - Database: {stats['total_items']} items ready")
    print(f"   - Images: {len(images)} images to upload")
    print(f"   - Scripts: All created")
    print()


if __name__ == "__main__":
    main()
