import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/cache_size_results.csv")

fig, ax = plt.subplots()
for pol in df["policy"].unique():
    sub = df[df["policy"] == pol]
    ax.plot(sub["cache_size"], sub["hit_ratio"], marker="o", label=pol)

ax.set_xlabel("Cache Size (C)")
ax.set_ylabel("Hit Ratio")
ax.set_title("Hit Ratio vs Cache Size")
ax.legend()
plt.show()
