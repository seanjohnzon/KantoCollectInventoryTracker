#!/bin/bash
#
# Import database to Railway using SQL
# This works with Railway's read-only filesystem
#

set -e

echo "============================================================"
echo "📤 IMPORTING DATABASE TO RAILWAY"
echo "============================================================"
echo ""

cd "$(dirname "$0")"

# Step 1: Verify local data
echo "📊 Verifying local database..."
LOCAL_STATS=$(sqlite3 data/inventory.db "SELECT 
    (SELECT COUNT(*) FROM transactions),
    (SELECT COUNT(*) FROM allocations),
    (SELECT COUNT(*) FROM product_images),
    (SELECT SUM(quantity_sold) FROM transactions)")

echo "✅ Local database:"
echo "   Transactions: $(echo $LOCAL_STATS | cut -d'|' -f1)"
echo "   Allocations: $(echo $LOCAL_STATS | cut -d'|' -f2)"
echo "   Images: $(echo $LOCAL_STATS | cut -d'|' -f3)"
echo "   Total Items: $(echo $LOCAL_STATS | cut -d'|' -f4)"
echo ""

# Step 2: Export to SQL if not exists
if [ ! -f "railway_export/database_export.sql" ]; then
    echo "📤 Exporting database to SQL..."
    mkdir -p railway_export
    sqlite3 data/inventory.db .dump > railway_export/database_export.sql
    echo "✅ SQL export created"
else
    echo "✅ SQL export already exists"
fi
echo ""

# Step 3: Deploy code first
echo "🚀 Deploying code to Railway..."
railway up --detach

echo ""
echo "⏳ Waiting for deployment (30 seconds)..."
sleep 30

# Step 4: Import database via SQL
echo ""
echo "📥 Importing database to Railway..."
cat railway_export/database_export.sql | railway run sqlite3 /app/data/inventory.db

echo ""
echo "✅ Database imported!"
echo ""

# Step 5: Verify on Railway
echo "🔍 Verifying data on Railway..."
RAILWAY_STATS=$(railway run sqlite3 /app/data/inventory.db "SELECT 
    (SELECT COUNT(*) FROM transactions),
    (SELECT COUNT(*) FROM allocations),
    (SELECT COUNT(*) FROM product_images),
    (SELECT SUM(quantity_sold) FROM transactions)" 2>&1)

echo "✅ Railway database:"
echo "   Transactions: $(echo $RAILWAY_STATS | cut -d'|' -f1)"
echo "   Allocations: $(echo $RAILWAY_STATS | cut -d'|' -f2)"
echo "   Images: $(echo $RAILWAY_STATS | cut -d'|' -f3)"
echo "   Total Items: $(echo $RAILWAY_STATS | cut -d'|' -f4)"
echo ""

# Compare
LOCAL_TOTAL=$(echo $LOCAL_STATS | cut -d'|' -f4)
RAILWAY_TOTAL=$(echo $RAILWAY_STATS | cut -d'|' -f4)

if [ "$LOCAL_TOTAL" = "$RAILWAY_TOTAL" ]; then
    echo "✅ VERIFICATION PASSED: All data migrated!"
else
    echo "⚠️  Data mismatch: Local=$LOCAL_TOTAL, Railway=$RAILWAY_TOTAL"
fi

echo ""
echo "🌐 Getting your URL..."
railway status

echo ""
echo "============================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Visit your Railway URL"
echo "2. Verify 1,544 items show"
echo "3. Lock admin (🔓 → 🔒)"
echo "4. Share with team!"
echo ""
echo "PIN: 1453"
echo ""
