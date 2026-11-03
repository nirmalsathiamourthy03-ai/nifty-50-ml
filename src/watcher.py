"""
End-of-Day (EOD) Post-Market Observation Watcher & Auto-Retraining Service
Monitors NIFTY 50 and India VIX after market close (post 3:30 PM IST), detects when the official
closing settlement candle is finalized, and automatically triggers the end-to-end retraining pipeline.
Strictly ignores live intraday market fluctuations during trading hours.
"""

import os
import sys
import json
import time
from datetime import datetime, time as dtime, timedelta
import pandas as pd
import yfinance as yf
from src.pipeline import run_pipeline

FORECAST_FILE = os.path.join("models", "latest_forecast.json")
NIFTY_TICKER = "^NSEI"
VIX_TICKER = "^INDIAVIX"
MARKET_CLOSE_TIME = dtime(15, 30)       # 3:30 PM IST (Cash market close)
SETTLEMENT_CHECK_TIME = dtime(15, 45)   # 3:45 PM IST (Official closing settlement available)


def get_current_model_state() -> dict:
    """Reads the last observation date and closing price recorded in the active model forecast."""
    if os.path.exists(FORECAST_FILE):
        try:
            with open(FORECAST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_closed_date": "1970-01-01", "last_day_closing_price": 0.0}


def is_market_open_now(dt: datetime = None) -> bool:
    """
    Checks if the given time is within active market trading hours on a weekday.
    NSE Market Hours: Monday to Friday, 09:15 to 15:30 IST.
    """
    if dt is None:
        dt = datetime.now()
    # Weekends (Saturday=5, Sunday=6) are closed
    if dt.weekday() >= 5:
        return False
    market_open = dtime(9, 15)
    market_close = dtime(15, 30)
    return market_open <= dt.time() < market_close


def get_seconds_until_next_eod_check(now: datetime = None) -> tuple[int, datetime]:
    """
    Calculates seconds remaining until the next post-market settlement check (15:45 IST).
    If it's already past 15:45 today, targets tomorrow 15:45 (or Monday if Friday/weekend).
    """
    if now is None:
        now = datetime.now()

    target_today = datetime.combine(now.date(), SETTLEMENT_CHECK_TIME)

    if now.time() < SETTLEMENT_CHECK_TIME and now.weekday() < 5:
        # Before 15:45 today on a weekday -> target today 15:45
        target = target_today
    else:
        # After 15:45 today or on a weekend -> find next weekday at 15:45
        days_ahead = 1
        next_day = now + timedelta(days=days_ahead)
        while next_day.weekday() >= 5:  # Skip Saturday and Sunday
            days_ahead += 1
            next_day = now + timedelta(days=days_ahead)
        target = datetime.combine(next_day.date(), SETTLEMENT_CHECK_TIME)

    seconds = max(60, int((target - now).total_seconds()))
    return seconds, target


def check_for_new_eod_observation(ticker: str = NIFTY_TICKER, force: bool = False) -> tuple[bool, dict]:
    """
    Checks if an official, completed End-Of-Day daily candle is published and newer
    than the model's recorded observation date.
    
    Strictly ignores live intraday ticks during market hours (09:15 - 15:30 IST).
    Only checks official daily ('1d') bars.
    """
    model_state = get_current_model_state()
    saved_date = model_state.get("last_closed_date", model_state.get("as_of_date", "1970-01-01"))
    saved_close = float(model_state.get("last_day_closing_price", model_state.get("current_nifty_close", 0.0)))

    now = datetime.now()

    # Rule 1: Never trigger during live market hours unless forced
    if is_market_open_now(now) and not force:
        return False, {
            "status": "market_open",
            "message": "Market is currently in active session (09:15 - 15:30 IST). Live updates are skipped to preserve pure EOD integrity.",
            "saved_date": saved_date,
            "saved_close": saved_close
        }

    try:
        t = yf.Ticker(ticker)
        # Fetch strictly daily ('1d') bars - no 60m, no fast_info
        h = t.history(period="10d", interval="1d", auto_adjust=False)
        if h.empty:
            return False, {"error": "No daily data returned from ticker feed"}

        h.index = pd.to_datetime(h.index).tz_localize(None)
        h = h.dropna(subset=["Close"])
        h = h[h["Close"] > 0]

        latest_daily_date = h.index[-1].strftime("%Y-%m-%d")
        latest_daily_close = float(h["Close"].iloc[-1])

        today_str = now.strftime("%Y-%m-%d")
        is_today_weekday = now.weekday() < 5
        is_post_close = now.time() >= MARKET_CLOSE_TIME

        is_new_day = latest_daily_date > saved_date
        is_settlement_adjustment = (latest_daily_date == saved_date) and (abs(latest_daily_close - saved_close) > 0.5) and is_post_close

        is_new = is_new_day or is_settlement_adjustment or force

        details = {
            "saved_date": saved_date,
            "saved_close": saved_close,
            "latest_market_date": latest_daily_date,
            "latest_market_close": round(latest_daily_close, 2),
            "is_new_day": is_new_day,
            "is_settlement_adjustment": is_settlement_adjustment,
            "price_diff": round(latest_daily_close - saved_close, 2),
            "today_date": today_str,
            "awaiting_today_settlement": (is_today_weekday and is_post_close and latest_daily_date < today_str)
        }

        return is_new, details

    except Exception as e:
        return False, {"error": str(e)}


def auto_update_eod_if_needed(force: bool = False) -> bool:
    """
    Checks if a new official EOD observation exists after market close.
    If so, triggers the full pipeline with feature engineering computed from the closing price.
    """
    is_new, details = check_for_new_eod_observation(force=force)

    if details.get("status") == "market_open":
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {details.get('message')}")
        return False

    if is_new or force:
        print("\n" + "=" * 75)
        print(" [EOD AUTO-UPDATER] NEW OFFICIAL CLOSING OBSERVATION DETECTED!")
        print(f"   Previous Recorded Session : {details.get('saved_date')} (Close: INR {details.get('saved_close'):,.2f})")
        print(f"   New Finalized EOD Session : {details.get('latest_market_date')} (Close: INR {details.get('latest_market_close'):,.2f})")
        print("   Action: Recalculating 16 Technical Features from End Closing Price...")
        print("   Action: Retraining Direction Classifiers & Forecasting Next Day Movement...")
        print("=" * 75)

        run_pipeline(force_download=True)
        print("\n[EOD AUTO-UPDATER] Next trading day forecast refreshed from finalized closing price!\n")
        return True
    else:
        if details.get("awaiting_today_settlement"):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Market closed today ({details.get('today_date')}), but official daily candle is still processing on exchange feed. Will check again shortly.")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Model is up-to-date with last closed session: {details.get('saved_date')} (Close: INR {details.get('saved_close'):,.2f})")
        return False


def start_market_watcher():
    """
    Runs the End-of-Day (EOD) observation watcher daemon.
    Smart scheduling:
      - If market is open: sleeps until market close (15:45 IST).
      - After 15:45 IST: checks for the official EOD daily bar.
      - Once updated: sleeps until the next trading day's close (zero CPU, zero intraday polling).
    """
    print("=" * 75)
    print("  NIFTY 50 END-OF-DAY (EOD) POST-MARKET OBSERVATION WATCHER")
    print(f"  Mode             : Pure EOD Feature Engineering (No Live Market Polling)")
    print(f"  Market Hours     : 09:15 to 15:30 IST (Skipped during live session)")
    print(f"  Target Update    : Post-Market Settlement (~15:45 IST)")
    print(f"  Started At       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75)

    # Initial check upon startup
    auto_update_eod_if_needed()

    while True:
        try:
            now = datetime.now()
            if is_market_open_now(now):
                # Market is open: calculate time until 15:45 IST and sleep
                secs_to_close, target_dt = get_seconds_until_next_eod_check(now)
                hrs = secs_to_close // 3600
                mins = (secs_to_close % 3600) // 60
                print(f"[{now.strftime('%H:%M:%S')}] Market is actively trading. Sleeping {hrs}h {mins}m until post-market check at {target_dt.strftime('%H:%M')} IST...")
                time.sleep(secs_to_close)
            else:
                # Post market or weekend
                updated = auto_update_eod_if_needed()
                if updated:
                    # Successfully updated for today's session! Sleep until tomorrow's close
                    secs_to_next, target_dt = get_seconds_until_next_eod_check(datetime.now())
                    hrs = secs_to_next // 3600
                    mins = (secs_to_next % 3600) // 60
                    print(f"Today's EOD update complete. Next check scheduled at {target_dt.strftime('%Y-%m-%d %H:%M')} IST (in {hrs}h {mins}m). Sleeping...")
                    time.sleep(secs_to_next)
                else:
                    # If awaiting today's settlement, sleep 5 minutes (300s) and retry
                    model_state = get_current_model_state()
                    saved_date = model_state.get("last_closed_date", "")
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    is_today_weekday = datetime.now().weekday() < 5
                    is_post_close = datetime.now().time() >= MARKET_CLOSE_TIME

                    if is_today_weekday and is_post_close and saved_date < today_str:
                        # Waiting for today's exchange feed to sync
                        print(f"Waiting 5 minutes (300s) for today's ({today_str}) exchange settlement to appear on Yahoo Finance...")
                        time.sleep(300)
                    else:
                        # Already up-to-date, sleep until next trading day's close
                        secs_to_next, target_dt = get_seconds_until_next_eod_check(datetime.now())
                        hrs = secs_to_next // 3600
                        mins = (secs_to_next % 3600) // 60
                        print(f"Model is current. Next check scheduled at {target_dt.strftime('%Y-%m-%d %H:%M')} IST (in {hrs}h {mins}m). Sleeping...")
                        time.sleep(secs_to_next)

        except KeyboardInterrupt:
            print("\n[EOD Watcher] Stopped by user.")
            break
        except Exception as e:
            print(f"[EOD Watcher] Exception: {e}. Retrying in 60 seconds...")
            time.sleep(60)


if __name__ == "__main__":
    start_market_watcher()
