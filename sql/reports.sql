-- =====================================================================
-- Mamaearth Returns & Growth Intelligence Pipeline
-- Part 1 - Task 3: SQL Business Reports (Queries a through i)
-- File: sql/reports.sql
-- Note: Exact query output is pasted as a comment above each query.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Task 3(a): Order Totals
-- Prompt: Total orders, revenue and average order value (NULL discount = 0%)
-- Note: Use 100.0 instead of 100 to avoid SQLite integer truncation.
--
-- Output:
-- total_orders | total_revenue | avg_order_value
-- 180          | 99860.20      | 554.78
-- ---------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
    ROUND(AVG(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;



-- ---------------------------------------------------------------------
-- Task 3(b): COUNT(*) vs COUNT(col)
-- Prompt: Show how many orders have no rating.
--
-- Output:
-- total_orders | orders_with_rating | missing_ratings
-- 180          | 165                | 15
-- ---------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_orders,
    COUNT(rating) AS orders_with_rating,
    COUNT(*) - COUNT(rating) AS missing_ratings
FROM orders;



-- ---------------------------------------------------------------------
-- Task 3(c): Find Customers with Zero Orders (Two Methods)
-- Prompt: Find customers with zero orders two ways - results must match.
--
-- Method 1: LEFT JOIN
-- Output:
-- customer_id | name
-- C045        | Vihaan
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;


-- Method 2: NOT IN subquery
-- Output:
-- customer_id | name
-- C045        | Vihaan
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE customer_id IS NOT NULL
)
ORDER BY customer_id ASC;



-- ---------------------------------------------------------------------
-- Task 3(d): GROUP BY + HAVING
-- Prompt: Return rate by city, keep only cities above 20%.
--
-- Output:
-- city      | total_orders | returned_orders | return_rate_pct
-- Jaipur    | 19           | 8               | 42.1
-- Lucknow   | 49           | 15              | 30.6
-- Bangalore | 33           | 8               | 24.2
-- ---------------------------------------------------------------------
SELECT 
    c.city,
    COUNT(*) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(AVG(o.returned) * 100.0, 1) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20.0
ORDER BY return_rate_pct DESC, c.city ASC;



-- ---------------------------------------------------------------------
-- Task 3(e): ORDER BY + LIMIT/OFFSET
-- Prompt: Top 5 customers by spend, then ranks 3–5 via OFFSET.
--
-- Query e1: Top 5 customers by total spend
-- Output:
-- customer_id | name    | total_spend
-- C043        | Reyansh | 12920.00
-- C026        | Isha    | 8371.60
-- C008        | Meera   | 4564.60
-- C011        | Arjun   | 4111.00
-- C042        | Sanya   | 3785.00
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;


-- Query e2: Ranks 3 to 5 using LIMIT 3 OFFSET 2
-- Output:
-- customer_id | name  | total_spend
-- C008        | Meera | 4564.60
-- C011        | Arjun | 4111.00
-- C042        | Sanya | 3785.00
-- ---------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;



-- ---------------------------------------------------------------------
-- Task 3(f): Three-Table JOIN
-- Prompt: Order count and revenue by product category.
--
-- Output:
-- category     | order_count | category_revenue
-- Haircare     | 54          | 44956.10
-- Skincare     | 60          | 27346.00
-- Babycare     | 30          | 16805.00
-- PersonalCare | 36          | 10753.10
-- ---------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC, p.category ASC;



-- ---------------------------------------------------------------------
-- Task 3(g): LIKE Pattern Matching
-- Prompt: Customers whose name starts with "A".
--
-- Output:
-- customer_id | name
-- C001        | Aarav
-- C003        | Aditi
-- C004        | Ananya
-- C011        | Arjun
-- C021        | Aryan
-- C030        | Anika
-- C031        | Aditya
-- C036        | Aisha
-- C041        | Ayaan
-- C044        | Aria
-- ---------------------------------------------------------------------
SELECT 
    customer_id,
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id ASC;



-- ---------------------------------------------------------------------
-- Task 3(h): DISTINCT
-- Prompt: Distinct acquisition sources.
--
-- Output:
-- acquisition_source
-- Ad
-- Organic
-- Referral
-- Social
-- ---------------------------------------------------------------------
SELECT DISTINCT 
    acquisition_source
FROM customers
ORDER BY acquisition_source ASC;



-- ---------------------------------------------------------------------
-- Task 3(i): ALTER + UPDATE CASE
-- Prompt: Add loyalty_tier: Gold for tier-1 cities, else Silver.
-- ---------------------------------------------------------------------

-- i1: Add loyalty_tier column
ALTER TABLE customers ADD COLUMN loyalty_tier TEXT;

-- i2: Update values conditionally using CASE
UPDATE customers 
SET loyalty_tier = CASE 
    WHEN city_tier = 1 THEN 'Gold' 
    ELSE 'Silver' 
END;

-- i3: Verification query to confirm tier assignment
-- Output:
-- loyalty_tier | customer_count
-- Gold         | 28
-- Silver       | 17
-- ---------------------------------------------------------------------
SELECT 
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier ASC;
