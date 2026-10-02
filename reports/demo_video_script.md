# FORESIGHT Demo Video Walkthrough Script

**(0:00 - 0:30) Problem & Client Context**
*👉 [Visual: Start on your GitHub repository page, scrolling slowly through the top of the README, or use a simple title slide]*
"Hey everyone. Today I'm walking you through Project Foresight—a predictive inventory solution I built for NorthBay Living. Right now, the company is kind of flying blind. When we run out of stock, we lose sales, and when we over-order, we just trap money in the warehouse. The goal here was simple: replace those manual spreadsheets with a smart, automated system that tells us exactly what to buy and what to clear out. And just a quick note before we dive in—while this started out as a team effort, I actually ended up designing and building the entire data pipeline, machine learning model, and dashboard all by myself."

**(0:30 - 1:30) Pipeline & Data Quality**
*👉 [Visual: Switch to VS Code. Briefly show `src/pipeline.py` on the screen. Then, click to open `reports/data_quality_report.md` to show the audit]*
"The very first thing I had to tackle was the data. I took our daily sales, promotions, and inventory snapshots and stitched them all together into clean, weekly datasets. It wasn't perfect right out of the gate—I realized pretty quickly that 150 of the 200 items in our inventory didn't actually have any historical sales data. So, for this first version, I just narrowed the focus down to the 50 SKUs that did. I also had to slice off some incomplete data at the end of the year to make sure the model had a perfectly clean target to learn from."

**(1:30 - 2:30) Model Backtest & Leakage Check**
*👉 [Visual: Stay in VS Code, but click over to open `reports/model_backtest_report.md`. Highlight the 8.79% and 8.74% lines with your cursor as you speak]*
"For the actual forecasting, I trained a LightGBM machine learning model. The results were honestly great—the model's error rate is just under 8.8%, which is a huge step up from the 11.2% error we were getting with our old baseline method. But I didn't want the model to just 'cheat' by memorizing things like future prices, so I ran a really strict sensitivity test. Even when I completely stripped out prices and promos, the accuracy barely budged by like 0.05%. So, we know the model's predictive power is the real deal."

**(2:30 - 3:30) Live Dashboard Walkthrough**
*👉 [Visual: Open your web browser and go to the Streamlit Dashboard (https://eavb6dso5hdkzgg5sz2zaw.streamlit.app).]*
*👉 [Action: Wave your mouse over the big KPI numbers at the top. Scroll down slightly to show the 'Action Required' table.]*
*👉 [Action: Click the 'Category' dropdown in the left sidebar and select "Furniture".]*
*👉 [Action: Click the 'SKU Deep Dive' page tab on the left sidebar. Select "SKU012" from the dropdown. Hover your mouse over the line chart to show the tooltip.]*
"Let's look at what this actually looks like for a planner. I built this interactive dashboard where you can see the top-level KPIs right away, plus this really clear 'Action Required' table. If you want to just look at Furniture, you can filter for that on the left. If you switch over to the 'SKU Deep Dive' tab, you can pick any item—like SKU012—and see exactly what my model thinks is going to happen, mapped right alongside historical sales, with a clear high-to-low confidence band."

**(3:30 - 4:30) Live API Demo**
*👉 [Visual: Open a new tab in your browser and go to the Render API Swagger docs (https://project-foresight-tqm3.onrender.com/docs).]*
*👉 [Action: Scroll down to the green `POST /score` endpoint and click it to expand.]*
*👉 [Action: Click the "Try it out" button. Enter `{"sku_ids": ["SKU012"]}` into the request body box and click the big blue "Execute" button.]*
*👉 [Action: Scroll down to the Response body and highlight the JSON output.]*
"But this isn't just a dashboard—I built it to be a real, production-ready backend. I spun up a live API using FastAPI, meaning our core ERP system can pull these numbers automatically. Here's a quick look at the documentation page. I set up endpoints where you can ask for the highest-risk stockouts, or even just send a giant batch of SKU IDs to get their latest forecasts back instantly."

**(4:30 - 5:00) Close, Impact & Recommendation**
*👉 [Visual: Switch back to the Streamlit Dashboard tab. Click back to the "Executive Summary" page. Highlight the big red and orange rupee numbers at the top.]*
"To sum it all up: right out of the gate, this system has found about 2.8 million rupees in stockout risks that we need to reorder immediately, and another 6.3 million rupees just sitting around in dead stock. My recommendation is that we cut purchase orders for our top three stockouts right now, and then start working on expanding this model to those other 150 SKUs. Thanks for your time."
