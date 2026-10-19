from __future__ import annotations

import warnings
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pymannkendall as mk
import ruptures as rpt
from statsmodels.tsa.seasonal import STL
from statsmodels.stats.multitest import multipletests

from src.config import PROJECT_DIR, DATA_PATH, OUT_DIR, PLATFORMS, TIKTOK_START, EVENTS

warnings.filterwarnings("default")
sns.set_theme(style="whitegrid", context="notebook")

COLORS = {
    "Shopee": "#EE4D2D",
    "Tokopedia": "#42B549",
    "Lazada": "#0F146D",
    "Blibli": "#0095DA",
    "TikTok Shop": "#111111",
}
JAWA = ["Banten", "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"]
ALPHA = 0.05


def savefig(name: str) -> None:
    plt.savefig(OUT_DIR / name, bbox_inches="tight", dpi=200)


def load_sheet(sheet_name: str) -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan: {DATA_PATH}\n"
            "Pastikan file Excel berada di data/raw/Dataset E-Commerce.xlsx."
        )
    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name, header=2)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = df.columns.astype(str).str.strip()
    df = df.rename(columns={"Tiktok Shop": "TikTok Shop", "Tiktok shop": "TikTok Shop"})
    return df


def prepare_data():
    ts0 = load_sheet("Time Series")
    reg0 = load_sheet("Regional")

    for name, df in [("Time Series", ts0), ("Regional", reg0)]:
        missing = [c for c in PLATFORMS if c not in df.columns]
        if missing:
            raise ValueError(f"Kolom platform tidak ditemukan di {name}: {missing}")

    if "Kode Periode" not in ts0.columns:
        raise ValueError("Kolom 'Kode Periode' tidak ditemukan pada Time Series.")
    if "Wilayah" not in reg0.columns:
        raise ValueError("Kolom 'Wilayah' tidak ditemukan pada Regional.")

    ts0["Kode Periode"] = pd.to_datetime(ts0["Kode Periode"], errors="coerce")
    if ts0["Kode Periode"].isna().any():
        raise ValueError("Ada tanggal kosong/tidak valid pada Time Series.")
    if ts0["Kode Periode"].duplicated().any():
        raise ValueError("Ada tanggal duplikat pada Time Series.")

    for p in PLATFORMS:
        ts0[p] = pd.to_numeric(ts0[p], errors="coerce")
        reg0[p] = pd.to_numeric(reg0[p], errors="coerce")

    if ts0[PLATFORMS].isna().any().any():
        raise ValueError("Time Series mengandung nilai kosong/nonnumerik. Jangan imputasi otomatis.")
    if reg0[PLATFORMS].isna().any().any():
        raise ValueError("Regional mengandung nilai kosong/nonnumerik. Jangan imputasi otomatis.")

    ts = ts0.set_index("Kode Periode").sort_index()
    expected = pd.date_range("2020-01-01", "2025-12-01", freq="MS")
    if not ts.index.equals(expected):
        raise ValueError("Tanggal Time Series harus lengkap bulanan dari Jan 2020 sampai Des 2025.")

    reg0["Wilayah"] = reg0["Wilayah"].astype("string").str.strip()
    if reg0["Wilayah"].isna().any() or reg0["Wilayah"].eq("").any():
        raise ValueError("Ada nama wilayah kosong.")
    if reg0["Wilayah"].duplicated().any():
        raise ValueError("Ada nama wilayah duplikat.")
    reg = reg0.set_index("Wilayah")[PLATFORMS].copy()
    if len(reg) != 34:
        raise ValueError(f"Jumlah baris Regional {len(reg)}, seharusnya 34 provinsi.")

    for label, df in [("Time Series", ts), ("Regional", reg)]:
        if not df[PLATFORMS].apply(lambda s: s.between(0, 100).all()).all():
            raise ValueError(f"Ada indeks di luar 0–100 pada {label}.")

    series = {p: ts[p].copy() for p in PLATFORMS}
    series["TikTok Shop"] = series["TikTok Shop"].loc[pd.Timestamp(TIKTOK_START):].copy()
    return ts, reg, series


def plot_temporal(ts, series):
    # A1 descriptive stats, using active-period series for TikTok Shop
    desc_rows = []
    for p, s in series.items():
        desc_rows.append({
            "Platform": p, "N": s.count(), "mean": s.mean(), "std": s.std(),
            "min": s.min(), "max": s.max(),
            "CV (%)": (s.std() / s.mean() * 100) if s.mean() != 0 else np.nan,
            "Bulan puncak": s.idxmax().strftime("%b %Y"),
        })
    desc = pd.DataFrame(desc_rows).set_index("Platform")
    display_if_notebook(desc.round(3))

    fig, axes = plt.subplots(len(PLATFORMS), 1, figsize=(12, 12), sharex=True)
    for ax, p in zip(axes, PLATFORMS):
        s = series[p]
        ax.plot(s.index, s, color=COLORS[p], alpha=.7, label="Indeks bulanan")
        ax.plot(s.index, s.rolling(12, min_periods=6).mean(), color="black", lw=1.8, label="Rata-rata bergerak")
        ax.set_ylabel(p)
        ax.legend(loc="upper left", fontsize=8)
    axes[0].set_title("A1. Search interest bulanan dan rata-rata bergerak")
    plt.tight_layout(); savefig("A1_tren_bulanan.png"); plt.close()

    # A2 annual mean, YoY, CAGR with explicit note for partial first year
    annual = ts[PLATFORMS].groupby(ts.index.year).mean()
    annual.loc[:, "TikTok Shop"] = series["TikTok Shop"].groupby(series["TikTok Shop"].index.year).mean()
    yoy = annual.pct_change() * 100
    cagr_rows = []
    for p in PLATFORMS:
        a = annual[p].dropna()
        first_year, last_year = int(a.index[0]), int(a.index[-1])
        first_value, last_value = float(a.iloc[0]), float(a.iloc[-1])
        if first_value <= 0 or last_value < 0 or last_year == first_year:
            cagr = np.nan
        else:
            # For TikTok Shop 2021 is partial year; CAGR is therefore labelled approximate.
            cagr = ((last_value / first_value) ** (1 / (last_year - first_year)) - 1) * 100
        cagr_rows.append({"Platform": p, "CAGR (%)": cagr,
                          "Tahun awal": first_year, "Tahun akhir": last_year,
                          "Catatan": "2021 parsial; interpretasi hati-hati" if p == "TikTok Shop" else ""})
    cagr_df = pd.DataFrame(cagr_rows).set_index("Platform")
    annual.plot(kind="bar", figsize=(11, 5), color=[COLORS[p] for p in PLATFORMS])
    plt.title("A2. Rata-rata search interest tahunan"); plt.ylabel("Indeks relatif"); plt.xticks(rotation=0)
    plt.tight_layout(); savefig("A2_rata_tahunan.png"); plt.close()

    # A3 Mann-Kendall and Sen's slope
    mk_rows = []
    for p, s in series.items():
        r = mk.original_test(s.dropna().values)
        mk_rows.append({"Platform": p, "N": len(s), "Tren": r.trend, "p-value": r.p,
                        "Kendall tau": r.Tau, "Sen slope (indeks/bulan)": r.slope,
                        "Sen slope (indeks/tahun)": r.slope * 12})
    mk_df = pd.DataFrame(mk_rows).set_index("Platform")
    mk_df["Signifikan (α=5%)"] = mk_df["p-value"] < ALPHA

    # A4 STL decomposition and seasonal strength
    stl_results, seasonal_strength = {}, {}
    for p, s in series.items():
        res = STL(s.dropna(), period=12, robust=True).fit()
        stl_results[p] = res
        denom = np.var(res.seasonal + res.resid)
        seasonal_strength[p] = max(0, 1 - np.var(res.resid) / denom) if denom > 0 else np.nan
    strength_df = pd.Series(seasonal_strength, name="Kekuatan musiman (Fs)").to_frame()

    fig, axes = plt.subplots(len(PLATFORMS), 3, figsize=(15, 12), sharex="col")
    for i, p in enumerate(PLATFORMS):
        r = stl_results[p]
        axes[i, 0].plot(r.observed.index, r.observed, color=COLORS[p], alpha=.55)
        axes[i, 0].plot(r.trend.index, r.trend, color="black", lw=1.5)
        axes[i, 1].plot(r.seasonal.index, r.seasonal, color=COLORS[p])
        axes[i, 2].plot(r.resid.index, r.resid, color="grey")
        axes[i, 0].set_ylabel(p)
    for ax, title in zip(axes[0], ["Observasi & tren", "Musiman", "Residu"]):
        ax.set_title(title)
    plt.suptitle("A4. Dekomposisi STL", y=1.01)
    plt.tight_layout(); savefig("A4_stl.png"); plt.close()

    seas = pd.DataFrame({
        p: pd.Series(stl_results[p].seasonal.values, index=stl_results[p].observed.index).groupby(
            pd.Series(stl_results[p].observed.index.month, index=stl_results[p].observed.index)
        ).mean() for p in PLATFORMS
    })
    seas.index = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    plt.figure(figsize=(10, 5))
    sns.heatmap(seas.T, cmap="RdBu_r", center=0, annot=True, fmt=".1f")
    plt.title("A4. Rata-rata komponen musiman per bulan"); plt.tight_layout()
    savefig("A4_heatmap_musiman.png"); plt.close()

    # A5 PELT exploratory break detection
    def detect_breaks(s, pen_scale=2.0, min_size=6):
        x = s.rolling(3, center=True, min_periods=1).mean().to_numpy().reshape(-1, 1)
        penalty = pen_scale * np.log(len(x)) * np.var(x)
        indices = rpt.Pelt(model="l2", min_size=min_size, jump=1).fit(x).predict(pen=penalty)[:-1]
        return [s.index[i] for i in indices if i < len(s)]

    breaks = {p: detect_breaks(s) for p, s in series.items()}
    fig, axes = plt.subplots(len(PLATFORMS), 1, figsize=(12, 12), sharex=True)
    for ax, p in zip(axes, PLATFORMS):
        s = series[p]
        ax.plot(s.index, s, color=COLORS[p])
        for d in breaks[p]:
            ax.axvline(d, color="crimson", ls="--", alpha=.8)
        ax.set_ylabel(p)
    axes[0].set_title("A5. PELT exploratory structural breaks")
    plt.tight_layout(); savefig("A5_structural_break.png"); plt.close()

    def chow_test(y, break_date):
        y = y.dropna()
        break_date = pd.Timestamp(break_date)
        idx = int(y.index.searchsorted(break_date))
        n = len(y); k = 2
        if idx < 6 or n - idx < 6:
            return np.nan, np.nan
        t = np.arange(n, dtype=float)
        def ssr(tt, yy):
            X = np.column_stack([np.ones(len(tt)), tt])
            beta = np.linalg.lstsq(X, yy, rcond=None)[0]
            return float(np.sum((yy - X @ beta) ** 2))
        ssr_pooled = ssr(t, y.to_numpy())
        ssr_split = ssr(t[:idx], y.to_numpy()[:idx]) + ssr(t[idx:], y.to_numpy()[idx:])
        denominator_df = n - 2 * k
        if denominator_df <= 0 or ssr_split <= 0:
            return np.nan, np.nan
        F = max(0, ((ssr_pooled - ssr_split) / k) / (ssr_split / denominator_df))
        return F, float(stats.f.sf(F, k, denominator_df))

    chow_rows, mw_rows = [], []
    for event, date in EVENTS.items():
        for p, s in series.items():
            F, pv = chow_test(s, date)
            chow_rows.append({"Peristiwa": event, "Tanggal": date, "Platform": p, "F": F,
                              "p-value": pv, "Signifikan (α=5%)": bool(pv < ALPHA) if pd.notna(pv) else False})
            before, after = s[s.index < pd.Timestamp(date)], s[s.index >= pd.Timestamp(date)]
            if len(before) >= 6 and len(after) >= 6:
                u, pvalue = stats.mannwhitneyu(before, after, alternative="two-sided")
                mw_rows.append({"Peristiwa": event, "Platform": p, "N sebelum": len(before),
                                "N sesudah": len(after), "Rata-rata sebelum": before.mean(),
                                "Rata-rata sesudah": after.mean(), "Selisih": after.mean()-before.mean(),
                                "p-value": pvalue})
    chow_df = pd.DataFrame(chow_rows)
    mw_df = pd.DataFrame(mw_rows)
    if not mw_df.empty:
        mw_df["p Holm"] = multipletests(mw_df["p-value"], method="holm")[1]

    # A6 Spearman on levels and first differences; cross-correlations
    common = ts.loc[pd.Timestamp(TIKTOK_START):, PLATFORMS]
    corr_level = common.corr(method="spearman")
    corr_diff = common.diff().dropna().corr(method="spearman")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, corr, title in zip(axes, [corr_level, corr_diff], ["Spearman level", "Spearman perubahan bulanan"]):
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax)
        ax.set_title(title)
    plt.tight_layout(); savefig("A6_korelasi.png"); plt.close()

    def ccf_table(x, y, max_lag=6):
        dx, dy = x.diff(), y.diff()
        return pd.Series({
            lag: dx.corr(dy.shift(-lag)) for lag in range(-max_lag, max_lag + 1)
        }, name=f"{x.name} vs {y.name}")

    pairs = [("TikTok Shop", "Tokopedia"), ("TikTok Shop", "Shopee"),
             ("TikTok Shop", "Lazada"), ("Shopee", "Tokopedia")]
    ccf_rows = []
    for a, b in pairs:
        cc = ccf_table(common[a], common[b])
        for lag, corr in cc.items():
            ccf_rows.append({"Platform X": a, "Platform Y": b, "Lag (bulan)": lag, "Korelasi": corr})
    ccf_df = pd.DataFrame(ccf_rows)

    results = {
        "A1_Deskriptif": desc,
        "A2_Tahunan": annual,
        "A2_YoY": yoy,
        "A2_CAGR": cagr_df,
        "A3_MannKendall": mk_df,
        "A4_KekuatanMusiman": strength_df,
        "A4_IndeksMusiman": seas,
        "A5_PELT": pd.DataFrame({p: [", ".join(d.strftime("%Y-%m") for d in breaks[p])] for p in PLATFORMS}).T.rename(columns={0:"Break terdeteksi"}),
        "A5_Chow": chow_df,
        "A5_MannWhitney": mw_df,
        "A6_KorelasiLevel": corr_level,
        "A6_KorelasiDiff": corr_diff,
        "A6_CrossCorrelation": ccf_df,
    }
    return results, breaks


def plot_regional(reg):
    # B1 descriptive stats and ranks
    regional_desc = reg.describe().T
    top_rows, bottom_rows = [], []
    for p in PLATFORMS:
        sorted_s = reg[p].sort_values(ascending=False)
        for rank, (province, value) in enumerate(sorted_s.head(5).items(), 1):
            top_rows.append({"Platform": p, "Peringkat": rank, "Provinsi": province, "Indeks": value})
        for rank, (province, value) in enumerate(sorted_s.tail(5).items(), 1):
            bottom_rows.append({"Platform": p, "Peringkat": rank, "Provinsi": province, "Indeks": value})

    # B2 heatmap and ranking chart
    order = reg.mean(axis=1).sort_values(ascending=False).index
    plt.figure(figsize=(10, 12))
    sns.heatmap(reg.loc[order, PLATFORMS], cmap="YlOrRd", vmin=0, vmax=100,
                linewidths=.2, cbar_kws={"label": "Indeks relatif"})
    plt.title("B2. Search interest per provinsi dan platform")
    plt.tight_layout(); savefig("B2_heatmap_provinsi.png"); plt.close()

    # B3 dominant platform, with scale caveat in README/report
    dominant = reg[PLATFORMS].idxmax(axis=1).rename("Platform dominan")
    dominant_counts = dominant.value_counts().reindex(PLATFORMS, fill_value=0).rename("Jumlah provinsi").to_frame()

    # B4 variation
    var_df = pd.DataFrame({
        "Rata-rata": reg.mean(), "Std": reg.std(),
        "CV (%)": reg.std() / reg.mean() * 100,
        "Rentang": reg.max() - reg.min(),
        "IQR": reg.quantile(.75) - reg.quantile(.25),
    })
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=reg[PLATFORMS])
    plt.title("B4. Sebaran indeks antarprovinsi"); plt.ylabel("Indeks relatif")
    plt.tight_layout(); savefig("B4_boxplot.png"); plt.close()

    # B5 Friedman, Kendall W, post-hoc Wilcoxon-Holm
    friedman_stat, friedman_p = stats.friedmanchisquare(*[reg[p].values for p in PLATFORMS])
    n, k = reg.shape[0], len(PLATFORMS)
    kendall_w = friedman_stat / (n * (k - 1))
    posthoc_rows = []
    for a, b in combinations(PLATFORMS, 2):
        try:
            w_stat, pvalue = stats.wilcoxon(reg[a], reg[b], alternative="two-sided")
        except ValueError:
            w_stat, pvalue = np.nan, np.nan
        posthoc_rows.append({"Pasangan": f"{a} vs {b}", "Median A": reg[a].median(),
                             "Median B": reg[b].median(), "Wilcoxon": w_stat, "p-value": pvalue})
    posthoc = pd.DataFrame(posthoc_rows)
    valid = posthoc["p-value"].notna()
    posthoc["p Holm"] = np.nan
    if valid.any():
        posthoc.loc[valid, "p Holm"] = multipletests(posthoc.loc[valid, "p-value"], method="holm")[1]
    posthoc["Signifikan (α=5%)"] = posthoc["p Holm"] < ALPHA
    friedman = pd.DataFrame([{"N provinsi": n, "Platform": k, "Chi-square": friedman_stat,
                              "p-value": friedman_p, "Kendall W": kendall_w,
                              "Signifikan (α=5%)": friedman_p < ALPHA}])

    # B6 Java vs outside Java, per-platform Holm correction
    missing_java = [p for p in JAWA if p not in reg.index]
    if missing_java:
        raise ValueError(f"Nama provinsi Jawa tidak ditemukan di dataset: {missing_java}")
    is_java = reg.index.isin(JAWA)
    java_rows = []
    for p in PLATFORMS:
        a, b = reg.loc[is_java, p], reg.loc[~is_java, p]
        u, pv = stats.mannwhitneyu(a, b, alternative="two-sided")
        rbc = 2 * u / (len(a) * len(b)) - 1
        java_rows.append({"Platform": p, "N Jawa": len(a), "N luar Jawa": len(b),
                          "Median Jawa": a.median(), "Median luar Jawa": b.median(),
                          "U": u, "p-value": pv, "Rank-biserial r": rbc})
    java_df = pd.DataFrame(java_rows).set_index("Platform")
    java_df["p Holm"] = multipletests(java_df["p-value"], method="holm")[1]

    # B7 Spearman across provinces
    corr_reg = reg.corr(method="spearman")
    corr_p = pd.DataFrame(index=PLATFORMS, columns=PLATFORMS, dtype=float)
    for a in PLATFORMS:
        for b in PLATFORMS:
            corr_p.loc[a, b] = 1.0 if a == b else stats.spearmanr(reg[a], reg[b]).pvalue
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(corr_reg, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax)
    ax.set_title("B7. Korelasi Spearman antarplatform lintas provinsi")
    plt.tight_layout(); savefig("B7_korelasi_regional.png"); plt.close()

    return {
        "B1_Deskriptif": regional_desc,
        "B1_Top5": pd.DataFrame(top_rows),
        "B1_Bottom5": pd.DataFrame(bottom_rows),
        "B3_DominanPerProvinsi": dominant.to_frame().join(reg.max(axis=1).rename("Indeks maksimum")),
        "B3_JumlahDominan": dominant_counts,
        "B4_Variasi": var_df,
        "B5_Friedman": friedman,
        "B5_PostHocHolm": posthoc,
        "B6_JawaLuarJawa": java_df,
        "B7_KorelasiSpearman": corr_reg,
        "B7_pValueKorelasi": corr_p,
    }, dominant, var_df


def display_if_notebook(obj):
    try:
        from IPython.display import display
        display(obj)
    except Exception:
        print(obj)


def main():
    print("=== VALIDASI DATA REGIONAL ===")
    ts, reg, series = prepare_data()
    val_table = pd.DataFrame({
        "Pemeriksaan": [
            "Jumlah provinsi",
            "Jumlah platform",
            "Jumlah indeks regional",
            "Nilai kosong",
            "Periode pengamatan"
        ],
        "Hasil yang diharapkan": [
            len(reg),
            len(PLATFORMS),
            len(reg) * len(PLATFORMS),
            f"{int(reg[PLATFORMS].isna().sum().sum())}, jika terverifikasi",
            "2020–2025"
        ]
    })
    print(val_table.to_string(index=False))

    print("\n=== STATISTIK DESKRIPTIF REGIONAL ===")
    desc_regional = pd.DataFrame({
        "N Provinsi": [len(reg[p]) for p in PLATFORMS],
        "Mean": [reg[p].mean() for p in PLATFORMS],
        "Median": [reg[p].median() for p in PLATFORMS],
        "Std. Dev.": [reg[p].std() for p in PLATFORMS],
        "Minimum": [reg[p].min() for p in PLATFORMS],
        "Maksimum": [reg[p].max() for p in PLATFORMS],
    }, index=PLATFORMS)
    print(desc_regional.round(2).to_string())

    print("\n=== EKSEKUSI ANALISIS REGIONAL & GRAFIK ===")
    regional_results, dominant, var_df = plot_regional(reg)

    print("\n=== EKSEKUSI ANALISIS TREN WAKTU ===")
    temporal_results, breaks = plot_temporal(ts, series)

    # C. Integrated summary
    mk_df = temporal_results["A3_MannKendall"]
    annual = temporal_results["A2_Tahunan"]
    cagr_df = temporal_results["A2_CAGR"]
    strength_df = temporal_results["A4_KekuatanMusiman"]
    seas = temporal_results["A4_IndeksMusiman"]
    summary = pd.DataFrame(index=PLATFORMS)
    summary["Tren Mann-Kendall"] = mk_df["Tren"]
    summary["p-value tren"] = mk_df["p-value"]
    summary["Sen slope/tahun"] = mk_df["Sen slope (indeks/tahun)"]
    summary["CAGR (%)"] = cagr_df["CAGR (%)"]
    summary["Kekuatan musiman Fs"] = strength_df["Kekuatan musiman (Fs)"]
    summary["Bulan puncak musiman"] = seas.idxmax()
    summary["Break terdeteksi"] = [
        ", ".join(d.strftime("%b %Y") for d in breaks[p]) or "-" for p in PLATFORMS
    ]
    summary["Rata-rata regional"] = reg.mean()
    summary["CV regional (%)"] = var_df["CV (%)"]
    summary["Provinsi tertinggi"] = [reg[p].idxmax() for p in PLATFORMS]
    summary["Jumlah provinsi dominan"] = regional_results["B3_JumlahDominan"]["Jumlah provinsi"]
    print("\n=== BAGIAN C: RINGKASAN TERPADU ===")
    display_if_notebook(summary.round(3))

    all_results = {"C_Ringkasan": summary, **temporal_results, **regional_results}
    output_path = OUT_DIR / "hasil_analisis.xlsx"
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet, df in all_results.items():
            if isinstance(df, pd.Series):
                df = df.to_frame()
            if not isinstance(df, pd.DataFrame):
                continue
            df.to_excel(writer, sheet_name=sheet[:31])
    print(f"\nSelesai. Tabel disimpan ke: {output_path}")
    print(f"Grafik disimpan di: {OUT_DIR}")
    print("Catatan: hasil statistik harus diinterpretasikan bersama batasan skala relatif Google Trends.")


if __name__ == "__main__":
    main()
