# 📈 NIFTY 50 Next Trading Day Movement Prediction

A production-grade Machine Learning framework and interactive dashboard dedicated exclusively to forecasting the **Next Trading Day Market Direction (Classification: UP 🔼 / DOWN 🔽)** for the **NIFTY 50 Index (`^NSEI`)**.

---

## 📌 Project Architecture

```
ML nifty_50_pj/
│
├── src/
│   ├── __init__.py               # Package initializer
│   ├── data_collection.py        # Fetches NIFTY 50 (^NSEI) & India VIX (^INDIAVIX) with live quote reconciliation
│   ├── preprocessing.py          # Data cleaning, calendar alignment, and percentage change computation
│   ├── feature_engineering.py    # SMAs, Volatility, RSI, MACD, Trading Range, and Target Direction builder
│   ├── models.py                 # Classification model training, evaluation, and selection (UP / DOWN)
│   ├── pipeline.py               # End-to-end orchestration and next trading day movement forecast
│   └── watcher.py                # Automated observation watcher and auto-retraining service
│
├── data/
│   ├── raw_market_data.csv       # Raw OHLCV snapshot (NIFTY 50 & India VIX)
│   └── processed_features.csv    # 4,113 cleaned trading records with 32 technical features
│
├── models/
│   ├── best_classification_bundle.joblib # Selected Best Direction Model (Gradient Boosting Classifier)
│   ├── classification_scaler.joblib      # Chronologically fitted feature scaler
│   ├── evaluation_results.json           # Classification metrics, confusion matrices, and test predictions
│   ├── latest_forecast.json              # Latest next trading day direction forecast
│   └── model_metadata.json               # Metadata summary and feature registries
│
├── app.py                        # Modern Streamlit interactive directional dashboard
├── run_pipeline.py               # CLI entrypoint to train models and generate forecasts
├── auto_watch.py                 # Background daemon to auto-retrain when new candles appear
├── start_dashboard.bat           # 1-Click Windows launcher for the dashboard
├── start_watcher.bat             # 1-Click Windows launcher for the auto watcher
├── requirements.txt              # Core project dependencies
└── README.md                     # Documentation and mathematical rationale
```

---

## 🚀 Key Features

### 1. Dual Movement Prediction Engine
- **Target 1: Opening Movement (Overnight Gap):**
  $$\text{Target\_Gap\_Direction}_t = \begin{cases} 1 \text{ (GAP UP 🔼)} & \text{if } Open_{t+1} > Close_t \\ 0 \text{ (GAP DOWN 🔽)} & \text{if } Open_{t+1} \le Close_t \end{cases}$$
- **Target 2: Full Next Trading Day Direction (Close-to-Close):**
  $$\text{Target\_Day\_Direction}_t = \begin{cases} 1 \text{ (UP 🔼)} & \text{if } Close_{t+1} > Close_t \\ 0 \text{ (DOWN 🔽)} & \text{if } Close_{t+1} \le Close_t \end{cases}$$
- **Feature Baseline:** All 16 stationary technical features are computed **strictly from the previous completed day's closing price**. Live intraday prices during open market hours are automatically filtered out.

### 2. Technical Indicators Suite
1. **Daily Returns:** Close-to-close returns of NIFTY 50 and India VIX.
2. **Lag Returns:** $[1, 2, 3, 5]$-day lagged returns capturing short-term mean-reversion and momentum.
3. **Simple Moving Averages (SMA):** $5, 10, 20$-day SMAs and stationary percentage distance ratios $\frac{Close - SMA}{SMA}$.
4. **Rolling Volatility:** $5, 10, 20$-day standard deviations of daily returns.
5. **RSI 14-Day:** Standard 14-day Wilder smoothed Relative Strength Index.
6. **MACD (12, 26, 9):** Fast 12-day EMA, slow 26-day EMA, 9-day Signal line, and MACD Histogram.
7. **Daily Trading Range:** Intraday spread $(High - Low)$ and range percentage $\frac{High - Low}{Open} \times 100$.

### 3. Chronological Model Validation
To prevent lookahead bias, training followed a strict **chronological split** (3,290 training samples: 2010–2023, and 823 out-of-sample test samples: 2023–2026). Scalers are fit strictly on training data.

---

## 🧠 Out-of-Sample Leaderboards (823 Test Days)

### 🌅 A. Opening Movement (Overnight Gap) Leaderboard
| Model | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC |
|---|:---:|:---:|:---:|:---:|:---:|
| 🏆 **Random Forest Classifier (Selected)** | **59.78%** | **59.78%** | **100.00%** | **74.83%** | **0.5242** |
| XGBoost Classifier | 59.78% | 59.78% | 100.00% | 74.83% | 0.5192 |
| LightGBM Classifier | 59.78% | 59.78% | 100.00% | 74.83% | 0.5177 |
| Gradient Boosting Classifier | 59.66% | 59.76% | 99.59% | 74.70% | 0.5223 |
| Logistic Regression (Baseline) | 59.30% | 59.58% | 99.19% | 74.45% | 0.5562 |

### 📈 B. Full Day Direction (Close-to-Close) Leaderboard
| Model | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC |
|---|:---:|:---:|:---:|:---:|:---:|
| 🏆 **Random Forest Classifier (Selected)** | **52.49%** | **53.80%** | **68.59%** | **60.30%** | **0.5227** |
| Gradient Boosting Classifier | 52.37% | 53.71% | 68.59% | 60.24% | 0.5197 |
| LightGBM Classifier | 51.76% | 53.23% | 68.59% | 59.94% | 0.5088 |
| XGBoost Classifier | 49.82% | 51.91% | 62.82% | 56.84% | 0.5120 |
| Logistic Regression (Baseline) | 47.75% | 50.26% | 67.90% | 57.76% | 0.4916 |

---

## ⚡ Cloud Automation: GitHub Actions (Runs Even When PC Is Off!)

The repository includes a cloud-native workflow [`.github/workflows/daily_eod_pipeline.yml`](.github/workflows/daily_eod_pipeline.yml):
* **Automatic Schedule:** Runs Monday to Friday at **11:00 UTC (16:30 IST)** on GitHub's cloud servers.
* **Zero Dependency on Local Machine:** Even if your computer is completely shut down or offline, GitHub Actions:
  1. Downloads official daily settlement data once NSE closes.
  2. Bypasses all live ticks and computes 16 features from the closing price.
  3. Retrains both models and generates predictions for the next trading day.
  4. Generates an executive daily markdown report (`reports/latest_summary.md`).
  5. Automatically commits and pushes updated data and forecasts back to your repository (`[skip ci]`).
  6. Displays the full report directly on GitHub Actions Job Summary.

---

## ⚡ End-of-Day (EOD) Quantitative & Automation Workflow

The system is built on **pure End-of-Day (EOD) feature engineering**:
- **No Intraday Noise:** Does not poll or scrape live market ticks during trading hours (09:15 - 15:30 IST).
- **Last Closed Day Reference:** Computes the 16 technical features (SMAs, RSI, MACD, Returns, Volatilities) from the **last completed trading session's official closing price**.
- **Next Day Movement Prediction:** Evaluates whether tomorrow's close will finish **UP 🔼** or **DOWN 🔽** compared to today's close.
- **Automated Post-Market Updates:** Once the market closes and NSE finalizes the official closing settlement (~15:45 IST), the system updates automatically without manual intervention.

---

## 🖥️ How to Run & Automate

### 1. Launch the Interactive Dashboard
Double-click **`start_dashboard.bat`** or run:
```powershell
python -m streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

### 2. Enable Automated Post-Market Daily Updates (Windows Task)
Double-click **`setup_post_market_task.bat`**:
- Registers a native Windows Scheduled Task that executes Monday to Friday at **4:00 PM IST** (30 mins after market close).
- Recalculates features from the new closing price and updates tomorrow's forecast.
- **Runs Even if PC Was Powered Off:** If your computer was off at 4:00 PM, it will automatically execute as soon as you power it on!

### 3. Run Standalone EOD Watcher Daemon
Double-click **`start_watcher.bat`** or run:
```powershell
python auto_watch.py
```
*Sleeps during live trading hours and triggers automatically once the daily settlement is published.*

### 4. Run Model Training Pipeline Manually via CLI
```powershell
python run_pipeline.py
```

### 5. Push to GitHub to Activate 24/7 Cloud Automation
1. Create a new empty repository on your GitHub account (e.g. `nifty50-ml-prediction`).
2. Double-click **`push_to_github.bat`** and paste your GitHub repository URL (or run in terminal):
   ```powershell
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```
3. **Done!** GitHub Actions is immediately activated. Every weekday at **16:30 IST**, GitHub's cloud runners will execute your pipeline, update your datasets, re-train models, and commit the daily forecast reports automatically.

### 6. Open the Complete Jupyter Notebook
```powershell
jupyter notebook nifty50_movement_prediction_backend.ipynb
```
