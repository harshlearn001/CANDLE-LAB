#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
from datetime import datetime

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\harami")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_harami_{today}.csv"

# =====================================================
# LOAD SYMBOLS
# =====================================================
fno_list = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).tolist()

# =====================================================
# HARAMI LOGIC
# =====================================================
def detect_harami(df):

    df = df.copy()

    df['Prev_Open'] = df['Open'].shift(1)
    df['Prev_Close'] = df['Close'].shift(1)

    # Previous candle body
    prev_high = df[['Prev_Open','Prev_Close']].max(axis=1)
    prev_low  = df[['Prev_Open','Prev_Close']].min(axis=1)

    # Current candle body
    curr_high = df[['Open','Close']].max(axis=1)
    curr_low  = df[['Open','Close']].min(axis=1)

    # Inside body condition
    inside = (curr_high < prev_high) & (curr_low > prev_low)

    # Bullish Harami
    df['Bullish_Harami'] = (
        (df['Prev_Close'] < df['Prev_Open']) &  # previous red
        (df['Close'] > df['Open']) &            # current green
        inside
    )

    # Bearish Harami
    df['Bearish_Harami'] = (
        (df['Prev_Close'] > df['Prev_Open']) &  # previous green
        (df['Close'] < df['Open']) &            # current red
        inside
    )

    return df

# =====================================================
# MAIN
# =====================================================
signals = []

for symbol in fno_list:

    file_path = EQUITY_DIR / f"{symbol}.csv"
    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)
        df.columns = [c.strip().capitalize() for c in df.columns]

        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values("Date")

        df = detect_harami(df)

        latest = df.iloc[-1]

        if latest['Bullish_Harami']:
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Type": "Bullish Harami"
            })
            print(f" Bullish Harami → {symbol}")

        elif latest['Bearish_Harami']:
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Type": "Bearish Harami"
            })
            print(f" Bearish Harami → {symbol}")

    except Exception as e:
        print(f" Error {symbol}: {e}")

# SAVE
pd.DataFrame(signals).to_csv(OUT_FILE, index=False)
print(" Harami scan done")