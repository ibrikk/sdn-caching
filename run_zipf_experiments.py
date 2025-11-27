import csv
from sim import run_sim

alphas = [0.6, 0.8, 1.0, 1.2]
policies = ["LRU", "LFU", "RANDOM", "NOCACHE"]

with open("results/zipf_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["alpha", "policy", "hit_ratio", "avg_latency", "p95_latency", "origin_load"])

    for a in alphas:
        for pol in policies:
            if pol == "NOCACHE":
               metrics = run_sim(
                n_contents=1000,
                n_edges=4,
                capacity=0,
                alpha=a,
                policy="LRU",
                n_requests=200_000,
                lat_edge_ms=10,
                lat_origin_ms=100,
                seed=42
            ) 
            else:
                metrics = run_sim(
                n_contents=1000,
                n_edges=4,
                capacity=100,
                alpha=a,
                policy=pol,
                n_requests=200_000,
                lat_edge_ms=10,
                lat_origin_ms=100,
                seed=42
            )

            writer.writerow([
                a,
                pol,
                metrics["hit_ratio"],
                metrics["avg_latency_ms"],
                metrics["p95_latency_ms"],
                metrics["origin_load"]
            ])

print("Zipf experiment complete!")
