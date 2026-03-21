#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔥 WEEKLY HANGING MAN SCANNER 🔥")

import pandas as pd
from pathlib import Path
from datetime import datetime

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\hangingman_weekly")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_hanging_man_weekly_{today}.csv"

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
print(f" Loaded {len(symbols)} symbols")

signals = []

# =====================================================
# SWING HIGH FUNCTION
# =====================================================
def is_near_swing_high(df, i, lookback=10):
    if i - lookback < 0:
        return False
    recent_high = df['High'].iloc[i-lookback:i].max()
    current_high = df['High'].iloc[i]
    return current_high >= 0.95 * recent_high

# =====================================================
# MAIN LOOP
# =====================================================
for symbol in symbols:

    file_path = EQUITY_DIR / f"{symbol}.csv"
    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)
        df.columns = [c.strip().capitalize() for c in df.columns]

        if not {'Date','Open','High','Low','Close'}.issubset(df.columns):
            continue

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        if len(df) < 250:
            continue

        # =====================================================
        # CONVERT TO WEEKLY
        # =====================================================
        df.set_index('Date', inplace=True)

        weekly = df.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last'
        }).dropna()

        if len(weekly) < 60:
            continue

        weekly.reset_index(inplace=True)

        # =====================================================
        # INDICATORS
        # =====================================================
        weekly['EMA20'] = weekly['Close'].ewm(span=20).mean()
        weekly['SMA50'] = weekly['Close'].rolling(window=50).mean()

        # =====================================================
        # SCAN LAST 3 WEEKS
        # =====================================================
        for i in range(-3, 0):

            row = weekly.iloc[i]

            open_ = row['Open']
            close = row['Close']
            high = row['High']
            low = row['Low']

            body = abs(close - open_)
            candle_range = high - low

            if candle_range == 0 or body == 0:
                continue

            upper_wick = high - max(open_, close)
            lower_wick = min(open_, close) - low

            # =====================================================
            # STRUCTURE
            # =====================================================
            structure = (
                lower_wick >= 2 * body and
                upper_wick <= 1.5 * body
            )

            # =====================================================
            # BODY POSITION
            # =====================================================
            body_top = max(open_, close)
            body_position = body_top >= (high - candle_range * 0.5)

            # =====================================================
            # TREND
            # =====================================================
            trend = (
                close > weekly['EMA20'].iloc[i] and
                weekly['EMA20'].iloc[i] > weekly['SMA50'].iloc[i]
            )

            # =====================================================
            # LOCATION
            # =====================================================
            location = is_near_swing_high(weekly, i)

            # =====================================================
            # FINAL SIGNAL
            # =====================================================
            if structure and body_position and trend and location:

                signals.append({
                    "Symbol": symbol,
                    "Date": row['Date'],
                    "Close": close,
                    "Signal": "WEEKLY HANGING MAN"
                })

                print(f" 🔻 Weekly Hanging Man → {symbol}")
                break

    except Exception as e:
        print(f" Error in {symbol}: {e}")

# =====================================================
# SAVE
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:
    signals_df.to_csv(OUT_FILE, index=False)

    print("\n🚀 WEEKLY HANGING MAN COMPLETED")
    print(f" Signals found: {len(signals_df)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n❌ No weekly hanging man found.")