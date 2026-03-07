#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | ENGULFING (EXACT TEXTBOOK VERSION)

✔ EXACT body-to-body engulfing
✔ NO doji
✔ NO trend
✔ NO volume
✔ MATCHES IMAGE PERFECTLY
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Save files with today's date
today = datetime.now().strftime("%Y-%m-%d")

OUT_BULL = OUT_DIR / f"fno_bullish_engulfing_{today}.csv"
OUT_BEAR = OUT_DIR / f"fno_bearish_engulfing_{today}.csv"

# =================================================
# PARAMETERS
# =================================================
MIN_BODY_RATIO = 0.40   # 40% of candle range → not doji

# =================================================
# CHECK CONFIG FILE
# =================================================
if not FNO_FILE.exists():
    print(f" Missing file: {FNO_FILE}")
    exit()

# =================================================
# LOAD SYMBOLS
# =================================================
symbols = set(
    pd.read_csv(FNO_FILE)["SYMBOL"]
    .astype(str).str.strip().str.upper()
)

bullish = []
bearish = []

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

        # DATE parse
        parsed = pd.to_datetime(df["DATE"], format="%d-%m-%Y", errors="coerce")
        df["DATE"] = parsed.fillna(pd.to_datetime(df["DATE"], errors="coerce"))

        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 2:
            continue

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        # BODY RATIO
        def body_ratio(c):
            rng = c["HIGH"] - c["LOW"]
            if rng <= 0:
                return 0
            return abs(c["CLOSE"] - c["OPEN"]) / rng

        # Reject DOJI
        if body_ratio(prev) < MIN_BODY_RATIO or body_ratio(curr) < MIN_BODY_RATIO:
            continue

        # -------------------------
        #  BULLISH ENGULFING
        # -------------------------
        if (
            prev["CLOSE"] < prev["OPEN"] and
            curr["CLOSE"] > curr["OPEN"] and
            curr["OPEN"]  < prev["CLOSE"] and
            curr["CLOSE"] > prev["OPEN"]
        ):

            bullish.append({
                "SYMBOL": symbol,
                "DATE": curr["DATE"].date(),
                "PATTERN": "BULLISH_ENGULFING"
            })

            print(f" EXACT BULLISH ENGULFING → {symbol}")
            continue

        # -------------------------
        #  BEARISH ENGULFING
        # -------------------------
        if (
            prev["CLOSE"] > prev["OPEN"] and
            curr["CLOSE"] < curr["OPEN"] and
            curr["OPEN"]  > prev["CLOSE"] and
            curr["CLOSE"] < prev["OPEN"]
        ):

            bearish.append({
                "SYMBOL": symbol,
                "DATE": curr["DATE"].date(),
                "PATTERN": "BEARISH_ENGULFING"
            })

            print(f" EXACT BEARISH ENGULFING → {symbol}")

    except Exception as e:
        print(f" ERROR → {symbol} | {e}")

# =================================================
# SAVE
# =================================================
if bullish:
    pd.DataFrame(bullish).to_csv(OUT_BULL, index=False)

if bearish:
    pd.DataFrame(bearish).to_csv(OUT_BEAR, index=False)

print("\n EXACT ENGULFING SCAN COMPLETED")
print(f" Bullish found: {len(bullish)}")
print(f" Bearish found: {len(bearish)}")