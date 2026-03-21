#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | SHOOTING STAR (UPTREND) - FINAL

✔ F&O only
✔ Price-based uptrend
✔ Strong candle quality filter
✔ Clean production code
"""

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\shooting_star")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_shooting_star_uptrend_{today}.csv"

# =================================================
# LOAD F&O SYMBOLS
# =================================================
if not FNO_FILE.exists():
    print(f"Missing file: {FNO_FILE}")
    exit()

fno_symbols = set(
    pd.read_csv(FNO_FILE)["SYMBOL"]
    .astype(str).str.strip().str.upper()
)

print(f"F&O symbols loaded: {len(fno_symbols)}")

results = []

# =================================================
# PROCESS
# =================================================
for symbol in sorted(fno_symbols):

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)

        if df.empty:
            continue

        # STANDARDIZE COLUMNS
        df.columns = df.columns.str.strip().str.upper()

        required = {"DATE","OPEN","HIGH","LOW","CLOSE"}
        if not required.issubset(df.columns):
            continue

        # DATE PARSE (robust)
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 10:
            continue

        # =================================================
        # UPTREND CHECK (IMPROVED)
        # =================================================
        c1 = df.iloc[-6]["CLOSE"]
        c2 = df.iloc[-3]["CLOSE"]
        c3 = df.iloc[-1]["CLOSE"]

        if not (c1 < c2 < c3):
            continue

        # =================================================
        # CURRENT CANDLE
        # =================================================
        c = df.iloc[-1]

        o, h, l, cl = c["OPEN"], c["HIGH"], c["LOW"], c["CLOSE"]

        rng = h - l
        if rng <= 0:
            continue

        body = abs(cl - o)
        upper = h - max(o, cl)
        lower = min(o, cl) - l

        body_pct  = body / rng
        upper_pct = upper / rng
        lower_pct = lower / rng

        # =================================================
        # QUALITY FILTER
        # =================================================
        recent_ranges = df.iloc[-10:-1]["HIGH"] - df.iloc[-10:-1]["LOW"]

        if rng < np.median(recent_ranges):
            continue

        # =================================================
        # SHOOTING STAR CONDITIONS
        # =================================================
        if (
            body_pct <= 0.40 and
            upper_pct >= 0.50 and
            lower_pct <= 0.15
        ):

            results.append({
                "SYMBOL": symbol,
                "DATE": c["DATE"].date(),
                "OPEN": o,
                "HIGH": h,
                "LOW": l,
                "CLOSE": cl,
                "BODY_%": round(body_pct*100,2),
                "UPPER_WICK_%": round(upper_pct*100,2),
                "LOWER_WICK_%": round(lower_pct*100,2),
                "PATTERN": "SHOOTING_STAR",
                "TREND": "UP"
            })

            print(f" SHOOTING STAR → {symbol}")

    except Exception as e:
        print(f" ERROR → {symbol} | {e}")

# =================================================
# SAVE
# =================================================
if results:

    out = pd.DataFrame(results)

    out = out.sort_values(
        "UPPER_WICK_%",
        ascending=False
    )

    out.to_csv(OUT_FILE, index=False)

    print("\n SHOOTING STAR SCAN COMPLETED")
    print(f" Stocks found: {len(out)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n No Shooting Star found")