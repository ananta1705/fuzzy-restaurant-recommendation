import numpy as np
import pandas as pd
import pymannkendall as mk
from statsmodels.tsa.seasonal import STL
from .config import PLATFORMS

def descriptive_statistics(series: dict) -> pd.DataFrame:
    rows = []
    for platform in PLATFORMS:
        s = series[platform].dropna()
        mean = s.mean()
        rows.append({
            "Platform": platform,
            "N": len(s),
            "Mean": mean,
            "Std": s.std(),
            "Min": s.min(),
            "Max": s.max(),
            "CV (%)": (s.std() / mean * 100) if mean else np.nan,
            "Peak month": s.idxmax(),
        })
    return pd.DataFrame(rows).set_index("Platform")

def mann_kendall_summary(series: dict) -> pd.DataFrame:
    rows = []
    for platform, s in series.items():
        result = mk.original_test(s.dropna().values)
        rows.append({
            "Platform": platform,
            "Trend": result.trend,
            "p_value": result.p,
            "Sen_slope_per_month": result.slope,
            "Sen_slope_per_year": result.slope * 12,
        })
    return pd.DataFrame(rows).set_index("Platform")

def stl_decomposition(series: dict) -> dict:
    results = {}
    for platform, s in series.items():
        if len(s.dropna()) < 24:
            continue
        results[platform] = STL(s.dropna(), period=12, robust=True).fit()
    return results
