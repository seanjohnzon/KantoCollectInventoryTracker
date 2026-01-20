#!/usr/bin/env python3
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
