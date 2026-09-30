# Foresight

Foresight is an end-to-end predictive supply chain intelligence platform. It bridges the gap between historical sales data and actionable inventory decisions using machine learning and intuitive dashboards.

## Live Deployments
- **Dashboard**: [Requires Deployment to Streamlit Cloud]
- **API**: [Requires Deployment to Render] (docs at `<url>/docs`)

## Overview
The goal of this project is to eliminate guesswork in inventory planning. By accurately forecasting weekly SKU-level demand and marrying it with current inventory positions, Foresight categorizes every SKU into actionable risk quadrants:
- **Reorder Now**: High risk of stockouts during the lead time.
- **Markdown / Clear**: Excess inventory tying up capital.
- **Healthy**: Perfectly balanced inventory.
- **Dead Stock**: Obsolete inventory with zero expected future demand.

## Results & Impact
- **Model Performance**: The ML model (LightGBM) achieved an **8.79% WAPE**, significantly outperforming the seasonal naive baseline (11.23%).
- **Leakage Robustness**: Sensitivity testing confirmed that the model's accuracy is genuine and not reliant on future-leaking price or promotion features (clean WAPE remained excellent at 8.74%).
- **Financial Risk Identified**:
  - **INR 2.8M** in potential lost sales (Stockout Risk)
  - **INR 6.3M** in tied-up capital (Overstock Risk)

## Key Assumptions & Limitations
- **Scope Limitation (50 SKUs)**: Modeling was done exclusively on the 50 SKUs common to `sales_daily`, `sku_master`, and `inventory_snapshots`. While the inventory data has 200 SKUs, the other 150 lack sales history. This is a known scope limitation pending the client's full dataset.
- **Pre-Known Business Features**: `unit_price` and `promo_share` are assumed to be a pre-known business planning calendar available at forecast time, not derived from realized sales after the fact. This assumption was validated via sensitivity testing (see backtest report) — removing these features changed WAPE by only ~0.05 percentage points, confirming they are not a meaningful source of leakage either way.
- **Differentiated Risk Windows**: Stockout risk is evaluated over each SKU's `lead_time_days` against `on_hand_units + on_order_units`. Overstock risk is evaluated over the full 8-week forecast horizon against `on_hand_units` alone. These are intentionally different windows for different risk types.

## Project Architecture
The project is modularized into the following distinct phases:

1. **Phase 1: Data Pipeline** (`src/pipeline.py`)
   Ingests raw sales, inventory, and calendar data, and generates a single analytical dataset.
2. **Phase 2: EDA & Baseline Model** (`src/eda.py` & `src/forecast_baseline.py`)
   Flags data quality issues and establishes a rigorous seasonal naive baseline to benchmark ML improvements.
3. **Phase 3: Machine Learning Model** (`src/forecast_model.py` & `src/run_sensitivity.py`)
   Trains a LightGBM regressor with quantile regression (P10, P50, P90) over a 4-fold expanding window cross-validation.
4. **Phase 4: Risk Scoring** (`src/risk.py`)
   Marries P10/P90 forecasts with `effective_inventory` and `lead_time_days` to classify SKUs into risk quadrants.
5. **Phase 5: Interactive Dashboard** (`src/dashboard.py`)
   A Streamlit dashboard for executives and planners to visualize risks, filter by category, and drill down into specific SKUs.
6. **Phase 6: Production API** (`service/main.py`)
   A FastAPI application exposing single-SKU and batch scoring endpoints for downstream system integration.

## How to Run

### 1. Run the Data Pipeline
Execute the full pipeline from raw data to final CSV outputs:
```bash
python run_all.py
```

### 2. Launch the Executive Dashboard
Explore the interactive inventory risk application:
```bash
pip install streamlit plotly
streamlit run src/dashboard.py
```

### 3. Start the API Service
Start the REST API for programmatic access to scores:
```bash
pip install fastapi uvicorn pydantic
uvicorn service.main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` to view the interactive Swagger API documentation.
