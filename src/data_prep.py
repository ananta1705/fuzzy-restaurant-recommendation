import pandas as pd
from .config import DATA_PATH, PLATFORMS, TIKTOK_START

def load_sheet(sheet_name: str) -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {DATA_PATH}")
    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name, header=2)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df.columns = df.columns.astype(str).str.strip()
    return df.rename(columns={
        "Tiktok Shop": "TikTok Shop",
        "Tiktok shop": "TikTok Shop",
    })

def prepare_data():
    ts_raw = load_sheet("Time Series")
    reg_raw = load_sheet("Regional")

    for name, df in [("Time Series", ts_raw), ("Regional", reg_raw)]:
        missing = [c for c in PLATFORMS if c not in df.columns]
        if missing:
            raise ValueError(f"Kolom platform hilang pada {name}: {missing}")

    if "Kode Periode" not in ts_raw:
        raise ValueError("Kolom 'Kode Periode' tidak ditemukan.")
    if "Wilayah" not in reg_raw:
        raise ValueError("Kolom 'Wilayah' tidak ditemukan.")

    ts_raw["Kode Periode"] = pd.to_datetime(ts_raw["Kode Periode"], errors="coerce")
    if ts_raw["Kode Periode"].isna().any():
        raise ValueError("Ada tanggal kosong/tidak valid.")
    if ts_raw["Kode Periode"].duplicated().any():
        raise ValueError("Ada tanggal duplikat.")

    for c in PLATFORMS:
        ts_raw[c] = pd.to_numeric(ts_raw[c], errors="coerce")
        reg_raw[c] = pd.to_numeric(reg_raw[c], errors="coerce")

    if ts_raw[PLATFORMS].isna().any().any():
        raise ValueError("Ada nilai kosong/nonnumerik pada Time Series.")
    if reg_raw[PLATFORMS].isna().any().any():
        raise ValueError("Ada nilai kosong/nonnumerik pada Regional.")

    ts = ts_raw.set_index("Kode Periode").sort_index()
    expected = pd.date_range("2020-01-01", "2025-12-01", freq="MS")
    if not ts.index.equals(expected):
        raise ValueError("Tanggal tidak lengkap atau tidak sesuai periode 2020–2025.")

    reg_raw["Wilayah"] = reg_raw["Wilayah"].astype("string").str.strip()
    if reg_raw["Wilayah"].isna().any() or (reg_raw["Wilayah"] == "").any():
        raise ValueError("Ada nama wilayah kosong.")
    if reg_raw["Wilayah"].duplicated().any():
        raise ValueError("Ada nama wilayah duplikat.")

    reg = reg_raw.set_index("Wilayah")[PLATFORMS].copy()
    if len(reg) != 34:
        raise ValueError(f"Jumlah wilayah {len(reg)}, seharusnya 34.")

    for name, df in [("Time Series", ts), ("Regional", reg)]:
        if not df[PLATFORMS].apply(lambda col: col.between(0, 100).all()).all():
            raise ValueError(f"Ada indeks di luar rentang 0–100 pada {name}.")

    series = {p: ts[p].copy() for p in PLATFORMS}
    series["TikTok Shop"] = series["TikTok Shop"].loc[pd.Timestamp(TIKTOK_START):].copy()
    return ts, reg, series

if __name__ == "__main__":
    ts, reg, series = prepare_data()
    print("Time Series:", ts.shape, ts.index.min(), ts.index.max())
    print("Regional:", reg.shape)
    print("TikTok Shop active observations:", len(series["TikTok Shop"]))
