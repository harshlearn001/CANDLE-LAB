#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CANDLE-LAB | RSI DIVERGENCE ENGINE (PRO)

✔ Data-driven date (FIXED)
✔ Correct RSI calculation
✔ EMA trend filter
✔ Swing-based divergence
✔ Clean output
"""

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================
# HEADER UI
# =====================================================
print("╭──────────────────────────────╮")
print("│ RSI DIVERGENCE SCANNER      │")
print("│ Smart Money Reversal Engine │")
print("╰──────────────────────────────╯\n")

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\rsi_divergence")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:,0].astype(str).str.strip().tolist()
print(f"Loaded Symbols: {len(symbols)}")

# =====================================================
# RSI
# =====================================================
def calculate_rsi(df, period=14):

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df

# =====================================================
# SWING DETECTION
# =====================================================
def find_swings(df, window=5):

    df['swing_high'] = df['High'][
        df['High'] == df['High'].rolling(window, center=True).max()
    ]

    df['swing_low'] = df['Low'][
        df['Low'] == df['Low'].rolling(window, center=True).min()
    ]

    return df

# =====================================================
# MAIN LOOP
# =====================================================
signals = []
checked = 0
all_dates = []   # ✅ collect data dates

for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)
        df.columns = [c.strip().capitalize() for c in df.columns]

        if not {'Date','Open','High','Low','Close'}.issubset(df.columns):
            continue

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        if len(df) < 60:
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["Date"].max())

        checked += 1

        df = calculate_rsi(df)
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df = find_swings(df)

        swing_lows = df.dropna(subset=['swing_low'])
        swing_highs = df.dropna(subset=['swing_high'])

        latest = df.iloc[-1]

        # =======================
        # BULLISH DIVERGENCE
        # =======================
        if len(swing_lows) >= 2:

            prev = swing_lows.iloc[-2]
            curr = swing_lows.iloc[-1]

            if (
                curr['Low'] < prev['Low'] and
                curr['RSI'] > prev['RSI'] and
                curr['RSI'] < 45 and
                curr['Close'] > df['EMA50'].iloc[-1]
            ):

                strength = round(curr['RSI'] - prev['RSI'], 2)

                signals.append({
                    "Symbol": symbol,
                    "Date": latest['Date'].strftime("%Y-%m-%d"),
                    "Close": latest['Close'],
                    "RSI": round(latest['RSI'],2),
                    "Type": "BULLISH",
                    "Strength": strength
                })

                print(f" 🟢 Bullish → {symbol}")

        # =======================
        # BEARISH DIVERGENCE
        # =======================
        if len(swing_highs) >= 2:

            prev = swing_highs.iloc[-2]
            curr = swing_highs.iloc[-1]

            if (
                curr['High'] > prev['High'] and
                curr['RSI'] < prev['RSI'] and
                curr['RSI'] > 55 and
                curr['Close'] < df['EMA50'].iloc[-1]
            ):

                strength = round(prev['RSI'] - curr['RSI'], 2)

                signals.append({
                    "Symbol": symbol,
                    "Date": latest['Date'].strftime("%Y-%m-%d"),
                    "Close": latest['Close'],
                    "RSI": round(latest['RSI'],2),
                    "Type": "BEARISH",
                    "Strength": strength
                })

                print(f" 🔴 Bearish → {symbol}")

    except Exception as e:
        print(f" ERROR → {symbol} | {e}")

# =====================================================
# FINAL DATE (FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_rsi_divergence_{final_date}.csv"

print(f"\n📅 Data Date Used: {final_date}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(signals)

print("\n" + "─"*110)
print("📊 DIVERGENCE SUMMARY")
print("─"*110)
print(f"📊 Total Checked: {checked}")
print(f"🔥 Signals Found: {len(df_out)}")

if not df_out.empty:

    df_out = df_out.sort_values("Strength", ascending=False)

    print("\n📊 TOP DIVERGENCE")
    print(df_out.head(10))

    df_out.to_csv(OUT_FILE, index=False)
    print(f"\n✔ Saved → {OUT_FILE}")

    print("─"*110)
    print("🎯 ACTION LIST\n")

    print("🟢 Bullish Reversal")
    for s in df_out[df_out["Type"]=="BULLISH"].head(5)["Symbol"]:
        print(f"  → {s}")

    print("\n🔴 Bearish Reversal")
    for s in df_out[df_out["Type"]=="BEARISH"].head(5)["Symbol"]:
        print(f"  → {s}")

else:
    print("\n❌ No divergence found")

print("─"*110)