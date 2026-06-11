import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# 1. DATASET WCSS (Inertia)
# ============================================================
kwcss_values = [
    834023808100,  # K=1
    97074870590,   # K=2
    63204170461,   # K=3
    58180003133,   # K=4
    18058104624,   # K=5
    13585591880,   # K=6
    3700633571,    # K=7
    2631784742,    # K=8
    1557638151,    # K=9
    72651958       # K=10
]

k_range = np.arange(1, len(kwcss_values) + 1)

# ============================================================
# 2. VISUALISASI METODE ELBOW
# ============================================================
plt.figure(figsize=(11, 6))

# Plot garis elbow
plt.plot(
    k_range,
    kwcss_values,
    marker='o',
    linestyle='-',
    linewidth=2,
    markersize=8
)

# ============================================================
# 3. HIGHLIGHT TITIK ELBOW
# ============================================================
optimal_k = 4

plt.scatter(
    optimal_k,
    kwcss_values[optimal_k - 1],
    s=180,
    zorder=5
)

# ============================================================
# 4. ANOTASI TITIK
# ============================================================
for i, val in enumerate(kwcss_values):
    plt.annotate(
        f"K={i+1}",
        (k_range[i], val),
        textcoords="offset points",
        xytext=(0,10),
        ha='center',
        fontsize=9
    )

# Highlight titik optimal
plt.annotate(
    "Elbow Point (K=4)",
    (optimal_k, kwcss_values[optimal_k - 1]),
    textcoords="offset points",
    xytext=(30, -20),
    fontsize=11,
    fontweight='bold',
    arrowprops=dict(arrowstyle='->', lw=1.5)
)

# ============================================================
# 5. KONFIGURASI GRAFIK
# ============================================================
plt.title(
    "Grafik Metode Elbow untuk Penentuan Jumlah Cluster Optimal",
    fontsize=14,
    pad=15
)

plt.xlabel("Jumlah Cluster (K)", fontsize=12)
plt.ylabel("Nilai WCSS (Within Cluster Sum of Squares)", fontsize=12)

plt.xticks(k_range)

# Gunakan skala log agar grafik tidak terlalu tajam
plt.yscale('log')

plt.grid(True, linestyle='--', alpha=0.5)

# ============================================================
# 6. TAMPILKAN GRAFIK
# ============================================================
plt.tight_layout()
plt.show()

# ============================================================
# 7. OUTPUT RINGKASAN DATA
# ============================================================
print("-" * 55)
print(f"{'Jumlah Cluster (K)':<25} | {'Nilai WCSS':>20}")
print("-" * 55)

for k, val in zip(k_range, kwcss_values):
    print(f"K = {k:<21} | {val:>20,}")

print("-" * 55)
print("K optimal berdasarkan metode elbow berada di sekitar K = 4")