"""
End-to-End NIFTY 50 Movement Prediction Pipeline
Orchestrates official EOD data collection, preprocessing, stationary feature engineering,
dual classification model training (Opening Movement + Full Day Direction),
forecasting, and automated daily executive summary generation.
"""

from datetime import datetime
import json
import os
from src.data_collection import collect_market_data
from src.preprocessing import clean_and_align_data
from src.feature_engineering import engineer_features
from src.models import (
    get_classification_features,
    chronological_split,
    train_and_evaluate_classification,
    save_direction_artifacts,
    predict_next_trading_day,
)
from src.summary_generator import generate_daily_summary


def run_pipeline(force_download: bool = False) -> dict:
    """
    Executes the complete Dual Movement Prediction pipeline:
    1. Collects official historical daily data (excludes live session if open).
    2. Cleans and aligns NIFTY 50 and India VIX on common trading calendar.
    3. Engineers 16 stationary features & builds dual targets (Opening Gap & Full Day).
    4. Trains and evaluates dual classifiers (80/20 chronological split).
    5. Predicts next trading day Opening Movement and Full Day Direction.
    6. Generates daily executive summary markdown report.
    """
    start_time = datetime.now()
    print("=" * 75)
    print("    NIFTY 50 NEXT TRADING DAY DUAL MOVEMENT PREDICTION PIPELINE")
    print(f"    Execution Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75)

    # 1. Data Collection
    print("\n[Step 1/5] Collecting Daily Market Data (NIFTY 50 & India VIX)...")
    nifty_df, vix_df = collect_market_data()

    # 2. Preprocessing & Alignment
    print("\n[Step 2/5] Cleaning Data & Aligning Daily Sessions...")
    clean_df = clean_and_align_data(nifty_df, vix_df)

    # 3. Feature Engineering based on Closing Prices
    print("\n[Step 3/5] Computing Technical Indicators & Dual Targets from Daily Closing Prices...")
    hist_df, last_day_sample_df = engineer_features(clean_df)

    clf_features = get_classification_features(hist_df)
    print(f"  - Classification Features ({len(clf_features)}): {', '.join(clf_features[:6])}...")

    # Chronological Split (80/20)
    train_df, test_df = chronological_split(hist_df, train_ratio=0.8)
    print(f"  - Historical Training Window : {len(train_df)} sessions ({train_df.index[0].date()} to {train_df.index[-1].date()})")
    print(f"  - Out-of-Sample Test Window  : {len(test_df)} sessions ({test_df.index[0].date()} to {test_df.index[-1].date()})")

    # 4. Model Training & Evaluation (Dual Targets)
    print("\n[Step 4/5] Training & Benchmarking Dual Classification Models...")
    clf_output = train_and_evaluate_classification(train_df, test_df, clf_features)

    # Save artifacts
    save_direction_artifacts(clf_output, save_dir="models")

    # 5. Live Prediction for the Next Trading Day based on Last Day's Features
    print("\n[Step 5/5] Generating Dual Movement Forecasts & Daily Summary Report...")
    forecast = predict_next_trading_day(last_day_sample_df, models_dir="models")

    # Generate Daily Executive Summary Markdown
    report_path, summary_md = generate_daily_summary(last_day_sample_df, forecast)

    gap_sym = "[+] GAP UP" if "UP" in forecast["predicted_gap"] else "[-] GAP DOWN"
    dir_sym = "[+] UP" if forecast["predicted_direction"] == "UP" else "[-] DOWN"

    print("\n" + "=" * 75)
    print("       NEXT TRADING DAY DUAL MOVEMENT PREDICTION (EOD BASIS)")
    print("=" * 75)
    print(f"  Previous Closed Trading Session: {forecast.get('previous_closed_date', forecast.get('last_closed_date'))}")
    print(f"  Previous Day Final Close Price : INR {forecast.get('previous_day_closing_price', forecast.get('last_day_closing_price')):,.2f}")
    print(f"  Previous Day India VIX Level   : {forecast['current_vix']:.2f}")
    print(f"  Live Market Data Filter        : ACTIVE (Live intraday ticks strictly excluded)")
    print("-" * 75)
    print(f"  [1] OPENING MOVEMENT (GAP)     : {gap_sym}")
    print(f"      Probability & Model        : {forecast['gap_confidence_up_percent']:.1f}% UP vs {forecast['gap_confidence_down_percent']:.1f}% DOWN ({forecast['best_gap_model']})")
    print("-" * 75)
    print(f"  [2] FULL DAY DIRECTION         : {dir_sym}")
    print(f"      Signal Bias & Strength     : {forecast['signal_strength']}")
    print(f"      Probability & Model        : {forecast['confidence_up_percent']:.1f}% UP vs {forecast['confidence_down_percent']:.1f}% DOWN ({forecast['best_classification_model']})")
    print("=" * 75)

    return {
        "status": "success",
        "clf_results": clf_output["all_results"],
        "best_day_model": clf_output["best_model_name"],
        "forecast": forecast,
        "report_path": report_path,
    }


if __name__ == "__main__":
    run_pipeline()
