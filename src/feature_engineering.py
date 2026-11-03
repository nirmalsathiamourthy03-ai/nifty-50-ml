"""
Feature Engineering Module
Computes technical indicators, returns, rolling volatility, and momentum features
based on daily closing prices to predict the next trading day movement (UP / DOWN).
"""

import time
import os
import pandas as pd
import numpy as np


def compute_returns_and_lags(df: pd.DataFrame, lags: list[int] = [1, 2, 3, 5]) -> pd.DataFrame:
    """
    Computes daily return of NIFTY 50 and India VIX, along with lag returns [1, 2, 3, 5].
    """
    data = df.copy()

    if "NIFTY_Return" not in data.columns:
        data["NIFTY_Return"] = data["NIFTY_Close"].pct_change()
    if "VIX_Return" not in data.columns:
        data["VIX_Return"] = data["VIX_Close"].pct_change()

    for lag in lags:
        data[f"NIFTY_Return_Lag{lag}"] = data["NIFTY_Return"].shift(lag)

    return data


def compute_moving_averages(df: pd.DataFrame, windows: list[int] = [5, 10, 20]) -> pd.DataFrame:
    """
    Computes Simple Moving Averages [5, 10, 20] of NIFTY 50 and percentage distance from SMA.
    """
    data = df.copy()

    for w in windows:
        data[f"NIFTY_SMA_{w}"] = data["NIFTY_Close"].rolling(window=w).mean()
        data[f"NIFTY_SMA_{w}_Ratio"] = (data["NIFTY_Close"] - data[f"NIFTY_SMA_{w}"]) / data[f"NIFTY_SMA_{w}"]

    return data


def compute_rolling_volatility(df: pd.DataFrame, windows: list[int] = [5, 10, 20]) -> pd.DataFrame:
    """
    Computes Rolling Volatility [5, 10, 20] of NIFTY 50 daily returns.
    """
    data = df.copy()

    for w in windows:
        data[f"NIFTY_Vol_{w}"] = data["NIFTY_Return"].rolling(window=w).std()

    return data


def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Computes standard 14-day Relative Strength Index (RSI) of NIFTY 50 based on closing prices.
    """
    data = df.copy()

    delta = data["NIFTY_Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    data[f"NIFTY_RSI_{period}"] = 100.0 - (100.0 / (1.0 + rs))

    return data


def compute_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Computes MACD (12, 26, 9) of NIFTY 50 based on closing prices.
    """
    data = df.copy()

    ema_fast = data["NIFTY_Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = data["NIFTY_Close"].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - signal_line

    data["NIFTY_MACD"] = macd_line
    data["NIFTY_MACD_Signal"] = signal_line
    data["NIFTY_MACD_Hist"] = macd_hist

    return data


def compute_daily_trading_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Daily trading range (absolute points & percentage) of NIFTY 50.
    """
    data = df.copy()

    data["NIFTY_Daily_Range"] = data["NIFTY_High"] - data["NIFTY_Low"]
    data["NIFTY_Daily_Range_Pct"] = (data["NIFTY_High"] - data["NIFTY_Low"]) / data["NIFTY_Open"] * 100.0

    return data


def create_target_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates target variables for dual classification:
    1. Target_Gap_Direction (Opening Movement):
       - 1.0 (GAP UP) if Tomorrow's Open > Today's Close
       - 0.0 (GAP DOWN) if Tomorrow's Open <= Today's Close
    2. Target_Day_Direction (Full Day Movement):
       - 1.0 (UP) if Tomorrow's Close > Today's Close
       - 0.0 (DOWN) if Tomorrow's Close <= Today's Close
    The last completed trading day has NaN for both targets because tomorrow hasn't traded yet.
    """
    data = df.copy()
    next_open = data["NIFTY_Open"].shift(-1)
    next_close = data["NIFTY_Close"].shift(-1)
    
    # 1. Opening Movement Target (Overnight Gap)
    data["Target_Gap_Direction"] = np.where(
        next_open.isna(), np.nan, np.where(next_open > data["NIFTY_Close"], 1.0, 0.0)
    )

    # 2. Full Day Movement Target (Close-to-Close)
    data["Target_Day_Direction"] = np.where(
        next_close.isna(), np.nan, np.where(next_close > data["NIFTY_Close"], 1.0, 0.0)
    )

    # Alias for backwards compatibility
    data["Target_Direction"] = data["Target_Day_Direction"]
    return data


def engineer_features(df: pd.DataFrame, 
                       save_path: str = "data/processed_features.csv") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executes full feature engineering workflow:
    1. Daily return of NIFTY 50 and India VIX
    2. Lag returns [1, 2, 3, 5] of NIFTY 50
    3. Moving average [5, 10, 20] of NIFTY 50 & distance ratios
    4. Rolling Volatility [5, 10, 20] of NIFTY 50
    5. RSI 14 day of NIFTY 50
    6. MACD of NIFTY 50
    7. Daily trading range of NIFTY 50
    8. Function for Target direction (UP / DOWN)
    9. Remove missing values for rolling indicators
    
    Returns:
    --------
    tuple of (historical_dataset, last_day_sample_df):
      - historical_dataset: Historical rows with completed targets ready for model training
      - last_day_sample_df: Feature vector computed from the LAST completed trading day's closing price,
                            used to predict the NEXT trading day movement!
    """
    data = df.copy()

    # Step 1 & 2: Returns and Lags
    data = compute_returns_and_lags(data, lags=[1, 2, 3, 5])

    # Step 3: Moving Averages [5, 10, 20]
    data = compute_moving_averages(data, windows=[5, 10, 20])

    # Step 4: Rolling Volatility [5, 10, 20]
    data = compute_rolling_volatility(data, windows=[5, 10, 20])

    # Step 5: RSI 14
    data = compute_rsi(data, period=14)

    # Step 6: MACD
    data = compute_macd(data, fast=12, slow=26, signal=9)

    # Step 7: Daily Trading Range
    data = compute_daily_trading_range(data)

    # Step 8: Create Target direction variable (UP: 1, DOWN: 0)
    data = create_target_variables(data)

    # Step 9: Isolate last day sample
    # The last row represents the last completed closed trading session.
    # Its features are fully engineered from its closing price, ready to predict the next trading day.
    last_day_sample_df = data.iloc[[-1]].copy()

    feature_cols = [c for c in data.columns if not c.startswith("Target_")]

    if last_day_sample_df[feature_cols].isnull().any().any():
        last_day_sample_df[feature_cols] = last_day_sample_df[feature_cols].bfill().ffill()

    # Training dataset: historical rows with completed features and completed targets
    historical_dataset = data.dropna(subset=feature_cols + ["Target_Gap_Direction", "Target_Day_Direction"]).copy()
    historical_dataset["Target_Gap_Direction"] = historical_dataset["Target_Gap_Direction"].astype(int)
    historical_dataset["Target_Day_Direction"] = historical_dataset["Target_Day_Direction"].astype(int)
    historical_dataset["Target_Direction"] = historical_dataset["Target_Day_Direction"]

    last_closed_date_str = last_day_sample_df.index[-1].strftime("%Y-%m-%d")
    last_close_val = last_day_sample_df["NIFTY_Close"].iloc[-1]
    print(f"Feature engineering complete:")
    print(f"  - Total features generated: {len(feature_cols)}")
    print(f"  - Historical training records: {len(historical_dataset)}")
    print(f"  - Previous completed trading day: {last_closed_date_str} (Official Closing Price: INR {last_close_val:,.2f})")
    print(f"  - Base for predicting NEXT trading day: Features computed strictly from previous day closing price")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        for attempt in range(3):
            try:
                historical_dataset.to_csv(save_path)
                print(f"Processed features saved to: {save_path}")
                break
            except PermissionError:
                time.sleep(0.5)

    return historical_dataset, last_day_sample_df
