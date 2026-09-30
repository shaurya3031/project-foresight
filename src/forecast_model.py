import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from src.forecast_baseline import prepare_weekly_data, calculate_wape, calculate_bias
from src.features import create_features

def run_model_backtest(data_path="data/processed/analysis_ready.csv", reports_dir="reports"):
    print("Starting Model Feature Engineering & Backtest...")
    df = pd.read_csv(data_path)
    
    # 1. Prepare data
    df_weekly = prepare_weekly_data(df)
    
    # Need to merge category for per-category WAPE
    # The 'category' column is available in original data but got dropped in groupby.
    # Let's map it back.
    sku_cats = df[['sku_id', 'category']].drop_duplicates().set_index('sku_id')['category']
    
    df_features = create_features(df_weekly)
    df_features['category'] = df_features['sku_id'].map(sku_cats)
    
    # Label encode category for LightGBM
    df_features['category_code'] = df_features['category'].astype('category').cat.codes
    
    # Sort chronologically for rolling-origin CV
    dates = np.sort(df_features['date'].unique())
    
    # 2. Rolling-origin CV (4 folds, 8-week test windows)
    # Fold 1: test is last 8 weeks
    # Fold 2: test is weeks -16 to -8
    # Fold 3: test is weeks -24 to -16
    # Fold 4: test is weeks -32 to -24
    
    n_folds = 4
    test_window = 8
    
    features = ['month', 'week_of_year', 'lag_8', 'lag_9', 'lag_10', 'lag_52', 
                'rolling_4_mean_lag_8', 'rolling_8_mean_lag_8', 'promo_share', 'unit_price', 'category_code']
    target = 'target'
    
    fold_results = []
    
    for fold in range(n_folds):
        # Determine cutoff dates
        test_end_idx = len(dates) - 1 - (fold * test_window)
        test_start_idx = test_end_idx - test_window
        
        if test_start_idx < 0:
            print(f"Not enough data for fold {fold+1}. Stopping CV.")
            break
            
        test_dates = dates[test_start_idx : test_end_idx]
        train_dates = dates[:test_start_idx]
        
        train_mask = df_features['date'].isin(train_dates)
        test_mask = df_features['date'].isin(test_dates)
        
        train = df_features[train_mask]
        test = df_features[test_mask]
        
        X_train, y_train = train[features], train[target]
        X_test, y_test = test[features], test[target]
        
        # Train LightGBM models (Median, P10, P90)
        # Median
        model_p50 = lgb.LGBMRegressor(objective='quantile', alpha=0.5, n_estimators=100, random_state=42)
        model_p50.fit(X_train, y_train)
        
        # P10
        model_p10 = lgb.LGBMRegressor(objective='quantile', alpha=0.1, n_estimators=100, random_state=42)
        model_p10.fit(X_train, y_train)
        
        # P90
        model_p90 = lgb.LGBMRegressor(objective='quantile', alpha=0.9, n_estimators=100, random_state=42)
        model_p90.fit(X_train, y_train)
        
        preds_p50 = model_p50.predict(X_test)
        preds_p50 = np.maximum(0, preds_p50) # Non-negative demand
        preds_p10 = np.maximum(0, model_p10.predict(X_test))
        preds_p90 = np.maximum(0, model_p90.predict(X_test))
        
        # Calculate baseline on this fold (seasonal naive, lag_52 or 4-week mean)
        baseline_preds = []
        for _, row in test.iterrows():
            last_year_date = row['date'] - pd.Timedelta(weeks=52)
            hist = train[(train['sku_id'] == row['sku_id'])]
            
            match = hist[hist['date'] == last_year_date]
            if not match.empty:
                b_pred = match['units_sold'].values[0]
            else:
                recent = hist.tail(4)
                if len(recent) > 0:
                    b_pred = recent['units_sold'].mean()
                else:
                    b_pred = 0
            baseline_preds.append(b_pred)
            
        # Compile fold results
        res_df = test[['date', 'sku_id', 'category', 'units_sold']].copy()
        res_df['fold'] = fold + 1
        res_df['model_p50'] = preds_p50
        res_df['model_p10'] = preds_p10
        res_df['model_p90'] = preds_p90
        res_df['baseline_pred'] = baseline_preds
        fold_results.append(res_df)
        
    all_results = pd.concat(fold_results)
    
    # 3. Output WAPE per fold
    summary_lines = []
    summary_lines.append("# Phase 3: Forecast Model Backtest Results\n")
    
    overall_model_wape = calculate_wape(all_results['units_sold'], all_results['model_p50'])
    overall_base_wape = calculate_wape(all_results['units_sold'], all_results['baseline_pred'])
    
    summary_lines.append(f"**Overall LightGBM WAPE**: {overall_model_wape:.2%}")
    summary_lines.append(f"**Overall Baseline WAPE**: {overall_base_wape:.2%}\n")
    
    summary_lines.append("## WAPE Per Fold")
    for f in range(1, n_folds+1):
        f_data = all_results[all_results['fold'] == f]
        m_wape = calculate_wape(f_data['units_sold'], f_data['model_p50'])
        b_wape = calculate_wape(f_data['units_sold'], f_data['baseline_pred'])
        summary_lines.append(f"- Fold {f}: Model WAPE = {m_wape:.2%} | Baseline WAPE = {b_wape:.2%}")
        
    summary_lines.append("\n## WAPE Per Category")
    cats = all_results['category'].unique()
    for c in cats:
        c_data = all_results[all_results['category'] == c]
        m_wape = calculate_wape(c_data['units_sold'], c_data['model_p50'])
        b_wape = calculate_wape(c_data['units_sold'], c_data['baseline_pred'])
        summary_lines.append(f"- {c}: Model = {m_wape:.2%} | Baseline = {b_wape:.2%}")
        
    # 4. Selection Rule
    summary_lines.append("\n## Final Verdict")
    if overall_model_wape < overall_base_wape:
        summary_lines.append("Verdict: LightGBM BEATS the baseline. Proceeding with LightGBM for production scoring.")
        # Save final model state indicators to be used by Risk Module
        all_results.to_csv("data/processed/final_forecast.csv", index=False)
    else:
        summary_lines.append("Verdict: LightGBM DID NOT beat the baseline. Shipping the Baseline Model per constraints.")
        # Use baseline as the primary prediction, and compute simple heuristic bounds for P10/P90.
        all_results['model_p50'] = all_results['baseline_pred']
        all_results['model_p10'] = all_results['baseline_pred'] * 0.8
        all_results['model_p90'] = all_results['baseline_pred'] * 1.2
        all_results.to_csv("data/processed/final_forecast.csv", index=False)
        
    report_path = os.path.join(reports_dir, "model_backtest_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))
        
    print(f"Backtest complete. Verdict logged to {report_path}.")

if __name__ == "__main__":
    run_model_backtest()
