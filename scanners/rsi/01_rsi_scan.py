#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
from datetime import datetime

# ==============================
# PATHS
# ==============================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\rsi")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 👉 timestamp (avoid overwrite)
now = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_rsi_below30_{now}.csv"

# ==============================
# LOAD SYMBOLS
# ==============================
fno_symbols = pd.read_csv(FNO_FILE)
fno_list = fno_symbols.iloc[:, 0].astype(str).str.strip().tolist()

print(f" Loaded {len(fno_list)} F&O symbols")

# ==============================
# RSI FUNCTION
# ==============================
def calculate_rsi(df, period=14):

    delta = df['close'].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df

# ==============================
# MAIN LOOP
# ==============================
results = []

for symbol in fno_list:

    file_path = EQUITY_DIR / f"{symbol}.csv"

    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)

        # clean columns
        df.columns = [c.strip().lower() for c in df.columns]

        if not {'date','close'}.issubset(df.columns):
            continue

        # clean data
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']).sort_values("date")

        if len(df) < 50:
            continue

        # calculate RSI
        df = calculate_rsi(df)

        latest = df.iloc[-1]

        # ==============================
        # CONDITION
        # ==============================
        if latest['rsi'] < 25:

            results.append({
                "Symbol": symbol,
                "Date": latest['date'],
                "Close": latest['close'],
                "RSI": round(latest['rsi'], 2)
            })

            print(f" RSI {latest['rsi']:.2f} → {symbol}")

    except Exception as e:
        print(f" Error in {symbol}: {e}")

# ==============================
# SAVE (ALWAYS SAVE)
# ==============================
df_out = pd.DataFrame(results)

print("\n==============================")
print(f" Total stocks found: {len(df_out)}")
print(f" Saving to: {OUT_FILE}")

# ✅ ALWAYS SAVE FILE
df_out.to_csv(OUT_FILE, index=False)

print(" File saved successfully")

# ==============================
# OPTIONAL MESSAGE
# ==============================
if df_out.empty:
    print("⚠️ No RSI < 30 stocks today")
else:
    print(" RSI BELOW 30 SCAN COMPLETED")