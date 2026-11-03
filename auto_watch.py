"""
NIFTY 50 Post-Market End-of-Day (EOD) Observation Auto-Updater
Triggers strictly after market close (post 3:30 PM IST) when the official daily
closing price is published. Computes 16 technical features from the end closing price.

Usage:
    python auto_watch.py           # Runs the smart post-market scheduler daemon
    python auto_watch.py --once    # Checks once and exits (used by Windows Task Scheduler)
    python auto_watch.py --force   # Forces immediate re-download, feature engineering & retraining
"""

import sys
from src.watcher import start_market_watcher, auto_update_eod_if_needed

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--once" in args:
        print("[EOD Auto-Updater] Performing single post-market check...")
        auto_update_eod_if_needed(force=False)
    elif "--force" in args:
        print("[EOD Auto-Updater] Forcing immediate EOD recalculation and model retraining...")
        auto_update_eod_if_needed(force=True)
    else:
        start_market_watcher()
