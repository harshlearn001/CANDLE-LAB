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

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\rsi")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_rsi_signals_{today}.csv"

# =====================================================
# LOAD F&O SYMBOLS
# =====================================================
fno_symbols = pd.read_csv(FNO_FILE)
fno_list = fno_symbols.iloc[:, 0].astype(str).str.strip().tolist()

print(f" Loaded {len(fno_list)} F&O symbols")

# =====================================================
# RSI CALCULATION
# =====================================================
def calculate_rsi(df, period=14):

    df = df.copy()

    delta = df['Close'].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain = pd.Series(gain).rolling(period).mean()
    loss = pd.Series(loss).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    df['RSI'] = rsi

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

        df = calculate_rsi(df)

        if len(df) < 20:
            continue

        latest = df.iloc[-1]

        # =====================================================
        # RSI CONDITIONS
        # =====================================================
        if latest['RSI'] < 30:
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Close": latest['Close'],
                "RSI": round(latest['RSI'], 2),
                "Signal": "OVERSOLD (BUY)"
            })

            print(f" RSI < 30 → {symbol}")

        elif latest['RSI'] > 70:
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Close": latest['Close'],
                "RSI": round(latest['RSI'], 2),
                "Signal": "OVERBOUGHT (SELL)"
            })

            print(f" RSI > 70 → {symbol}")

    except Exception as e:
        print(f" Error in {symbol}: {e}")

# =====================================================
# SAVE OUTPUT
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:
    signals_df.to_csv(OUT_FILE, index=False)

    print("\n RSI SCAN COMPLETED")
    print(f" Signals found: {len(signals_df)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n No RSI signals found.")