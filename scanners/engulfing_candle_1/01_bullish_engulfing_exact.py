#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | BULLISH ENGULFING (EXACT TEXTBOOK)

✔ Previous candle RED (not doji)
✔ Current candle GREEN (not doji)
✔ Current BODY fully engulfs previous BODY
✔ NO trend, NO volume, NO smart logic
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\engulfing")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_bullish_engulfing_{today}.csv"
# =================================================
# PARAMETERS
# =================================================
MIN_BODY_RATIO = 0.40   # 40% of range = not doji

# =================================================
# LOAD SYMBOLS
# =================================================
symbols = set(
    pd.read_csv(FNO_FILE)["SYMBOL"]
    .astype(str).str.strip().str.upper()
)

results = []

print(f" F&O symbols loaded: {len(symbols)}")

# =================================================
# PROCESS
# =================================================
for symbol in sorted(symbols):

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)

        if len(df) < 2:
            continue

        df.columns = df.columns.str.strip()

        req = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}
        if not req.issubset(df.columns):
            continue

        # ---------------------------------------------
        # DATE PARSE
        # ---------------------------------------------
        parsed = pd.to_datetime(df["DATE"], format="%d-%m-%Y", errors="coerce")
        df["DATE"] = parsed.fillna(pd.to_datetime(df["DATE"], errors="coerce"))

        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 2:
            continue

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        # ---------------------------------------------
        # BODY RATIO (DOJI FILTER)
        # ---------------------------------------------
        def body_ratio(c):
            rng = c["HIGH"] - c["LOW"]
            if rng <= 0:
                return 0
            return abs(c["CLOSE"] - c["OPEN"]) / rng

        if body_ratio(prev) < MIN_BODY_RATIO:
            continue

        if body_ratio(curr) < MIN_BODY_RATIO:
            continue

        # ---------------------------------------------
        # EXACT BULLISH ENGULFING
        # ---------------------------------------------
        if (
            prev["CLOSE"] < prev["OPEN"] and
            curr["CLOSE"] > curr["OPEN"] and
            curr["OPEN"]  < prev["CLOSE"] and
            curr["CLOSE"] > prev["OPEN"]
        ):

            results.append({
                "SYMBOL": symbol,
                "DATE": curr["DATE"].date(),
                "PATTERN": "BULLISH_ENGULFING"
            })

            print(f" EXACT BULLISH ENGULFING → {symbol}")

    except Exception as e:
        print(f" ERROR  {symbol} | {e}")

# =================================================
# SAVE
# =================================================
if results:
    pd.DataFrame(results).to_csv(OUT_FILE, index=False)

print("\n BULLISH ENGULFING SCAN COMPLETED")
print(f" Stocks found: {len(results)}")
print(f"Saved  {OUT_FILE}")