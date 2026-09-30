import sys
import os

def main():
    print("=" * 60)
    print(" PROJECT FORESIGHT - End-to-End Orchestrator ")
    print("=" * 60)

    # 1. Run Data Ingestion & Quality Pipeline
    print("\n--- PHASE 1: Data Pipeline & Quality Audit ---")
    from src.pipeline import run_pipeline
    run_pipeline()

    print("\n[SUCCESS] Phase 1 completed successfully.")

    # 2. Run EDA & Baseline Forecast
    print("\n--- PHASE 2: EDA & Baseline Model ---")
    from src.eda import run_eda
    run_eda()
    
    from src.forecast_baseline import run_baseline_forecast
    run_baseline_forecast()
    
    print("\n[SUCCESS] Phase 2 completed successfully.")

    # 3. Run Phase 3 Features, Tests, and Backtest
    print("\n--- PHASE 3: Features & Model Backtest ---")
    
    print("Running no-leakage unit tests...")
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_no_leakage.py", "-v"], capture_output=True, text=True)
    if result.returncode != 0:
        print("FAILED: Feature leakage detected or test failed!")
        print(result.stdout)
        print(result.stderr)
        return
    print("Unit tests passed: No future data leakage verified.")
    
    from src.forecast_model import run_model_backtest
    run_model_backtest()
    
    print("\nRunning Sensitivity Check...")
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "src.run_sensitivity"])
    
    print("\n[SUCCESS] Phase 3 completed successfully.")

    # 4. Phase 4: Risk Scoring
    print("\n--- PHASE 4: Risk Scoring ---")
    from src.risk import run_risk_scoring
    run_risk_scoring()
    print("\n[SUCCESS] Phase 4 completed successfully.")



if __name__ == "__main__":
    main()
