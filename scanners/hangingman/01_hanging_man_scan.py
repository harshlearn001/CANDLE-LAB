#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔥 HANGING MAN FINAL (CHART ACCURATE) 🔥")

import pandas as pd
from pathlib import Path
from datetime import datetime

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\hangingman")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_hanging_man_{today}.csv"

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
print(f" Loaded {len(symbols)} symbols")

signals = []

# =====================================================
# SWING HIGH FUNCTION (CRITICAL)
# =====================================================
def is_near_swing_high(df, i, lookback=10):
    if i - lookback < 0:
        return False
    recent_high = df['High'].iloc[i-lookback:i].max()
    current_high = df['High'].iloc[i]
    return current_high >= 0.97 * recent_high

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

        if len(df) < 220:
            continue

        # =====================================================
        # INDICATORS
        # =====================================================
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()

        # =====================================================
        # SCAN LAST 5 CANDLES
        # =====================================================
        for i in range(-5, 0):

            row = df.iloc[i]

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
            # 1. STRUCTURE
            # =====================================================
            structure = (
                lower_wick >= 2 * body and
                upper_wick <= body
            )

            # =====================================================
            # 2. BODY AT TOP
            # =====================================================
            body_top = max(open_, close)
            body_position = body_top >= (high - candle_range * 0.4)

            # =====================================================
            # 3. TREND (EMA + SMA)
            # =====================================================
            trend = (
                close > df['EMA50'].iloc[i] and
                df['EMA50'].iloc[i] > df['SMA200'].iloc[i]
            )

            # =====================================================
            # 4. LOCATION (SWING HIGH)
            # =====================================================
            location = is_near_swing_high(df, i)

            # =====================================================
            # FINAL SIGNAL
            # =====================================================
            if structure and body_position and trend and location:

                signals.append({
                    "Symbol": symbol,
                    "Date": row['Date'],
                    "Close": close,
                    "EMA50": round(df['EMA50'].iloc[i], 2),
                    "SMA200": round(df['SMA200'].iloc[i], 2),
                    "Signal": "HANGING MAN (VALID)"
                })

                print(f" 🔻 VALID Hanging Man → {symbol}")
                break

    except Exception as e:
        print(f" Error in {symbol}: {e}")

# =====================================================
# SAVE
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:
    signals_df.to_csv(OUT_FILE, index=False)

    print("\n🚀 FINAL HANGING MAN SCAN COMPLETED")
    print(f" Signals found: {len(signals_df)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n❌ No valid hanging man (chart-accurate filter).")