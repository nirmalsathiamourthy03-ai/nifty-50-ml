"""
Data Collection Module
Fetches official historical daily OHLCV data for NIFTY 50 (^NSEI) and India VIX (^INDIAVIX)
from 2010-01-01 up to the latest completed trading session closing price.
"""

import os
from datetime import datetime, time as dtime
import pandas as pd
import yfinance as yf

NIFTY_TICKER = "^NSEI"
VIX_TICKER = "^INDIAVIX"
DEFAULT_START_DATE = "2010-01-01"


def fetch_ticker_data(ticker: str, start_date: str = DEFAULT_START_DATE) -> pd.DataFrame:
    """
    Downloads official daily OHLCV data for a given ticker from start_date to the latest closed session.
    
    Parameters:
    -----------
    ticker : str
        Ticker symbol on Yahoo Finance (e.g. '^NSEI', '^INDIAVIX')
    start_date : str
        Start date formatted as 'YYYY-MM-DD' (default '2010-01-01')
        
    Returns:
    --------
    pd.DataFrame: Cleaned daily OHLCV dataframe indexed by Date.
    """
    print(f"[{ticker}] Downloading official daily OHLCV data from {start_date}...")
    df = yf.download(ticker, start=start_date, progress=False, auto_adjust=False)

    if df.empty:
        raise ValueError(f"Failed to fetch data for ticker '{ticker}'. Please check your network connection.")

    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Standardize expected columns
    expected_cols = ["Open", "High", "Low", "Close", "Volume"]
    available_cols = [c for c in expected_cols if c in df.columns]
    df = df[available_cols].copy()

    # Format Date index
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    df.sort_index(inplace=True)

    # Clean missing values: drop any row where Close is NaN or 0
    df = df.dropna(subset=["Close"])
    df = df[df["Close"] > 0]

    # STRICT RULE: Never include live, incomplete intraday candles!
    # Yahoo Finance appends today's live/partial bar during market hours.
    # Feature engineering MUST be computed based on only the PREVIOUS completed day closing price.
    now = datetime.now()
    today_date = now.date()
    # Market closes at 15:30 IST; official NSE closing settlement is finalized by 15:45 IST
    market_settlement_time = dtime(15, 45)

    if not df.empty and df.index[-1].date() == today_date and now.time() < market_settlement_time:
        live_price = df["Close"].iloc[-1]
        print(f"[{ticker}] Detected active LIVE market session for today ({today_date}) at price: INR {live_price:,.2f}.")
        print(f"[{ticker}] Bypassing live market tick. Using strictly the PREVIOUS COMPLETED trading day closing price.")
        df = df.iloc[:-1].copy()

    latest_date_str = df.index[-1].strftime("%Y-%m-%d")
    latest_close = df["Close"].iloc[-1]
    print(f"[{ticker}] Collected {len(df)} daily sessions. Previous completed day: {latest_date_str} | Official Close: {latest_close:,.2f}")
    return df


def collect_market_data(start_date: str = DEFAULT_START_DATE, 
                        save_raw_path: str = "data/raw_market_data.csv") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Collects both NIFTY 50 and India VIX daily market data and caches the raw data.
    
    Returns:
    --------
    tuple of (nifty_df, vix_df)
    """
    if save_raw_path:
        os.makedirs(os.path.dirname(save_raw_path), exist_ok=True)

    nifty_df = fetch_ticker_data(NIFTY_TICKER, start_date=start_date)
    vix_df = fetch_ticker_data(VIX_TICKER, start_date=start_date)

    if save_raw_path:
        combined_raw = nifty_df.add_prefix("NIFTY_").join(vix_df.add_prefix("VIX_"), how="outer")
        combined_raw.to_csv(save_raw_path)
        print(f"Raw daily market data snapshot saved to: {save_raw_path}")

    return nifty_df, vix_df


if __name__ == "__main__":
    nifty, vix = collect_market_data()
    print("NIFTY last closed session:\n", nifty.tail(2))
    print("VIX last closed session:\n", vix.tail(2))
