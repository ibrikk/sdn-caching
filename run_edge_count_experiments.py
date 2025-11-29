import csv
from sim import run_sim

edge_counts = [1, 2, 4, 8]
policies = ["NOCACHE", "LRU", "LFU", "FIFO", "RANDOM"]

with open("results/edge_count_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["n_edges", "policy", "hit_ratio", "avg_latency", "p95_latency", "origin_load"])

    for k in edge_counts:
        for pol in policies:

            # NoCache = capacity 0
            C = 0 if pol == "NOCACHE" else 100

            metrics = run_sim(
                n_contents=1000,
                n_edges=k,
                capacity=C,
                alpha=1.0,
                policy=pol,
                n_requests=200_000,
                lat_edge_ms=10,
                lat_origin_ms=100,
                seed=42
            )

            writer.writerow([
                k,
                pol,
                metrics["hit_ratio"],
                metrics["avg_latency_ms"],
                metrics["p95_latency_ms"],
                metrics["origin_load"]
            ])

print("Edge count experiment complete!")
