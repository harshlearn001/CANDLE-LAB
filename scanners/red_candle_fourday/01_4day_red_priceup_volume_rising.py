#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | STEP-5 (PRO)

✔ 4 RED candles
✔ Rising volume
✔ Momentum breakdown scanner
✔ Data-driven date system (FIXED)
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =====================================================
# HEADER UI
# =====================================================
print("╭──────────────────────────────╮")
print("│ 4-DAY RED + RISING VOLUME   │")
print("│ Breakdown Momentum Engine   │")
print("╰──────────────────────────────╯\n")

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\volume")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
if not FNO_FILE.exists():
    print(f"❌ Missing file: {FNO_FILE}")
    exit()

fno_df = pd.read_csv(FNO_FILE)

fno_symbols = set(
    fno_df["SYMBOL"]
    .astype(str)
    .str.strip()
    .str.upper()
)

print(f"Loaded Symbols: {len(fno_symbols)}")

# =====================================================
# PROCESS
# =====================================================
results = []
checked = 0
all_dates = []   # ✅ collect data dates

for symbol in sorted(fno_symbols):

    file_path = EQUITY_DIR / f"{symbol}.csv"

    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)

        if df.empty:
            continue

        df.columns = df.columns.str.strip().str.upper()

        required = {"DATE", "OPEN", "CLOSE", "TOTTRDQTY"}
        if not required.issubset(df.columns):
            continue

        # DATE PARSE
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 4:
            continue

        # ✅ collect latest date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        last4 = df.tail(4).copy()
        checked += 1

        # ============================
        # 4 RED CANDLES
        # ============================
        if not (last4["CLOSE"] < last4["OPEN"]).all():
            continue

        # ============================
        # RISING VOLUME
        # ============================
        vols = last4["TOTTRDQTY"].values

        if not (vols[0] < vols[1] < vols[2] < vols[3]):
            continue

        # ============================
        # STRENGTH CALCULATION
        # ============================
        last4["BODY"] = last4["OPEN"] - last4["CLOSE"]

        total_body = last4["BODY"].sum()
        vol_ratio = vols[3] / vols[:3].mean()

        if vol_ratio > 1.8:
            strength = "STRONG"
        elif vol_ratio > 1.3:
            strength = "NORMAL"
        else:
            strength = "WEAK"

        results.append({
            "Symbol": symbol,
            "To": last4.iloc[-1]["DATE"].strftime("%Y-%m-%d"),
            "Close": last4.iloc[-1]["CLOSE"],
            "VolRatio": round(vol_ratio, 2),
            "Momentum": round(total_body, 2),
            "Strength": strength
        })

        print(f" {symbol:12} → BREAKDOWN")

    except Exception as e:
        print(f" ERROR → {symbol} | {e}")

# =====================================================
# FINAL DATE (FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_4day_red_volume_rising_{final_date}.csv"

print(f"\n📅 Data Date Used: {final_date}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(results)

print("\n" + "─"*110)
print("📊 BREAKDOWN SUMMARY")
print("─"*110)
print(f"📊 Total Checked: {checked}")
print(f"🔥 Signals Found: {len(df_out)}")

if not df_out.empty:

    df_out = df_out.sort_values("Momentum", ascending=False)

    print("\n🔴 4-DAY RED + VOLUME")
    print(df_out.head(10))

    df_out.to_csv(OUT_FILE, index=False)

    print(f"\n✔ Saved → {OUT_FILE}")

    # ACTION LIST
    print("─"*110)
    print("🎯 ACTION LIST\n")

    print("🔴 Breakdown Candidates")
    for s in df_out.head(5)["Symbol"]:
        print(f"  → {s}")

    # INSIGHT
    print("─"*110)
    print("🧠 TRADING INSIGHT")

    if len(df_out) > 10:
        print("💀 Strong selling pressure in market")
        print("👉 Favor SHORT setups")
    elif len(df_out) > 0:
        print("⚠ Selective breakdowns")
        print("👉 Stock-specific shorts only")
    else:
        print("🚫 No selling pressure")
        print("👉 Avoid shorts")

else:
    print("\n❌ No Breakdown Setup Found")