# FORESIGHT Demo Video Walkthrough Script

**(0:00 - 0:30) Problem & Client Context**
"Hello everyone, today I am excited to walk you through Project Foresight, my end-to-end predictive inventory solution for NorthBay Living. Currently, we are flying blind on inventory—stockouts are costing us active revenue, and overstock is locking up vital warehouse space and capital. I set out to replace our manual spreadsheets with a machine learning engine that flags exactly what to buy, and what to liquidate, before the problem hits. While I initially started this as a team project, I ended up designing and building the entire pipeline, model, and dashboard independently from the ground up."

**(0:30 - 1:30) Pipeline & Data Quality**
"My first step was building a robust data pipeline. I took the raw daily sales logs, calendar events, and inventory snapshots and stitched them into a unified weekly dataset. I did find some data quality hurdles early on—specifically, 150 of the 200 items in our inventory snapshot lacked any historical sales data, so for V1, I scoped my model to the 50 SKUs with complete records. I also resolved missing target variables by explicitly dropping incomplete trailing weeks to ensure pristine validation."

**(1:30 - 2:30) Model Backtest & Leakage Check**
"I tested a LightGBM machine learning model against our historical data using a 4-fold expanding window backtest. The results were fantastic: my model hit an 8.79% error rate, easily beating the previous baseline which sat at 11.23%. More importantly, I ran a rigorous leakage check. I proved that removing future-leaning assumptions like price and promotions only dropped the accuracy by 0.05%, meaning this predictive power is genuine and not just memorizing the test set."

**(2:30 - 3:30) Live Dashboard Walkthrough**
"Let's look at how planners will actually use this. Here is the Executive Summary of the Foresight dashboard that I built. Right away, you see the key KPIs and the 'Action Required' table highlighting our highest-risk items. You can filter by category on the left to drill into just the Furniture department. Over on the 'SKU Deep Dive' tab, a planner can select a specific item, like SKU012, and see my forecasted demand mapped directly against historical sales, complete with a P10 to P90 confidence band."

**(3:30 - 4:30) Live API Demo**
"This isn't just a dashboard—it's a production system. I've deployed a live FastAPI service so our ERP can query these scores programmatically. Let me open the `/docs` endpoint. As you can see in the Swagger UI, I have built endpoints to pull the top stockouts, or even run a batch POST request to the `/score` endpoint. If I pass in a list of SKU IDs, the API instantly returns the exact forecast arrays and risk classifications for each item."

**(4:30 - 5:00) Close, Impact & Recommendation**
"To sum up the immediate impact: this model has identified ₹2.8 million in impending stockout risks that need immediate reordering, and ₹6.3 million in capital tied up in dead stock. My recommendation is to immediately trigger purchase orders for the top 3 stockout risks identified today, and then proceed with expanding this model to the remaining 150 SKUs once that sales history is secured. Thank you."
