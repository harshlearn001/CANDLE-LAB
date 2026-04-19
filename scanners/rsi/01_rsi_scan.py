#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | RSI OVERSOLD ENGINE (PRO)

✔ RSI < 25 (deep oversold)
✔ Data-driven date system (FIXED)
✔ Strength classification
✔ Clean terminal UI
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =====================================================
# HEADER UI
# =====================================================
print("╭──────────────────────────────╮")
print("│ RSI OVERSOLD SCANNER        │")
print("│ Mean Reversion Engine       │")
print("╰──────────────────────────────╯\n")

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\rsi")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
print(f"Loaded Symbols: {len(symbols)}")

# =====================================================
# RSI FUNCTION
# =====================================================
def calculate_rsi(df, period=14):

    delta = df['close'].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df

# =====================================================
# MAIN LOOP
# =====================================================
results = []
checked = 0
all_dates = []   # ✅ collect data dates

for symbol in symbols:

    file_path = EQUITY_DIR / f"{symbol}.csv"

    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)

        df.columns = [c.strip().lower() for c in df.columns]

        if not {'date','close'}.issubset(df.columns):
            continue

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']).sort_values("date")

        if len(df) < 50:
            continue

        # ✅ collect latest date
        if not df.empty:
            all_dates.append(df["date"].max())

        checked += 1

        df = calculate_rsi(df)

        latest = df.iloc[-1]
        rsi = latest['rsi']

        # =====================================================
        # SIGNAL
        # =====================================================
        if rsi < 25:

            if rsi < 15:
                strength = "EXTREME"
            elif rsi < 20:
                strength = "STRONG"
            else:
                strength = "NORMAL"

            results.append({
                "Symbol": symbol,
                "Date": latest['date'].strftime("%Y-%m-%d"),
                "Close": latest['close'],
                "RSI": round(rsi, 2),
                "Strength": strength
            })

            print(f" {symbol:12} → RSI {rsi:.2f}")

    except Exception as e:
        print(f" ERROR → {symbol} | {e}")

# =====================================================
# FINAL DATE (FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_rsi_below25_{final_date}.csv"

print(f"\n📅 Data Date Used: {final_date}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(results)

print("\n" + "─"*110)
print("📊 RSI SUMMARY")
print("─"*110)
print(f"📊 Total Checked: {checked}")
print(f"🔥 Signals Found: {len(df_out)}")

if not df_out.empty:

    df_out = df_out.sort_values("RSI")

    print("\n🟢 RSI < 25 (OVERSOLD)")
    print(df_out.head(10))

    df_out.to_csv(OUT_FILE, index=False)

    print(f"\n✔ Saved → {OUT_FILE}")

    # ACTION LIST
    print("─"*110)
    print("🎯 ACTION LIST\n")

    print("🟢 Mean Reversion Buy Watchlist")
    for s in df_out.head(5)["Symbol"]:
        print(f"  → {s}")

    # MARKET INSIGHT
    print("─"*110)
    print("🧠 TRADING INSIGHT")

    if len(df_out) > 15:
        print("🔥 Market deeply oversold")
        print("👉 Bounce / reversal likely")
    elif len(df_out) > 5:
        print("⚠ Selective oversold stocks")
        print("👉 Watch for reversal setups")
    else:
        print("🚫 No strong oversold condition")

else:
    print("\n❌ No RSI < 25 stocks found")

print("─"*110)