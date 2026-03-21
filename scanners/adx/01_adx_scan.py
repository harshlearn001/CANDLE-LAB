#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔥 ADX SCANNER RUNNING 🔥")

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\adx")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_adx_signals_{today}.csv"

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
print(f" Loaded {len(symbols)} symbols")

signals = []

# =====================================================
# ADX CALCULATION
# =====================================================
def calculate_adx(df, period=14):

    df = df.copy()

    df['TR'] = np.maximum.reduce([
        df['High'] - df['Low'],
        abs(df['High'] - df['Close'].shift()),
        abs(df['Low'] - df['Close'].shift())
    ])

    df['+DM'] = np.where(
        (df['High'] - df['High'].shift()) > (df['Low'].shift() - df['Low']),
        np.maximum(df['High'] - df['High'].shift(), 0),
        0
    )

    df['-DM'] = np.where(
        (df['Low'].shift() - df['Low']) > (df['High'] - df['High'].shift()),
        np.maximum(df['Low'].shift() - df['Low'], 0),
        0
    )

    TR_n = df['TR'].rolling(period).sum()
    plus_DM_n = df['+DM'].rolling(period).sum()
    minus_DM_n = df['-DM'].rolling(period).sum()

    df['+DI'] = 100 * (plus_DM_n / TR_n)
    df['-DI'] = 100 * (minus_DM_n / TR_n)

    df['DX'] = 100 * abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])
    df['ADX'] = df['DX'].rolling(period).mean()

    return df

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

        if len(df) < 50:
            continue

        df = calculate_adx(df)

        latest = df.iloc[-1]

        adx = latest['ADX']
        plus_di = latest['+DI']
        minus_di = latest['-DI']

        # =====================================================
        # SIGNAL LOGIC
        # =====================================================
        signal = None

        if adx < 20:
            signal = "WEAK TREND (REVERSAL ZONE)"

        elif adx > 25:
            if plus_di > minus_di:
                signal = "STRONG UPTREND"
            elif minus_di > plus_di:
                signal = "STRONG DOWNTREND"

        if signal:
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'],
                "Close": latest['Close'],
                "ADX": round(adx, 2),
                "+DI": round(plus_di, 2),
                "-DI": round(minus_di, 2),
                "Signal": signal
            })

            print(f" {symbol} → {signal}")

    except Exception as e:
        print(f" Error in {symbol}: {e}")

# =====================================================
# SAVE OUTPUT
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:
    signals_df.to_csv(OUT_FILE, index=False)

    print("\n🚀 ADX SCAN COMPLETED")
    print(f" Signals found: {len(signals_df)}")
    print(f" Saved → {OUT_FILE}")

else:
    print("\n❌ No ADX signals found.")