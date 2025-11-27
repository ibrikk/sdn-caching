import csv
from sim import run_sim

cache_sizes = [20, 50, 100, 200]
policies = ["LRU", "LFU", "RANDOM"]

with open("results/cache_size_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["cache_size", "policy", "hit_ratio", "avg_latency", "p95_latency", "origin_load"])

    for C in cache_sizes:
        for pol in policies:
            metrics = run_sim(
                n_contents=1000,
                n_edges=4,
                capacity=C,
                alpha=1.0,
                policy=pol,
                n_requests=200_000,
                lat_edge_ms=10,
                lat_origin_ms=100,
                seed=42
            )

            writer.writerow([
                C,
                pol,
                metrics["hit_ratio"],
                metrics["avg_latency_ms"],
                metrics["p95_latency_ms"],
                metrics["origin_load"]
            ])

print("Cache size experiment complete!")
