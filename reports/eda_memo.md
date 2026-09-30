# Exploratory Data Analysis (EDA) Memo

## Business Insights

### 1. Promo Effectiveness
Promotions drive a **38.1% lift** in average daily units sold compared to non-promotional days. This indicates high price sensitivity.

![Promo Effect](figures/promo_effect.png)

### 2. Product Concentration (Top Movers vs Dead Stock)
The top-selling SKU (SKU012) sold 19,067 units, vastly outperforming the bottom-tier SKUs like SKU004 (3,380 units). This suggests opportunities to rationalise dead stock.

![Top Movers](figures/top_movers.png)

### 3. Category Revenue Drivers
The **Home Decor** category generates the highest total revenue (₹888,468,077.72), making it the most critical category for inventory protection.

![Category Revenue](figures/category_revenue.png)

### 4. Seasonality
Month 3 shows the highest sales volume, pointing to strong seasonal demand peaks that must be anticipated in our supply chain.

![Seasonality Trend](figures/seasonality.png)

---
*Note: An accompanying EDA notebook (`notebooks/01_eda.ipynb`) contains the working analysis code and interactive Plotly visuals.*