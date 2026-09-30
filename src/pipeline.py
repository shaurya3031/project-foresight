import os
import pandas as pd
import numpy as np

def run_pipeline(data_raw_dir="data/raw", data_processed_dir="data/processed", reports_dir="reports"):
    os.makedirs(data_processed_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    log_entries = []
    
    def log(msg):
        log_entries.append(msg)
        print(f"[PIPELINE LOG] {msg}")

    log("Starting Data Pipeline Execution...")

    # 1. Load Raw Data
    sales_path = os.path.join(data_raw_dir, "sales_daily.csv")
    sku_path = os.path.join(data_raw_dir, "sku_master.csv")
    cal_path = os.path.join(data_raw_dir, "calendar.csv")
    inv_path = os.path.join(data_raw_dir, "inventory_snapshots.csv")

    df_sales = pd.read_csv(sales_path)
    df_sku = pd.read_csv(sku_path)
    df_cal = pd.read_csv(cal_path)
    df_inv = pd.read_csv(inv_path)

    log("Loaded raw CSV files successfully.")
    
    # User debug request: Print first 3 rows of sku_id before any processing
    log("First 3 rows of raw df_sales['SKU']:")
    log("\n" + df_sales['SKU'].head(3).to_string())
    log("First 3 rows of raw df_sku['SKU']:")
    log("\n" + df_sku['SKU'].head(3).to_string())


    # 2. Standardize Column Names to snake_case
    sales_rename = {
        "Date": "date",
        "SKU": "sku_id",
        "Units_Sold": "units_sold",
        "Revenue": "revenue",
        "Price": "unit_price",
        "Promotion": "promo_flag"
    }
    sku_rename = {
        "SKU": "sku_id",
        "Product_Name": "product_name",
        "Category": "category",
        "Subcategory": "subcategory",
        "Launch_Date": "launch_date",
        "Cost_Price": "cost_price",
        "Selling_Price": "selling_price",
        "Gross_Margin_Per_Unit": "gross_margin_per_unit"
    }
    inv_rename = {
        "Snapshot_Date": "snapshot_date",
        "SKU": "sku_id",
        "Current_Stock": "on_hand_units",
        "On_Order": "on_order_units",
        "Lead_Time_Days": "lead_time_days",
        "Safety_Stock": "safety_stock",
        "Reorder_Point": "reorder_point",
        "Inventory_Value": "inventory_value"
    }

    df_sales = df_sales.rename(columns=sales_rename)
    df_sku = df_sku.rename(columns=sku_rename)
    df_inv = df_inv.rename(columns=inv_rename)
    
    # Standardize calendar dates & column names if needed
    df_cal = df_cal.rename(columns={"Date": "date", "SKU": "sku_id"})

    log("Renamed columns to standardized snake_case.")

    # Convert date columns to datetime
    df_sales["date"] = pd.to_datetime(df_sales["date"])
    df_cal["date"] = pd.to_datetime(df_cal["date"])
    df_inv["snapshot_date"] = pd.to_datetime(df_inv["snapshot_date"])
    if "launch_date" in df_sku.columns:
        df_sku["launch_date"] = pd.to_datetime(df_sku["launch_date"])

    # 3. Known Issue 1: SKU Coverage Analysis
    sales_skus = set(df_sales["sku_id"].dropna().unique())
    sku_master_skus = set(df_sku["sku_id"].dropna().unique())
    inv_skus = set(df_inv["sku_id"].dropna().unique())

    all_skus = sales_skus.union(sku_master_skus).union(inv_skus)
    common_skus = sales_skus.intersection(sku_master_skus).intersection(inv_skus)

    missing_in_sales = sorted(list(all_skus - sales_skus))
    missing_in_sku_master = sorted(list(all_skus - sku_master_skus))
    missing_in_inv = sorted(list(all_skus - inv_skus))

    log(f"SKU Coverage: Total unique SKUs across tables = {len(all_skus)}.")
    log(f"SKUs present in sales: {len(sales_skus)}, sku_master: {len(sku_master_skus)}, inventory: {len(inv_skus)}.")
    log(f"SKUs present in all 3 tables (intersection for modeling): {len(common_skus)}.")
    log(f"SKUs missing in sales table: {len(missing_in_sales)}.")
    log(f"SKUs missing in SKU Master table: {len(missing_in_sku_master)}.")
    log(f"SKUs missing in Inventory table: {len(missing_in_inv)}.")

    # 4. Known Issue 2: Negative Gross Margins
    df_sku["calculated_margin"] = df_sku["selling_price"] - df_sku["cost_price"]
    neg_margin_skus = df_sku[df_sku["calculated_margin"] < 0]
    log(f"Found {len(neg_margin_skus)} SKUs with negative gross margins (cost_price > selling_price). These are flagged in report and left un-altered per specifications.")

    # 5. Known Issue 4: Calendar NaN Handling
    df_cal["holiday"] = df_cal["holiday"].fillna("No Holiday")
    df_cal["promotion_event"] = df_cal["promotion_event"].fillna("No Promotion")
    # Replace any accidental literal string "None" just in case
    df_cal["holiday"] = df_cal["holiday"].replace("None", "No Holiday")
    df_cal["promotion_event"] = df_cal["promotion_event"].replace("None", "No Promotion")
    log("Calendar missing values filled with 'No Holiday' and 'No Promotion'. Literal 'None' strings avoided.")

    # 6. Known Issue 5: Data Cleaning (Duplicates, Negative Units, Outliers)
    initial_sales_count = len(df_sales)
    
    # Check for negative units_sold
    neg_units_count = (df_sales["units_sold"] < 0).sum()
    if neg_units_count > 0:
        df_sales = df_sales[df_sales["units_sold"] >= 0]
        log(f"Removed {neg_units_count} rows with negative units_sold.")
    else:
        log("No negative units_sold found.")

    # Check for duplicates on (date, sku_id)
    dup_mask = df_sales.duplicated(subset=["date", "sku_id"], keep="first")
    dup_count = dup_mask.sum()
    if dup_count > 0:
        df_sales = df_sales[~dup_mask]
        log(f"Deduplicated sales dataset: removed {dup_count} duplicate (date, sku_id) rows.")
    else:
        log("No duplicate (date, sku_id) records found.")

    # Outlier detection on units_sold (99.9th percentile)
    q999 = df_sales["units_sold"].quantile(0.999)
    outliers = df_sales[df_sales["units_sold"] > q999]
    log(f"Outlier threshold (99.9th percentile) = {q999:.1f} units. Flagged {len(outliers)} outlier rows for inspection (kept in dataset to reflect real demand peaks).")

    # 7. Known Issue 3: Monthly Inventory Forward-Fill (No Back-fill)
    min_date = df_sales["date"].min()
    max_date = df_sales["date"].max()
    full_date_range = pd.date_range(start=min_date, end=max_date, freq="D")

    # Expand inventory to daily grid per SKU
    inv_daily_list = []
    for sku in inv_skus:
        sku_inv = df_inv[df_inv["sku_id"] == sku].sort_values("snapshot_date")
        if sku_inv.empty:
            continue
        
        # Create full date template for this SKU
        sku_grid = pd.DataFrame({"date": full_date_range, "sku_id": sku})
        sku_merged = pd.merge_asof(
            sku_grid.sort_values("date"),
            sku_inv.rename(columns={"snapshot_date": "date"}).sort_values("date"),
            on="date",
            by="sku_id",
            direction="backward" # ONLY use past snapshots, no future back-fill!
        )
        inv_daily_list.append(sku_merged)

    df_inv_daily = pd.concat(inv_daily_list, ignore_index=True)
    log("Monthly inventory snapshots successfully forward-filled to daily grid per SKU using past snapshots only (no future data leakage).")

    # 8. Merge into Analysis Ready Dataset
    # Merge Sales + Calendar
    df_merged = pd.merge(df_sales, df_cal, on="date", how="left")
    # Merge SKU Master
    df_merged = pd.merge(df_merged, df_sku, on="sku_id", how="left")
    # Merge Daily Inventory
    df_merged = pd.merge(df_merged, df_inv_daily, on=["date", "sku_id"], how="left")

    log(f"Final merged dataset shape: {df_merged.shape} covering {df_merged['sku_id'].nunique()} SKUs from {df_merged['date'].min().strftime('%Y-%m-%d')} to {df_merged['date'].max().strftime('%Y-%m-%d')}.")

    # Save to Parquet
    parquet_path = os.path.join(data_processed_dir, "analysis_ready.parquet")
    csv_path = os.path.join(data_processed_dir, "analysis_ready.csv")
    try:
        df_merged.to_parquet(parquet_path, index=False)
        log(f"Saved processed dataset to {parquet_path}.")
    except Exception as e:
        log(f"Parquet export warning: {e}. Saving to CSV as backup...")
        df_merged.to_csv(csv_path, index=False)
        log(f"Saved processed dataset to {csv_path}.")

    # 9. Generate Markdown Data Quality Report
    report_path = os.path.join(reports_dir, "data_quality_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Project FORESIGHT - Data Quality & Coverage Report\n\n")
        f.write("## Executive Summary\n")
        f.write(f"- **Total SKUs Analyzed**: {len(all_skus)}\n")
        f.write(f"- **Intersection Modeling SKUs**: {len(common_skus)}\n")
        f.write(f"- **Date Range**: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}\n")
        f.write(f"- **Total Sales Records Processed**: {len(df_merged)}\n\n")
        
        f.write("## 1. SKU Coverage & Cross-Table Audit\n")
        f.write(f"- **Sales Daily SKUs**: {len(sales_skus)}\n")
        f.write(f"- **SKU Master SKUs**: {len(sku_master_skus)}\n")
        f.write(f"- **Inventory Snapshots SKUs**: {len(inv_skus)}\n\n")
        
        if missing_in_sales:
            f.write(f"### SKUs Missing in Sales Data ({len(missing_in_sales)})\n")
            f.write(f"`{', '.join(missing_in_sales[:30])}`" + ("..." if len(missing_in_sales) > 30 else "") + "\n\n")
        
        if missing_in_sku_master:
            f.write(f"### SKUs Missing in SKU Master ({len(missing_in_sku_master)})\n")
            f.write(f"`{', '.join(missing_in_sku_master[:30])}`" + ("..." if len(missing_in_sku_master) > 30 else "") + "\n\n")

        if missing_in_inv:
            f.write(f"### SKUs Missing in Inventory Snapshots ({len(missing_in_inv)})\n")
            f.write(f"`{', '.join(missing_in_inv[:30])}`" + ("..." if len(missing_in_inv) > 30 else "") + "\n\n")

        f.write("## 2. Negative Gross Margin Audit\n")
        f.write(f"Identified **{len(neg_margin_skus)} SKUs** where `cost_price > selling_price`. Per specifications, these SKUs have been flagged without auto-correcting raw pricing data:\n\n")
        if not neg_margin_skus.empty:
            f.write("| SKU | Product Name | Category | Cost Price | Selling Price | Gross Margin |\n")
            f.write("| --- | --- | --- | --- | --- | --- |\n")
            for _, row in neg_margin_skus.iterrows():
                f.write(f"| {row['sku_id']} | {row['product_name']} | {row['category']} | ₹{row['cost_price']:.2f} | ₹{row['selling_price']:.2f} | ₹{row['calculated_margin']:.2f} |\n")
            f.write("\n")

        f.write("## 3. Data Cleaning & Integrity Actions\n")
        f.write(f"- **Duplicates Removed**: {dup_count} duplicate rows found on `(date, sku_id)` and removed.\n")
        f.write(f"- **Negative Units Handled**: {neg_units_count} records with negative sales removed.\n")
        f.write(f"- **Calendar Imputation**: `holiday` missing values replaced with `'No Holiday'`; `promotion_event` missing values replaced with `'No Promotion'`. Literal `'None'` strings avoided.\n")
        f.write(f"- **Inventory Snapshots Alignment**: Monthly inventory snapshots forward-filled to daily levels using `pd.merge_asof(direction='backward')`. No back-fill from future snapshots applied.\n\n")
        
        f.write("## 4. Processing Pipeline Execution Logs\n")
        f.write("```text\n")
        for entry in log_entries:
            f.write(f"{entry}\n")
        f.write("```\n")

    log(f"Generated data quality report at {report_path}.")

if __name__ == "__main__":
    run_pipeline()
