# FORESIGHT Demo Video Walkthrough Script

**(0:00 - 0:30) Problem & Client Context**
"Hello team, today we are excited to walk you through Project Foresight, our end-to-end predictive inventory solution for NorthBay Living. Currently, we are flying blind on inventory—stockouts are costing us active revenue, and overstock is locking up vital warehouse space and capital. We set out to replace our manual spreadsheets with a machine learning engine that flags exactly what to buy, and what to liquidate, before the problem hits."

**(0:30 - 1:30) Pipeline & Data Quality**
"Our first step was building a robust data pipeline. We took the raw daily sales logs, calendar events, and inventory snapshots and stitched them into a unified weekly dataset. We did find some data quality hurdles early on—specifically, 150 of the 200 items in our inventory snapshot lacked any historical sales data, so for V1, we scoped our model to the 50 SKUs with complete records. We also resolved missing target variables by explicitly dropping incomplete trailing weeks to ensure pristine validation."

**(1:30 - 2:30) Model Backtest & Leakage Check**
"We tested a LightGBM machine learning model against our historical data using a 4-fold expanding window backtest. The results were fantastic: our model hit an 8.79% error rate, easily beating our previous baseline which sat at 11.23%. More importantly, we ran a rigorous leakage check. We proved that removing future-leaning assumptions like price and promotions only dropped the accuracy by 0.05%, meaning this predictive power is genuine and not just memorizing the test set."

**(2:30 - 3:30) Live Dashboard Walkthrough**
"Let's look at how planners will actually use this. Here is the Executive Summary of the Foresight dashboard. Right away, you see our key KPIs and the 'Action Required' table highlighting our highest-risk items. You can filter by category on the left to drill into just the Furniture department. Over on the 'SKU Deep Dive' tab, a planner can select a specific item, like SKU012, and see our forecasted demand mapped directly against historical sales, complete with a P10 to P90 confidence band."

**(3:30 - 4:30) Live API Demo**
"This isn't just a dashboard—it's a production system. We've deployed a live FastAPI service so our ERP can query these scores programmatically. Let me open the `/docs` endpoint. As you can see in the Swagger UI, we have endpoints to pull the top stockouts, or even run a batch POST request to the `/score` endpoint. If we pass in a list of SKU IDs, the API instantly returns the exact forecast arrays and risk classifications for each item."

**(4:30 - 5:00) Close, Impact & Recommendation**
"To sum up the immediate impact: this model has identified ₹2.8 million in impending stockout risks that need immediate reordering, and ₹6.3 million in capital tied up in dead stock. Our recommendation is to immediately trigger purchase orders for the top 3 stockout risks identified today, and then proceed with expanding this model to the remaining 150 SKUs once that sales history is secured. Thank you."
