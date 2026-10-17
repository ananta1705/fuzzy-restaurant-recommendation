from pathlib import Path

# Sesuaikan jika menjalankan dari lokasi kerja yang berbeda.
PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "raw" / "Dataset E-Commerce.xlsx"
OUT_DIR = PROJECT_DIR / "output_analisis"

PLATFORMS = ["Shopee", "Tokopedia", "Lazada", "Blibli", "TikTok Shop"]
TIKTOK_START = "2021-09-01"

EVENTS = {
    "Larangan social commerce (Permendag 31/2023)": "2023-10-01",
    "Integrasi Tokopedia–TikTok Shop": "2023-12-01",
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
