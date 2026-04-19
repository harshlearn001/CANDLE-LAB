#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | STEP-0 FINAL (FIXED FOR NSE FUT DATA)

✔ Uses TRADE_DATE column
✔ Filters only ACTIVE symbols
✔ No external CSV needed
✔ Fully compatible with your data
"""

from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# =================================================
# PATHS
# =================================================
FUT_DIR = Path(r"H:\MarketForge\data\master\Futures_master\FUTSTK")

OUT_DIR = Path(r"H:\CANDLE-LAB\config")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "fno_symbols.csv"

# =================================================
# SETTINGS
# =================================================
CUTOFF_DAYS = 10   # adjust if needed
MIN_ROWS = 20

# =================================================
# LOAD FILES
# =================================================
csv_files = list(FUT_DIR.glob("*.csv"))

print(f"📁 FUTSTK files found: {len(csv_files)}")

if not csv_files:
    print("❌ No files found")
    exit()

# =================================================
# STEP-1: RAW SYMBOLS
# =================================================
raw_symbols = [f.stem.upper() for f in csv_files]
print(f"🔍 Raw symbols extracted: {len(raw_symbols)}")

# =================================================
# STEP-2: FILTER USING TRADE_DATE
# =================================================
cutoff_date = datetime.now() - timedelta(days=CUTOFF_DAYS)

filtered_symbols = []

for file in csv_files:
    try:
        df = pd.read_csv(file)

        # must have TRADE_DATE
        if "TRADE_DATE" not in df.columns:
            continue

        # convert date
        df["TRADE_DATE"] = pd.to_datetime(df["TRADE_DATE"], format="%Y%m%d", errors="coerce")

        last_date = df["TRADE_DATE"].max()

        if pd.notna(last_date) and last_date >= cutoff_date and len(df) >= MIN_ROWS:
            filtered_symbols.append(file.stem.upper())

    except Exception as e:
        print(f"⚠ Skipped {file.name} | {e}")

# remove duplicates
filtered_symbols = sorted(set(filtered_symbols))

print(f"✅ Active F&O symbols (filtered): {len(filtered_symbols)}")

# =================================================
# STEP-3: REMOVE INDEX (OPTIONAL)
# =================================================
EXCLUDE = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]

filtered_symbols = [s for s in filtered_symbols if s not in EXCLUDE]

# =================================================
# SAVE
# =================================================
if filtered_symbols:

    df_out = pd.DataFrame(filtered_symbols, columns=["SYMBOL"])
    df_out.to_csv(OUT_FILE, index=False)

    print("\n🎯 F&O SYMBOL MASTER BUILT (FINAL CLEAN)")
    print(f"📊 Total Symbols : {len(df_out)}")
    print(f"💾 Saved → {OUT_FILE}")

else:
    print("❌ No valid symbols after filtering")