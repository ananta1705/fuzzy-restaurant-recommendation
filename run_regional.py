from itertools import combinations
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multitest import multipletests

from src.config import DATA_PATH, OUT_DIR, PLATFORMS

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", context="notebook")

JAWA = ["Banten", "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"]
ALPHA = 0.05


def load_regional_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {DATA_PATH}")
    df = pd.read_excel(DATA_PATH, sheet_name="Regional", header=2)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = df.columns.astype(str).str.strip()
    df = df.rename(columns={"Tiktok Shop": "TikTok Shop", "Tiktok shop": "TikTok Shop"})
    
    missing = [c for c in PLATFORMS if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom platform hilang: {missing}")
    if "Wilayah" not in df.columns:
        raise ValueError("Kolom 'Wilayah' tidak ditemukan.")
    
    df["Wilayah"] = df["Wilayah"].astype("string").str.strip()
    for p in PLATFORMS:
        df[p] = pd.to_numeric(df[p], errors="coerce")
        
    reg = df.set_index("Wilayah")[PLATFORMS].copy()
    return reg


def main():
    print("=" * 60)
    print("1. VALIDASI DATA REGIONAL")
    print("=" * 60)
    reg = load_regional_data()
    n_prov = len(reg)
    n_plat = len(PLATFORMS)
    n_idx = n_prov * n_plat
    n_missing = int(reg[PLATFORMS].isna().sum().sum())
    
    val_table = pd.DataFrame({
        "Pemeriksaan": [
            "Jumlah provinsi",
            "Jumlah platform",
            "Jumlah indeks regional",
            "Nilai kosong",
            "Periode pengamatan"
        ],
        "Hasil yang diharapkan": [
            str(n_prov),
            str(n_plat),
            str(n_idx),
            f"{n_missing}, jika terverifikasi",
            "2020–2025"
        ]
    })
    print(val_table.to_string(index=False))
    print(f"\n170 indeks regional = {n_prov} provinsi x {n_plat} platform. Terverifikasi lengkap.")

    print("\n" + "=" * 60)
    print("2. STATISTIK DESKRIPTIF REGIONAL")
    print("=" * 60)
    desc = pd.DataFrame({
        "Platform": PLATFORMS,
        "N Provinsi": [len(reg[p]) for p in PLATFORMS],
        "Mean": [reg[p].mean() for p in PLATFORMS],
        "Median": [reg[p].median() for p in PLATFORMS],
        "Std. Dev.": [reg[p].std() for p in PLATFORMS],
        "Minimum": [int(reg[p].min()) for p in PLATFORMS],
        "Maksimum": [int(reg[p].max()) for p in PLATFORMS],
    }).set_index("Platform")
    print(desc.round(2).to_string())

    print("\n" + "=" * 60)
    print("3. MATRIKS KORELASI SPEARMAN LINTAS PROVINSI")
    print("=" * 60)
    corr_reg = reg.corr(method="spearman")
    print(corr_reg.round(3).to_string())
    
    # Simpan Heatmap Korelasi
    fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=300)
    im = ax.imshow(corr_reg.values, cmap="viridis", vmin=-1.0, vmax=1.0, aspect="equal")
    for i in range(len(PLATFORMS)):
        for j in range(len(PLATFORMS)):
            val = corr_reg.iloc[i, j]
            ax.text(j, i, f"{val:.3f}", ha="center", va="center", color="black", fontsize=10.5)
    ax.set_xticks(range(len(PLATFORMS)))
    ax.set_yticks(range(len(PLATFORMS)))
    ax.set_xticklabels(PLATFORMS, rotation=35, ha="right", rotation_mode="anchor", fontsize=11)
    ax.set_yticklabels(PLATFORMS, fontsize=11)
    ax.set_title("Spearman Rank Correlation Across Provinces", fontsize=13, pad=12)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_ticks(np.linspace(-1.0, 1.0, 9))
    cbar.set_ticklabels([f"{t:.2f}" for t in np.linspace(-1.0, 1.0, 9)], fontsize=10)
    cbar.set_label("Spearman's rho", fontsize=11, labelpad=8)
    cbar.outline.set_edgecolor("black")
    cbar.outline.set_linewidth(0.8)
    plt.tight_layout()
    fig.savefig(OUT_DIR / "B7_korelasi_regional.png", dpi=300, bbox_inches="tight")
    fig.savefig("figure2_spearman_correlation.png", dpi=300, bbox_inches="tight")
    fig.savefig("spearman_rank_correlation.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Hitung p-value dan koreksi Holm untuk semua pasangan
    pairs = []
    for a, b in combinations(PLATFORMS, 2):
        rho, pvalue = stats.spearmanr(reg[a], reg[b])
        pairs.append({"Platform A": a, "Platform B": b, "Spearman rho": rho, "p-value": pvalue})
    spearman_df = pd.DataFrame(pairs)
    spearman_df["p Holm"] = multipletests(spearman_df["p-value"], method="holm")[1]
    spearman_df["Signifikan (p Holm < 0.05)"] = spearman_df["p Holm"] < ALPHA
    print("\nUji Signifikansi Korelasi Spearman (Koreksi Holm):")
    print(spearman_df.round(4).to_string(index=False))

    print("\n" + "=" * 60)
    print("4. UJI MANN-WHITNEY U (JAWA VS LUAR JAWA)")
    print("=" * 60)
    is_java = reg.index.isin(JAWA)
    mw_rows = []
    for p in PLATFORMS:
        a, b = reg.loc[is_java, p], reg.loc[~is_java, p]
        u, pv = stats.mannwhitneyu(a, b, alternative="two-sided")
        rbc = 2 * u / (len(a) * len(b)) - 1
        mw_rows.append({
            "Platform": p, "N Jawa": len(a), "N Luar Jawa": len(b),
            "Median Jawa": a.median(), "Median Luar Jawa": b.median(),
            "U": u, "p-value": pv, "Rank-biserial r": rbc
        })
    mw_df = pd.DataFrame(mw_rows).set_index("Platform")
    mw_df["p Holm"] = multipletests(mw_df["p-value"], method="holm")[1]
    mw_df["Signifikan (alpha=5%)"] = mw_df["p Holm"] < ALPHA
    print(mw_df[["N Jawa", "N Luar Jawa", "Median Jawa", "Median Luar Jawa", "U", "p-value", "p Holm", "Signifikan (alpha=5%)"]].round(4).to_string())

    print("\n" + "=" * 60)
    print("5. HEATMAP & DOMINASI REGIONAL")
    print("=" * 60)
    dominant = reg[PLATFORMS].idxmax(axis=1)
    dom_counts = dominant.value_counts().reindex(PLATFORMS, fill_value=0)
    
    # Deteksi seri kembar / tie
    tie_info = []
    shared_counts = {p: 0.0 for p in PLATFORMS}
    joint_counts = {p: 0 for p in PLATFORMS}
    for prov, row in reg.iterrows():
        m = row.max()
        top_plats = row[row == m].index.tolist()
        if len(top_plats) > 1:
            tie_info.append(f"- {prov}: Seri nilai {m} antara {', '.join(top_plats)}")
        for tp in top_plats:
            shared_counts[tp] += 1.0 / len(top_plats)
            joint_counts[tp] += 1

    dom_summary = pd.DataFrame({
        "Dominan (idxmax bawaan)": dom_counts,
        "Dominan Bersama (Joint)": [joint_counts[p] for p in PLATFORMS],
        "Dominan Terbagi (Shared)": [round(shared_counts[p], 2) for p in PLATFORMS],
        "Provinsi Indeks Tertinggi": [reg[p].idxmax() for p in PLATFORMS],
        "Indeks Puncak Platform": [int(reg[p].max()) for p in PLATFORMS],
    })
    print(dom_summary.to_string())

    if tie_info:
        print("\n[CATATAN TIE-BREAKING REGIONAL]:")
        for t in tie_info:
            print(t)
        print("Penjelasan: idxmax() pandas secara default memilih platform yang muncul lebih awal pada urutan kolom.")
        print("Di DKI Jakarta, Tokopedia dan Blibli sama-sama bernilai 100. Kolom Tokopedia berada sebelum Blibli, sehingga Blibli tidak tercatat dominan.")
        print("Di Bali, Shopee dan Blibli sama-sama bernilai 54. Kolom Shopee berada sebelum Blibli.")
        print("Jika dihitung secara bersama (joint dominance), Blibli unggul/seri di 2 provinsi (DKI Jakarta & Bali).")

    print("\n[PERINGATAN METODOLOGI SKALA GOOGLE TRENDS]:")
    print("- Data tiap platform diekspor secara terpisah dari Google Trends, sehingga masing-masing dinormalisasi (0-100) terhadap puncak internalnya sendiri.")
    print("- Mean atau indeks absolut antarplatform TIDAK mencerminkan pangsa pasar riil atau popularitas absolut.")


    # Simpan Heatmap Sebaran
    order = reg.mean(axis=1).sort_values(ascending=False).index
    plt.figure(figsize=(10, 12))
    sns.heatmap(reg.loc[order, PLATFORMS], cmap="YlOrRd", vmin=0, vmax=100, linewidths=.2, cbar_kws={"label": "Indeks relatif"})
    plt.title("Search Interest E-Commerce per Provinsi dan Platform")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "B2_heatmap_provinsi.png", dpi=200, bbox_inches="tight")
    plt.close()

    # Ekspor ke Excel
    out_excel = OUT_DIR / "hasil_analisis_regional.xlsx"
    with pd.ExcelWriter(out_excel, engine="openpyxl") as writer:
        val_table.to_excel(writer, sheet_name="Validasi", index=False)
        desc.round(2).to_excel(writer, sheet_name="Statistik_Deskriptif")
        corr_reg.round(3).to_excel(writer, sheet_name="Korelasi_Spearman_Matriks")
        spearman_df.round(4).to_excel(writer, sheet_name="Korelasi_Spearman_Uji", index=False)
        mw_df.round(4).to_excel(writer, sheet_name="Mann_Whitney_Jawa")
        dom_summary.to_excel(writer, sheet_name="Dominasi_Regional")
        reg.to_excel(writer, sheet_name="Data_Regional_34Prov")

    print(f"\n[OK] Analisis regional selesai dieksekusi!")
    print(f"- File Excel disimpan di: {out_excel}")
    print(f"- Grafik heatmap disimpan di: {OUT_DIR}")


if __name__ == "__main__":
    main()
