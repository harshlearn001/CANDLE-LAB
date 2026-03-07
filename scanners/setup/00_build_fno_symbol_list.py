#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | STEP-0
Build F&O Symbol Master from NSE Futures (FUTSTK)

✔ NSE source of truth
✔ Deduplicated
✔ Reusable across scanners
✔ Safe & deterministic
"""

from pathlib import Path
import pandas as pd

# =================================================
# PATHS
# =================================================
FUT_DIR = Path(
    r"H:\MarketForge\data\master\Futures_master\FUTSTK"
)

OUT_DIR = Path(
    r"H:\CANDLE-LAB\config"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "fno_symbols.csv"

# =================================================
# CHECK SOURCE DIRECTORY
# =================================================
if not FUT_DIR.exists():
    print(f" FUTSTK directory not found → {FUT_DIR}")
    exit()

# =================================================
# PROCESS
# =================================================
symbols = set()

csv_files = sorted(FUT_DIR.glob("*.csv"))
print(f" FUTSTK files found: {len(csv_files)}")

if not csv_files:
    print(" No FUTSTK CSV files found")
    exit()

for file in csv_files:

    try:
        df = pd.read_csv(file)

        if "SYMBOL" not in df.columns:
            print(f"SKIPPED (NO SYMBOL COLUMN) → {file.name}")
            continue

        syms = (
            df["SYMBOL"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # remove invalid entries
        syms = syms[syms != "NAN"]

        symbols.update(syms)

    except Exception as e:
        print(f" ERROR  {file.name} | {e}")

# =================================================
# SAVE
# =================================================
if symbols:

    out_df = pd.DataFrame(
        sorted(symbols),
        columns=["SYMBOL"]
    )

    out_df.to_csv(OUT_FILE, index=False)

    print("\n F&O SYMBOL MASTER BUILT")
    print(f" Total F&O symbols : {len(out_df)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n No F&O symbols found")