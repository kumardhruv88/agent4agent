import time
from agent4target.orchestrator.workflow import run_pipeline

def run_benchmark(targets):
    print("Agent4Target - Simple Benchmark")
    print("-" * 50)
    
    start_time = time.time()
    
    results = []
    for t in targets:
        print(f"\nEvaluating target: {t}")
        res = run_pipeline(t)
        if res.get("scored_target"):
            score = res["scored_target"].aggregate_score
            print(f"[{t}] Score: {score:.3f}")
            results.append((t, score))
        else:
            print(f"[{t}] Failed to compute score. Errors: {res.get('errors')}")
            
    end_time = time.time()
    print("-" * 50)
    print(f"Processed {len(targets)} targets in {end_time - start_time:.2f} seconds.")
    
    # Sort and rank targets
    print("\nRanking:")
    results.sort(key=lambda x: x[1], reverse=True)
    for rank, (t, score) in enumerate(results, start=1):
        print(f"{rank}. {t}: {score:.3f}")

if __name__ == "__main__":
    test_targets = ["BRAF", "EGFR", "TP53", "KRAS"]
    run_benchmark(test_targets)
