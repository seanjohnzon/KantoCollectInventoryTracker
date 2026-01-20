# Admin Lock Protection

**Date:** January 20, 2026 - 04:30 PST  
**PIN:** 1453

## Overview

Admin mode can now be locked to prevent accidental edits. When locked, all edit controls are hidden and the interface becomes view-only.

## How to Lock Admin Mode

1. Look at top-right of navigation
2. Click **🔓 Admin Enabled** button
3. Confirm you want to lock
4. ✅ Admin mode is now locked

## How to Unlock Admin Mode

1. Click **🔒 Admin Locked** button
2. Enter PIN: **1453**
3. Click OK
4. ✅ Admin mode is unlocked

## What Gets Hidden When Locked

### ❌ All Edit Controls Hidden:
- ✏️ Name edit buttons
- ✏️ Price edit buttons  
- 🖼️ Image edit buttons
- **Qty** buttons
- **Assign** buttons
- **Delete** buttons
- ⚙️ **Admin** tab

### ✅ View-Only Access:
- Can view all inventory
- Can see allocations
- Can browse all tabs
- Can search items
- **Cannot modify anything**
- **Items with 0 quantity are hidden** (cleaner view for users)

## Smart Filtering

### 0 Quantity Items

**When Admin is LOCKED:**
- Items with 0 quantity are automatically hidden
- Shows only items with actual inventory
- Cleaner view for non-admin users
- No placeholder items visible

**When Admin is UNLOCKED:**
- ALL items shown (including 0 quantity)
- Placeholder items visible
- Can edit and manage everything
- Full inventory view

This makes the locked view perfect for showing to team members or customers - they only see what's actually available!

## Use Cases

### When to Lock:
- Reviewing inventory with others
- Presenting data to team
- Preventing accidental changes
- When letting others browse
- After making changes (to prevent mistakes)
- **Showing clean inventory view (no 0 qty items)**

### When to Unlock:
- Need to edit names/prices
- Need to assign items
- Need to add new items
- Need to change quantities
- Need to update images
- **Need to see ALL items including placeholders**

## Button States

**🔓 Admin Enabled** (Green)
- All controls visible
- Full editing access
- Admin tab available
- Click to lock

**🔒 Admin Locked** (Red)
- All controls hidden
- View-only mode
- Admin tab hidden
- Click + enter PIN to unlock

## PIN Security

**PIN:** 1453  
**Storage:** Browser localStorage  
**Scope:** Per browser/device  

If someone clears their browser data, admin mode resets to enabled (will need to lock again).

## Example Workflow

### Daily Use:
1. Start with admin **unlocked** (default)
2. Make your edits/assignments
3. When done, **lock** admin mode
4. Share screen or let team browse
5. **Unlock** when you need to edit again

### Team Review:
1. **Lock** admin before meeting
2. Show inventory to team
3. No risk of accidental clicks
4. **Unlock** after meeting

## Troubleshooting

**Forgot PIN?**
- PIN is: **1453**
- Written in this document
- Stored in code

**Admin button not showing?**
- Refresh browser (Cmd+R)
- Check you're on http://localhost:5173
- Admin mode might be locked

**Can't click anything?**
- Admin mode is locked
- Click 🔒 button
- Enter PIN 1453

**Changes not saving?**
- Admin mode might be locked
- Check button shows 🔓 (unlocked)
- If locked, unlock with PIN

## Technical Details

- Uses browser localStorage
- CSS hides elements with `.admin-control` class
- JavaScript toggles `admin-disabled` class on body
- PIN is checked client-side
- State persists across page refreshes

---

**Admin mode gives you full control when unlocked, complete protection when locked!** 🔐
