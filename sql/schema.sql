-- =====================================================================
-- Mamaearth Returns & Growth Intelligence Pipeline
-- Part 1 - Task 1: Relational Schema Definition
-- File: sql/schema.sql
-- =====================================================================

-- Enforce foreign key constraints in SQLite
PRAGMA foreign_keys = ON;

-- Drop existing tables to ensure the script is re-runnable
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ---------------------------------------------------------------------
-- Table: customers
-- Description: Stores customer profile, location tier, and acquisition data
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    customer_id         TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    city                TEXT NOT NULL,
    city_tier           INTEGER NOT NULL,
    signup_date         TEXT NOT NULL,
    acquisition_source  TEXT NOT NULL
);

-- ---------------------------------------------------------------------
-- Table: products
-- Description: Stores product catalog, categories, and unit prices in INR
-- ---------------------------------------------------------------------
CREATE TABLE products (
    product_id          TEXT PRIMARY KEY,
    product_name        TEXT NOT NULL,
    category            TEXT NOT NULL,
    price               REAL NOT NULL
);

-- ---------------------------------------------------------------------
-- Table: orders
-- Description: Stores transactional orders with quantity, discount,
--              payment method, customer rating, and return status.
-- Note: discount_pct and rating stay nullable as per specifications.
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id            TEXT PRIMARY KEY,
    customer_id         TEXT NOT NULL,
    product_id          TEXT NOT NULL,
    order_date          TEXT NOT NULL,
    quantity            INTEGER NOT NULL,
    discount_pct        INTEGER,           -- Stays nullable for orders without discounts
    payment_method      TEXT NOT NULL,
    rating              INTEGER,           -- Stays nullable for unrated orders
    returned            INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);
