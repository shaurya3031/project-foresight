import pandas as pd
import numpy as np

def create_features(df_weekly):
    """
    Generate features for the weekly aggregated dataset.
    STRICT NO-LEAKAGE: Since forecast horizon is 8 weeks, we use a minimum 
    lag of 8 weeks for all historical demand features to allow direct forecasting 
    without recursive steps.
    """
    df_weekly = df_weekly.sort_values(['sku_id', 'date']).copy()
    
    # 1. Calendar / Seasonal Features (known in advance, no leakage)
    df_weekly['month'] = df_weekly['date'].dt.month
    df_weekly['week_of_year'] = df_weekly['date'].dt.isocalendar().week.astype(int)
    
    # 2. Historical Demand Lags & Rolling Stats (Minimum Lag = 8)
    # This guarantees we only use data available 8 weeks prior to the target date.
    
    # We define lag_8 as the demand 8 weeks ago
    df_weekly['lag_8'] = df_weekly.groupby('sku_id')['units_sold'].shift(8)
    df_weekly['lag_9'] = df_weekly.groupby('sku_id')['units_sold'].shift(9)
    df_weekly['lag_10'] = df_weekly.groupby('sku_id')['units_sold'].shift(10)
    df_weekly['lag_52'] = df_weekly.groupby('sku_id')['units_sold'].shift(52) # Same week last year
    
    # Rolling stats on the lag_8 (e.g. 4-week trailing mean as of 8 weeks ago)
    df_weekly['rolling_4_mean_lag_8'] = df_weekly.groupby('sku_id')['lag_8'].transform(lambda x: x.rolling(4, min_periods=1).mean())
    df_weekly['rolling_8_mean_lag_8'] = df_weekly.groupby('sku_id')['lag_8'].transform(lambda x: x.rolling(8, min_periods=1).mean())
    
    # 3. Future known features (Promo share, Price)
    # We assume 'promo_days' and 'unit_price' are known for the forecast period (planned promotions and prices).
    df_weekly['promo_share'] = df_weekly['promo_days'] / 7.0
    
    # Fill NAs in price if any
    df_weekly['unit_price'] = df_weekly.groupby('sku_id')['unit_price'].ffill().bfill()
    
    # 4. Target variable
    df_weekly['target'] = df_weekly['units_sold']
    
    # Drop rows where lag_8 is NaN (first 8 weeks)
    df_features = df_weekly.dropna(subset=['lag_8']).copy()
    
    return df_features
