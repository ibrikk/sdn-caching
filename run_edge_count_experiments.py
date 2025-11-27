import csv
from sim import run_sim

edge_counts = [1, 2, 4, 8]

with open("results/edge_count_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["n_edges", "hit_ratio", "avg_latency", "p95_latency", "origin_load"])

    for k in edge_counts:
        metrics = run_sim(
            n_contents=1000,
            n_edges=k,
            capacity=100,
            alpha=1.0,
            policy="LRU",
            n_requests=200_000,
            lat_edge_ms=10,
            lat_origin_ms=100,
            seed=42
        )

        writer.writerow([
            k,
            metrics["hit_ratio"],
            metrics["avg_latency_ms"],
            metrics["p95_latency_ms"],
            metrics["origin_load"]
        ])

print("Edge count experiment complete!")
