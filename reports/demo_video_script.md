# FORESIGHT Demo Video Walkthrough Script

**(0:00 - 0:30) Problem & Client Context**
"Hey everyone. Today I'm walking you through Project Foresight—a predictive inventory solution I built for NorthBay Living. Right now, the company is kind of flying blind. When we run out of stock, we lose sales, and when we over-order, we just trap money in the warehouse. The goal here was simple: replace those manual spreadsheets with a smart, automated system that tells us exactly what to buy and what to clear out. And just a quick note before we dive in—while this started out as a team effort, I actually ended up designing and building the entire data pipeline, machine learning model, and dashboard all by myself."

**(0:30 - 1:30) Pipeline & Data Quality**
"The very first thing I had to tackle was the data. I took our daily sales, promotions, and inventory snapshots and stitched them all together into clean, weekly datasets. It wasn't perfect right out of the gate—I realized pretty quickly that 150 of the 200 items in our inventory didn't actually have any historical sales data. So, for this first version, I just narrowed the focus down to the 50 SKUs that did. I also had to slice off some incomplete data at the end of the year to make sure the model had a perfectly clean target to learn from."

**(1:30 - 2:30) Model Backtest & Leakage Check**
"For the actual forecasting, I trained a LightGBM machine learning model. The results were honestly great—the model's error rate is just under 8.8%, which is a huge step up from the 11.2% error we were getting with our old baseline method. But I didn't want the model to just 'cheat' by memorizing things like future prices, so I ran a really strict sensitivity test. Even when I completely stripped out prices and promos, the accuracy barely budged by like 0.05%. So, we know the model's predictive power is the real deal."

**(2:30 - 3:30) Live Dashboard Walkthrough**
"Let's look at what this actually looks like for a planner. I built this interactive dashboard where you can see the top-level KPIs right away, plus this really clear 'Action Required' table. If you want to just look at Furniture, you can filter for that on the left. If you switch over to the 'SKU Deep Dive' tab, you can pick any item—like SKU012—and see exactly what my model thinks is going to happen, mapped right alongside historical sales, with a clear high-to-low confidence band."

**(3:30 - 4:30) Live API Demo**
"But this isn't just a dashboard—I built it to be a real, production-ready backend. I spun up a live API using FastAPI, meaning our core ERP system can pull these numbers automatically. Here's a quick look at the documentation page. I set up endpoints where you can ask for the highest-risk stockouts, or even just send a giant batch of SKU IDs to get their latest forecasts back instantly."

**(4:30 - 5:00) Close, Impact & Recommendation**
"To sum it all up: right out of the gate, this system has found about 2.8 million rupees in stockout risks that we need to reorder immediately, and another 6.3 million rupees just sitting around in dead stock. My recommendation is that we cut purchase orders for our top three stockouts right now, and then start working on expanding this model to those other 150 SKUs. Thanks for your time."
