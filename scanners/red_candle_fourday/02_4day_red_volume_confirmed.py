#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | STEP-6 (REFINED)

F&O stocks with:
✔ Last 4 RED candles
✔ Last day volume > avg of previous 3 days

Short momentum confirmation scanner
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Daily output file
today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_4day_red_volume_confirmed_{today}.csv"

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
    .astype(str)
    .str.strip()
    .str.upper()
)

print(f" F&O symbols loaded: {len(fno_symbols)}")

results = []

# =================================================
# PROCESS
# =================================================
for symbol in sorted(fno_symbols):

    csv_file = EQUITY_DIR / f"{symbol}.csv"

    if not csv_file.exists():
        continue

    try:
        df = pd.read_csv(csv_file)

        if df.empty:
            continue

        df.columns = df.columns.str.strip()

        req = {"DATE", "OPEN", "CLOSE", "TOTTRDQTY"}
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

        if len(df) < 4:
            continue

        last4 = df.tail(4)

        # --------------------------------------------------
        # CONDITION 1 → 4 RED CANDLES
        # --------------------------------------------------
        if not (last4["CLOSE"] < last4["OPEN"]).all():
            continue

        vols = last4["TOTTRDQTY"].values
        avg_prev_3 = vols[:3].mean()

        # --------------------------------------------------
        # CONDITION 2 → VOLUME CONFIRMATION
        # --------------------------------------------------
        if vols[3] <= avg_prev_3:
            continue

        total_body = (last4["OPEN"] - last4["CLOSE"]).sum()

        results.append({
            "SYMBOL": symbol,
            "FROM_DATE": last4.iloc[0]["DATE"].date(),
            "TO_DATE": last4.iloc[-1]["DATE"].date(),
            "VOL_LAST": int(vols[3]),
            "AVG_VOL_PREV_3": int(avg_prev_3),
            "TOTAL_BODY": round(total_body, 2)
        })

        print(f" RED + VOL CONFIRMED → {symbol}")

    except Exception as e:
        print(f"ERROR  {symbol} | {e}")

# =================================================
# SAVE
# =================================================
if results:

    out = pd.DataFrame(results).sort_values(
        "TOTAL_BODY",
        ascending=False
    )

    out.to_csv(OUT_FILE, index=False)

    print("\ RED + VOLUME CONFIRMED SCAN COMPLETED")
    print(f" Stocks found: {len(out)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n No stocks matched refined red + volume criteria")