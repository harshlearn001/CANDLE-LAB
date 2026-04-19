#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
from datetime import datetime

# =====================================================
# HEADER UI
# =====================================================
print("╭──────────────────────────────╮")
print("│ PCR ENGINE                  │")
print("│ Options Sentiment Engine    │")
print("╰──────────────────────────────╯\n")

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(r"H:\MarketForge\data\master\option_master")

INDEX_DIR = BASE_DIR / "INDICES"
STOCK_DIR = BASE_DIR / "STOCKS"

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\options_pcr")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD FILES
# =====================================================
all_files = list(INDEX_DIR.glob("*")) + list(STOCK_DIR.glob("*"))
print(f"Loaded Files: {len(all_files)}")

# =====================================================
# PCR COLLECTION
# =====================================================
data = {}
all_dates = []   # ✅ collect data dates

for file in all_files:

    if file.suffix not in [".csv", ".parquet"]:
        continue

    try:
        if file.suffix == ".parquet":
            df = pd.read_parquet(file)
        else:
            df = pd.read_csv(file)

        if df.empty:
            continue

        # Standardize columns
        df.columns = df.columns.str.upper().str.strip()

        # =====================================================
        # DATE EXTRACTION (IMPORTANT FIX)
        # =====================================================
        if "DATE" in df.columns:
            df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
            if df["DATE"].notna().any():
                all_dates.append(df["DATE"].max())

        # Flexible OI detection
        if "OPEN_INT" not in df.columns:
            if "OPENINTEREST" in df.columns:
                df["OPEN_INT"] = df["OPENINTEREST"]
            elif "OI" in df.columns:
                df["OPEN_INT"] = df["OI"]
            else:
                continue

        required = {"SYMBOL", "OPT_TYPE", "OPEN_INT"}
        if not required.issubset(df.columns):
            continue

        symbol = df["SYMBOL"].iloc[0]

        ce_oi = df[df["OPT_TYPE"] == "CE"]["OPEN_INT"].sum()
        pe_oi = df[df["OPT_TYPE"] == "PE"]["OPEN_INT"].sum()

        if ce_oi == 0:
            continue

        # =====================================================
        # AGGREGATE PER SYMBOL
        # =====================================================
        if symbol not in data:
            data[symbol] = {"CE": 0, "PE": 0}

        data[symbol]["CE"] += ce_oi
        data[symbol]["PE"] += pe_oi

    except:
        continue

# =====================================================
# FINAL DATE (FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"pcr_{final_date}.csv"

print(f"\n📅 Data Date Used: {final_date}")

# =====================================================
# BUILD FINAL DATAFRAME
# =====================================================
rows = []

for sym, vals in data.items():

    ce = vals["CE"]
    pe = vals["PE"]

    if ce == 0:
        continue

    pcr = pe / ce

    # =====================================================
    # SIGNAL LOGIC
    # =====================================================
    if pcr > 1.3:
        signal = "STRONG_BULLISH"
    elif pcr > 1.1:
        signal = "BULLISH"
    elif pcr < 0.7:
        signal = "STRONG_BEARISH"
    elif pcr < 0.9:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"

    rows.append({
        "Symbol": sym,
        "CE_OI": int(ce),
        "PE_OI": int(pe),
        "PCR": round(pcr, 2),
        "Signal": signal
    })

df = pd.DataFrame(rows)

# =====================================================
# CHECK EMPTY
# =====================================================
if df.empty:
    print("\n❌ No PCR data found")
    exit()

# =====================================================
# SORT
# =====================================================
df = df.sort_values("PCR", ascending=False)

# =====================================================
# SUMMARY
# =====================================================
bull = len(df[df["Signal"].str.contains("BULLISH")])
bear = len(df[df["Signal"].str.contains("BEARISH")])
neutral = len(df[df["Signal"] == "NEUTRAL"])

print("─"*110)
print("📊 PCR SUMMARY")
print("─"*110)
print(f"🟢 Bullish: {bull}")
print(f"🔴 Bearish: {bear}")
print(f"⚪ Neutral: {neutral}")
print(f"📊 Total Symbols: {len(df)}")

# =====================================================
# MARKET STRUCTURE
# =====================================================
bull_pct = round(bull / len(df) * 100, 1)
bear_pct = round(bear / len(df) * 100, 1)
neutral_pct = round(neutral / len(df) * 100, 1)

print("\n📊 Market Structure:")
print(f"Bullish: {bull_pct}%")
print(f"Bearish: {bear_pct}%")
print(f"Neutral: {neutral_pct}%")

# =====================================================
# TOP EXTREMES
# =====================================================
print("\n🟢 HIGH PCR (OVER BULLISH)")
print(df.head(10)[["Symbol","PCR","Signal"]])

print("\n🔴 LOW PCR (OVER BEARISH)")
print(df.tail(10)[["Symbol","PCR","Signal"]])

# =====================================================
# SAVE
# =====================================================
df.to_csv(OUT_FILE, index=False)
print(f"\n✔ Saved → {OUT_FILE}")

# =====================================================
# MARKET INSIGHT
# =====================================================
print("─"*110)
print("🧠 MARKET SENTIMENT")

if bull_pct > 60:
    print("💥 EXTREME BULLISH (Crowded longs → Risk of fall)")
elif bear_pct > 60:
    print("💀 EXTREME BEARISH (Crowded shorts → Bounce likely)")
else:
    print("⚖ BALANCED MARKET")

# =====================================================
# ACTION LIST
# =====================================================
print("─"*110)
print("🎯 ACTION LIST\n")

print("🟢 Watch for SHORT (Over Bullish)")
for s in df.head(5)["Symbol"]:
    print(f"  → {s}")

print("\n🔴 Watch for LONG (Over Bearish)")
for s in df.tail(5)["Symbol"]:
    print(f"  → {s}")

print("\n💡 Strategy:")
print("PCR LOW + Bullish Pattern → BUY")
print("PCR HIGH + Bearish Pattern → SELL")