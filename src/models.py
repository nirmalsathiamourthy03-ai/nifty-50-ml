"""
Model Training, Evaluation, and Selection Module
Dedicated to Dual Classification:
  1. Opening Movement Prediction (Overnight Gap: GAP UP 🔼 / GAP DOWN 🔽)
  2. Full Next Trading Day Direction (Close-to-Close: UP 🔼 / DOWN 🔽)
Computes Accuracy, Precision, Recall, F1-Score, Confusion Matrix, and ROC-AUC.
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
import xgboost as xgb
import lightgbm as lgb


def get_classification_features(df: pd.DataFrame) -> list[str]:
    """
    Returns stationary feature column list for market direction classification.
    """
    clf_features = [
        "NIFTY_Return", "VIX_Return",
        "NIFTY_Return_Lag1", "NIFTY_Return_Lag2", "NIFTY_Return_Lag3", "NIFTY_Return_Lag5",
        "NIFTY_SMA_5_Ratio", "NIFTY_SMA_10_Ratio", "NIFTY_SMA_20_Ratio",
        "NIFTY_Vol_5", "NIFTY_Vol_10", "NIFTY_Vol_20",
        "NIFTY_RSI_14", "NIFTY_MACD_Hist",
        "NIFTY_Daily_Range_Pct", "VIX_Close"
    ]
    return [f for f in clf_features if f in df.columns]


def chronological_split(df: pd.DataFrame, train_ratio: float = 0.8) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs chronological time-series train-test split without shuffling
    to prevent lookahead leakage.
    """
    split_idx = int(len(df) * train_ratio)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()
    return train_df, test_df


def train_single_target(train_df: pd.DataFrame, 
                        test_df: pd.DataFrame, 
                        clf_features: list[str],
                        target_col: str, 
                        target_label: str) -> dict:
    """
    Trains and benchmarks 5 classification models on a specified binary target.
    """
    print(f"\n--- Training Models for: {target_label} ({target_col}) ---")

    X_train = train_df[clf_features].copy()
    y_train = train_df[target_col].values.astype(int)

    X_test = test_df[clf_features].copy()
    y_test = test_df[target_col].values.astype(int)

    # Fit scaler strictly on training data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Candidate Classification Models
    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Random Forest Classifier": RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=10, random_state=42, n_jobs=1),
        "Gradient Boosting Classifier": GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.03, random_state=42),
        "XGBoost Classifier": xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.03, eval_metric="logloss", random_state=42, n_jobs=1),
        "LightGBM Classifier": lgb.LGBMClassifier(n_estimators=100, max_depth=3, learning_rate=0.03, random_state=42, verbose=-1, n_jobs=1),
    }

    results = {}
    best_name = None
    best_score = -1.0
    best_model = None
    feature_importances = {}

    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        
        # Predict probabilities
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X_test_scaled)[:, 1]
            try:
                auc = float(roc_auc_score(y_test, probs))
            except Exception:
                auc = 0.5
        else:
            probs = preds.astype(float)
            auc = 0.5

        if hasattr(model, "feature_importances_"):
            feature_importances[name] = dict(zip(clf_features, model.feature_importances_.tolist()))
        elif hasattr(model, "coef_"):
            feature_importances[name] = dict(zip(clf_features, np.abs(model.coef_[0]).tolist()))

        acc = float(accuracy_score(y_test, preds))
        prec = float(precision_score(y_test, preds, zero_division=0))
        rec = float(recall_score(y_test, preds, zero_division=0))
        f1 = float(f1_score(y_test, preds, zero_division=0))
        cm = confusion_matrix(y_test, preds).tolist()

        results[name] = {
            "Accuracy": round(acc * 100.0, 2),
            "Precision": round(prec * 100.0, 2),
            "Recall": round(rec * 100.0, 2),
            "F1_Score": round(f1 * 100.0, 2),
            "ROC_AUC": round(auc, 4),
            "Confusion_Matrix": cm,
            "sample_predictions": preds.tolist(),
            "sample_probabilities": probs.tolist(),
        }

        print(f"{name:28s} | Acc: {acc*100:5.2f}% | Prec: {prec*100:5.2f}% | Rec: {rec*100:5.2f}% | F1: {f1*100:5.2f}% | AUC: {auc:6.4f}")

        selection_score = f1 * 0.7 + acc * 0.3
        if selection_score > best_score:
            best_score = selection_score
            best_name = name
            best_model = model

    print(f">> Champion for {target_label}: '{best_name}' (F1: {results[best_name]['F1_Score']}%, Acc: {results[best_name]['Accuracy']}%)")

    return {
        "all_results": results,
        "best_model_name": best_name,
        "best_model": best_model,
        "feature_importances": feature_importances,
        "scaler": scaler,
        "features": clf_features,
        "y_test": y_test.tolist(),
        "test_dates": test_df.index.strftime("%Y-%m-%d").tolist(),
    }


def train_and_evaluate_classification(train_df: pd.DataFrame, 
                                      test_df: pd.DataFrame, 
                                      clf_features: list[str]) -> dict:
    """
    Trains dual classification systems:
    1. Full Day Direction (Target_Day_Direction)
    2. Opening Movement (Target_Gap_Direction)
    """
    # 1. Full Day Movement (Close-to-Close)
    day_output = train_single_target(
        train_df, test_df, clf_features, 
        target_col="Target_Day_Direction" if "Target_Day_Direction" in train_df.columns else "Target_Direction",
        target_label="Full Day Movement (UP / DOWN)"
    )

    # 2. Opening Movement (Overnight Gap)
    gap_col = "Target_Gap_Direction" if "Target_Gap_Direction" in train_df.columns else "Target_Direction"
    gap_output = train_single_target(
        train_df, test_df, clf_features, 
        target_col=gap_col, 
        target_label="Opening Movement (GAP UP / GAP DOWN)"
    )

    return {
        "day": day_output,
        "gap": gap_output,
        # Default alias for backwards compatibility
        "all_results": day_output["all_results"],
        "best_model_name": day_output["best_model_name"],
        "best_model": day_output["best_model"],
        "scaler": day_output["scaler"],
        "features": clf_features,
    }


def save_direction_artifacts(dual_output: dict, save_dir: str = "models"):
    """
    Persists dual classification models, scaler, metadata, and evaluation results to disk.
    """
    os.makedirs(save_dir, exist_ok=True)

    day_out = dual_output["day"]
    gap_out = dual_output["gap"]

    # Save Day Model and Gap Model
    joblib.dump({"model": day_out["best_model"], "name": day_out["best_model_name"]}, 
                os.path.join(save_dir, "best_classification_bundle.joblib"))
    joblib.dump({"model": gap_out["best_model"], "name": gap_out["best_model_name"]}, 
                os.path.join(save_dir, "best_gap_bundle.joblib"))
    joblib.dump(day_out["scaler"], os.path.join(save_dir, "classification_scaler.joblib"))

    eval_data = {
        "classification": {
            "best_model": day_out["best_model_name"],
            "features": day_out["features"],
            "metrics": {k: {m: v[m] for m in ["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"]}
                        for k, v in day_out["all_results"].items()},
            "feature_importances": day_out["feature_importances"].get(day_out["best_model_name"], {}),
            "confusion_matrices": {k: v["Confusion_Matrix"] for k, v in day_out["all_results"].items()},
            "test_dates": day_out["test_dates"],
            "actual_targets": day_out["y_test"],
            "best_predictions": day_out["all_results"][day_out["best_model_name"]]["sample_predictions"],
            "best_probabilities": day_out["all_results"][day_out["best_model_name"]]["sample_probabilities"],
        },
        "opening_gap": {
            "best_model": gap_out["best_model_name"],
            "metrics": {k: {m: v[m] for m in ["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"]}
                        for k, v in gap_out["all_results"].items()},
            "confusion_matrices": {k: v["Confusion_Matrix"] for k, v in gap_out["all_results"].items()},
            "actual_targets": gap_out["y_test"],
            "best_predictions": gap_out["all_results"][gap_out["best_model_name"]]["sample_predictions"],
            "best_probabilities": gap_out["all_results"][gap_out["best_model_name"]]["sample_probabilities"],
        }
    }

    eval_path = os.path.join(save_dir, "evaluation_results.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2)

    metadata = {
        "project_type": "NIFTY 50 Dual Movement Prediction (Opening Gap & Full Day Direction)",
        "best_day_model": day_out["best_model_name"],
        "best_gap_model": gap_out["best_model_name"],
        "features_count": len(day_out["features"]),
        "test_samples_count": len(day_out["y_test"]),
    }
    with open(os.path.join(save_dir, "model_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nAll dual classification models and evaluation artifacts successfully saved to '{save_dir}/'")


def predict_next_trading_day(last_day_sample_df: pd.DataFrame, 
                             models_dir: str = "models") -> dict:
    """
    Uses both trained classification models to predict:
    1. Opening Movement (GAP UP / GAP DOWN)
    2. Full Day Direction (UP / DOWN)
    Computed strictly from the features of the last completed trading day.
    """
    # Load Day Model & Gap Model
    day_bundle = joblib.load(os.path.join(models_dir, "best_classification_bundle.joblib"))
    day_model = day_bundle["model"]
    day_model_name = day_bundle["name"]

    gap_bundle_path = os.path.join(models_dir, "best_gap_bundle.joblib")
    if os.path.exists(gap_bundle_path):
        gap_bundle = joblib.load(gap_bundle_path)
        gap_model = gap_bundle["model"]
        gap_model_name = gap_bundle["name"]
    else:
        gap_model = day_model
        gap_model_name = day_model_name

    clf_scaler = joblib.load(os.path.join(models_dir, "classification_scaler.joblib"))

    with open(os.path.join(models_dir, "evaluation_results.json"), "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    clf_features = eval_data["classification"]["features"]

    last_closed_date = last_day_sample_df.index[-1].strftime("%Y-%m-%d")
    last_close = float(last_day_sample_df["NIFTY_Close"].iloc[-1])
    last_vix = float(last_day_sample_df["VIX_Close"].iloc[-1])

    X_clf = last_day_sample_df[clf_features]
    X_clf_scaled = clf_scaler.transform(X_clf)

    # 1. Full Day Direction Prediction
    day_pred = int(day_model.predict(X_clf_scaled)[0])
    if hasattr(day_model, "predict_proba"):
        day_probs = day_model.predict_proba(X_clf_scaled)[0]
        day_prob_up = float(day_probs[1]) * 100.0
        day_prob_down = float(day_probs[0]) * 100.0
    else:
        day_prob_up = 100.0 if day_pred == 1 else 0.0
        day_prob_down = 100.0 - day_prob_up

    day_label = "UP" if day_pred == 1 else "DOWN"
    max_day_prob = max(day_prob_up, day_prob_down)
    if max_day_prob >= 65.0:
        strength = f"Strong {'Bullish' if day_pred == 1 else 'Bearish'}"
    elif max_day_prob >= 55.0:
        strength = f"Moderate {'Bullish' if day_pred == 1 else 'Bearish'}"
    else:
        strength = "Neutral / Mild Bias"

    # 2. Opening Movement Prediction (Overnight Gap)
    gap_pred = int(gap_model.predict(X_clf_scaled)[0])
    if hasattr(gap_model, "predict_proba"):
        gap_probs = gap_model.predict_proba(X_clf_scaled)[0]
        gap_prob_up = float(gap_probs[1]) * 100.0
        gap_prob_down = float(gap_probs[0]) * 100.0
    else:
        gap_prob_up = 100.0 if gap_pred == 1 else 0.0
        gap_prob_down = 100.0 - gap_prob_up

    gap_label = "GAP UP" if gap_pred == 1 else "GAP DOWN"

    forecast = {
        "previous_closed_date": last_closed_date,
        "previous_day_closing_price": round(last_close, 2),
        "last_closed_date": last_closed_date,
        "as_of_date": last_closed_date,
        "last_day_closing_price": round(last_close, 2),
        "current_nifty_close": round(last_close, 2),
        "current_vix": round(last_vix, 2),
        # Opening Movement
        "predicted_gap": gap_label,
        "predicted_gap_code": gap_pred,
        "gap_confidence_up_percent": round(gap_prob_up, 1),
        "gap_confidence_down_percent": round(gap_prob_down, 1),
        "best_gap_model": gap_model_name,
        # Full Day Movement
        "predicted_direction": day_label,
        "predicted_direction_code": day_pred,
        "confidence_up_percent": round(day_prob_up, 1),
        "confidence_down_percent": round(day_prob_down, 1),
        "signal_strength": strength,
        "best_classification_model": day_model_name,
    }

    forecast_path = os.path.join(models_dir, "latest_forecast.json")
    with open(forecast_path, "w", encoding="utf-8") as f:
        json.dump(forecast, f, indent=2)

    return forecast
