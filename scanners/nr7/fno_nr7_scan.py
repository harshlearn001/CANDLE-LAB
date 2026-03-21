#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | NR7 VOLATILITY SCANNER (FILTERED)

✔ F&O only
✔ NR7 (lowest range of last 7 candles)
✔ Trend filter (MA20)
✔ Volume contraction
✔ Production-ready
"""

import pandas as pd
import os
from datetime import datetime

print("\nNR7 VOLATILITY SCANNER STARTED\n")

# =====================================================
# PATHS
# =====================================================
EQUITY_MASTER = r"H:\MarketForge\data\master\Equity_stock_master"
FNO_SYMBOLS   = r"H:\CANDLE-LAB\config\fno_symbols.csv"
OUTPUT        = r"H:\CANDLE-LAB\analysis\equity\signals\nr7"

os.makedirs(OUTPUT, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
fno = pd.read_csv(FNO_SYMBOLS)
symbols = fno["SYMBOL"].astype(str).str.strip().str.upper().tolist()

print("F&O symbols loaded:", len(symbols))

nr7_list = []

# =====================================================
# PROCESS
# =====================================================
for sym in symbols:

    file = os.path.join(EQUITY_MASTER, f"{sym}.csv")

    if not os.path.exists(file):
        continue

    try:
        df = pd.read_csv(file)

        if df.empty or len(df) < 30:
            continue

        # STANDARDIZE COLUMNS
        df.columns = df.columns.str.strip().str.upper()

        required = {"DATE","OPEN","HIGH","LOW","CLOSE"}
        if not required.issubset(df.columns):
            continue

        # HANDLE VOLUME COLUMN SAFELY
        if "TOTTRDQTY" not in df.columns:
            df["TOTTRDQTY"] = 0

        # DATE PARSE (robust)
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 30:
            continue

        # =====================================================
        # CALCULATIONS
        # =====================================================
        df["RANGE"] = df["HIGH"] - df["LOW"]
        df["MA20"] = df["CLOSE"].rolling(20).mean()
        df["VOL_AVG"] = df["TOTTRDQTY"].rolling(20).mean()

        # DROP NA (important)
        df = df.dropna(subset=["MA20", "VOL_AVG"])

        if len(df) < 7:
            continue

        last7 = df.tail(7)

        today = last7.iloc[-1]
        prev6 = last7.iloc[:-1]

        # =====================================================
        # NR7 CONDITION
        # =====================================================
        nr7 = today["RANGE"] < prev6["RANGE"].min()

        # =====================================================
        # TREND FILTER
        # =====================================================
        trend = today["CLOSE"] > today["MA20"]

        # =====================================================
        # VOLUME CONTRACTION
        # =====================================================
        vol_contract = today["TOTTRDQTY"] < today["VOL_AVG"]

        # =====================================================
        # FINAL SIGNAL
        # =====================================================
        if nr7 and trend and vol_contract:

            print(f" NR7 FOUND → {sym}")

            nr7_list.append({
                "SYMBOL": sym,
                "DATE": today["DATE"].date(),
                "CLOSE": today["CLOSE"],
                "RANGE": round(today["RANGE"], 2),
                "MA20": round(today["MA20"], 2),
                "VOLUME": int(today["TOTTRDQTY"]),
                "VOL_AVG": int(today["VOL_AVG"]),
                "TYPE": "NR7_BREAKOUT_SETUP"
            })

    except Exception as e:
        print(f" ERROR → {sym} | {e}")

# =====================================================
# SAVE OUTPUT
# =====================================================
out = pd.DataFrame(nr7_list)

today_str = datetime.now().strftime("%Y-%m-%d")

outfile = os.path.join(
    OUTPUT, f"fno_nr7_filtered_{today_str}.csv"
)

if not out.empty:
    out = out.sort_values("RANGE")  # tightest first
    out.to_csv(outfile, index=False)

    print("\n NR7 FILTERED SCAN COMPLETED")
    print(" Stocks found:", len(out))
    print(" Saved →", outfile)

else:
    print("\n No NR7 signals found")