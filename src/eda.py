import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_eda(data_path="data/processed/analysis_ready.csv", reports_dir="reports"):
    print("Starting EDA Image Generation...")
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    
    fig_dir = os.path.join(reports_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    
    # 1. Top Movers
    sku_sales = df.groupby('sku_id')['units_sold'].sum().sort_values(ascending=False)
    top_movers = sku_sales.head(10)
    plt.figure(figsize=(10, 6))
    top_movers.plot(kind='bar', color='skyblue')
    plt.title('Top 10 SKUs by Volume (Top Movers)')
    plt.ylabel('Total Units Sold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "top_movers.png"))
    plt.close()
    
    # 2. Promo Effect
    promo_sales = df.groupby('promo_flag')['units_sold'].mean()
    plt.figure(figsize=(6, 6))
    promo_sales.rename(index={0: 'No Promo', 1: 'Promo'}).plot(kind='bar', color=['lightcoral', 'lightgreen'])
    plt.title('Average Daily Sales: Promo vs Non-Promo')
    plt.ylabel('Average Units Sold')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "promo_effect.png"))
    plt.close()
    
    # 3. Category Effects
    cat_sales = df.groupby('category')['revenue'].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 8))
    cat_sales.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title('Revenue Breakdown by Category')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "category_revenue.png"))
    plt.close()
    
    # 4. Seasonality (monthly trend)
    df['month'] = df['date'].dt.month
    monthly_sales = df.groupby('month')['units_sold'].sum()
    plt.figure(figsize=(10, 6))
    monthly_sales.plot(kind='line', marker='o', color='purple', linewidth=2)
    plt.title('Monthly Seasonality Trend')
    plt.xlabel('Month')
    plt.ylabel('Total Units Sold')
    plt.xticks(range(1, 13))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "seasonality.png"))
    plt.close()

    # Calculate memo stats
    promo_lift = (promo_sales[1] / promo_sales[0] - 1) * 100 if 0 in promo_sales and 1 in promo_sales else 0
    best_month = monthly_sales.idxmax()
    dead_stock = sku_sales.tail(5)

    # Write to memo with embedded images
    memo_path = os.path.join(reports_dir, "eda_memo.md")
    with open(memo_path, "w", encoding="utf-8") as f:
        f.write("# Exploratory Data Analysis (EDA) Memo\n\n")
        f.write("## Business Insights\n\n")
        
        f.write("### 1. Promo Effectiveness\n")
        f.write(f"Promotions drive a **{promo_lift:.1f}% lift** in average daily units sold compared to non-promotional days. This indicates high price sensitivity.\n\n")
        f.write("![Promo Effect](figures/promo_effect.png)\n\n")
        
        f.write("### 2. Product Concentration (Top Movers vs Dead Stock)\n")
        f.write(f"The top-selling SKU ({top_movers.index[0]}) sold {top_movers.iloc[0]:,.0f} units, vastly outperforming the bottom-tier SKUs like {dead_stock.index[0]} ({dead_stock.iloc[0]:,.0f} units). This suggests opportunities to rationalise dead stock.\n\n")
        f.write("![Top Movers](figures/top_movers.png)\n\n")
        
        f.write("### 3. Category Revenue Drivers\n")
        f.write(f"The **{cat_sales.index[0]}** category generates the highest total revenue (₹{cat_sales.iloc[0]:,.2f}), making it the most critical category for inventory protection.\n\n")
        f.write("![Category Revenue](figures/category_revenue.png)\n\n")
        
        f.write("### 4. Seasonality\n")
        f.write(f"Month {best_month} shows the highest sales volume, pointing to strong seasonal demand peaks that must be anticipated in our supply chain.\n\n")
        f.write("![Seasonality Trend](figures/seasonality.png)\n\n")
        
        f.write("---\n*Note: An accompanying EDA notebook (`notebooks/01_eda.ipynb`) contains the working analysis code and interactive Plotly visuals.*")
        
    print(f"EDA memo with images saved to {memo_path}")

    # Generate the actual Plotly notebook
    from src.generate_notebook import create_eda_notebook
    create_eda_notebook()


if __name__ == "__main__":
    run_eda()
