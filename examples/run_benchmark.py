"""
Agent4Target Benchmark Suite
Evaluates pipeline scoring against ground-truth validated drug targets.
Metrics: AUROC, Precision@K, Mean Score Separation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from sklearn.metrics import roc_auc_score
from agent4target.orchestrator.workflow import run_pipeline


def run_benchmark(csv_path: str = "data/benchmark_targets.csv"):
    df = pd.read_csv(csv_path)
    
    results = []
    
    print("=" * 60)
    print("Agent4Target Benchmark Suite")
    print("=" * 60)
    
    for _, row in df.iterrows():
        symbol = row["symbol"]
        label = int(row["label"])
        
        print(f"\nEvaluating {symbol} (label={label})...")
        
        try:
            result = run_pipeline(symbol)
            scored = result.get("scored_target")
            
            if scored is None:
                print(f"  WARNING: No scored target returned for {symbol}")
                score = 0.0
            else:
                score = scored.aggregate_score
                
            results.append({
                "symbol": symbol,
                "label": label,
                "score": score,
                "rationale": row["rationale"]
            })
            print(f"  Score: {score:.4f}")
            
        except Exception as e:
            print(f"  ERROR on {symbol}: {e}")
            results.append({
                "symbol": symbol,
                "label": label,
                "score": 0.0,
                "rationale": row["rationale"]
            })
    
    # ── Metrics ──────────────────────────────────────────────────
    results_df = pd.DataFrame(results)
    
    labels = results_df["label"].tolist()
    scores = results_df["score"].tolist()
    
    # AUROC
    auroc = roc_auc_score(labels, scores)
    
    # Mean score separation
    pos_mean = results_df[results_df["label"] == 1]["score"].mean()
    neg_mean = results_df[results_df["label"] == 0]["score"].mean()
    separation = pos_mean - neg_mean
    
    # Precision@K (top K scores, how many are true positives)
    k = 6
    top_k = results_df.nlargest(k, "score")
    precision_at_k = top_k["label"].sum() / k
    
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)
    print(f"  AUROC          : {auroc:.4f}  (random=0.50, perfect=1.00)")
    print(f"  Precision@{k}    : {precision_at_k:.4f}  (of top {k} scored, fraction are true targets)")
    print(f"  Pos Mean Score : {pos_mean:.4f}")
    print(f"  Neg Mean Score : {neg_mean:.4f}")
    print(f"  Separation     : {separation:.4f}  (higher is better)")
    print("=" * 60)
    
    print("\nPer-Target Results:")
    print(results_df[["symbol", "label", "score"]].sort_values("score", ascending=False).to_string(index=False))
    
    # Save results
    out_path = "data/benchmark_results.csv"
    results_df.to_csv(out_path, index=False)
    print(f"\nResults saved to {out_path}")
    
    return results_df, auroc


if __name__ == "__main__":
    run_benchmark()