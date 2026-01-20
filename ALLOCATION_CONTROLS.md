# Allocation Management Controls

**Date:** January 20, 2026 - 02:15 PST

## Overview

You now have full control to quickly edit, move, and manage allocations directly in the UI without any complex workflows.

## Unallocated Items (Bottom of Dashboard)

### Available Actions:

1. **Edit Qty** - Change the total quantity available for an item
   - Updates the master inventory count
   - Affects what's available to assign

2. **Assign** - Assign items to an owner
   - Opens modal with dropdown (Cihan, Nima, Askar, Kanto)
   - Enter quantity to assign
   - Automatically includes pricing

3. **Delete** - Remove item entirely
   - Deletes ALL transactions for this item
   - Use with caution - cannot be undone

## Owner Views (Cihan, Nima, Askar, Kanto)

### Available Actions on Allocated Items:

1. **Edit Qty** - Change the allocated quantity
   - Example: Change Cihan's 17 blisters to 20
   - Set to 0 to remove allocation
   - Doesn't move items, just changes the count

2. **Move To** - Transfer items to another owner
   - Prompts for destination owner name
   - Type "Unallocated" to remove assignment
   - Moves ALL quantity for that item
   - Examples:
     - "Nima" - moves to Nima
     - "Unallocated" - returns to unallocated

3. **Remove** - Remove allocation entirely
   - Moves item back to Unallocated
   - Preserves inventory count
   - Can be reassigned later

## Quick Workflows

### Scenario 1: Correct an Assigned Quantity
1. Go to owner's view (e.g., Cihan)
2. Find the item
3. Click **Edit Qty**
4. Enter new quantity

### Scenario 2: Move Item Between Owners
1. Go to current owner's view
2. Find the item
3. Click **Move To**
4. Type destination owner name (e.g., "Askar")

### Scenario 3: Reassign Items
1. Go to owner's view
2. Click **Remove** on item
3. Go to Unallocated view
4. Click **Assign** on item
5. Select new owner

### Scenario 4: Add Newly Discovered Items
1. Go to Unallocated view
2. Find item (should show 0 quantity if placeholder)
3. Click **Edit Qty**
4. Enter actual count
5. Click **Assign** to allocate

## Tips

- **All changes are immediate** - No need to save, refresh automatically
- **Pricing follows items** - Unit costs transfer when moving allocations
- **Edit Qty on allocated items** just changes that owner's allocation, not the total inventory
- **Edit Qty on unallocated items** changes the master inventory count
- **Move To is fastest** for transferring items between owners (one step vs remove + reassign)

## Owner Names (Case-Insensitive)

- Cihan
- Nima
- Askar
- Kanto
- Unallocated (special keyword to remove assignments)

---

**All controls work in real-time. Changes are saved immediately to the database.** 🎯
