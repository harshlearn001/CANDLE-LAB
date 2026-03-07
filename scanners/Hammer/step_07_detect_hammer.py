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

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_hammer_reference_{today}.csv"

# =====================================================
# CHECK CONFIG FILE
# =====================================================
if not FNO_FILE.exists():
    print(f" Missing file: {FNO_FILE}")
    exit()

# =====================================================
# LOAD F&O SYMBOL LIST
# =====================================================
fno_symbols = pd.read_csv(FNO_FILE)
fno_list = fno_symbols.iloc[:, 0].astype(str).str.strip().tolist()

print(f" Loaded {len(fno_list)} F&O symbols")

# =====================================================
# HAMMER DETECTION ENGINE
# =====================================================
def detect_hammer(df):

    df = df.copy()

    # -----------------------------
    # Basic Candle Structure
    # -----------------------------
    df['range'] = df['High'] - df['Low']
    df = df[df['range'] > 0]

    df['body'] = abs(df['Close'] - df['Open'])
    df['upper_shadow'] = df['High'] - df[['Open','Close']].max(axis=1)
    df['lower_shadow'] = df[['Open','Close']].min(axis=1) - df['Low']

    df['body_pct'] = df['body'] / df['range']
    df['lower_shadow_pct'] = df['lower_shadow'] / df['range']
    df['upper_shadow_pct'] = df['upper_shadow'] / df['range']

    structure_check = (
        (df['body_pct'] <= 0.30) &
        (df['lower_shadow_pct'] >= 0.60) &
        (df['upper_shadow_pct'] <= 0.10)
    )

    # -----------------------------
    # TREND CHECK (5 EMA)
    # -----------------------------
    df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
    trend_check = df['Close'] < df['EMA5']

    # -----------------------------
    # VOLUME CHECK
    # -----------------------------
    if 'Volume' in df.columns:
        df['vol_avg20'] = df['Volume'].rolling(20).mean()
        volume_check = df['Volume'] > 1.5 * df['vol_avg20']
    else:
        volume_check = False

    # -----------------------------
    # ATR CHECK
    # -----------------------------
    df['prev_close'] = df['Close'].shift(1)

    df['tr1'] = df['High'] - df['Low']
    df['tr2'] = abs(df['High'] - df['prev_close'])
    df['tr3'] = abs(df['Low'] - df['prev_close'])

    df['TR'] = df[['tr1','tr2','tr3']].max(axis=1)

    df['ATR14'] = df['TR'].rolling(14).mean()

    atr_check = df['range'] > (0.8 * df['ATR14'])

    # -----------------------------
    # FINAL HAMMER CONDITION
    # -----------------------------
    df['Hammer'] = structure_check & trend_check & (volume_check | atr_check)

    return df


# =====================================================
# MAIN SCAN LOOP
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

        # Parse date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        df = detect_hammer(df)

        if df.empty:
            continue

        latest = df.iloc[-1]

        if latest['Hammer']:

            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Open": latest['Open'],
                "High": latest['High'],
                "Low": latest['Low'],
                "Close": latest['Close'],
                "Volume": latest.get('Volume', None),
                "Range": latest['range'],
                "Body_pct": round(latest['body_pct'],3),
                "LowerShadow_pct": round(latest['lower_shadow_pct'],3)
            })

            print(f" HAMMER → {symbol}")

    except Exception as e:
        print(f" Error in {symbol}: {e}")


# =====================================================
# SAVE OUTPUT
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:

    signals_df.to_csv(OUT_FILE, index=False)

    print("\n HAMMER SCAN COMPLETED")
    print(f" Signals found: {len(signals_df)}")
    print(f" Saved  {OUT_FILE}")

else:
    print("\n No Hammer signals found today.")