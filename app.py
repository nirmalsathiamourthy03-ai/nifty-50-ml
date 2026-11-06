"""
NIFTY 50 Next Trading Day Movement Prediction Engine
Interactive Streamlit Dashboard
Predicts next trading day movement (UP / DOWN) based on feature engineering from the last day closing price.
"""

import os
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="NIFTY 50 Direction Predictor | ML Movement Forecast",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-box {
        background: linear-gradient(135deg, #1e222d 0%, #2a2e39 100%);
        border: 1px solid #363c4e;
        border-radius: 10px;
        padding: 16px 20px;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9aa0a6;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.85rem;
        margin-top: 4px;
    }
    .badge-up {
        background-color: rgba(38, 166, 154, 0.25);
        color: #26a69a;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        border: 1px solid #26a69a;
        display: inline-block;
        font-size: 1.1rem;
    }
    .badge-down {
        background-color: rgba(239, 83, 80, 0.25);
        color: #ef5350;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        border: 1px solid #ef5350;
        display: inline-block;
        font-size: 1.1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def load_datasets():
    """Loads processed features if available."""
    processed_path = "data/processed_features.csv"
    if os.path.exists(processed_path):
        df = pd.read_csv(processed_path, index_col="Date", parse_dates=True)
        return df
    return None


@st.cache_data(ttl=60)
def load_evaluation_artifacts():
    """Loads classification model evaluation results and latest forecast."""
    eval_path = "models/evaluation_results.json"
    forecast_path = "models/latest_forecast.json"

    eval_data = None
    forecast_data = None

    if os.path.exists(eval_path):
        with open(eval_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

    if os.path.exists(forecast_path):
        with open(forecast_path, "r", encoding="utf-8") as f:
            forecast_data = json.load(f)

    return eval_data, forecast_data


# Sidebar Configuration
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/National_Stock_Exchange_of_India_Logo.svg", width=160)
st.sidebar.title("NIFTY 50 ML Studio")
st.sidebar.caption("Next Trading Day Movement Prediction")
st.sidebar.markdown("---")

df_data = load_datasets()
eval_data, forecast = load_evaluation_artifacts()

if df_data is None or eval_data is None or forecast is None:
    st.warning("Model artifacts or processed data not found. Please click below to train models.")
    if st.button("🚀 Train Models on Historical Data"):
        with st.spinner("Downloading data from 2010 to last closed session, engineering features, and training models..."):
            from src.pipeline import run_pipeline
            run_pipeline()
            st.rerun()
    st.stop()

# Sidebar summary controls
last_date = forecast.get("last_closed_date", forecast.get("as_of_date"))
last_close = forecast.get("last_day_closing_price", forecast.get("current_nifty_close"))
best_model_name = forecast["best_classification_model"]

st.sidebar.subheader("📅 Model & Data Summary")
st.sidebar.write(f"**Previous Completed Day:** `{last_date}`")
st.sidebar.write(f"**Previous Day Closing Price:** ₹`{last_close:,.2f}`")
st.sidebar.write(f"**Historical Records:** `{len(df_data):,}` days")
st.sidebar.write(f"**Best Model Selected:** `{best_model_name}`")
st.sidebar.write(f"**Live Market Updates:** `Disabled (EOD Only)`")

if st.sidebar.button("🔄 Retrain / Sync with Latest Closed Session"):
    with st.spinner("Fetching latest completed daily session and updating models..."):
        from src.pipeline import run_pipeline
        run_pipeline(force_download=True)
        st.cache_data.clear()
        st.sidebar.success("Updated successfully!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
**Methodology:**
- **Goal:** Predict next trading day movement (**UP 🔼 / DOWN 🔽**) relative to the previous completed trading day's closing price.
- **Features:** 16 technical indicators computed strictly from previous day closing prices (Returns, Lags, Moving Average Ratios, Rolling Volatilities, RSI 14, MACD).
- **Live Market Feeds:** Strictly excluded during market hours to prevent partial candle distortion.
- **Validation:** Chronological out-of-sample split (no future data leakage).
""")

# --- Top Hero Banner ---
direction = forecast["predicted_direction"]
is_up = direction == "UP"
conf_up = forecast["confidence_up_percent"]
conf_down = forecast["confidence_down_percent"]
strength = forecast.get("signal_strength", "Moderate")
vix_val = forecast["current_vix"]

st.title("📈 NIFTY 50 Next Trading Day Movement Prediction")
st.caption(f"Machine Learning classification predicting whether NIFTY 50 will move UP or DOWN on the next trading day compared with the previous completed day's closing price (₹{last_close:,.2f} on {last_date}). Live market updates are excluded.")

# Extract dual forecast metrics
pred_gap = forecast.get("predicted_gap", "GAP UP")
gap_is_up = "UP" in pred_gap
gap_conf_up = forecast.get("gap_confidence_up_percent", 50.0)
gap_conf_down = forecast.get("gap_confidence_down_percent", 50.0)
best_gap_model = forecast.get("best_gap_model", best_model_name)

# Top KPI Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">Previous Closed Day</div>
        <div class="metric-val">₹{last_close:,.2f}</div>
        <div class="metric-sub" style="color: #9aa0a6;">Session Date: {last_date}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    gap_badge_cls = "badge-up" if gap_is_up else "badge-down"
    gap_dir_label = "▲ GAP UP" if gap_is_up else "▼ GAP DOWN"
    gap_dir_color = "#26a69a" if gap_is_up else "#ef5350"
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">🌅 Opening Movement (Gap)</div>
        <div class="metric-val" style="color: {gap_dir_color}; font-size: 1.55rem;">{gap_dir_label}</div>
        <div class="metric-sub"><span class="{gap_badge_cls}">{gap_conf_up if gap_is_up else gap_conf_down:.1f}% Probability</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    badge_cls = "badge-up" if is_up else "badge-down"
    dir_label = "▲ UP" if is_up else "▼ DOWN"
    dir_color = "#26a69a" if is_up else "#ef5350"
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">📈 Full Day Direction</div>
        <div class="metric-val" style="color: {dir_color}; font-size: 1.55rem;">{dir_label}</div>
        <div class="metric-sub"><span class="{badge_cls}">{conf_up if is_up else conf_down:.1f}% Probability</span></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    vix_badge = "Low Volatility (Calm)" if vix_val < 15 else ("Moderate Volatility" if vix_val < 20 else "Elevated Risk")
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">India VIX (Market Vol)</div>
        <div class="metric-val">{vix_val:.2f}</div>
        <div class="metric-sub" style="color: #ffb74d;">{vix_badge}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    latest_rsi = df_data["NIFTY_RSI_14"].iloc[-1]
    rsi_state = "Overbought" if latest_rsi > 70 else ("Oversold" if latest_rsi < 30 else "Neutral Momentum")
    rsi_color = "#ef5350" if latest_rsi > 70 else ("#26a69a" if latest_rsi < 30 else "#9aa0a6")
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">14-Day RSI (at Close)</div>
        <div class="metric-val" style="color: {rsi_color};">{latest_rsi:.1f}</div>
        <div class="metric-sub" style="color: {rsi_color};">{rsi_state}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- TABS FOR WORKFLOW ---
tab_forecast, tab_summary, tab_charts, tab_models, tab_eval, tab_data = st.tabs([
    "🎯 Dual Movement Predictions",
    "📋 Daily EOD Executive Report",
    "📊 Technical Charts & Indicators",
    "🏆 Model Leaderboards (Gap & Day)",
    "🔬 Evaluation & Diagnostics",
    "💾 Data Explorer & Feature Insights"
])

# ==============================================================================
# TAB 1: DUAL MOVEMENT PREDICTIONS
# ==============================================================================
with tab_forecast:
    st.subheader("🎯 Next Trading Day Dual Movement Predictions")

    mcol1, mcol2 = st.columns(2)

    with mcol1:
        st.markdown(f"""
        <div style="background: rgba(30,34,45,0.7); border: 1px solid #363c4e; border-radius: 8px; padding: 18px 22px;">
            <h3 style="margin-top:0;">🌅 1. Opening Movement (Overnight Gap)</h3>
            <p><strong>Question:</strong> Will tomorrow open <strong>HIGHER</strong> or <strong>LOWER</strong> than today's close (₹{last_close:,.2f})?</p>
            <p style="font-size: 1.25rem;"><strong>Verdict:</strong> <span class="{'badge-up' if gap_is_up else 'badge-down'}">{pred_gap}</span></p>
            <p><strong>Probabilities:</strong> <span style="color:#26a69a; font-weight:700;">{gap_conf_up:.1f}% GAP UP</span> vs <span style="color:#ef5350; font-weight:700;">{gap_conf_down:.1f}% GAP DOWN</span></p>
            <p style="color:#9aa0a6; margin-bottom:0;"><strong>Champion Model:</strong> {best_gap_model}</p>
        </div>
        """, unsafe_allow_html=True)

    with mcol2:
        st.markdown(f"""
        <div style="background: rgba(30,34,45,0.7); border: 1px solid #363c4e; border-radius: 8px; padding: 18px 22px;">
            <h3 style="margin-top:0;">📈 2. Full Day Movement (Close-to-Close)</h3>
            <p><strong>Question:</strong> Will tomorrow's close finish <strong>HIGHER</strong> or <strong>LOWER</strong> than today's close?</p>
            <p style="font-size: 1.25rem;"><strong>Verdict:</strong> <span class="{'badge-up' if is_up else 'badge-down'}">{direction}</span> ({strength})</p>
            <p><strong>Probabilities:</strong> <span style="color:#26a69a; font-weight:700;">{conf_up:.1f}% UP</span> vs <span style="color:#ef5350; font-weight:700;">{conf_down:.1f}% DOWN</span></p>
            <p style="color:#9aa0a6; margin-bottom:0;"><strong>Champion Model:</strong> {best_model_name}</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    fcol1, fcol2 = st.columns([1.1, 1])

    with fcol1:
        st.markdown(f"""
        #### 💡 How Dual Predictions Work:
        1. All 16 technical indicators (SMAs, RSI, MACD, Volatility, Lags) are calculated up to the **previous completed day's closing price (₹{last_close:,.2f})**.
        2. **Opening Movement Engine:** Classifies the overnight sentiment jump (`Target_Gap_Direction`: $Open_{{t+1}} > Close_t$).
        3. **Full Day Movement Engine:** Classifies the full session trend (`Target_Day_Direction`: $Close_{{t+1}} > Close_t$).
        4. No live intraday ticks are used; predictions remain fixed until today's session officially settles post-3:30 PM.
        """)

    with fcol2:
        prob_summary_df = pd.DataFrame({
            "Prediction": ["Opening Gap", "Opening Gap", "Full Day", "Full Day"],
            "Outcome": ["GAP UP 🔼", "GAP DOWN 🔽", "UP 🔼", "DOWN 🔽"],
            "Probability (%)": [gap_conf_up, gap_conf_down, conf_up, conf_down]
        })
        fig_prob = px.bar(
            prob_summary_df,
            x="Outcome",
            y="Probability (%)",
            color="Outcome",
            color_discrete_map={
                "GAP UP 🔼": "#26a69a", "GAP DOWN 🔽": "#ef5350",
                "UP 🔼": "#26a69a", "DOWN 🔽": "#ef5350"
            },
            text="Probability (%)",
            height=280
        )
        fig_prob.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_prob.update_layout(
            yaxis_range=[0, 100],
            showlegend=False,
            margin=dict(l=20, r=20, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_prob, use_container_width=True)

    st.markdown("---")
    st.subheader(f"🧭 Supporting Technical Indicators (Calculated from Close on {last_date})")

    scol1, scol2, scol3, scol4 = st.columns(4)
    with scol1:
        sma5 = df_data["NIFTY_SMA_5"].iloc[-1]
        sma20 = df_data["NIFTY_SMA_20"].iloc[-1]
        sma_bias = "Bullish (Above 5 & 20 SMA)" if last_close > sma5 and last_close > sma20 else ("Bearish" if last_close < sma5 and last_close < sma20 else "Neutral")
        st.metric("5-Day / 20-Day SMA", f"{sma5:,.0f} / {sma20:,.0f}", sma_bias)

    with scol2:
        macd_val = df_data["NIFTY_MACD"].iloc[-1]
        macd_sig = df_data["NIFTY_MACD_Signal"].iloc[-1]
        macd_hist = df_data["NIFTY_MACD_Hist"].iloc[-1]
        macd_bias = "Bullish Momentum" if macd_hist > 0 else "Bearish Momentum"
        st.metric("MACD Line / Signal", f"{macd_val:.1f} / {macd_sig:.1f}", f"{macd_bias} ({macd_hist:.1f})")

    with scol3:
        vol10 = df_data["NIFTY_Vol_10"].iloc[-1] * 100
        st.metric("10-Day Realized Volatility", f"{vol10:.2f}%", f"{df_data['NIFTY_Vol_20'].iloc[-1]*100:.2f}% (20D Vol)")

    with scol4:
        daily_rng = df_data["NIFTY_Daily_Range"].iloc[-1]
        rng_pct = df_data["NIFTY_Daily_Range_Pct"].iloc[-1]
        st.metric("Previous Day Range", f"{daily_rng:,.1f} pts", f"{rng_pct:.2f}% of Open")


# ==============================================================================
# TAB 2: DAILY EOD EXECUTIVE REPORT
# ==============================================================================
with tab_summary:
    st.subheader("📋 Daily EOD Market Summary & Executive Report")

    summary_path = "reports/latest_summary.md"
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_content = f.read()

        st.markdown(summary_content)

        st.download_button(
            label="📥 Download Daily Summary Report (Markdown)",
            data=summary_content,
            file_name=f"nifty50_daily_summary_{last_date.replace('-', '')}.md",
            mime="text/markdown"
        )
    else:
        st.info("No daily summary report generated yet. Click 'Retrain / Sync with Latest Closed Session' in the sidebar to generate today's report.")


    with scol4:
        ret_1d = df_data["NIFTY_Return"].iloc[-1] * 100
        ret_lag1 = df_data["NIFTY_Return_Lag1"].iloc[-1] * 100
        st.metric("Last Day Return", f"{ret_1d:+.2f}%", f"Lag-1: {ret_lag1:+.2f}%")


# ==============================================================================
# TAB 2: TECHNICAL CHARTS & INDICATORS
# ==============================================================================
with tab_charts:
    st.subheader("📊 Interactive Technical Charting Studio")

    timeframe = st.radio(
        "Select Time Horizon:",
        ["3 Months", "6 Months", "1 Year", "3 Years", "All Historical (2010-Today)"],
        horizontal=True,
        index=2
    )

    now = df_data.index[-1]
    if timeframe == "3 Months":
        plot_df = df_data.loc[now - pd.DateOffset(months=3):]
    elif timeframe == "6 Months":
        plot_df = df_data.loc[now - pd.DateOffset(months=6):]
    elif timeframe == "1 Year":
        plot_df = df_data.loc[now - pd.DateOffset(years=1):]
    elif timeframe == "3 Years":
        plot_df = df_data.loc[now - pd.DateOffset(years=3):]
    else:
        plot_df = df_data

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=("NIFTY 50 Daily OHLC & Moving Averages (5, 10, 20)", "Trading Volume", "14-Day RSI", "MACD (12, 26, 9)"),
        row_heights=[0.5, 0.15, 0.17, 0.18]
    )

    fig.add_trace(go.Candlestick(
        x=plot_df.index,
        open=plot_df["NIFTY_Open"],
        high=plot_df["NIFTY_High"],
        low=plot_df["NIFTY_Low"],
        close=plot_df["NIFTY_Close"],
        name="NIFTY 50 OHLC",
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["NIFTY_SMA_5"], line=dict(color="#29b6f6", width=1.2), name="SMA 5"), row=1, col=1)
    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["NIFTY_SMA_10"], line=dict(color="#ffa726", width=1.2), name="SMA 10"), row=1, col=1)
    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["NIFTY_SMA_20"], line=dict(color="#ab47bc", width=1.5), name="SMA 20"), row=1, col=1)

    vol_colors = ["#26a69a" if c >= o else "#ef5350" for c, o in zip(plot_df["NIFTY_Close"], plot_df["NIFTY_Open"])]
    fig.add_trace(go.Bar(x=plot_df.index, y=plot_df["NIFTY_Volume"], marker_color=vol_colors, name="Volume"), row=2, col=1)

    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["NIFTY_RSI_14"], line=dict(color="#e040fb", width=1.5), name="RSI 14"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=3, col=1)

    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["NIFTY_MACD"], line=dict(color="#42a5f5", width=1.2), name="MACD"), row=4, col=1)
    fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["NIFTY_MACD_Signal"], line=dict(color="#ff7043", width=1.2), name="Signal"), row=4, col=1)
    hist_colors = ["#26a69a" if h >= 0 else "#ef5350" for h in plot_df["NIFTY_MACD_Hist"]]
    fig.add_trace(go.Bar(x=plot_df.index, y=plot_df["NIFTY_MACD_Hist"], marker_color=hist_colors, name="Histogram"), row=4, col=1)

    fig.update_layout(
        height=850,
        xaxis_rangeslider_visible=False,
        margin=dict(l=30, r=30, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 India VIX & Daily Range")
    vcol1, vcol2 = st.columns(2)
    with vcol1:
        fig_vix = px.line(plot_df, x=plot_df.index, y="VIX_Close", title="India VIX Volatility Index", color_discrete_sequence=["#ffca28"])
        fig_vix.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_vix, use_container_width=True)
    with vcol2:
        fig_rng = px.line(plot_df, x=plot_df.index, y="NIFTY_Daily_Range", title="NIFTY 50 Daily Trading Range (Points)", color_discrete_sequence=["#26c6da"])
        fig_rng.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_rng, use_container_width=True)


# ==============================================================================
# TAB 4: MODEL LEADERBOARDS (GAP & DAY)
# ==============================================================================
with tab_models:
    st.subheader("🏆 Dual Model Comparison & Leaderboard")
    st.caption("Rigorous evaluation on chronological out-of-sample test split (823 trading days).")

    subtab_gap, subtab_day = st.tabs(["🌅 Opening Movement (Gap) Leaderboard", "📈 Full Day Movement Leaderboard"])

    with subtab_gap:
        if "opening_gap" in eval_data:
            gap_metrics = eval_data["opening_gap"]["metrics"]
            gap_df = pd.DataFrame.from_dict(gap_metrics, orient="index")
            gap_df.index.name = "Model"
            gap_df = gap_df.sort_values(by="F1_Score", ascending=False)
            best_g_name = eval_data["opening_gap"].get("best_model", "Random Forest Classifier")

            st.success(f"🏅 **Best Opening Movement Model:** `{best_g_name}` with F1-Score of **{gap_df.loc[best_g_name, 'F1_Score']}%** and Accuracy of **{gap_df.loc[best_g_name, 'Accuracy']}%**")
            st.dataframe(gap_df.style.highlight_max(subset=["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"], color="#1b4d3e"),
                         use_container_width=True)

            melted_gap = gap_df[["Accuracy", "Precision", "Recall", "F1_Score"]].reset_index().melt(id_vars="Model", var_name="Metric", value_name="Score (%)")
            fig_gap = px.bar(melted_gap, x="Model", y="Score (%)", color="Metric", barmode="group", title="Opening Movement (Overnight Gap) Metrics Comparison")
            fig_gap.update_layout(height=380, yaxis_range=[40, 100])
            st.plotly_chart(fig_gap, use_container_width=True)

    with subtab_day:
        clf_metrics = eval_data["classification"]["metrics"]
        clf_df = pd.DataFrame.from_dict(clf_metrics, orient="index")
        clf_df.index.name = "Model"
        clf_df = clf_df.sort_values(by="F1_Score", ascending=False)

        st.success(f"🏅 **Best Full Day Model Selected:** `{best_model_name}` with F1-Score of **{clf_df.loc[best_model_name, 'F1_Score']}%**, Accuracy of **{clf_df.loc[best_model_name, 'Accuracy']}%**, and ROC-AUC of **{clf_df.loc[best_model_name, 'ROC_AUC']}**")
        st.dataframe(clf_df.style.highlight_max(subset=["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"], color="#1b4d3e"),
                     use_container_width=True)

        metrics_to_plot = ["Accuracy", "Precision", "Recall", "F1_Score"]
        melted_clf = clf_df[metrics_to_plot].reset_index().melt(id_vars="Model", var_name="Metric", value_name="Score (%)")
        fig_clf = px.bar(melted_clf, x="Model", y="Score (%)", color="Metric", barmode="group", title="Full Day Movement Metrics Comparison Across All Models")
        fig_clf.update_layout(height=380, yaxis_range=[40, 80])
        st.plotly_chart(fig_clf, use_container_width=True)


# ==============================================================================
# TAB 4: EVALUATION & DIAGNOSTICS
# ==============================================================================
with tab_eval:
    st.subheader("🔬 Out-of-Sample Classification Diagnostics")

    ccol1, ccol2 = st.columns(2)
    with ccol1:
        st.markdown(f"#### 1. Confusion Matrix: `{best_model_name}`")
        cm = eval_data["classification"]["confusion_matrices"][best_model_name]
        cm_matrix = np.array(cm)
        fig_cm = px.imshow(
            cm_matrix,
            labels=dict(x="Predicted Direction", y="Actual Direction", color="Count"),
            x=["DOWN (0)", "UP (1)"],
            y=["DOWN (0)", "UP (1)"],
            text_auto=True,
            color_continuous_scale="Tealgrn"
        )
        fig_cm.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_cm, use_container_width=True)

    with ccol2:
        st.markdown(f"#### 2. Top Feature Importances (`{best_model_name}`)")
        fi = eval_data["classification"]["feature_importances"]
        if fi:
            fi_df = pd.DataFrame(list(fi.items()), columns=["Feature", "Importance"]).sort_values(by="Importance", ascending=True).tail(12)
            fig_fi = px.bar(fi_df, x="Importance", y="Feature", orientation="h", color="Importance", color_continuous_scale="Purples")
            fig_fi.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
            st.plotly_chart(fig_fi, use_container_width=True)
        else:
            st.info("Feature importance not directly available.")

    st.markdown("---")
    st.markdown("#### 3. Test Set Directional Probabilities Over Time")
    test_dates = pd.to_datetime(eval_data["classification"]["test_dates"])
    probs = [p * 100.0 for p in eval_data["classification"]["best_probabilities"]]
    actual_dir = eval_data["classification"]["actual_targets"]

    prob_time_df = pd.DataFrame({
        "Date": test_dates,
        "Bullish_Probability": probs,
        "Actual_Direction": ["UP" if y == 1 else "DOWN" for y in actual_dir]
    }).set_index("Date")

    fig_prob_time = px.line(prob_time_df, x=prob_time_df.index, y="Bullish_Probability", title="Predicted Bullish Probability Over Out-of-Sample Period", color_discrete_sequence=["#29b6f6"])
    fig_prob_time.add_hline(y=50, line_dash="dash", line_color="#ffa726", annotation_text="50% Threshold (Neutral)")
    fig_prob_time.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20), yaxis_title="Bullish Probability (%)")
    st.plotly_chart(fig_prob_time, use_container_width=True)


# ==============================================================================
# TAB 5: DATA EXPLORER & FEATURE INSIGHTS
# ==============================================================================
with tab_data:
    st.subheader("💾 Engineered Dataset Explorer")

    st.write(f"Displaying processed daily dataset with **{df_data.shape[0]:,} rows** and **{df_data.shape[1]} engineered features**.")

    st.dataframe(df_data.tail(50), use_container_width=True)

    dcol_left, dcol_right = st.columns(2)
    with dcol_left:
        csv_bytes = df_data.to_csv().encode("utf-8")
        st.download_button(
            label="📥 Download Full Engineered Dataset (CSV)",
            data=csv_bytes,
            file_name="nifty50_direction_features.csv",
            mime="text/csv",
        )

    with dcol_right:
        if st.button("🚀 Re-Run Data Ingestion & Model Training", key="retrain_tab"):
            with st.spinner("Downloading updated daily market data and retraining models..."):
                from src.pipeline import run_pipeline
                run_pipeline(force_download=True)
                st.cache_data.clear()
                st.success("Training complete! Refreshing dashboard...")
                st.rerun()

    st.markdown("---")
    st.subheader("📈 Feature Correlation Heatmap with Target Direction")
    corr_features = [
        "NIFTY_Return", "VIX_Return", "NIFTY_Return_Lag1", "NIFTY_Return_Lag2",
        "NIFTY_SMA_5_Ratio", "NIFTY_SMA_20_Ratio", "NIFTY_Vol_10", "NIFTY_RSI_14",
        "NIFTY_MACD_Hist", "NIFTY_Daily_Range_Pct", "Target_Direction"
    ]
    avail_corr = [c for c in corr_features if c in df_data.columns]
    corr_df = df_data[avail_corr].corr()
    fig_corr = px.imshow(corr_df, text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto")
    fig_corr.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")
    st.subheader("⚡ Automated Post-Market Observation Updates")
    st.info("""
    **End-of-Day (EOD) Automation Rules:**
    1. **Zero Live Polling:** During market hours (09:15 - 15:30 IST), live tick updates are strictly bypassed so partial candles do not distort technical indicators.
    2. **Post-Market Settlement:** After 3:30 PM IST, NSE calculates the official volume-weighted closing price.
    3. **Automatic Daily Update:** 
       - Scheduled to run every weekday at **4:00 PM IST** via Windows Task Scheduler (`setup_post_market_task.bat`).
       - Features are re-engineered exclusively from the finalized closing price.
       - The next day's movement forecast is computed and ready before the next trading day starts!
       - If your computer was powered off at 4:00 PM, the task automatically executes the update as soon as you turn your PC on.
    """)

# Footer
st.markdown("---")
st.caption("NIFTY 50 Next Trading Day Movement Prediction System | Pair-programmed with Google DeepMind Antigravity")


if __name__ == "__main__":
    try:
        from streamlit.runtime import exists as _st_exists
        is_running_in_streamlit = _st_exists()
    except Exception:
        is_running_in_streamlit = False

    if not is_running_in_streamlit:
        import sys
        import os
        print("===================================================")
        print("  Starting NIFTY 50 Exact Replica Dashboard (FastAPI + React)")
        print("  Serving on: http://127.0.0.1:8501 (or http://localhost:8501)")
        print("===================================================")
        os.system(f'"{sys.executable}" api.py')

