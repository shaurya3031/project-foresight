# Project FORESIGHT - Data Quality & Coverage Report

## Executive Summary
- **Total SKUs Analyzed**: 200
- **Intersection Modeling SKUs**: 50
- **Date Range**: 2024-01-01 to 2025-12-31
- **Total Sales Records Processed**: 36550

## 1. SKU Coverage & Cross-Table Audit
- **Sales Daily SKUs**: 50
- **SKU Master SKUs**: 50
- **Inventory Snapshots SKUs**: 200

### SKUs Missing in Sales Data (150)
`SKU051, SKU052, SKU053, SKU054, SKU055, SKU056, SKU057, SKU058, SKU059, SKU060, SKU061, SKU062, SKU063, SKU064, SKU065, SKU066, SKU067, SKU068, SKU069, SKU070, SKU071, SKU072, SKU073, SKU074, SKU075, SKU076, SKU077, SKU078, SKU079, SKU080`...

### SKUs Missing in SKU Master (150)
`SKU051, SKU052, SKU053, SKU054, SKU055, SKU056, SKU057, SKU058, SKU059, SKU060, SKU061, SKU062, SKU063, SKU064, SKU065, SKU066, SKU067, SKU068, SKU069, SKU070, SKU071, SKU072, SKU073, SKU074, SKU075, SKU076, SKU077, SKU078, SKU079, SKU080`...

## 2. Negative Gross Margin Audit
Identified **16 SKUs** where `cost_price > selling_price`. Per specifications, these SKUs have been flagged without auto-correcting raw pricing data:

| SKU | Product Name | Category | Cost Price | Selling Price | Gross Margin |
| --- | --- | --- | --- | --- | --- |
| SKU002 | Product 002 | Home Decor | ₹3867.09 | ₹3805.69 | ₹-61.40 |
| SKU007 | Product 007 | Home Decor | ₹7748.20 | ₹5114.09 | ₹-2634.11 |
| SKU009 | Product 009 | Lighting | ₹3121.06 | ₹2336.89 | ₹-784.17 |
| SKU010 | Product 010 | Storage | ₹3889.06 | ₹663.46 | ₹-3225.60 |
| SKU011 | Product 011 | Furniture | ₹1718.40 | ₹1444.56 | ₹-273.84 |
| SKU016 | Product 016 | Furniture | ₹3637.93 | ₹2166.82 | ₹-1471.11 |
| SKU018 | Product 018 | Kitchen | ₹5677.05 | ₹5575.41 | ₹-101.64 |
| SKU020 | Product 020 | Storage | ₹6700.01 | ₹3897.54 | ₹-2802.47 |
| SKU023 | Product 023 | Kitchen | ₹2484.54 | ₹1416.74 | ₹-1067.80 |
| SKU024 | Product 024 | Lighting | ₹5539.34 | ₹1768.87 | ₹-3770.47 |
| SKU028 | Product 028 | Kitchen | ₹6348.66 | ₹3484.09 | ₹-2864.57 |
| SKU033 | Product 033 | Kitchen | ₹4657.74 | ₹3558.00 | ₹-1099.74 |
| SKU037 | Product 037 | Home Decor | ₹3901.00 | ₹2747.42 | ₹-1153.58 |
| SKU038 | Product 038 | Kitchen | ₹4630.58 | ₹3949.10 | ₹-681.48 |
| SKU040 | Product 040 | Storage | ₹5169.07 | ₹2450.56 | ₹-2718.51 |
| SKU048 | Product 048 | Kitchen | ₹6863.87 | ₹1379.55 | ₹-5484.32 |

## 3. Data Cleaning & Integrity Actions
- **Duplicates Removed**: 0 duplicate rows found on `(date, sku_id)` and removed.
- **Negative Units Handled**: 0 records with negative sales removed.
- **Calendar Imputation**: `holiday` missing values replaced with `'No Holiday'`; `promotion_event` missing values replaced with `'No Promotion'`. Literal `'None'` strings avoided.
- **Inventory Snapshots Alignment**: Monthly inventory snapshots forward-filled to daily levels using `pd.merge_asof(direction='backward')`. No back-fill from future snapshots applied.

## 4. Processing Pipeline Execution Logs
```text
Starting Data Pipeline Execution...
Loaded raw CSV files successfully.
First 3 rows of raw df_sales['SKU']:

0    SKU001
1    SKU002
2    SKU003
First 3 rows of raw df_sku['SKU']:

0    SKU001
1    SKU002
2    SKU003
Renamed columns to standardized snake_case.
SKU Coverage: Total unique SKUs across tables = 200.
SKUs present in sales: 50, sku_master: 50, inventory: 200.
SKUs present in all 3 tables (intersection for modeling): 50.
SKUs missing in sales table: 150.
SKUs missing in SKU Master table: 150.
SKUs missing in Inventory table: 0.
Found 16 SKUs with negative gross margins (cost_price > selling_price). These are flagged in report and left un-altered per specifications.
Calendar missing values filled with 'No Holiday' and 'No Promotion'. Literal 'None' strings avoided.
No negative units_sold found.
No duplicate (date, sku_id) records found.
Outlier threshold (99.9th percentile) = 46.0 units. Flagged 27 outlier rows for inspection (kept in dataset to reflect real demand peaks).
Monthly inventory snapshots successfully forward-filled to daily grid per SKU using past snapshots only (no future data leakage).
Final merged dataset shape: (36550, 30) covering 50 SKUs from 2024-01-01 to 2025-12-31.
Parquet export warning: Unable to find a usable engine; tried using: 'pyarrow', 'fastparquet'.
A suitable version of pyarrow or fastparquet is required for parquet support.
Trying to import the above resulted in these errors:
 - `Import pyarrow` failed. pyarrow is required for parquet support. Use pip or conda to install the pyarrow package.
 - `Import fastparquet` failed. fastparquet is required for parquet support. Use pip or conda to install the fastparquet package.. Saving to CSV as backup...
Saved processed dataset to data/processed\analysis_ready.csv.
```
