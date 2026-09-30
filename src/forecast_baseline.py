import os
import pandas as pd
import numpy as np

def calculate_wape(y_true, y_pred):
    """Primary metric: Weighted Absolute Percentage Error"""
    total_abs_err = np.sum(np.abs(y_true - y_pred))
    total_actual = np.sum(np.abs(y_true))
    if total_actual == 0:
        return 0.0
    return total_abs_err / total_actual

def calculate_bias(y_true, y_pred):
    """Secondary metric: Bias (mean prediction - mean actual)"""
    return np.mean(y_pred - y_true)

def prepare_weekly_data(df):
    """Aggregate daily data to weekly SKU-level demand (filtering out partial weeks)"""
    df['date'] = pd.to_datetime(df['date'])
    # Resample to weekly (starting Monday)
    df_weekly = df.groupby(['sku_id', pd.Grouper(key='date', freq='W-MON')]).agg(
        units_sold=('units_sold', 'sum'),
        unit_price=('unit_price', 'mean'), # average price over week
        promo_days=('promo_flag', 'sum'), # number of promo days in week
        days_count=('date', 'count') # count the number of daily records in this week
    ).reset_index()
    
    # Drop any partial weeks (e.g., at the end of the dataset) to avoid artificial errors
    df_weekly = df_weekly[df_weekly['days_count'] == 7].copy()
    
    return df_weekly.sort_values(['sku_id', 'date'])

def run_baseline_forecast(data_path="data/processed/analysis_ready.csv", reports_dir="reports"):
    print("Starting Baseline Forecasting...")
    
    # 1. Load data
    df = pd.read_csv(data_path)
    
    # 2. Aggregate to weekly demand
    df_weekly = prepare_weekly_data(df)
    
    # 3. Create Seasonal-Naive Baseline
    # Seasonal naive: same week last year (shift by 52 weeks). 
    # Fallback: last 4-week mean.
    
    wape_scores = []
    
    skus = df_weekly['sku_id'].unique()
    baseline_predictions = []
    
    # We simulate a test set for the LAST 8 WEEKS of available data across all SKUs.
    max_date = df_weekly['date'].max()
    test_cutoff = max_date - pd.Timedelta(weeks=8)
    
    train = df_weekly[df_weekly['date'] <= test_cutoff].copy()
    test = df_weekly[df_weekly['date'] > test_cutoff].copy()
    
    for sku in skus:
        sku_train = train[train['sku_id'] == sku].set_index('date')
        sku_test = test[test['sku_id'] == sku].set_index('date')
        
        if len(sku_test) == 0:
            continue
            
        preds = []
        for test_date in sku_test.index:
            last_year_date = test_date - pd.Timedelta(weeks=52)
            
            # Try seasonal naive
            if last_year_date in sku_train.index:
                pred = sku_train.loc[last_year_date, 'units_sold']
            else:
                # Fallback to last 4-week mean
                recent = sku_train[sku_train.index < test_date].tail(4)
                if len(recent) > 0:
                    pred = recent['units_sold'].mean()
                else:
                    pred = 0 # No history
            preds.append(pred)
            
        sku_test['baseline_pred'] = preds
        baseline_predictions.append(sku_test.reset_index())
    
    if len(baseline_predictions) == 0:
        print("No test data available for evaluation.")
        return
        
    results_df = pd.concat(baseline_predictions)
    
    # 4. Calculate WAPE and Bias
    overall_wape = calculate_wape(results_df['units_sold'], results_df['baseline_pred'])
    overall_bias = calculate_bias(results_df['units_sold'], results_df['baseline_pred'])
    
    print(f"\n--- BASELINE EVALUATION (Last 8 Weeks Holdout) ---")
    print(f"Overall WAPE: {overall_wape:.2%}")
    print(f"Overall Bias: {overall_bias:.2f} units/week")
    
    # 5. Save outputs
    os.makedirs(reports_dir, exist_ok=True)
    with open(os.path.join(reports_dir, "baseline_results.md"), "w") as f:
        f.write("# Baseline Model Evaluation\n\n")
        f.write("## Setup\n")
        f.write("- **Aggregation**: Weekly\n")
        f.write("- **Horizon**: 8 Weeks\n")
        f.write("- **Method**: Seasonal Naive (52-week lag), fallback to 4-week trailing mean.\n\n")
        f.write("## Results\n")
        f.write(f"- **Overall WAPE**: {overall_wape:.2%}\n")
        f.write(f"- **Overall Bias**: {overall_bias:.2f}\n")

if __name__ == "__main__":
    run_baseline_forecast()
