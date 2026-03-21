#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔥 RSI DIVERGENCE BALANCED VERSION RUNNING 🔥")

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================
# PATH SETTINGS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\rsi_divergence")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_rsi_divergence_{today}.csv"

# =====================================================
# LOAD SYMBOLS
# =====================================================
fno_symbols = pd.read_csv(FNO_FILE)
fno_list = fno_symbols.iloc[:, 0].astype(str).str.strip().tolist()

print(f" Loaded {len(fno_list)} F&O symbols")

# =====================================================
# RSI
# =====================================================
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain = pd.Series(gain).rolling(period).mean()
    loss = pd.Series(loss).rolling(period).mean()

    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df

# =====================================================
# EMA
# =====================================================
def add_ema(df):
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    return df

# =====================================================
# SWINGS
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
# DIVERGENCE LOGIC (BALANCED)
# =====================================================
def detect_divergence(df):

    bullish = False
    bearish = False

    swing_lows = df.dropna(subset=['swing_low'])
    swing_highs = df.dropna(subset=['swing_high'])

    # ---------------- BULLISH ----------------
    if len(swing_lows) >= 2:
        prev = swing_lows.iloc[-2]
        curr = swing_lows.iloc[-1]

        is_recent = (len(df) - df.index.get_loc(curr.name)) <= 5

        if (
            is_recent and
            curr['Low'] < prev['Low'] and
            curr['RSI'] > prev['RSI'] and
            curr['RSI'] < 45 and
            curr['Close'] > df['EMA50'].iloc[-1]
        ):
            bullish = True

    # ---------------- BEARISH ----------------
    if len(swing_highs) >= 2:
        prev = swing_highs.iloc[-2]
        curr = swing_highs.iloc[-1]

        is_recent = (len(df) - df.index.get_loc(curr.name)) <= 5

        if (
            is_recent and
            curr['High'] > prev['High'] and
            curr['RSI'] < prev['RSI'] and
            curr['RSI'] > 55 and
            curr['Close'] < df['EMA50'].iloc[-1]
        ):
            bearish = True

    return bullish, bearish

# =====================================================
# MAIN LOOP
# =====================================================
signals = []

for symbol in fno_list:

    file_path = EQUITY_DIR / f"{symbol}.csv"

    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)
        df.columns = [c.strip().capitalize() for c in df.columns]

        required = {'Date','Open','High','Low','Close'}
        if not required.issubset(df.columns):
            continue

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        if len(df) < 60:
            continue

        df = calculate_rsi(df)
        df = add_ema(df)
        df = find_swings(df)

        bullish, bearish = detect_divergence(df)

        latest = df.iloc[-1]

        if bullish:
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Close": latest['Close'],
                "RSI": round(latest['RSI'], 2),
                "Signal": "BULLISH DIVERGENCE"
            })
            print(f" ✅ Bullish → {symbol}")

        elif bearish:
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Close": latest['Close'],
                "RSI": round(latest['RSI'], 2),
                "Signal": "BEARISH DIVERGENCE"
            })
            print(f" 🔻 Bearish → {symbol}")

    except Exception as e:
        print(f" Error in {symbol}: {e}")

# =====================================================
# SAVE OUTPUT
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:
    signals_df.to_csv(OUT_FILE, index=False)

    print("\n🚀 BALANCED DIVERGENCE SCAN COMPLETED")
    print(f" Signals found: {len(signals_df)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n❌ No divergence found (balanced filter).")