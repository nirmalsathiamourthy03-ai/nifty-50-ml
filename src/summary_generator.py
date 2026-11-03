"""
Daily EOD Market Summary & Executive Report Generator
Generates structured Markdown reports summarizing daily market settlement,
technical indicator state, and dual ML predictions (Opening Movement & Full Day Direction).
"""

import os
from datetime import datetime
import pandas as pd


def generate_daily_summary(last_day_sample_df: pd.DataFrame, 
                           forecast: dict,
                           output_dir: str = "reports") -> tuple[str, str]:
    """
    Generates a structured daily executive report and saves it to reports/daily_summary_YYYYMMDD.md
    Also returns the markdown text so it can be exported to GitHub Actions step summary or Streamlit.
    """
    os.makedirs(output_dir, exist_ok=True)

    date_str = forecast.get("previous_closed_date", forecast.get("last_closed_date", datetime.now().strftime("%Y-%m-%d")))
    close_price = forecast.get("previous_day_closing_price", forecast.get("last_day_closing_price", 0.0))
    vix_val = forecast.get("current_vix", 0.0)

    # Extract available candle metrics from last_day_sample_df
    open_val = float(last_day_sample_df.get("NIFTY_Open", pd.Series([close_price])).iloc[-1])
    high_val = float(last_day_sample_df.get("NIFTY_High", pd.Series([close_price])).iloc[-1])
    low_val = float(last_day_sample_df.get("NIFTY_Low", pd.Series([close_price])).iloc[-1])
    ret_pct = float(last_day_sample_df.get("NIFTY_Return", pd.Series([0.0])).iloc[-1]) * 100.0
    vix_ret_pct = float(last_day_sample_df.get("VIX_Return", pd.Series([0.0])).iloc[-1]) * 100.0

    # Technical indicators
    rsi_val = float(last_day_sample_df.get("NIFTY_RSI_14", pd.Series([50.0])).iloc[-1])
    macd_hist = float(last_day_sample_df.get("NIFTY_MACD_Hist", pd.Series([0.0])).iloc[-1])
    sma5_dist = float(last_day_sample_df.get("NIFTY_SMA_5_Ratio", pd.Series([0.0])).iloc[-1]) * 100.0
    sma20_dist = float(last_day_sample_df.get("NIFTY_SMA_20_Ratio", pd.Series([0.0])).iloc[-1]) * 100.0

    # Calculate Classic Pivot Points for reference
    pivot = (high_val + low_val + close_price) / 3.0
    r1 = 2 * pivot - low_val
    s1 = 2 * pivot - high_val

    # Opening Movement
    gap_dir = forecast.get("predicted_gap", "GAP UP")
    gap_prob_up = forecast.get("gap_confidence_up_percent", 50.0)
    gap_prob_down = forecast.get("gap_confidence_down_percent", 50.0)
    gap_model = forecast.get("best_gap_model", "Classifier")
    gap_sym = "🔼 GAP UP" if "UP" in gap_dir else "🔽 GAP DOWN"

    # Full Day Movement
    day_dir = forecast.get("predicted_direction", "UP")
    day_prob_up = forecast.get("confidence_up_percent", 50.0)
    day_prob_down = forecast.get("confidence_down_percent", 50.0)
    day_model = forecast.get("best_classification_model", "Classifier")
    day_sym = "🔼 UP" if day_dir == "UP" else "🔽 DOWN"
    strength = forecast.get("signal_strength", "Moderate")

    # Build Markdown
    md = f"""# 📊 NIFTY 50 Daily EOD Market Summary & Forecast
**Session Date:** `{date_str}` | **Generated At:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}`

---

## 📌 1. Official Closing Settlement
| Metric | Value | Reference / Context |
|---|---|---|
| **NIFTY 50 Final Close** | **₹{close_price:,.2f}** | {'+' if ret_pct >= 0 else ''}{ret_pct:.2f}% vs prior day |
| **Day's High / Low** | ₹{high_val:,.2f} / ₹{low_val:,.2f} | Spread: {high_val - low_val:,.2f} pts |
| **Day's Open** | ₹{open_val:,.2f} | Intraday Move: {((close_price - open_val)/open_val)*100.0:+.2f}% |
| **India VIX (Market Fear)** | **{vix_val:.2f}** | {'+' if vix_ret_pct >= 0 else ''}{vix_ret_pct:.2f}% ({'Calm' if vix_val < 15 else 'Volatile'}) |

---

## 🎯 2. Dual Machine Learning Predictions for Next Trading Session

### 🌅 A. Opening Movement Prediction (Overnight Gap)
> Predicts whether tomorrow's session opens **GAP UP** or **GAP DOWN** relative to today's close (₹{close_price:,.2f}).

* **Forecast Verdict:** **{gap_sym}**
* **Probabilities:** **{gap_prob_up:.1f}% GAP UP** vs **{gap_prob_down:.1f}% GAP DOWN**
* **Best Model:** `{gap_model}`

### 📈 B. Full Next Trading Day Direction (Close-to-Close)
> Predicts whether tomorrow's final close finishes **HIGHER (UP)** or **LOWER (DOWN)** compared to today's close.

* **Forecast Verdict:** **{day_sym}**
* **Signal Bias & Strength:** **{strength}**
* **Probabilities:** **{day_prob_up:.1f}% UP** vs **{day_prob_down:.1f}% DOWN**
* **Best Model:** `{day_model}`

---

## 🔬 3. Technical Indicator Health
* **RSI (14-Day):** `{rsi_val:.1f}` — {'Overbought (>70)' if rsi_val > 70 else ('Oversold (<30)' if rsi_val < 30 else 'Neutral Zone (30-70)')}
* **MACD Histogram:** `{macd_hist:+.2f}` — {'Bullish Momentum Acceleration' if macd_hist > 0 else 'Bearish Momentum Deceleration'}
* **5-Day SMA Distance:** `{sma5_dist:+.2f}%` from 5-day trend baseline
* **20-Day SMA Distance:** `{sma20_dist:+.2f}%` from monthly trend baseline

---

## 📐 4. Next Session Technical Pivot Levels (Reference)
* **Resistance 1 (R1):** ₹{r1:,.2f}
* **Central Pivot Point (P):** ₹{pivot:,.2f}
* **Support 1 (S1):** ₹{s1:,.2f}

---
*Note: This report is automatically generated strictly from confirmed End-of-Day (EOD) closing data without live market tick noise.*
"""

    report_filename = f"daily_summary_{date_str.replace('-', '')}.md"
    report_path = os.path.join(output_dir, report_filename)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    latest_path = os.path.join(output_dir, "latest_summary.md")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(md)

    # If running inside GitHub Actions, also append to GITHUB_STEP_SUMMARY
    github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_step_summary and os.path.exists(os.path.dirname(github_step_summary)):
        try:
            with open(github_step_summary, "a", encoding="utf-8") as gf:
                gf.write(md)
        except Exception:
            pass

    print(f"[Summary Generator] Daily EOD summary saved to: {report_path}")
    return report_path, md
