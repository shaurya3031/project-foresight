import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from src.forecast_baseline import prepare_weekly_data, calculate_wape, calculate_bias
from src.features import create_features

def run_sensitivity():
    print("Running Sensitivity Check: Removing 'promo_share' and 'unit_price' features to test leakage impact...")
    
    df = pd.read_csv("data/processed/analysis_ready.csv")
    df_weekly = prepare_weekly_data(df)
    sku_cats = df[['sku_id', 'category']].drop_duplicates().set_index('sku_id')['category']
    
    df_features = create_features(df_weekly)
    df_features['category'] = df_features['sku_id'].map(sku_cats)
    df_features['category_code'] = df_features['category'].astype('category').cat.codes
    
    dates = np.sort(df_features['date'].unique())
    n_folds = 4
    test_window = 8
    
    # REMOVED promo_share and unit_price
    features = ['month', 'week_of_year', 'lag_8', 'lag_9', 'lag_10', 'lag_52', 
                'rolling_4_mean_lag_8', 'rolling_8_mean_lag_8', 'category_code']
    target = 'target'
    
    fold_results = []
    
    for fold in range(n_folds):
        test_end_idx = len(dates) - 1 - (fold * test_window)
        test_start_idx = test_end_idx - test_window
        if test_start_idx < 0:
            break
            
        test_dates = dates[test_start_idx : test_end_idx]
        train_dates = dates[:test_start_idx]
        
        train = df_features[df_features['date'].isin(train_dates)]
        test = df_features[df_features['date'].isin(test_dates)]
        
        X_train, y_train = train[features], train[target]
        X_test, y_test = test[features], test[target]
        
        model = lgb.LGBMRegressor(objective='quantile', alpha=0.5, n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        preds = np.maximum(0, model.predict(X_test))
        
        res_df = test[['date', 'sku_id', 'units_sold']].copy()
        res_df['model_pred'] = preds
        fold_results.append(res_df)
        
    all_results = pd.concat(fold_results)
    wape_no_leakage = calculate_wape(all_results['units_sold'], all_results['model_pred'])
    
    # Let's compare with the original run WAPE (using unit_price and promo_share)
    features_orig = ['month', 'week_of_year', 'lag_8', 'lag_9', 'lag_10', 'lag_52', 
                'rolling_4_mean_lag_8', 'rolling_8_mean_lag_8', 'promo_share', 'unit_price', 'category_code']
    
    fold_results_orig = []
    for fold in range(n_folds):
        test_end_idx = len(dates) - 1 - (fold * test_window)
        test_start_idx = test_end_idx - test_window
        if test_start_idx < 0:
            break
        test_dates = dates[test_start_idx : test_end_idx]
        train_dates = dates[:test_start_idx]
        train = df_features[df_features['date'].isin(train_dates)]
        test = df_features[df_features['date'].isin(test_dates)]
        X_train, y_train = train[features_orig], train[target]
        X_test, y_test = test[features_orig], test[target]
        model = lgb.LGBMRegressor(objective='quantile', alpha=0.5, n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        preds = np.maximum(0, model.predict(X_test))
        res_df = test[['date', 'sku_id', 'units_sold']].copy()
        res_df['model_pred'] = preds
        fold_results_orig.append(res_df)
        
    all_results_orig = pd.concat(fold_results_orig)
    wape_orig = calculate_wape(all_results_orig['units_sold'], all_results_orig['model_pred'])
    
    print(f"\n--- SENSITIVITY TEST RESULTS ---")
    print(f"Original Model WAPE (with unit_price & promo_share): {wape_orig:.2%}")
    print(f"Sensitivity Model WAPE (WITHOUT unit_price & promo_share): {wape_no_leakage:.2%}")
    print(f"WAPE Difference (Absolute): {abs(wape_orig - wape_no_leakage):.2%}")
    
    if wape_no_leakage > 0.2314:
        print("ALERT: Without these features, the model fails to beat the Baseline WAPE (23.14%)!")
    else:
        print("The model STILL beats the baseline even without these features.")
        
    # Write to report (guarding against double append)
    report_path = "reports/model_backtest_report.md"
    with open(report_path, "r") as f:
        content = f.read()
    
    if "## Leakage Sensitivity Check" in content:
        content = content.split("## Leakage Sensitivity Check")[0]
        
    with open(report_path, "w") as f:
        f.write(content)
        f.write("\n## Leakage Sensitivity Check\n")
        f.write("Assumption: `promotion_event` in calendar.csv is a pre-planned business calendar, and `unit_price` is static or known in advance. ")
        f.write("However, currently they are derived from realized sales which leaks future data.\n")
        f.write(f"- Original WAPE (with potential leak): **{wape_orig:.2%}**\n")
        f.write(f"- Clean WAPE (without price/promo): **{wape_no_leakage:.2%}**\n")
        f.write(f"- WAPE Degradation: **{abs(wape_orig - wape_no_leakage):.2%}**\n")
        
if __name__ == "__main__":
    run_sensitivity()
