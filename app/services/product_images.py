"""Helper script to add product images to the database."""

from __future__ import annotations

from pathlib import Path
from app.db import get_engine, get_session_factory
from app.models import ProductImage
from app.services.reporting import get_item_counts
from sqlalchemy import select


def add_product_image(
    session,
    normalized_item_name: str,
    image_url: str,
    description: str = None
) -> None:
    """
    Add or update a product image.
    
    Args:
        session: Database session
        normalized_item_name: The normalized item name (from inventory)
        image_url: URL or path to the product image
        description: Optional description
    """
    # Check if image already exists
    existing = session.execute(
        select(ProductImage).where(ProductImage.normalized_item_name == normalized_item_name)
    ).scalar()
    
    if existing:
        existing.image_url = image_url
        existing.thumbnail_url = image_url  # Same for now, can add thumbnail generation later
        if description:
            existing.description = description
        print(f"✓ Updated image for: {normalized_item_name}")
    else:
        new_image = ProductImage(
            normalized_item_name=normalized_item_name,
            image_url=image_url,
            thumbnail_url=image_url,
            description=description
        )
        session.add(new_image)
        print(f"✓ Added image for: {normalized_item_name}")
    
    session.commit()


def list_products_without_images(session) -> list[dict]:
    """
    List all products that don't have images yet.
    
    Args:
        session: Database session
        
    Returns:
        List of products without images
    """
    items = get_item_counts(
        session=session,
        group_by_buyer=False,
        include_non_sales=True,
        title_match="custom",
    )
    
    # Get existing images
    existing_images = session.execute(
        select(ProductImage.normalized_item_name)
    ).scalars().all()
    
    existing_set = set(existing_images)
    
    # Filter items without images
    without_images = [
        item for item in items
        if item.get('normalized_name') not in existing_set
    ]
    
    return without_images


if __name__ == "__main__":
    db_path = Path("data/inventory.db")
    engine = get_engine(f"sqlite+pysqlite:///{db_path}")
    session_factory = get_session_factory(engine)
    
    with session_factory() as session:
        # Example usage - list products without images
        products = list_products_without_images(session)
        
        print("="*80)
        print(f"PRODUCTS WITHOUT IMAGES ({len(products)} total)")
        print("="*80)
        print()
        
        # Group by set
        from collections import defaultdict
        by_set = defaultdict(list)
        for item in products:
            set_name = item.get('set_name', 'Other')
            by_set[set_name].append(item)
        
        for set_name in sorted(by_set.keys()):
            items = by_set[set_name]
            print(f"\n{set_name}:")
            for item in sorted(items, key=lambda x: -x['quantity_sold'])[:5]:
                normalized = item.get('normalized_name', item['listing_title'].lower())
                print(f"  - {item['quantity_sold']:>3}  {item['listing_title']}")
                print(f"       normalized: '{normalized}'")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")
        
        print()
        print("="*80)
        print("TO ADD AN IMAGE:")
        print("="*80)
        print()
        print("from app.services.product_images import add_product_image")
        print()
        print("add_product_image(")
        print("    session=session,")
        print("    normalized_item_name='phantasmal flames sleeve',")
        print("    image_url='https://example.com/image.jpg',")
        print("    description='Phantasmal Flames Single Pack'")
        print(")")
