## Project FORESIGHT
**NorthBay Living**
*September 2026*

## The Business Problem
Stockouts are costing us lost sales while excess overstock is tying up critical working capital, and our current manual planning can't see these problems coming soon enough to act.

## What We Built
- **Forecast Engine**: A machine learning model predicting weekly sales demand per item.
- **Risk Scoring**: Automated logic that compares forecasts against current inventory to flag exact overstock and stockout risks.
- **Dashboard**: A live, interactive web app for planners to easily view items needing attention.
- **API Service**: A secure integration endpoint so other company systems can automatically pull these inventory risk scores.

## Headline Financial Impact
- **₹2.8M** in immediate stockout risk (potential lost sales).
- **₹6.3M** in capital tied up in overstock.

## Model Accuracy
- **Our Model**: 8.79% Error
- **Previous Baseline**: 11.23% Error
Our forecasts are off by about 9% on average, meaningfully better than assuming this week looks like the same week last year.

## Action Required: Top 3 Urgent SKUs
1. **SKU012** (Home Decor) — Reorder Now to prevent ₹1,736,695 in lost sales.
2. **SKU031** (Furniture) — Reorder Now to prevent ₹897,781 in lost sales.
3. **SKU040** (Storage) — Reorder Now to prevent ₹124,647 in lost sales.

## Day-to-Day Operations
Planners will open the dashboard daily, use the category filter for their department, and work down the "Action Required" table to immediately issue purchase orders for stockout risks or markdown campaigns for overstock.

## Honest Limitations
- **Current Scope**: Modeling was done exclusively on the 50 SKUs that had full sales history available; the remaining 150 SKUs in the inventory master lack historical data.
- **Forecast Uncertainty**: This is a statistical forecast, not a guarantee of the future, and extreme market events will require human override.

## Recommended Next Steps
1. Expand the model to the full 200-SKU dataset once historical sales are provided.
2. Integrate a live inventory feed instead of relying on the static snapshot.
3. Revisit and tune the risk thresholds after a month of real-world usage.

## Resources & Links
- **Live Dashboard**: [Streamlit Cloud URL Pending Deployment]
- **Live API**: [Render API URL Pending Deployment]
- **GitHub Repository**: [GitHub Repo URL Pending Deployment]
