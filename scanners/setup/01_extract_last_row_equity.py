#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | STEP-1 (F&O ONLY)

Extract LAST ROW from each F&O Equity Stock Master CSV

✔ DATE kept in CAPITAL
✔ Mixed NSE date formats handled
✔ F&O universe only
✔ Deterministic & safe
"""

from pathlib import Path
import pandas as pd

# =================================================
# PATHS
# =================================================
SRC_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")

FNO_FILE = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\last_row")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "fno_equity_last_row.csv"

# =================================================
# CHECK CONFIG FILE
# =================================================
if not FNO_FILE.exists():
    print(f" Missing file → {FNO_FILE}")
    exit()

# =================================================
# LOAD F&O SYMBOLS
# =================================================
fno_df = pd.read_csv(FNO_FILE)

if "SYMBOL" not in fno_df.columns:
    print(" SYMBOL column missing in fno_symbols.csv")
    exit()

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
rows = []

csv_files = sorted(SRC_DIR.glob("*.csv"))
print(f" Equity files found: {len(csv_files)}")

for file in csv_files:

    symbol = file.stem.strip().upper()

    # -------------------------------------------------
    # F&O FILTER
    # -------------------------------------------------
    if symbol not in fno_symbols:
        continue

    try:
        df = pd.read_csv(file)

        if df.empty:
            print(f" EMPTY FILE → {symbol}")
            continue

        # keep headers EXACT
        df.columns = df.columns.str.strip()

        if "DATE" not in df.columns:
            print(f"SKIPPED (NO DATE) → {symbol}")
            continue

        # -------------------------------------------------
        # NSE-safe DATE parsing
        # -------------------------------------------------
        parsed = pd.to_datetime(
            df["DATE"],
            format="%d-%m-%Y",
            errors="coerce"
        )

        df["DATE"] = parsed.fillna(
            pd.to_datetime(df["DATE"], errors="coerce")
        )

        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if df.empty:
            print(f" NO VALID DATE ROWS → {symbol}")
            continue

        last_row = df.iloc[-1].copy()

        # ensure symbol always exists
        last_row["SYMBOL"] = symbol

        rows.append(last_row)

        print(f" {symbol} | LAST DATE → {last_row['DATE'].date()}")

    except Exception as e:
        print(f" ERROR {symbol} | {e}")

# =================================================
# SAVE
# =================================================
if rows:

    out_df = pd.DataFrame(rows)

    # put SYMBOL column first
    if "SYMBOL" in out_df.columns:
        cols = ["SYMBOL"] + [c for c in out_df.columns if c != "SYMBOL"]
        out_df = out_df[cols]

    out_df.to_csv(OUT_FILE, index=False)

    print("\nF&O LAST ROW EXTRACTION COMPLETED")
    print(f" Saved → {OUT_FILE}")
    print(f" F&O symbols written: {len(out_df)}")

else:
    print("\n No valid F&O equity data found")