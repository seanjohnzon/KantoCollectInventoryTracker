#!/usr/bin/env python3
"""
Update database with ImageKit URLs.

Since you've already uploaded images to ImageKit, this script will:
1. List all local images
2. Generate ImageKit URLs for each
3. Update the database

Usage:
    python3 update_imagekit_urls.py
"""

import sqlite3
from pathlib import Path
from urllib.parse import quote
import unicodedata

# Your ImageKit configuration
# Format: https://ik.imagekit.io/{account}/{folder}
# Your account: homecraft
# Your folder: Item Pics
IMAGEKIT_BASE_URL = "https://ik.imagekit.io/homecraft/Item%20Pics"

# Local images directory
LOCAL_IMAGES = Path("/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics")

# Database path
DB_PATH = Path("../data/inventory.db")


def normalize_path(path_str: str) -> str:
    """Normalize Unicode characters in path."""
    return unicodedata.normalize('NFC', str(path_str))


def get_imagekit_url(filename: str) -> str:
    """
    Generate ImageKit URL for a given filename.
    
    ImageKit URLs follow the pattern:
    https://ik.imagekit.io/account/path/to/file.ext
    """
    # URL-encode the filename to handle special characters and spaces
    encoded_filename = quote(filename)
    return f"{IMAGEKIT_BASE_URL}/{encoded_filename}"


def list_local_images():
    """List all images in the local directory."""
    if not LOCAL_IMAGES.exists():
        print(f"❌ Images directory not found: {LOCAL_IMAGES}")
        return []
    
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        images.extend(LOCAL_IMAGES.glob(ext))
    
    print(f"✅ Found {len(images)} local images")
    return images


def update_database():
    """Update product_images table with ImageKit URLs."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    # Get local images
    local_images = list_local_images()
    if not local_images:
        return
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current product images
    cursor.execute("SELECT id, normalized_item_name, image_url FROM product_images")
    rows = cursor.fetchall()
    
    updated = 0
    not_found = []
    
    for row_id, normalized_name, old_url in rows:
        if not old_url or not old_url.startswith('/Users/'):
            continue  # Skip if not local path
        
        # Normalize old URL for matching
        old_url_normalized = normalize_path(old_url)
        old_path = Path(old_url_normalized)
        old_filename = old_path.name
        
        # Find matching local image
        matched = False
        for local_image in local_images:
            local_filename = local_image.name
            local_filename_normalized = normalize_path(local_filename)
            
            if local_filename_normalized == normalize_path(old_filename):
                # Generate ImageKit URL
                imagekit_url = get_imagekit_url(local_filename)
                
                # Update database
                cursor.execute(
                    "UPDATE product_images SET image_url = ? WHERE id = ?",
                    (imagekit_url, row_id)
                )
                
                updated += 1
                print(f"✅ Updated: {normalized_name}")
                print(f"   {imagekit_url}")
                matched = True
                break
        
        if not matched:
            not_found.append(normalized_name)
    
    conn.commit()
    conn.close()
    
    print()
    print(f"✅ Updated {updated} image URLs")
    
    if not_found:
        print()
        print(f"⚠️  {len(not_found)} images not found:")
        for name in not_found:
            print(f"   - {name}")
    
    print()
    print("✅ Database ready for Railway!")


def main():
    """Main function."""
    print("=" * 60)
    print("🚀 ImageKit URL Update")
    print("=" * 60)
    print()
    print(f"📁 Local images: {LOCAL_IMAGES}")
    print(f"🗄️  Database: {DB_PATH}")
    print(f"🌐 ImageKit base: {IMAGEKIT_BASE_URL}")
    print()
    
    # Check if base URL needs to be updated
    if "homecraft" not in IMAGEKIT_BASE_URL:
        print("⚠️  Please update IMAGEKIT_BASE_URL in this script!")
        print()
        print("To find your ImageKit base URL:")
        print("1. Go to your ImageKit folder")
        print("2. Click on any image's 'Copy URL' button")
        print("3. Paste the URL here")
        print("4. Remove the filename from the end")
        print()
        print("Example:")
        print("Full URL: https://ik.imagekit.io/homecraft/Item%20Pics/image.jpg")
        print("Base URL: https://ik.imagekit.io/homecraft/Item%20Pics")
        print()
        return
    
    # Update database
    update_database()


if __name__ == "__main__":
    main()
