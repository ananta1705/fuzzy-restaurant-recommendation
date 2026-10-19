from src.data_prep import prepare_data
from src.config import PLATFORMS

_, reg, _ = prepare_data()

print("\n=== VALIDASI DATA REGIONAL ===")
print(f"Jumlah provinsi: {len(reg)}")
print(f"Jumlah platform: {len(PLATFORMS)}")
print(f"Jumlah indeks regional: {len(reg) * len(PLATFORMS)}")
print(f"Nilai kosong: {int(reg[PLATFORMS].isna().sum().sum())}")
print("Periode pengamatan: 2020–2025")
print("\nValidasi selesai.")
