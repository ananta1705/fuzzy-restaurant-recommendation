import pandas as pd
from scipy import stats
from .config import PLATFORMS

JAWA = ["Banten", "DKI Jakarta", "Jawa Barat", "Jawa Tengah",
        "DI Yogyakarta", "Jawa Timur"]

def regional_descriptives(reg: pd.DataFrame) -> pd.DataFrame:
    out = reg[PLATFORMS].describe().T
    out["CV (%)"] = reg[PLATFORMS].std() / reg[PLATFORMS].mean() * 100
    return out

def friedman_test(reg: pd.DataFrame) -> dict:
    statistic, p_value = stats.friedmanchisquare(
        *[reg[p].values for p in PLATFORMS]
    )
    return {"statistic": statistic, "p_value": p_value, "n_provinces": len(reg)}

def dominant_platform_by_province(reg: pd.DataFrame) -> pd.Series:
    return reg[PLATFORMS].idxmax(axis=1).rename("Platform dominan")
