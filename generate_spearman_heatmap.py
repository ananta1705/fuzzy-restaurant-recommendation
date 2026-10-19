"""
Script untuk menghasilkan visualisasi akademik Spearman Rank Correlation Across Provinces
menggunakan data final Google Trends (Regional, 34 Provinsi, 2020-2025).
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def generate_spearman_heatmap():
    data_path = Path("data/raw/Dataset E-Commerce.xlsx")
    if not data_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {data_path}")

    # Load dataset regional final
    df = pd.read_excel(data_path, sheet_name="Regional", header=2)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = df.columns.astype(str).str.strip()
    df = df.rename(columns={"Tiktok Shop": "TikTok Shop", "Tiktok shop": "TikTok Shop"})
    
    platforms = ["Shopee", "Tokopedia", "Lazada", "Blibli", "TikTok Shop"]
    reg = df.set_index("Wilayah")[platforms].copy()
    for col in platforms:
        reg[col] = pd.to_numeric(reg[col], errors="coerce")

    # Hitung korelasi Spearman
    corr = reg.corr(method="spearman")

    # Konfigurasi plot
    plt.style.use("default")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    plt.rcParams["axes.edgecolor"] = "black"
    plt.rcParams["axes.linewidth"] = 0.8

    fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=300)

    im = ax.imshow(corr.values, cmap="viridis", vmin=-1.0, vmax=1.0, aspect="equal")

    # Anotasi nilai di setiap sel (format 3 desimal, warna teks hitam pekat)
    for i in range(len(platforms)):
        for j in range(len(platforms)):
            val = corr.iloc[i, j]
            ax.text(
                j,
                i,
                f"{val:.3f}",
                ha="center",
                va="center",
                color="black",
                fontsize=10.5,
                fontweight="normal",
            )

    # Label sumbu X dan Y
    ax.set_xticks(range(len(platforms)))
    ax.set_yticks(range(len(platforms)))
    ax.set_xticklabels(platforms, rotation=35, ha="right", rotation_mode="anchor", fontsize=11)
    ax.set_yticklabels(platforms, fontsize=11)

    # Judul
    ax.set_title("Spearman Rank Correlation Across Provinces", fontsize=13, pad=12, fontweight="normal")

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_ticks(np.linspace(-1.0, 1.0, 9))
    cbar.set_ticklabels([f"{t:.2f}" for t in np.linspace(-1.0, 1.0, 9)], fontsize=10)
    cbar.set_label("Spearman's rho", fontsize=11, labelpad=8)
    cbar.outline.set_edgecolor("black")
    cbar.outline.set_linewidth(0.8)

    # Minor visual polish
    ax.tick_params(which="both", length=4, color="black", width=0.8)
    plt.tight_layout()

    # Simpan ke tujuan
    out_paths = [
        Path("figure2_spearman_correlation.png"),
        Path("spearman_rank_correlation.png"),
        Path("output_analisis/B7_korelasi_regional.png"),
    ]
    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=300, bbox_inches="tight")
        print(f"Tersimpan: {p}")

    plt.close()

if __name__ == "__main__":
    generate_spearman_heatmap()
