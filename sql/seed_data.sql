-- =====================================================================
-- Mamaearth Returns & Growth Intelligence Pipeline
-- Part 1 - Task 2: Seed Data Loading Script & Verification
-- File: sql/seed_data.sql
-- =====================================================================

-- Instructions for SQLite CLI:
-- 1. Open SQLite: sqlite3 mamaearth.db
-- 2. Execute schema: .read sql/schema.sql
-- 3. Set CSV mode:   .mode csv
-- 4. Import files (use --skip 1 to skip header row):
--    .import --skip 1 data/customers.csv customers
--    .import --skip 1 data/products.csv products
--    .import --skip 1 data/orders.csv orders
--
-- Alternatively, use the automated helper: python sql/run_sql.py

-- Convert empty string values to NULL so nullable columns reflect true NULLs
UPDATE orders SET discount_pct = NULL WHERE discount_pct = '';
UPDATE orders SET rating = NULL WHERE rating = '';

-- Verification Query: Check imported row counts (Must be 45 / 16 / 180)
-- Expected verification output:
-- table_name | row_count
-- customers  | 45
-- products   | 16
-- orders     | 180

SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;
