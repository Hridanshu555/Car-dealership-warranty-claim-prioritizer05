"""
AutoTriage AI — Dealership Warranty Claim Prioritization System
=================================================================
Future Interns | Machine Learning Internship | Task 2

End-to-end pipeline:
  1. Load claim data (sample_claims.csv, or live_nhtsa_claims.csv if present)
  2. Clean text
  3. Train + compare 3 NLP classifiers to predict the affected COMPONENT
  4. Apply a rule-based PRIORITY engine (Critical / High / Medium / Low)
  5. Save charts + a summary report to outputs/

Run:
    pip install -r requirements.txt
    python main.py
"""

import os
import json
import pandas as pd

from src.preprocess import load_data, split_data
from src.classify import train_and_compare
from src.prioritize import apply_priority
from src.dashboard import (
    save_model_comparison,
    save_confusion_matrix,
    save_priority_distribution,
    save_component_distribution,
)

DATA_PATH = "data/live_nhtsa_claims.csv" if os.path.exists("data/live_nhtsa_claims.csv") else "data/sample_claims.csv"
OUT_DIR = "outputs"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Loading data from {DATA_PATH} ...")
    df = load_data(DATA_PATH)
    print(f"Loaded {len(df)} claims across {df['component'].nunique()} categories.\n")

    # --- Classification ---
    train_df, test_df = split_data(df)
    results, vectorizer, best_name, best_model, y_test, y_pred = train_and_compare(train_df, test_df)

    print("=== Model comparison (predicting affected component) ===")
    for name, r in results.items():
        print(f"{name:22s} accuracy={r['accuracy']:.3f}  macro_f1={r['macro_f1']:.3f}")
    print(f"\nBest model: {best_name}\n")
    print(results[best_name]["report"])

    # --- Priority engine ---
    df = apply_priority(df)
    priority_counts = df["priority"].value_counts().to_dict()
    print("=== Priority breakdown (all claims) ===")
    for p in ["Critical", "High", "Medium", "Low"]:
        print(f"{p:10s}: {priority_counts.get(p, 0)}")

    # --- Save charts ---
    save_model_comparison(results, f"{OUT_DIR}/model_comparison.png")
    save_confusion_matrix(y_test, y_pred, sorted(df["component"].unique()), f"{OUT_DIR}/confusion_matrix.png")
    save_priority_distribution(df, f"{OUT_DIR}/priority_distribution.png")
    save_component_distribution(df, f"{OUT_DIR}/component_distribution.png")

    # --- Save processed data + summary ---
    df.to_csv(f"{OUT_DIR}/prioritized_claims.csv", index=False)
    summary = {
        "total_claims": len(df),
        "best_model": best_name,
        "best_model_accuracy": results[best_name]["accuracy"],
        "best_model_macro_f1": results[best_name]["macro_f1"],
        "model_comparison": {k: {"accuracy": v["accuracy"], "macro_f1": v["macro_f1"]} for k, v in results.items()},
        "priority_breakdown": priority_counts,
        "component_breakdown": df["component"].value_counts().to_dict(),
    }
    with open(f"{OUT_DIR}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAll charts, the prioritized claim list, and summary.json saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
