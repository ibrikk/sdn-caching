You're right! I see the issue - I was using triple backticks inside the markdown code block, which was breaking the formatting. Here's the complete README.md file:

```markdown
# Edge Caching Simulation (Future Networks Project)

This project simulates a simplified Content Delivery Network (CDN) with multiple edge servers, Zipf-distributed content popularity, and several cache replacement policies (LRU, LFU, Random). The goal is to analyze how cache size, popularity skew, and number of edge caches affect:

- cache hit ratio
- average latency
- 95th percentile latency (p95)
- origin server load

This project was developed as part of the **Future Networks** course.

## 📦 Project Structure

    project/
    │
    ├── sim.py                          # Core simulator (Zipf sampling + edge caches)
    ├── run_cache_size_experiments.py   # Sweep cache sizes
    ├── run_zipf_experiments.py         # Sweep Zipf alpha values
    ├── run_edge_count_experiments.py   # Sweep number of edges
    │
    ├── plot_cache_size.py              # Generate graphs for cache-size experiments
    ├── plot_zipf.py                    # Graphs for Zipf-sweeps
    ├── plot_edge_count.py              # Graphs for edge-count sweeps
    │
    ├── results/                        # CSV outputs from experiments
    │   ├── cache_size_results.csv
    │   ├── zipf_results.csv
    │   └── edge_count_results.csv
    │
    └── README.md

## 🏗️ System Architecture

            +-------------+
            |   Users     |
            +-------------+
                    |
                    v
          +-------------------+
          |   Edge Caches     |   (LRU / LFU / Random)
          |  E1, E2, ..., Ek  |
          +-------------------+
                    |
            Cache Misses Only
                    |
                    v
          +-------------------+
          |   Origin Server   |
          +-------------------+

## 🧠 Simulation Model

### **Content Popularity (Zipf Distribution)**
We simulate `N` videos whose popularity follows a Zipf(α) distribution:

    P(video i) ∝ 1 / i^α

This reflects real-world video platforms (Netflix, YouTube), where a small subset of popular content generates the majority of requests.

Requests are sampled using **inverse transform sampling**:
- generate a random number `u ∈ [0,1]`
- use the CDF to map `u` to a content ID
- more popular videos occupy larger sections of the CDF ⇒ sampled more often

### **Edge Caches**
We simulate `K` edge servers, each with cache capacity `C` videos.  
Each edge has a configurable caching policy:

- **LRU** — Least Recently Used  
- **LFU** — Least Frequently Used  
- **RANDOM** — Evict a random cached item  
- (Optional baseline) **NoCache**

Caches are independent and receive randomly assigned requests.

### **Latency Model**
To highlight caching effects, we use a simple two-level latency model:

- **Edge hit latency:** 10 ms  
- **Origin miss latency:** 100 ms  

This reflects the large performance gap between nearby edge servers and a distant origin server.

We compute:
- average latency  
- 95th percentile latency (p95)  
- total number of origin fetches  

## ▶️ Running Simulations

### **1. Cache-size sweep**

    python run_cache_size_experiments.py

Generates:

    results/cache_size_results.csv

### **2. Zipf α sweep**

    python run_zipf_experiments.py

### **3. Edge-count sweep**

    python run_edge_count_experiments.py

## 📈 Plotting Results

Example:

    python plot_cache_size.py

Each plotting script loads the CSVs and generates:

- hit ratio vs cache size
- average latency vs cache size
- p95 latency vs cache size

Additional graphs exist for α-sweeps and edge-count sweeps.

## 📊 Interpreting Results

Typical findings (expected):

- Increasing cache size improves hit ratio but with diminishing returns.
- Higher Zipf α (more skew) dramatically improves caching effectiveness.
- LRU and LFU outperform Random, especially under skewed popularity.
- p95 latency drops significantly when hit ratio improves.
- More edge caches reduce load on the origin server.

These observations mirror real CDN behavior.

## 📝 Requirements

- Python 3.8+
- pandas
- matplotlib

Install with:

    pip install pandas matplotlib

## ✨ Author

Developed as a Future Networks course project.  
The simulator is built from scratch using Python and includes multiple experiments to analyze caching behavior under realistic request patterns.

## 📚 License

Free for academic use.
```