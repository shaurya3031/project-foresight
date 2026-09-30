from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np

app = FastAPI(title="Foresight API", description="API for Inventory Risk and Forecasting")

class ScoreRequest(BaseModel):
    sku_ids: List[str]

# Load data at startup
try:
    df_risk = pd.read_csv("data/processed/risk_summary.csv")
    df_forecast = pd.read_csv("data/processed/final_forecast.csv")
    # Filter forecast to Fold 1 only for production serving
    df_forecast = df_forecast[df_forecast['fold'] == 1].copy()
    
    # Replace NaN with None to ensure valid JSON output
    df_risk = df_risk.replace({np.nan: None})
    df_forecast = df_forecast.replace({np.nan: None})
except Exception as e:
    df_risk = pd.DataFrame()
    df_forecast = pd.DataFrame()
    print(f"Warning: Could not load processed data on startup. {e}")

def _get_sku_result(sku_id: str):
    sku_data = df_risk[df_risk['sku_id'] == sku_id]
    if sku_data.empty:
        return {"sku_id": sku_id, "status": "not found"}
        
    sku_info = sku_data.iloc[0].to_dict()
    fcst_data = df_forecast[df_forecast['sku_id'] == sku_id]
    forecast_list = fcst_data[['date', 'model_p10', 'model_p50', 'model_p90']].to_dict(orient="records")
    
    return {
        "sku_id": sku_id,
        "status": "success",
        "category": sku_info.get("category", "Unknown"),
        "on_hand_units": sku_info.get("on_hand_units", 0),
        "lead_time_days": sku_info.get("lead_time_days", 0),
        "risk_quadrant": sku_info.get("quadrant", "Unknown"),
        "rupee_impact": sku_info.get("rupee_impact", 0.0),
        "forecast": forecast_list
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/sku/{sku_id}")
def get_sku_info(sku_id: str):
    if df_risk.empty:
        raise HTTPException(status_code=500, detail="Data not available")
        
    result = _get_sku_result(sku_id)
    if result.get("status") == "not found":
        raise HTTPException(status_code=404, detail="SKU not found")
        
    return result

@app.post("/score")
def score_batch(request: ScoreRequest):
    if df_risk.empty:
        raise HTTPException(status_code=500, detail="Data not available")
        
    results = []
    for sku_id in request.sku_ids:
        results.append(_get_sku_result(sku_id))
    return {"results": results}

@app.get("/risk/stockouts")
def get_top_stockouts(limit: int = 5):
    if df_risk.empty:
        raise HTTPException(status_code=500, detail="Data not available")
        
    stockouts = df_risk[df_risk['quadrant'] == 'Reorder Now'].sort_values('rupee_impact', ascending=False)
    return stockouts.head(limit).to_dict(orient="records")

@app.get("/risk/overstock")
def get_top_overstock(limit: int = 5):
    if df_risk.empty:
        raise HTTPException(status_code=500, detail="Data not available")
        
    overstock = df_risk[df_risk['quadrant'].isin(['Markdown / Clear', 'Dead Stock'])].sort_values('rupee_impact', ascending=False)
    return overstock.head(limit).to_dict(orient="records")
