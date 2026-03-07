#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | STEP-5
F&O stocks with:
✔ Last 4 consecutive RED candles
✔ STRICTLY increasing volume (TOTTRDQTY)

Short momentum confirmation scanner
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(
    r"H:\MarketForge\data\master\Equity_stock_master"
)

FNO_FILE = Path(
    r"H:\CANDLE-LAB\config\fno_symbols.csv"
)

OUT_DIR = Path(
    r"H:\CANDLE-LAB\analysis\equity\signals"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Daily output file
today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_4day_red_volume_rising_{today}.csv"

# =================================================
# CHECK CONFIG FILE
# =================================================
if not FNO_FILE.exists():
    print(f" Missing file: {FNO_FILE}")
    exit()

# =================================================
# LOAD F&O SYMBOLS
# =================================================
fno_df = pd.read_csv(FNO_FILE)

fno_symbols = set(
    fno_df["SYMBOL"]
    .astype(str)
    .str.strip()
    .str.upper()
)

print(f" F&O symbols loaded: {len(fno_symbols)}")

# =================================================
# PROCESS
# =================================================
results = []

for symbol in sorted(fno_symbols):

    csv_file = EQUITY_DIR / f"{symbol}.csv"

    if not csv_file.exists():
        continue

    try:
        df = pd.read_csv(csv_file)

        if df.empty:
            continue

        df.columns = df.columns.str.strip()

        required_cols = {"DATE", "OPEN", "CLOSE", "TOTTRDQTY"}

        if not required_cols.issubset(df.columns):
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

        if len(df) < 4:
            continue

        last4 = df.tail(4).copy()

        # --------------------------------------------------
        # CONDITION 1 → 4 RED CANDLES
        # --------------------------------------------------
        if not (last4["CLOSE"] < last4["OPEN"]).all():
            continue

        # --------------------------------------------------
        # CONDITION 2 → STRICTLY INCREASING VOLUME
        # --------------------------------------------------
        vols = last4["TOTTRDQTY"].values

        if not (vols[0] < vols[1] < vols[2] < vols[3]):
            continue

        # Strength metrics
        last4["BODY"] = last4["OPEN"] - last4["CLOSE"]

        results.append({
            "SYMBOL": symbol,
            "FROM_DATE": last4.iloc[0]["DATE"].date(),
            "TO_DATE": last4.iloc[-1]["DATE"].date(),
            "VOL_D1": int(vols[0]),
            "VOL_D2": int(vols[1]),
            "VOL_D3": int(vols[2]),
            "VOL_D4": int(vols[3]),
            "AVG_BODY": round(last4["BODY"].mean(), 2),
            "TOTAL_BODY": round(last4["BODY"].sum(), 2)
        })

        print(f" 4D RED + VOL ↑ → {symbol}")

    except Exception as e:
        print(f" ERROR {symbol} | {e}")

# =================================================
# SAVE
# =================================================
if results:

    out_df = pd.DataFrame(results)

    out_df = out_df.sort_values(
        "TOTAL_BODY",
        ascending=False
    )

    out_df.to_csv(OUT_FILE, index=False)

    print("\n 4-DAY RED + VOLUME RISING SCAN COMPLETED")
    print(f" Stocks found: {len(out_df)}")
    print(f" Saved {OUT_FILE}")

else:
    print("\n No stocks matched red + volume criteria")