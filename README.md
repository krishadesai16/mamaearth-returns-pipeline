# Mamaearth Returns & Growth Intelligence Pipeline
**Capstone Project — Data Analytics with AI & Gen AI**  
*E&ICT Academy, IIT Roorkee*  
**Student Name:** Krisha Desai  
**Submission Date:** October 2026  

---

## 📌 Executive Summary & Problem Statement

As a Data Analyst on Mamaearth's Growth Analytics team, this project investigates whether product returns are eroding operating margins across order subsets and uncovers the true organic revenue trajectory after resolving data anomalies.

### Core Business Questions Answered:
1. **Where are returns really coming from?**  
   Returns are heavily concentrated in **Cash on Delivery (COD)** orders, which experience a **44.4% return rate** (compared to **14.7% for Card** and **18.9% for UPI**). The single highest-risk customer cohort is **COD orders in Tier-2 cities**, which suffers an alarming **54.5% return rate**.
2. **What is the true revenue picture once data is cleaned?**  
   - **Part 1 Raw Booked Revenue:** `INR 99,860.20` across 180 raw orders.  
   - **Part 2 Cleaned Booked Revenue:** `INR 97,358.30` across 175 legitimate orders.  
   - **Reconciliation Variance:** Exactly `INR 2,501.90`, 100% accounted for by 5 double-submitted duplicate orders.  
   - **True Organic Peak:** January 2026 was artificially inflated by two bulk wholesale orders (`INR 29,582.10` apparent vs `INR 11,637.10` corrected). Removing bulk outliers reveals **March 2026** as the true organic peak month at **`INR 20,318.90`**.

---

## 🏛️ Pipeline Architecture & Repository Layout

The project follows a strict three-layer architecture where **no layer reports a number it did not compute itself or receive directly from the layer before it** (The Golden Rule).

```
<repo>/
├── README.md                           # Documentation, run order, and business findings
├── requirements.txt                   # Environment dependencies
├── sql/
│   ├── schema.sql                     # SQLite DDL with PK, FK, NOT NULL, DEFAULT
│   ├── seed_data.sql                   # Re-runnable seed script with NULL conversions
│   ├── reports.sql                    # 9 business queries (a–i) with outputs as comments
│   └── run_sql.py                     # Automated Python runner for SQLite verification
├── data/
│   ├── customers.csv                  # 45 customer profile records (never hand-edited)
│   ├── products.csv                   # 16 catalog items with unit prices in INR
│   └── orders.csv                     # 180 raw transactional order rows
├── analysis/
│   ├── clean_and_eda.py               # 10 pandas tasks, reconciliation & findings exporter
│   ├── visualize.py                   # Automated chart generator for visualizations/
│   └── generated/                     # Exported intermediate tables for plotting
├── visualizations/
│   ├── return_rate_by_payment.png     # Publication-grade chart of payment return rates
│   └── monthly_revenue_trend.png      # Apparent vs. outlier-corrected monthly revenue trend
└── narrator/
    ├── findings.json                  # Programmatically written JSON of verified metrics
    ├── generate_narrative.py          # Gemini API caller, error handling & offline fallback
    └── sample_output.txt              # Verified executive SCR narrative output
```

---

## 🚀 Quickstart & Reproduction Guide

To reproduce every number and chart top to bottom, execute the following steps in order:

### 1. Environment Setup
Clone this repository and install the lightweight requirements:
```bash
git clone https://github.com/krishadesai16/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

### 2. Step 1: SQL Relational Layer & Reporting (Part 1)
Execute the complete database build, CSV seeding, and run all 9 business queries:
```bash
python sql/run_sql.py
```
*(Or use the SQLite CLI directly: `sqlite3 mamaearth.db < sql/schema.sql`, import data per `sql/seed_data.sql`, and execute `sql/reports.sql`.)*

### 3. Step 2: Python Data Wrangling & EDA (Part 2)
Run the automated cleaning and exploratory analysis pipeline:
```bash
python analysis/clean_and_eda.py
```
This loads raw CSVs, cleans casing, drops duplicates, imputes missing values, checks IQR outliers, tests hypotheses, reconciles revenue, and automatically exports `narrator/findings.json`.

### 4. Step 3: Generate Visualizations
Generate both publication-grade figures saved to `visualizations/`:
```bash
python analysis/visualize.py
```

### 5. Step 4: GenAI Insight Narrator (Part 3)
Run the executive SCR business narrator:
```bash
# Offline deterministic mode (zero API spend, works with no network or key):
python narrator/generate_narrative.py --offline

# Or with your Google AI Studio free API key:
set GEMINI_API_KEY=your_free_api_key_here
python narrator/generate_narrative.py
```
Both modes validate the output against all 5 key numeric benchmarks and save the narrative to `narrator/sample_output.txt`.

---

## 📊 Detailed Technical & Business Walkthrough

### Part 1: SQL Relational Layer (`sql/`)

- **Task 1 — Schema (`sql/schema.sql`):**  
  Defined `customers`, `products`, and `orders` tables with rigorous relational integrity:
  - `customer_id` and `product_id` enforced as primary keys and foreign keys.
  - `discount_pct` and `rating` maintained as nullable columns.
  - `returned` defaulted to `0`.
- **Task 2 — Seed Data (`sql/seed_data.sql`):**  
  Loaded 45 customers, 16 products, and 180 raw orders. Converted empty strings to SQL `NULL` so nullable fields are preserved accurately.
- **Task 3 — The Nine SQL Reports (`sql/reports.sql`):**
  - **a) Order Totals:** Total Orders = `180`, Total Revenue = `INR 99,860.20`, Average Order Value = `INR 554.78`. *(Used `100.0` to avoid SQLite integer division truncation).*
  - **b) Rating Completeness:** Total Orders = `180`, Rated Orders = `165`, Missing Ratings = `15`.
  - **c) Zero-Order Customers:** Identified customer `C045 | Vihaan` using both `LEFT JOIN ... WHERE o.order_id IS NULL` and `NOT IN (SELECT customer_id FROM orders)`. Both methods match identically.
  - **d) City Return Rates (>20%):** Jaipur (`42.1%`, 8/19), Lucknow (`30.6%`, 15/49), Bangalore (`24.2%`, 8/33).
  - **e) Spend Ranking & Pagination:** Top spenders identified: `C043` (`INR 12,920.00`), `C026` (`INR 8,371.60`), `C008` (`INR 4,564.60`), `C011` (`INR 4,111.00`), `C042` (`INR 3,785.00`). Query e2 applies `LIMIT 3 OFFSET 2` to isolate ranks 3–5 (`C008`, `C011`, `C042`).
  - **f) Product Category Contribution:** Haircare leads in revenue (`INR 44,956.10`, 54 orders), followed by Skincare (`INR 27,346.00`, 60 orders), Babycare (`INR 16,805.00`, 30 orders), and PersonalCare (`INR 10,753.10`, 36 orders).
  - **g) Customers Starting with 'A':** 10 customers retrieved (`Aarav`, `Aditi`, `Ananya`, `Arjun`, `Aryan`, `Anika`, `Aditya`, `Aisha`, `Ayaan`, `Aria`).
  - **h) Acquisition Channels:** Distinct sources identified: `Ad`, `Organic`, `Referral`, `Social`.
  - **i) Loyalty Tiering:** Altered table and populated `loyalty_tier` (`Gold` for Tier-1 cities, `Silver` for others): `Gold` = 28 customers, `Silver` = 17 customers.

---

### Part 2: Python Data Wrangling & EDA (`analysis/`)

- **Task 1 — Inspection:** Confirmed raw orders shape `(180, 9)`, customers `(45, 6)`, products `(16, 4)`.
- **Task 2 — Casing Standardization:** Standardized 7 messy raw payment representations (`['upi', 'UPI', 'COD', 'Card', 'cod', 'CARD', 'card']`) into 3 consistent categories: `CARD` (70), `COD` (55), and `UPI` (55).
- **Task 3 — Deduplication:** Detected 5 double-submitted duplicate records on the natural business key (`['customer_id', 'product_id', 'order_date', 'quantity', 'discount_pct', 'payment_method', 'rating', 'returned']`). Dropped duplicate IDs: `['O0176', 'O0177', 'O0178', 'O0179', 'O0180']`. Validated clean orders shape: `(175, 9)`.
- **Task 4 — Missing Value Imputation:** Imputed 12 missing `discount_pct` values with `0.0`, and 15 missing `rating` values with the sample median (`3.0`).
- **Task 5 — Financial Reconciliation:**
  - Part 1 Raw Total Revenue: `INR 99,860.20`
  - Part 2 Cleaned Total Revenue: `INR 97,358.30`
  - Reconciliation Delta: `INR 2,501.90`
  - *Proof:* The sum of values of the 5 dropped duplicate orders is exactly `INR 2,501.90`, providing 100% mathematical reconciliation.
- **Task 6 — Quantity Outlier Analysis (IQR Rule):**
  - Q1 = 1.0, Q3 = 2.0, IQR = 1.0, Upper Bound = `3.5`.
  - Identified 2 bulk wholesale orders: `O0011` (Qty = 25, Value = `INR 7,475.00`) and `O0098` (Qty = 30, Value = `INR 10,470.00`).
  - *Per ground rules, these rows were flagged with `is_outlier=True` and NOT dropped.*
- **Task 7 — COD Return Hypothesis Testing:**
  - *Hypothesis:* "COD orders suffer from significantly higher return rates than prepaid digital payment methods."
  - *Results:* COD = **`44.4%`** (24/54), UPI = **`18.9%`** (10/53), CARD = **`14.7%`** (10/68).
  - *Verdict:* **CONFIRMED / SUPPORTED.** COD returns are more than triple Card and more than double UPI.
- **Task 8 — Multi-Level Risk Segmentation:**
  - Cross-tabulated `payment_method` × `city_tier`.
  - **Highest-Risk Segment:** **COD in Tier-2 Cities** with a **`54.5%` return rate** (12 returns out of 22 orders).
- **Task 9 — Correlation Matrix:**
  - Quantity vs. Order Value: `r = +0.976` (Strong)
  - Discount Pct vs. Order Value: `r = -0.213` (Weak)
  - Rating vs. Returned: `r = -0.101` (Negligible)
  - Discount Pct vs. Returned: `r = -0.088` (Negligible)
  - Price vs. Order Value: `r = +0.158` (Negligible)
- **Task 10 — Outlier-Corrected Monthly Trend:**
  - January apparent revenue of `INR 29,582.10` fell to `INR 11,637.10` once bulk outliers were separated.
  - **True Organic Peak:** **March 2026** at **`INR 20,318.90`**.
- **Task 11 — Visualizations:** Created `return_rate_by_payment.png` and `monthly_revenue_trend.png`.

---

### Part 3: GenAI Insight Narrator (`narrator/`)

- **Task 1 — Structured JSON (`findings.json`):** Programmatically exported from `clean_and_eda.py` ensuring zero human drift or hand-entered numbers.
- **Task 2 — Dynamic Prompt Construction:** Built directly from `findings.json` with an explicit executive role prompt.
- **Task 3 — Model Parameters & Exception Handling:**
  - `temperature = 0.0` for maximum factual precision.
  - `max_output_tokens = 2048` (preventing response truncation).
  - `HttpOptions(timeout=30000)` configured in milliseconds.
  - Structured `try/except` returning `{ "status": ..., "narrative": ..., "mode": ... }`.
- **Task 4 — Deterministic Offline Fallback:** Fully functional offline mode requiring zero network calls or API keys, generating an executive SCR text using the verified figures.
- **Task 5 — Numeric Accuracy Checker:** Verifies that all 5 critical numbers are present and uncorrupted:
  1. Cleaned total revenue: `97,358.30` ✅
  2. Duplicate reconciliation delta: `2,501.90` ✅
  3. COD return rate: `44.4%` ✅
  4. Highest-risk segment: `Tier-2` & `54.5%` ✅
  5. True peak month and revenue: `March` & `20,318.90` ✅
- **Task 6 — Sample Output (`sample_output.txt`):** Saved clean narrative ready for executive briefing.

---

## 🏆 Key Business Recommendations (SCR Summary)

```
SITUATION
Mamaearth's cleaned total booked revenue stands at INR 97,358.30, reconciled from the raw total of INR 99,860.20. The exact variance of INR 2,501.90 is entirely attributable to five double-submitted duplicate orders identified and removed during data cleaning. This reconciled baseline provides regional ops and finance with an accurate foundation for evaluating return exposures and demand patterns.

COMPLICATION
Returns are heavily concentrated rather than evenly distributed. Cash on Delivery (COD) orders suffer an alarming return rate of 44.4%, more than triple CARD (14.7%) and more than double UPI (18.9%). Multi-level segmentation identifies COD in Tier-2 cities as the single highest-risk segment, peaking at a 54.5% return rate. Furthermore, quantity outlier analysis reveals that January's apparent revenue of INR 29,582.10 was artificially inflated by two bulk orders; when corrected to INR 11,637.10, March emerges as the true organic peak month at INR 20,318.90.

RESOLUTION
Operations and growth teams must implement targeted return-mitigation workflows rather than blanket policies. Prioritize two-step order confirmation protocols and delivery tracking in Tier-2 COD corridors, while testing small prepaid checkout incentives to migrate customers to UPI and Card. Fix frontend duplicate order submissions, validate B2B bulk orders separately from D2C demand, and align regional inventory planning with the true March seasonal peak.
```

---

## 🛡️ Ground Rules & Pitfalls Avoided

| Rule / Pitfall | Implementation in This Repository |
| :--- | :--- |
| **No hand-editing CSVs** | Raw CSVs in `data/` remain 100% untouched; all cleaning is performed in Python. |
| **SQL Integer Division** | Explicitly used `100.0` in SQL revenue formulas to avoid SQLite integer truncation. |
| **Header Import in SQLite** | Used `--skip 1` and converted empty strings to SQL `NULL` for nullable columns. |
| **Order of Cleaning** | Deduplicated before computing medians/imputations; detected outliers prior to trend analysis. |
| **No dropping outliers** | Bulk orders (`O0011`, `O0098`) are flagged (`is_outlier=True`) and retained in the master dataset. |
| **Zero hardcoded numbers** | All prompt variables and `findings.json` values are computed dynamically by code. |
| **Gemini Timeout Unit** | `HttpOptions(timeout=30000)` configured in milliseconds, not seconds. |
| **API Key Security** | No API keys committed. Loaded strictly from `GEMINI_API_KEY` with deterministic fallback. |
