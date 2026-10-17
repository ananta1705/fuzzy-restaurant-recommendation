from pathlib import Path
import pandas as pd
from .config import OUT_DIR

def export_excel(sheets: dict[str, pd.DataFrame], filename="hasil_analisis.xlsx") -> Path:
    path = OUT_DIR / filename
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name[:31])
    return path
