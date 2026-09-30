# Phase 3: Forecast Model Backtest Results

**Overall LightGBM WAPE**: 8.79%
**Overall Baseline WAPE**: 11.23%

## WAPE Per Fold
- Fold 1: Model WAPE = 9.11% | Baseline WAPE = 11.85%
- Fold 2: Model WAPE = 9.03% | Baseline WAPE = 11.38%
- Fold 3: Model WAPE = 8.80% | Baseline WAPE = 11.61%
- Fold 4: Model WAPE = 8.36% | Baseline WAPE = 10.32%

## WAPE Per Category
- Furniture: Model = 9.36% | Baseline = 11.44%
- Home Decor: Model = 8.33% | Baseline = 10.56%
- Kitchen: Model = 8.57% | Baseline = 11.29%
- Lighting: Model = 8.71% | Baseline = 11.31%
- Storage: Model = 9.28% | Baseline = 11.87%

## Final Verdict
Verdict: LightGBM BEATS the baseline. Proceeding with LightGBM for production scoring.

## Leakage Sensitivity Check
Assumption: `promotion_event` in calendar.csv is a pre-planned business calendar, and `unit_price` is static or known in advance. However, currently they are derived from realized sales which leaks future data.
- Original WAPE (with potential leak): **8.79%**
- Clean WAPE (without price/promo): **8.74%**
- WAPE Degradation: **0.05%**
