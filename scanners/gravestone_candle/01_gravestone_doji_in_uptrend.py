#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | GRAVESTONE DOJI (UPTREND) - FINAL

✔ F&O only
✔ Valid only in UPTREND
✔ Practical market rules
✔ No indicators
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

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\gravestone")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_gravestone_doji_uptrend_{today}.csv"

# =================================================
# CHECK CONFIG FILE
# =================================================
if not FNO_FILE.exists():
    print(f" Missing file: {FNO_FILE}")
    exit()

# =================================================
# LOAD F&O SYMBOLS
# =================================================
fno_symbols = set(
    pd.read_csv(FNO_FILE)["SYMBOL"]
    .astype(str).str.strip().str.upper()
)

print(f" F&O symbols loaded: {len(fno_symbols)}")

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

        df.columns = df.columns.str.strip()

        req = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}

        if not req.issubset(df.columns):
            continue

        # --------------------------------------------------
        # DATE PARSE (NSE SAFE)
        # --------------------------------------------------
        parsed = pd.to_datetime(
            df["DATE"],
            format="%d-%m-%Y",
            errors="coerce"
        )

        df["DATE"] = parsed.fillna(
            pd.to_datetime(df["DATE"], errors="coerce")
        )

        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 10:
            continue

        # --------------------------------------------------
        # UPTREND CONTEXT
        # --------------------------------------------------
        if df.iloc[-3]["CLOSE"] <= df.iloc[-6]["CLOSE"]:
            continue

        # --------------------------------------------------
        # CURRENT CANDLE
        # --------------------------------------------------
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

        # --------------------------------------------------
        # QUALITY FILTER (ACTIVE CANDLE)
        # --------------------------------------------------
        recent_ranges = (
            df.iloc[-10:-1]["HIGH"] - df.iloc[-10:-1]["LOW"]
        )

        if rng < np.median(recent_ranges):
            continue

        # --------------------------------------------------
        # GRAVESTONE CONDITIONS
        # --------------------------------------------------
        if (
            body_pct <= 0.20 and
            upper_pct >= 0.50 and
            lower_pct <= 0.20
        ):

            results.append({
                "SYMBOL": symbol,
                "DATE": c["DATE"].date(),
                "OPEN": o,
                "HIGH": h,
                "LOW": l,
                "CLOSE": cl,
                "BODY_%": round(body_pct * 100, 2),
                "UPPER_WICK_%": round(upper_pct * 100, 2),
                "LOWER_WICK_%": round(lower_pct * 100, 2),
                "TREND": "UP"
            })

            print(f" GRAVESTONE (UPTREND) → {symbol}")

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

    print("\n GRAVESTONE DOJI (UPTREND) SCAN COMPLETED")
    print(f"Stocks found: {len(out)}")
    print(f" Saved  {OUT_FILE}")

else:
    print("\n No Gravestone Doji found in uptrend")