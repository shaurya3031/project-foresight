# FORESIGHT Detailed Demo Video Walkthrough Script

**(0:00 - 0:30) Introduction & Problem Context**
*👉 [Visual: Start on a simple presentation title slide reading "Project Foresight: NorthBay Living", or on the GitHub repository page.]*
"Hey everyone. Today I'm going to walk you through Project Foresight, which is a predictive inventory intelligence solution that I built for NorthBay Living. Right now, the supply chain team is basically flying blind. They rely on disconnected manual spreadsheets, which means they are constantly reacting instead of predicting. When we run out of stock, we actively lose revenue, and when we over-order, we just trap working capital in the warehouse. The goal of this project was to completely replace that manual guesswork with an automated machine learning engine that tells us exactly what to buy, and exactly what to liquidate. And as a quick bit of context before we dive in—while this was originally planned as a collaborative team project, I ended up architecting, designing, and coding the entire data pipeline, machine learning model, and web application completely by myself from the ground up."

**(0:30 - 1:30) Pipeline & Data Quality Audit**
*👉 [Visual: Switch to VS Code. Have `src/pipeline.py` open on the left, and click to open `reports/data_quality_report.md` on the right.]*
"The very first hurdle I had to tackle was the raw data. I ingested three separate data streams: daily sales logs, promotional calendar events, and static inventory snapshots. I built a pipeline to clean and stitch all of this together into a unified weekly dataset. But it wasn't perfect right out of the gate. As you can see here in the data quality report, I ran an automated audit and realized pretty quickly that 150 of the 200 items in our inventory snapshot didn't actually have any historical sales data attached to them. Because machine learning relies on history to predict the future, I couldn't forecast those. So, for this V1 build, I narrowed the scope down to the 50 SKUs that had complete records. I also had to explicitly slice off a partial, incomplete week at the end of the calendar year to make sure the model had a perfectly clean, full-week target to learn from without artificially skewing the results downward."

**(1:30 - 2:30) Model Backtest & Leakage Check**
*👉 [Visual: Click over to `reports/model_backtest_report.md`. Use your cursor to highlight the WAPE metrics.]*
"For the actual forecasting engine, I trained a LightGBM machine learning model using Quantile Regression. This means I'm not just predicting one single number; I'm predicting a P10, P50, and P90 confidence band to account for uncertainty. I tested the model's accuracy using a 4-fold expanding window backtest—essentially forcing the model to walk forward through time, training on the past and predicting the future exactly how it would in the real world. The results were fantastic. My model hit an 8.79% error rate—or WAPE—which easily beat the 11.23% error we were getting with the old baseline method. 
*👉 [Action: Scroll down slightly to the Leakage Sensitivity section.]*
"But I didn't want the model to just 'cheat' by memorizing things like future prices or promotions. So I ran a really strict sensitivity test. Even when I completely stripped out prices and promos from the training data, the model's accuracy barely budged by 0.05%. This proves that the model's predictive power is genuine."

**(2:30 - 3:30) Live Dashboard Walkthrough**
*👉 [Visual: Open your web browser and navigate to the live Streamlit Dashboard: `https://eavb6dso5hdkzgg5sz2zaw.streamlit.app`]*
"Let's look at what this actually looks like for a planner on the floor. I built this interactive web dashboard. Right at the top of the Executive Summary, you can see our macro KPIs. Below that is this 'Action Required' table, which mathematically categorizes every item into 'Reorder Now', 'Markdown', or 'Healthy' based on my forecasts and their lead times. 
*👉 [Action: Click the 'Category' dropdown on the left and select "Furniture".]*
"If I'm the Furniture category manager, I can filter the entire app to just see my items. 
*👉 [Action: Click the 'SKU Deep Dive' tab on the left. Select "SKU012" from the dropdown. Hover your mouse over the line chart.]*
"And if I switch over to the 'SKU Deep Dive' tab, I can pick a specific high-risk item like SKU012. You can see my model's forecast mapped right alongside historical sales, complete with that shaded confidence interval I mentioned earlier."

**(3:30 - 4:30) Live API Demo**
*👉 [Visual: Open a new tab and go to the Render API Swagger docs: `https://project-foresight-tqm3.onrender.com/docs`]*
"But a dashboard alone isn't enough for an enterprise. We need this to integrate with our ERP. So I also built and deployed this production-ready backend using FastAPI. 
*👉 [Action: Click the green `POST /score` endpoint. Click "Try it out".]*
"Here on the interactive documentation page, you can see the endpoints I've set up. We can run a batch POST request right here. 
*👉 [Action: Type `{"sku_ids": ["SKU012"]}` into the box and click Execute. Scroll down to show the JSON output.]*
"If our ordering system passes in a list of SKU IDs, the API instantly returns the exact forecast arrays, the risk quadrant, and the rupee impact for each item, making automated reordering completely seamless."

**(4:30 - 5:00) Close, Impact & Recommendation**
*👉 [Visual: Switch back to the Streamlit Dashboard tab. Click back to the "Executive Summary" page. Highlight the big red and orange rupee numbers at the top.]*
"To sum it all up: right out of the gate, this pipeline has successfully audited our inventory and found about 2.8 million rupees in stockout risks that are going to cost us sales, alongside another 6.3 million rupees just sitting around in dead stock. My recommendation is that we cut purchase orders for our top three stockouts right this afternoon, run a clearance event for the overstock, and then start working on acquiring the missing sales data so I can expand this model to the remaining 150 SKUs. Thank you for your time."
