"""
Preprocessing Module
Cleans collected NIFTY 50 and India VIX daily market data, aligns trading calendar,
handles missing values, and computes core percentage changes.
"""

import pandas as pd
import numpy as np


def clean_and_align_data(nifty_df: pd.DataFrame, vix_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and merges NIFTY 50 and India VIX daily dataframes on date index.
    
    Parameters:
    -----------
    nifty_df : pd.DataFrame
        Daily OHLCV data for NIFTY 50 (^NSEI)
    vix_df : pd.DataFrame
        Daily OHLCV data for India VIX (^INDIAVIX)
        
    Returns:
    --------
    pd.DataFrame: Aligned and cleaned dataframe with standardized column names.
    """
    nifty_clean = nifty_df[["Open", "High", "Low", "Close", "Volume"]].copy()
    nifty_clean.columns = [f"NIFTY_{col}" for col in nifty_clean.columns]

    vix_clean = vix_df[["Open", "High", "Low", "Close"]].copy()
    vix_clean.columns = [f"VIX_{col}" for col in vix_clean.columns]

    # Align on NIFTY calendar dates
    merged_df = nifty_clean.join(vix_clean, how="left")
    merged_df.sort_index(inplace=True)

    # Impute any single-day missing VIX values via forward fill
    merged_df = merged_df.ffill().bfill()

    print(f"Data alignment complete: {len(merged_df)} daily sessions from {merged_df.index[0].date()} to {merged_df.index[-1].date()}.")
    return merged_df


def compute_percentage_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes standard daily returns and percentage changes for NIFTY 50 and India VIX.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Aligned daily market dataframe.
        
    Returns:
    --------
    pd.DataFrame: DataFrame with percentage change columns added.
    """
    data = df.copy()

    # 1. Daily close-to-close returns
    data["NIFTY_Return"] = data["NIFTY_Close"].pct_change()
    data["VIX_Return"] = data["VIX_Close"].pct_change()

    # 2. Daily Intraday percentage change (Open to Close)
    data["NIFTY_Intraday_Return"] = (data["NIFTY_Close"] - data["NIFTY_Open"]) / data["NIFTY_Open"]

    # 3. Overnight Gap percentage change (Previous Close to Today's Open)
    data["NIFTY_Gap_Return"] = (data["NIFTY_Open"] - data["NIFTY_Close"].shift(1)) / data["NIFTY_Close"].shift(1)

    return data


def preprocess_pipeline(nifty_df: pd.DataFrame, vix_df: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing execution pipeline.
    """
    aligned = clean_and_align_data(nifty_df, vix_df)
    preprocessed = compute_percentage_changes(aligned)
    return preprocessed
