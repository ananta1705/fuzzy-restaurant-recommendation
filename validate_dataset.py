from src.data_prep import prepare_data
from src.config import PLATFORMS

ts, reg, series = prepare_data()

print("\\n=== VALIDASI DATASET ===")
print(f"Time Series: {len(ts)} baris | {ts.index.min().date()} s.d. {ts.index.max().date()}")
print(f"Nilai kosong Time Series: {ts[PLATFORMS].isna().sum().sum()}")
print(f"Regional: {len(reg)} provinsi")
print(f"Nilai kosong Regional: {reg[PLATFORMS].isna().sum().sum()}")
print(f"TikTok Shop: {len(series['TikTok Shop'])} observasi sejak {series['TikTok Shop'].index.min().date()}")
print("\\nValidasi selesai.")
