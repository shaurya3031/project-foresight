# Project FORESIGHT: Live Evaluation & Viva Reference Guide

This document is a comprehensive breakdown of the entire architecture, technical decisions, and business logic of Project FORESIGHT. Use this to prepare for your live evaluation or technical interview.

---

## 1. Business Problem & Goal
**The Problem:** The client (NorthBay Living) relies on manual spreadsheets and gut feelings for inventory ordering. This leads to two massive problems:
* **Stockouts:** Running out of popular items, leading to lost revenue.
* **Overstock/Dead Stock:** Ordering too much of slow-moving items, trapping working capital in the warehouse.

**The Solution:** Project FORESIGHT is an automated predictive inventory intelligence engine. It predicts future demand using machine learning and automatically flags which items to reorder (and exactly how many) or markdown, converting data directly into Rupee-impact decisions.

---

## 2. Architecture & Data Pipeline (`src/pipeline.py` & `src/features.py`)
### A. Data Ingestion & Cleaning
* **Sources:** We ingest three distinct datasets: Daily Sales, a Promotional Calendar, and a static Inventory Snapshot.
* **Aggregation:** Inventory decisions are made weekly, so daily sales are aggregated to a **weekly frequency** (`W-MON`).
* **Filtering (The 50 SKU Scope):** The raw inventory file had 200 items, but only 50 had historical sales logs. Since machine learning requires historical patterns to predict the future, the pipeline automatically filters the scope down to the 50 actionable SKUs.
* **Edge Handling:** The pipeline explicitly drops the final, incomplete week of the year to prevent the model from learning a false "drop in sales" target.

### B. Feature Engineering
We engineered features that actually influence demand:
* **Time Features:** Month, Week of Year, Quarter (captures seasonality).
* **Lag Features:** Sales from 1 week ago, 4 weeks ago, 8 weeks ago.
* **Rolling Windows:** 4-week and 8-week moving averages (captures recent momentum/trend).
* **Business Rules:** `unit_price` and `promo_share`. (Note: We assume the business knows future prices/promos at forecast time. Our sensitivity test proved the model doesn't "cheat" heavily on these).

---

## 3. The Machine Learning Engine (`src/forecast_model.py`)
### A. Why LightGBM?
We chose **LightGBM**, a gradient-boosted decision tree algorithm, because it handles tabular data exceptionally well, trains extremely fast, and naturally captures complex non-linear interactions (e.g., how a promotion affects a specific category in December).

### B. Quantile Regression (Probabilistic Forecasting)
Standard models predict a single number (a "point estimate"). We used **Quantile Regression** to predict a range:
* **P10 (Pessimistic):** 10% chance demand is this low. Used to calculate overstock risk.
* **P50 (Median/Expected):** The most likely demand.
* **P90 (Optimistic):** 90% chance demand is at or below this level. Used to calculate stockout risk.
* *Why?* Supply chains require safety margins. Predicting a confidence band allows the business to order conservatively or aggressively based on risk tolerance.

### C. Backtesting & Validation (`src/forecast_baseline.py`)
We validated the model using a **4-Fold Expanding Window Cross-Validation**. 
* We trained on past data, predicted the immediate future, recorded the error, then expanded the training window forward. This perfectly simulates how the model acts in production.
* **Results:** The model achieved an **8.79% WAPE** (Weighted Absolute Percentage Error), comfortably beating the traditional 8-week rolling average baseline (11.23%).

---

## 4. The Risk & Decision Engine (`src/risk.py`)
This is where ML turns into Business Intelligence. The engine takes the 8-week forecast and cross-references it with current warehouse data (`on_hand_units`, `on_order_units`, `lead_time_days`).

### A. Effective Inventory Calculation
`Effective Inventory = On-Hand Inventory + On-Order Inventory` (What we have now + what is already on a truck heading to us).

### B. Risk Categorization (Quadrants)
1. **Reorder Now (Stockout Risk):** If `Effective Inventory` is less than the demand expected during the item's `lead_time_days` (using the P90 aggressive forecast). 
   * *Rupee Impact:* `(Shortfall Units) * Selling Price` = Revenue we will lose if we don't order today.
2. **Markdown / Clear (Overstock Risk):** If `Effective Inventory` is significantly higher than the maximum expected 8-week demand.
   * *Rupee Impact:* `(Excess Units) * Cost Price` = Capital trapped in the warehouse.
3. **Healthy:** Inventory levels are perfectly balanced against forecasted demand.

---

## 5. Deployment & User Interfaces
To make the engine accessible to the business, we deployed two interfaces:

### A. Streamlit Executive Dashboard (`app/dashboard.py`)
* **URL:** `https://eavb6dso5hdkzgg5sz2zaw.streamlit.app`
* **Purpose:** For category managers and supply chain planners.
* **Features:** Shows macro KPIs (Total Value at Risk: ~₹2.8M Stockout, ~₹6.3M Overstock). Allows filtering by category and drilling down into a specific SKU to visually see the P10-P90 forecast bands plotted against historical sales.

### B. FastAPI REST API (`service/main.py`)
* **URL:** `https://project-foresight-tqm3.onrender.com/docs`
* **Purpose:** For automated machine-to-machine integration (e.g., plugging into the company's SAP/ERP system).
* **Features:** A `/score` endpoint where an ERP can POST a JSON list of `sku_ids` and receive back the immediate risk quadrant and 8-week forecast arrays in milliseconds.

---

## Typical Evaluation Q&A

**Q: What was your biggest challenge?**
*A:* Handling the incomplete data. Out of 200 inventory items, 150 had no historical sales log. I had to programmatically audit and filter the dataset down to the 50 viable SKUs to prevent the model from training on noise.

**Q: How do you know your model is actually good?**
*A:* I didn't rely on a simple train/test split. I used expanding window backtesting, simulating real-world time progression. I also measured it against a naive baseline (an 8-week rolling average) to prove the ML actually added value (dropping WAPE from 11.23% to 8.79%).

**Q: Why predict P10/P90 instead of just P50?**
*A:* A single number is useless for inventory. If I predict we'll sell 100 chairs, and we order 100, but demand spikes to 120, we stock out. P90 gives the supply chain planner a "safety stock" upper bound to ensure we don't lose sales during volatile periods.

**Q: What would you do next? (Future Roadmap)**
*A:* First, work with data engineering to capture the missing sales history for the other 150 SKUs. Second, integrate external macroeconomic variables (like inflation or housing market trends) to see if it improves the Home Decor category predictions.
