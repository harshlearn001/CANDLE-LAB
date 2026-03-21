#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================
# PATH SETTINGS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\hammer")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_hammer_confirmation_{today}.csv"

# =====================================================
# LOAD F&O SYMBOLS
# =====================================================
fno_symbols = pd.read_csv(FNO_FILE)
fno_list = fno_symbols.iloc[:, 0].astype(str).str.strip().tolist()

print(f" Loaded {len(fno_list)} F&O symbols")

# =====================================================
# HAMMER DETECTION
# =====================================================
def detect_hammer(df):

    df = df.copy()

    df['range'] = df['High'] - df['Low']
    df = df[df['range'] > 0]

    df['body'] = abs(df['Close'] - df['Open'])
    df['upper_shadow'] = df['High'] - df[['Open','Close']].max(axis=1)
    df['lower_shadow'] = df[['Open','Close']].min(axis=1) - df['Low']

    df['body_pct'] = df['body'] / df['range']
    df['lower_shadow_pct'] = df['lower_shadow'] / df['range']
    df['upper_shadow_pct'] = df['upper_shadow'] / df['range']

    structure = (
        (df['body_pct'] <= 0.30) &
        (df['lower_shadow_pct'] >= 0.60) &
        (df['upper_shadow_pct'] <= 0.10)
    )

    df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
    trend = df['Close'] < df['EMA5']

    df['Hammer'] = structure & trend

    return df

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

        df = detect_hammer(df)

        if len(df) < 3:
            continue

        # -----------------------------
        # Hammer candle (previous)
        # -----------------------------
        hammer_candle = df.iloc[-2]

        # -----------------------------
        # Confirmation candle (latest)
        # -----------------------------
        confirm_candle = df.iloc[-1]

        if hammer_candle['Hammer']:

            # Confirmation conditions
            confirm_breakout = confirm_candle['Close'] > hammer_candle['High']
            bullish = confirm_candle['Close'] > confirm_candle['Open']

            if confirm_breakout and bullish:

                signals.append({
                    "Symbol": symbol,
                    "Hammer_Date": hammer_candle['Date'],
                    "Confirm_Date": confirm_candle['Date'],
                    "Hammer_Low": hammer_candle['Low'],
                    "Hammer_High": hammer_candle['High'],
                    "Confirm_Close": confirm_candle['Close'],
                    "Strength": round(confirm_candle['Close'] - hammer_candle['High'], 2)
                })

                print(f" HAMMER + CONFIRMATION → {symbol}")

    except Exception as e:
        print(f" Error in {symbol}: {e}")

# =====================================================
# SAVE OUTPUT
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:
    signals_df.to_csv(OUT_FILE, index=False)

    print("\n HAMMER CONFIRMATION SCAN COMPLETED")
    print(f" Signals found: {len(signals_df)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n No Hammer + Confirmation signals found.")