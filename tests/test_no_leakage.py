import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.features import create_features

def test_no_future_leakage():
    # Create dummy weekly data
    dates = pd.date_range("2024-01-01", periods=20, freq="W-MON")
    df = pd.DataFrame({
        'date': dates,
        'sku_id': ['SKU001'] * 20,
        'units_sold': np.arange(1, 21), # 1 to 20
        'unit_price': np.arange(101, 121),
        'promo_days': np.arange(0, 20)
    })
    
    df_feat = create_features(df)
    
    # 1. Check Lag Leakage
    val = df_feat[df_feat['units_sold'] == 9]['lag_8'].values[0]
    assert val == 1, f"Expected lag_8 to be 1, got {val}. Future leakage detected!"

    # 2. Check lag_9
    val9 = df_feat[df_feat['units_sold'] == 10]['lag_9'].values[0]
    assert val9 == 1, f"Expected lag_9 to be 1, got {val9}. Future leakage detected!"

    print("Test passed: Verified no future data enters lagged features.")
