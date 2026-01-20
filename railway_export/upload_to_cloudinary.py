#!/usr/bin/env python3
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
IMAGES = [
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Destined Rivals Sleeved Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Portgas.D.Ace (119) (Parallel) - Carrying On His Will (OP13).jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Stellar Crown Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Black Kyurem ex Box.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/The Azure Sea's Seven Booster Pack (OP14).jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Monkey.D.Luffy (118) (Parallel) - Carrying On His Will (OP13).jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Mega Kangaskhan ex Box.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Mega Latias ex Box.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Phantasmal Flames Booster Bundle.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Melmetal ex Box.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Phantasmal Flames Single Pack Blister [Whimsicott].jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Unova Heavy Hitters Premium Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Surging Sparks Elite Trainer Box.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Hydreigon ex & Dragapult ex Premium Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Phantasmal Flames Single Pack Blister [Cottonee].jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Team Rocket’s Moltres ex Ultra-Premium Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/random pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Paldean Fates Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Black Bolt Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/One Piece Card Game Illustration Box Vol. 3 .jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Fall 2025 Collector Chest.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Mega Battle Deck (Mega Diancie ex).jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Phantasmal Flames 3 Pack Blister [Sneasel].jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Armarouge ex Premium Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Prismatic Evolutions Booster Bundle.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Shrouded Fable Booster Bundle.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Mega Heroes Mini Tin.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Phantasmal Flames Elite Trainer Box.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Mega Charizard X ex Ultra Premium Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/White Flare Elite Trainer Box.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Surging Sparks Booster Bundle.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Prismatic Evolutions Premium Figure Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Twilight Masquerade Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Mega Lucario ex Premium Figure Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Mega Venusaur ex Premium Collection.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Journey Together Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/The Azure Sea's Seven Booster Box(OP14).jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Prismatic Evolutions Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Crown Zenith Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Black Bolt Booster Bundle.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Prismatic Evolutions Mini Tin.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Surging Sparks Booster Pack.jpg",
    r"/Users/sahcihansahin/Desktop/pokemon and one piece/Pokemon/Item Pics/Twilight Masquerade Elite Trainer Box.jpg",
]

def upload_images():
    """Upload all images to Cloudinary."""
    url_mapping = {}
    
    print("🚀 Starting upload to Cloudinary...")
    print()
    
    for i, image_path in enumerate(IMAGES, 1):
        try:
            path = Path(image_path)
            if not path.exists():
                print(f"⚠️  Skipping (not found): {path.name}")
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
            print(f"✅ [{i}/{len(IMAGES)}] {path.name}")
            print(f"   URL: {result['secure_url']}")
            
        except Exception as e:
            print(f"❌ Failed: {path.name} - {e}")
    
    print()
    print(f"✅ Uploaded {len(url_mapping)} images")
    
    # Save URL mapping
    import json
    mapping_file = Path("cloudinary_urls.json")
    with open(mapping_file, 'w') as f:
        json.dump(url_mapping, f, indent=2)
    
    print(f"✅ URL mapping saved: {mapping_file}")
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
