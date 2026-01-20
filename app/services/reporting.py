"""Reporting service for sold item counts."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Transaction


def _apply_custom_rules(title: str) -> str:
    """
    Apply custom normalization rules for known item patterns.

    Args:
        title (str): Raw title.

    Returns:
        str: Normalized title after applying rules.
    """
    lowered = title.lower()
    
    # Reason: Giveaways and random packs are all the same category
    if any(x in lowered for x in ["giv", "giveaway", "random asian pack", "random pokemon pack", "asian pokemon pack", "free"]):
        return "random asian pack"
    
    # Strip event prefixes (they don't affect the product)
    for prefix in ["friday fiesta", "friday surprise", "new years spin out", "kanto christmas gifts"]:
        if prefix in lowered:
            lowered = lowered.replace(prefix, "").strip()
            lowered = re.sub(r"^[\s\-]+", "", lowered)
    
    # Extract product type
    product_type = None
    if "elite trainer box" in lowered or "etb" in lowered:
        product_type = "etb"
    elif "booster bundle" in lowered:
        product_type = "booster bundle"
    elif "premium collection" in lowered:
        product_type = "premium collection"
    elif "ultra premium collection" in lowered or "upc" in lowered:
        product_type = "upc"
    elif "plush collection" in lowered:
        product_type = "plush collection"
    elif "figure collection" in lowered:
        product_type = "figure collection"
    elif "battle deck" in lowered:
        product_type = "battle deck"
    elif "blister" in lowered:
        product_type = "blister"
    elif "sleeve" in lowered or "sleeved" in lowered:
        product_type = "sleeve"
    elif "poke ball tin" in lowered or "pokeball tin" in lowered:
        product_type = "poke ball tin"
    elif "pack" in lowered:
        # Note: This will combine single packs, 2 packs, 5 packs, etc. into one entry
        # The quantities are already multiplied during ingestion
        product_type = "pack"
    
    # Extract set/item name by removing product-type keywords and numbers
    clean = re.sub(r"\b(1x?|2x?|pack|single|sleeve|sleeved|booster|blister|elite|trainer|box|etb|bundle|premium|ultra|collection|figure|plush|battle|deck|poke|ball|tin|upc)\b", " ", lowered)
    clean = re.sub(r"#\d+", "", clean)  # Remove #numbers
    clean = re.sub(r"[^\w\s]", " ", clean)  # Remove special chars
    clean = " ".join(clean.split()).strip()
    
    # Combine set name + product type
    if product_type and clean:
        return f"{clean} {product_type}"
    elif product_type:
        return product_type
    elif clean:
        return clean
    
    return lowered


def _extract_set_name(title: str) -> str:
    """
    Extract the set/product line name from a normalized title.

    Args:
        title (str): Normalized title.

    Returns:
        str: Set name or "Other".
    """
    lowered = title.lower()
    
    # Special categories
    if "random asian pack" in lowered or "giv" in lowered:
        return "Giveaways"
    
    # Pokemon sets
    if "phantasmal flames" in lowered or "phantasmal" in lowered:
        return "Phantasmal Flames"
    if "destined rivals" in lowered or "destined rival" in lowered:
        return "Destined Rivals"
    if "prismatic evolutions" in lowered or "prismatic" in lowered:
        return "Prismatic Evolutions"
    if "mega evolutions" in lowered or "mega evolution" in lowered or "mega heroes" in lowered:
        return "Mega Evolutions"
    if "crown zenith" in lowered:
        return "Crown Zenith"
    if "paldean fates" in lowered or "paldaen fates" in lowered:
        return "Paldean Fates"
    if "surging sparks" in lowered:
        return "Surging Sparks"
    if "twilight masquerade" in lowered or "twilight masqerade" in lowered:
        return "Twilight Masquerade"
    if "stellar crown" in lowered:
        return "Stellar Crown"
    if "shrouded fables" in lowered:
        return "Shrouded Fables"
    if "journey together" in lowered:
        return "Journey Together"
    if "black bolt" in lowered:
        return "Black Bolt"
    if "white flare" in lowered:
        return "White Flare"
    if "trick or treat" in lowered:
        return "Trick or Treat"
    
    # One Piece sets
    if "one piece" in lowered or "op " in lowered or "op14" in lowered or "op13" in lowered or "op12" in lowered or "op11" in lowered or "op08" in lowered or "op 08" in lowered:
        if "azure sea" in lowered:
            return "One Piece - Azure Sea"
        elif "op 14" in lowered or "op14" in lowered:
            return "One Piece - OP14"
        elif "op 13" in lowered or "op13" in lowered:
            return "One Piece - OP13"
        elif "op 12" in lowered or "op12" in lowered:
            return "One Piece - OP12"
        elif "op 11" in lowered or "op11" in lowered:
            return "One Piece - OP11"
        elif "op 08" in lowered or "op08" in lowered or "op 8" in lowered:
            return "One Piece - OP08"
        return "One Piece"
    
    # Special products/collections
    if "plush collection" in lowered:
        return "Plush Collections"
    if "figure collection" in lowered:
        return "Figure Collections"
    if "premium collection" in lowered or "upc" in lowered:
        if "charizard" in lowered:
            return "Charizard Collections"
        if "venusaur" in lowered:
            return "Venusaur Collections"
        if "moltres" in lowered:
            return "Moltres Collections"
        return "Premium Collections"
    if "battle deck" in lowered:
        return "Battle Decks"
    if "poke ball tin" in lowered or "pokeball tin" in lowered:
        return "Poke Ball Tins"
    if "lunch chest" in lowered or "collector chest" in lowered:
        return "Storage/Chests"
    if "single" in lowered or "card" in lowered:
        return "Singles/Cards"
    if "unova heavy hitters" in lowered:
        return "Unova Heavy Hitters"
    
    return "Other"


def _format_display_title(normalized: str, mode: str) -> str:
    """
    Format a display title for normalized values.

    Args:
        normalized (str): Normalized title.
        mode (str): Normalization mode.

    Returns:
        str: Display title for reports.
    """
    if mode != "custom":
        return normalized
    if normalized == "random asian pack":
        return "Random Asian Pack"
    
    # Properly capitalize common acronyms
    result = normalized.title()
    result = result.replace("Etb", "ETB")
    result = result.replace("Upc", "UPC")
    return result


def _extract_pack_multiplier_for_display(title: str) -> str:
    """
    Extract pack multiplier suffix for display name (e.g., "2x Pack", "5x").
    Only extracts multipliers, not product names like "3 Pack Blister".
    Ignores # numbers (shipping identifiers).
    
    Args:
        title (str): Raw listing title.
        
    Returns:
        str: Pack multiplier suffix (e.g., " - 2x Pack", " - 5x") or empty string.
    """
    import re
    lowered = title.lower()
    
    # Skip product names with "blister" - these are product types, not multipliers
    if "blister" in lowered:
        return ""
    
    # Match patterns like "2x Pack", "5x Pack", "2x", "5x"
    match = re.search(r'\b(\d+)x\s*pack\b', lowered)
    if match:
        num = match.group(1)
        return f" - {num}x Pack"
    
    match = re.search(r'\b(\d+)x\b', lowered)
    if match:
        num = match.group(1)
        return f" - {num}x"
    
    # Match patterns like "packs x 5", "pack x 3"
    match = re.search(r'\bpacks?\s*x\s*(\d+)\b', lowered)
    if match:
        num = match.group(1)
        return f" - {num}x Pack"
    
    return ""


def normalize_title(title: str, mode: str) -> str:
    """
    Normalize listing titles for grouping.

    Args:
        title (str): Raw listing title.
        mode (str): Normalization mode: exact, case_insensitive, or aggressive.

    Returns:
        str: Normalized title.
    """
    if mode == "exact":
        return title
    cleaned = " ".join(title.strip().split()).lower()
    if mode == "case_insensitive":
        return cleaned
    if mode in {"aggressive", "custom"}:
        normalized = (
            unicodedata.normalize("NFKD", cleaned).encode("ascii", "ignore").decode("ascii")
        )
        normalized = re.sub(r"[^a-z0-9#]+", " ", normalized)
        normalized = " ".join(normalized.split())
        normalized = _apply_custom_rules(normalized)
        normalized = re.sub(r"\s+#\d+$", "", normalized)
        return normalized
    return cleaned


def get_item_counts(
    session: Session,
    group_by_buyer: bool = False,
    include_non_sales: bool = False,
    title_match: str = "exact",
) -> list[dict[str, str | int | None]]:
    """
    Retrieve aggregated item counts.

    Args:
        session (Session): SQLAlchemy session.
        group_by_buyer (bool): Whether to group counts by buyer name.
        include_non_sales (bool): Whether to include giveaways or non-sales.
        title_match (str): How to match titles (exact, case_insensitive, aggressive).

    Returns:
        list[dict[str, str | int | None]]: Aggregated results.
    """
    if title_match not in {"exact", "case_insensitive", "aggressive", "custom"}:
        title_match = "exact"

    if title_match == "exact":
        columns = [
            Transaction.listing_title.label("listing_title"),
            func.sum(Transaction.quantity_sold).label("quantity_sold"),
        ]
        if group_by_buyer:
            columns.append(Transaction.buyer_name.label("buyer_name"))

        query = select(*columns)
        if not include_non_sales:
            query = query.where(Transaction.is_sale.is_(True))

        group_by_columns = [Transaction.listing_title]
        if group_by_buyer:
            group_by_columns.append(Transaction.buyer_name)

        query = query.group_by(*group_by_columns).order_by(Transaction.listing_title)
        results = session.execute(query).mappings().all()
        return [dict(result) for result in results]

    query = select(
        Transaction.listing_title,
        Transaction.buyer_name,
        Transaction.quantity_sold,
    )
    if not include_non_sales:
        query = query.where(Transaction.is_sale.is_(True))

    rows = session.execute(query).all()
    counts: Counter[tuple[str, str | None]] = Counter()
    title_variants: defaultdict[str, Counter[str]] = defaultdict(Counter)
    # Track original titles for pack multiplier extraction
    original_titles: defaultdict[str, str] = defaultdict(str)

    for title, buyer, quantity in rows:
        normalized = normalize_title(title, title_match)
        key = (normalized, buyer if group_by_buyer else None)
        counts[key] += int(quantity)
        title_variants[normalized][title] += int(quantity)
        # Store the most common original title for this normalized name
        if not original_titles[normalized]:
            original_titles[normalized] = title

    results: list[dict[str, str | int | None]] = []
    for (normalized, buyer), quantity in counts.items():
        display_title = title_variants[normalized].most_common(1)[0][0]
        if title_match in {"case_insensitive", "aggressive", "custom"}:
            display_title = _format_display_title(normalized, title_match)
        
        # Extract set name
        set_name = _extract_set_name(normalized) if title_match == "custom" else None
        
        # Get image URL, display name, and unit cost if available
        from app.models import ProductImage
        image_data = session.execute(
            select(ProductImage.image_url, ProductImage.description, ProductImage.unit_cost)
            .where(ProductImage.normalized_item_name == normalized)
        ).first()
        
        # Use the clean name from image description if available
        # Otherwise use formatted title + pack multiplier suffix
        if image_data and image_data[1]:  # description exists (has image)
            display_title = image_data[1]
        else:  # NO image - add pack multiplier to display name
            if title_match in {"case_insensitive", "aggressive", "custom"}:
                display_title = _format_display_title(normalized, title_match)
            # Add pack multiplier suffix for items without images
            original_title = original_titles.get(normalized, "")
            pack_suffix = _extract_pack_multiplier_for_display(original_title)
            display_title += pack_suffix
        
        results.append(
            {
                "listing_title": display_title,
                "quantity_sold": int(quantity),
                "buyer_name": buyer if group_by_buyer else None,
                "set_name": set_name,
                "image_url": image_data[0] if image_data else None,
                "unit_cost": float(image_data[2]) if image_data and len(image_data) > 2 else 0.00,
                "normalized_name": normalized,
            }
        )
    results.sort(key=lambda item: (item.get("set_name") or "ZZZ", item["listing_title"]))
    return results
