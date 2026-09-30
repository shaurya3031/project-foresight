import pandas as pd
import numpy as np

def run_risk_scoring():
    print("Starting Phase 4: Risk Scoring...")
    
    # 1. Load forecast and historical data
    df_forecast = pd.read_csv("data/processed/final_forecast.csv")
    df_history = pd.read_csv("data/processed/analysis_ready.csv")
    
    # We will use Fold 1 (the most recent 8 weeks) as our proxy for the "current" forecast period
    df_recent_forecast = df_forecast[df_forecast['fold'] == 1].copy()
    
    # Aggregate 8-week demand per SKU for Overstock risk
    forecast_agg = df_recent_forecast.groupby('sku_id').agg({
        'model_p10': 'sum',
        'model_p50': 'sum',
        'model_p90': 'sum'
    }).reset_index()
    forecast_agg.rename(columns={
        'model_p10': 'p10_8wk',
        'model_p50': 'p50_8wk',
        'model_p90': 'p90_8wk'
    }, inplace=True)
    
    # 2. Get current inventory (latest day per SKU)
    df_history['date'] = pd.to_datetime(df_history['date'])
    latest_inv = df_history.sort_values('date').groupby('sku_id').tail(1)[
        ['sku_id', 'on_hand_units', 'on_order_units', 'lead_time_days', 'selling_price', 'cost_price', 'category']
    ]
    
    # Merge
    risk_df = pd.merge(forecast_agg, latest_inv, on='sku_id', how='left')
    
    # Calculate lead-time demand explicitly by summing up to lead_time_days
    # For simplicity and given weekly forecast, we prorate the 8-week total. 
    # (56 days = 8 weeks)
    risk_df['lead_time_p10'] = risk_df['p10_8wk'] * (risk_df['lead_time_days'] / 56.0)
    risk_df['lead_time_p90'] = risk_df['p90_8wk'] * (risk_df['lead_time_days'] / 56.0)
    risk_df['effective_inventory'] = risk_df['on_hand_units'] + risk_df['on_order_units']
    
    # 3. Calculate Risk Quadrants and Rupee Impact
    def determine_quadrant(row):
        inv = row['on_hand_units']
        eff_inv = row['effective_inventory']
        
        lt_p10 = row['lead_time_p10']
        
        p50_8wk = row['p50_8wk']
        p90_8wk = row['p90_8wk']
        
        # (1) dead stock check (using 8-week horizon for demand)
        if p50_8wk <= 0.1 and inv > 0:
            return 'Dead Stock'
            
        # (2) stockout risk (using lead time horizon and effective inventory)
        elif eff_inv < lt_p10:
            return 'Reorder Now'
            
        # (3) overstock risk (using 8-week horizon and on-hand inventory)
        elif inv > p90_8wk:
            return 'Markdown / Clear'
            
        # (4) everything else -> Healthy
        else:
            return 'Healthy'

    risk_df['quadrant'] = risk_df.apply(determine_quadrant, axis=1)
    
    # Calculate Rupee Impact
    def calculate_impact(row):
        inv = row['on_hand_units']
        eff_inv = row['effective_inventory']
        
        if row['quadrant'] == 'Reorder Now':
            # Lost sales revenue (stockout impact over lead time)
            shortage = max(0, row['lead_time_p90'] - eff_inv)
            return shortage * row['selling_price']
        elif row['quadrant'] in ['Markdown / Clear', 'Dead Stock']:
            # Tied-up capital in excess inventory (over 8-week horizon)
            excess = max(0, inv - row['p10_8wk'])
            return excess * row['cost_price']
        else:
            return 0.0
            
    risk_df['rupee_impact'] = risk_df.apply(calculate_impact, axis=1)
    
    # Sort by impact
    risk_df = risk_df.sort_values('rupee_impact', ascending=False)
    
    # Save output
    risk_df.to_csv("data/processed/risk_summary.csv", index=False)
    
    # 4. Generate text report summary
    total_stockout = risk_df[risk_df['quadrant'] == 'Reorder Now']['rupee_impact'].sum()
    total_overstock = risk_df[risk_df['quadrant'].isin(['Markdown / Clear', 'Dead Stock'])]['rupee_impact'].sum()
    
    report_lines = [
        "# Phase 4: Inventory Risk Summary",
        "",
        f"**Total Value at Risk (Stockout):** ₹{total_stockout:,.2f}",
        f"**Total Capital Tied Up (Overstock/Dead Stock):** ₹{total_overstock:,.2f}",
        "",
        "## Quadrant Breakdown"
    ]
    
    counts = risk_df['quadrant'].value_counts()
    for quad, count in counts.items():
        impact = risk_df[risk_df['quadrant'] == quad]['rupee_impact'].sum()
        report_lines.append(f"- **{quad}**: {count} SKUs | Impact: ₹{impact:,.2f}")
        
    with open("reports/risk_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Risk scoring complete. Summary saved to data/processed/risk_summary.csv")

if __name__ == "__main__":
    run_risk_scoring()
