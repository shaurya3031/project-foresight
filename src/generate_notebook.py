import nbformat as nbf
import os

def create_eda_notebook():
    os.makedirs("notebooks", exist_ok=True)
    nb = nbf.v4.new_notebook()
    
    markdown_intro = nbf.v4.new_markdown_cell("# Exploratory Data Analysis (EDA)\n\nThis notebook analyzes the NorthBay Living demand dataset. We explore seasonality, promo effects, top movers, and category drivers.")
    
    code_imports = nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os

# Load Data
df = pd.read_csv('../data/processed/analysis_ready.csv')
df['date'] = pd.to_datetime(df['date'])
""")
    
    code_top_movers = nbf.v4.new_code_cell("""# 1. Top Movers vs Dead Stock
sku_sales = df.groupby('sku_id')['units_sold'].sum().sort_values(ascending=False).reset_index()

fig = px.bar(sku_sales.head(10), x='sku_id', y='units_sold', title='Top 10 SKUs by Volume (Top Movers)')
fig.show()

fig2 = px.bar(sku_sales.tail(10), x='sku_id', y='units_sold', title='Bottom 10 SKUs by Volume (Dead Stock)')
fig2.show()
""")

    code_promo = nbf.v4.new_code_cell("""# 2. Promo Effect
promo_sales = df.groupby('promo_flag')['units_sold'].mean().reset_index()
promo_sales['promo_flag'] = promo_sales['promo_flag'].map({0: 'No Promo', 1: 'Promo'})

fig3 = px.bar(promo_sales, x='promo_flag', y='units_sold', title='Average Daily Sales: Promo vs Non-Promo', color='promo_flag')
fig3.show()
""")

    code_category = nbf.v4.new_code_cell("""# 3. Category Effects
cat_sales = df.groupby('category')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)

fig4 = px.pie(cat_sales, values='revenue', names='category', title='Revenue Breakdown by Category')
fig4.show()
""")

    code_seasonality = nbf.v4.new_code_cell("""# 4. Seasonality (Monthly Trend)
df['month'] = df['date'].dt.month
monthly_sales = df.groupby('month')['units_sold'].sum().reset_index()

fig5 = px.line(monthly_sales, x='month', y='units_sold', title='Monthly Seasonality Trend', markers=True)
fig5.show()
""")

    nb['cells'] = [markdown_intro, code_imports, code_top_movers, code_promo, code_category, code_seasonality]
    
    with open('notebooks/01_eda.ipynb', 'w') as f:
        nbf.write(nb, f)
    print("Real EDA notebook created at notebooks/01_eda.ipynb")

if __name__ == '__main__':
    create_eda_notebook()
