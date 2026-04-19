#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | SHOOTING STAR (PRO)

✔ Data-driven date (FIXED)
✔ Strong uptrend logic
✔ Candle quality + strength ranking
✔ Clean terminal UI
"""

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================
# HEADER UI
# =====================================================
print("╭──────────────────────────────╮")
print("│ SHOOTING STAR SCANNER       │")
print("│ Top Reversal Exhaustion     │")
print("╰──────────────────────────────╯\n")

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\shooting_star")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.strip().str.upper().tolist()
print(f"Loaded Symbols: {len(symbols)}")

results = []
checked = 0
all_dates = []   # ✅ collect data dates

# =====================================================
# PROCESS
# =====================================================
for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.upper()

        if not {"DATE","OPEN","HIGH","LOW","CLOSE"}.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 20:
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        # =====================================
        # TREND FILTER
        # =====================================
        df["EMA20"] = df["CLOSE"].ewm(span=20).mean()

        if not (
            df.iloc[-1]["CLOSE"] > df.iloc[-1]["EMA20"] and
            df.iloc[-3]["CLOSE"] < df.iloc[-1]["CLOSE"]
        ):
            continue

        # =====================================
        # CURRENT CANDLE
        # =====================================
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

        # =====================================
        # QUALITY FILTER
        # =====================================
        recent_ranges = df.iloc[-10:-1]["HIGH"] - df.iloc[-10:-1]["LOW"]

        if rng < np.median(recent_ranges):
            continue

        # =====================================
        # SHOOTING STAR LOGIC
        # =====================================
        if (
            body_pct <= 0.35 and
            upper_pct >= 0.50 and
            lower_pct <= 0.15
        ):

            if upper_pct > 0.7:
                strength = "STRONG"
            elif upper_pct > 0.6:
                strength = "NORMAL"
            else:
                strength = "WEAK"

            results.append({
                "Symbol": symbol,
                "Date": c["DATE"].strftime("%Y-%m-%d"),
                "Close": cl,
                "UpperWick%": round(upper_pct*100,2),
                "Body%": round(body_pct*100,2),
                "Strength": strength
            })

            print(f" 🔴 Shooting Star → {symbol}")

    except Exception as e:
        print(f" ERROR → {symbol} | {e}")

# =====================================================
# FINAL DATE (FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_shooting_star_{final_date}.csv"

print(f"\n📅 Data Date Used: {final_date}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(results)

print("\n" + "─"*110)
print("📊 SHOOTING STAR SUMMARY")
print("─"*110)
print(f"📊 Total Checked: {checked}")
print(f"🔥 Signals Found: {len(df_out)}")

if not df_out.empty:

    df_out = df_out.sort_values("UpperWick%", ascending=False)

    print("\n🔴 TOP EXHAUSTION SETUPS")
    print(df_out.head(10))

    df_out.to_csv(OUT_FILE, index=False)
    print(f"\n✔ Saved → {OUT_FILE}")

    print("─"*110)
    print("🎯 ACTION LIST\n")

    print("🔴 Potential Short Candidates")
    for s in df_out.head(5)["Symbol"]:
        print(f"  → {s}")

else:
    print("\n❌ No Shooting Star found")

print("─"*110)