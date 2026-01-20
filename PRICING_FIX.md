# Pricing System - Automatic Unit Cost Assignment

**Date:** January 20, 2026 - 01:25 PST

## Issue Fixed

Previously, when items were assigned to owners (either manually via UI or through Excel import), the unit cost was not being automatically populated from the database. This resulted in allocations showing $0.00 for unit cost and total cost.

## Solution Implemented

### 1. Created Centralized Helper Function

Added `get_unit_cost_for_item()` in `app/services/allocation.py`:
- Looks up unit cost from `ProductImage` table
- Returns the correct unit cost for any normalized item name
- Falls back to $0.00 if no pricing data exists

### 2. Updated All Allocation Creation Points

**Manual UI Assignment** (`app/ui.py` - `_handle_assign`):
- Now uses `get_unit_cost_for_item()` helper
- Automatically looks up and applies correct unit cost when assigning

**Excel Import** (`app/services/allocation.py` - `import_allocations_from_excel`):
- Prioritizes database unit costs over Excel costs
- Falls back to Excel cost if database cost is $0.00
- Ensures consistency with master pricing data

### 3. Fixed Existing Allocations

Created migration script (`/tmp/fix_all_allocations.py`) to:
- Scan all existing allocations
- Update any with missing/incorrect unit costs
- Use centralized helper for consistency

## Benefits

✅ **Automatic**: Unit costs are always pulled from the master pricing database  
✅ **Consistent**: Single source of truth for all pricing  
✅ **Future-proof**: Any new allocation method will automatically get correct pricing  
✅ **Maintainable**: One helper function to update if pricing logic changes  

## Testing Verification

Tested with:
- Manual assignment via UI: ✅ Gets correct unit cost ($5.29 for Black Bolt pack)
- Excel import: ✅ Prioritizes database cost over Excel cost
- Existing allocations: ✅ Can be batch-updated with correct costs

## Files Modified

1. `app/services/allocation.py`:
   - Added `get_unit_cost_for_item()` helper function
   - Updated `import_allocations_from_excel()` to use helper

2. `app/ui.py`:
   - Updated `_handle_assign()` to use helper
   - Removed duplicate unit cost lookup logic

## Example Output

```
Assignment: Phantasmal Flames Sleeved Booster Pack
Owner: Cihan
Quantity: 150
Unit Cost: $5.29 (automatically fetched)
Total Cost: $793.50 (automatically calculated)
```

---

**All allocations now automatically include correct pricing data! 🎯**
