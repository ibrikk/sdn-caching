import random
import bisect
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# -----------------------------
# Zipf distribution utilities
# -----------------------------

def build_zipf_cdf(n_contents: int, alpha: float) -> Tuple[List[int], List[float]]:
    """
    Build CDF for a Zipf(alpha) distribution over content ids 1..n_contents.
    Returns:
        contents: [1, 2, ..., n_contents] -- A list of video IDs
        cdf: cumulative probabilities (same length) -- The cumulative distribution function for the Zipf probabilities
    """
    weights = [1.0 / (i ** alpha) for i in range(1, n_contents + 1)] # weights reflect popularity but do NOT sum to 1 yet. 
                                                                     # The i-th most popular item gets ~1/i^α of the total traffic.
    total = sum(weights) # Normalize weights into probabilities. We divide each weight by the sum so that all probabilities add up to 1.
    probs = [w / total for w in weights]

    cdf = [] # It transforms probabilities into “rolling sums.” or sum of probs up to i. Example: probs  = [0.50, 0.25, 0.15, 0.10]
                                                                                                # cdf    = [0.50, 0.75, 0.90, 1.00]
                                                                                                # cumulative mapping from probabilities → ranges in [0,1]
    cumulative = 0.0
    for p in probs:
        cumulative += p
        cdf.append(cumulative)

    contents = list(range(1, n_contents + 1))
    return contents, cdf


def sample_zipf(contents: List[int], cdf: List[float]) -> int:
    """
    Sample one content id from the Zipf CDF.
    """
    u = random.random() # random floating number [0.0 to 1.0)
    idx = bisect.bisect_left(cdf, u) # find u >= cdf
    return contents[idx]


# -----------------------------
# Edge cache implementation
# -----------------------------

@dataclass
class EdgeCache:
    capacity: int
    policy: str  # "LRU", "LFU", "Random"

    # Internal state
    cache: set = field(default_factory=set, init=False)
    # For LRU: key order represents recency (rightmost is most recent)
    lru_order: "OrderedDict[int, None]" = field(default_factory=OrderedDict, init=False)
    # For LFU: frequency counts for each content in cache
    freq: Dict[int, int] = field(default_factory=dict, init=False)
    # Simple access counter for tie breaking in LFU (optional)
    access_counter: int = field(default=0, init=False)

    def request(self, content_id: int, lat_edge: float, lat_origin: float) -> Tuple[bool, float]:
        """
        Process a request for content_id.
        Returns:
            (hit, latency_ms)
        """
        self.access_counter += 1

        if content_id in self.cache:
            # Cache hit
            self._update_on_hit(content_id)
            return True, lat_edge
        else:
            # Cache miss
            self._insert_on_miss(content_id)
            return False, lat_origin

    # -----------------------------
    # Policy helpers
    # -----------------------------

    def _update_on_hit(self, content_id: int) -> None:
        if self.policy.upper() == "LRU":
            # Move to most recent
            if content_id in self.lru_order:
                self.lru_order.move_to_end(content_id, last=True)
        elif self.policy.upper() == "LFU":
            # Increase frequency count
            self.freq[content_id] = self.freq.get(content_id, 0) + 1
        else:
            # Random policy has no state to update on hit
            pass

    def _insert_on_miss(self, content_id: int) -> None:
        if self.capacity <= 0:
            # No caching
            return

        if len(self.cache) < self.capacity:
            # There is space, just insert
            self._add_new_content(content_id)
        else:
            # Need to evict
            self._evict_one()
            self._add_new_content(content_id)

    def _add_new_content(self, content_id: int) -> None:
        self.cache.add(content_id)

        if self.policy.upper() == "LRU":
            self.lru_order[content_id] = None
            self.lru_order.move_to_end(content_id, last=True)
        elif self.policy.upper() == "LFU":
            # New content starts with frequency 1
            self.freq[content_id] = 1
        elif self.policy.upper() == "RANDOM":
            # No extra metadata needed
            pass

    def _evict_one(self) -> None:
        if not self.cache:
            return

        policy = self.policy.upper()

        if policy == "LRU":
            # Evict least recently used (leftmost)
            victim, _ = self.lru_order.popitem(last=False)
            self.cache.remove(victim)
            # Also clean freq if it exists
            self.freq.pop(victim, None)

        elif policy == "LFU":
            # Evict least frequently used
            # Simple O(C) scan is fine for our project sizes
            victim = None
            victim_freq = None

            for cid in self.cache:
                f = self.freq.get(cid, 0)
                if victim is None or f < victim_freq:
                    victim = cid
                    victim_freq = f

            if victim is not None:
                self.cache.remove(victim)
                self.freq.pop(victim, None)
                # Also remove from LRU order if present (optional)
                if victim in self.lru_order:
                    self.lru_order.pop(victim)

        elif policy == "RANDOM":
            # Evict random item from cache
            victim = random.choice(tuple(self.cache))
            self.cache.remove(victim)
            self.freq.pop(victim, None)
            if victim in self.lru_order:
                self.lru_order.pop(victim)
        else:
            # Fallback to random if unknown policy
            victim = random.choice(tuple(self.cache))
            self.cache.remove(victim)
            self.freq.pop(victim, None)
            if victim in self.lru_order:
                self.lru_order.pop(victim)


# -----------------------------
# Simulation driver
# -----------------------------

def run_sim(
    n_contents: int,
    n_edges: int,
    capacity: int,
    alpha: float,
    policy: str,
    n_requests: int,
    lat_edge_ms: float = 10.0,
    lat_origin_ms: float = 100.0,
    seed: Optional[int] = None,
) -> Dict[str, float]:
    """
    Run a simulation for given parameters and a single cache policy.

    Returns a dict with:
        "hit_ratio"
        "miss_ratio"
        "avg_latency_ms"
        "p95_latency_ms"
        "origin_load" (number of origin fetches)
    """
    if seed is not None:
        random.seed(seed)

    # Build Zipf CDF
    contents, cdf = build_zipf_cdf(n_contents, alpha)

    # Initialize edge caches
    edges = [EdgeCache(capacity=capacity, policy=policy) for _ in range(n_edges)]

    total_hits = 0
    total_misses = 0
    latencies: List[float] = []

    for _ in range(n_requests):
        edge_idx = random.randrange(n_edges)
        edge = edges[edge_idx]

        content_id = sample_zipf(contents, cdf)
        hit, latency = edge.request(content_id, lat_edge_ms, lat_origin_ms)

        latencies.append(latency)
        if hit:
            total_hits += 1
        else:
            total_misses += 1

    # Compute metrics
    total = max(n_requests, 1)
    hit_ratio = total_hits / total
    miss_ratio = total_misses / total
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    # 95th percentile
    if latencies:
        sorted_lat = sorted(latencies)
        idx = int(0.95 * len(sorted_lat)) - 1
        idx = max(0, min(idx, len(sorted_lat) - 1))
        p95_latency = sorted_lat[idx]
    else:
        p95_latency = 0.0

    metrics = {
        "hit_ratio": hit_ratio,
        "miss_ratio": miss_ratio,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
        "origin_load": float(total_misses),
    }
    return metrics


# -----------------------------
# Example usage
# -----------------------------

if __name__ == "__main__":
    # Small sanity test
    params = {
        "n_contents": 1000,
        "n_edges": 4,
        "capacity": 100,
        "alpha": 1.0, #popularity skew α low (0.6 or 0.8) → popularity is flat → caching works worse 
                      # α high (1.0, 1.2) → few videos dominate → caching works great 
                      # alpha=1.0 is a very typical real-world Zipf skew for content delivery.
        "policy": "LRU",
        "n_requests": 100_000, # video views are simulated
        "lat_edge_ms": 10.0, # Latency if the video is found in the edge cache. Typically 5-20ms
        "lat_origin_ms": 100.0, # Latency if the video must be fetched from the origin
        "seed": 42,
    }
    
    metrics = run_sim(**params)
    print("Params:", params)
    print("Metrics:", metrics)
    
    #NoCache
    params = {
        "n_contents": 1000,
        "n_edges": 4,
        "capacity": 0,
        "alpha": 1.0, #popularity skew α low (0.6 or 0.8) → popularity is flat → caching works worse 
                      # α high (1.0, 1.2) → few videos dominate → caching works great 
                      # alpha=1.0 is a very typical real-world Zipf skew for content delivery.
        "policy": "LRU",
        "n_requests": 100_000, # video views are simulated
        "lat_edge_ms": 10.0, # Latency if the video is found in the edge cache. Typically 5-20ms
        "lat_origin_ms": 100.0, # Latency if the video must be fetched from the origin
        "seed": 42,
    }

    metrics = run_sim(**params)
    print("Params:", params)
    print("Metrics:", metrics)
