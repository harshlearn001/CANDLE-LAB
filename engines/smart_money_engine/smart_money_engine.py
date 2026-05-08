#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
from datetime import datetime

INPUT_DIR = Path(r"H:\MarketForge\data\master\Futures_master\FUTSTK")
OUTPUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\smart_money")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
def load_recent_data(days=2):
    files = list(INPUT_DIR.glob("*.csv"))
    all_data = []

    for file in files:
        try:
            df = pd.read_csv(file)
            df.columns = df.columns.str.upper()

            if 'TRADE_DATE' not in df.columns:
                continue

            df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'], format='%Y%m%d')

            df = df.sort_values('TRADE_DATE')
            df = df.groupby(['SYMBOL', 'EXP_DATE']).tail(days)

            all_data.append(df)

        except Exception as e:
            print(f"[WARNING] Skipped {file.name}: {e}")

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)

# =========================================================
def classify(row):
    if row['PRICE_CHANGE'] > 0 and row['OI_CHANGE'] > 0:
        return 'LONG_BUILDUP'
    elif row['PRICE_CHANGE'] < 0 and row['OI_CHANGE'] > 0:
        return 'SHORT_BUILDUP'
    elif row['PRICE_CHANGE'] > 0 and row['OI_CHANGE'] < 0:
        return 'SHORT_COVERING'
    elif row['PRICE_CHANGE'] < 0 and row['OI_CHANGE'] < 0:
        return 'LONG_UNWINDING'
    return 'NEUTRAL'

# =========================================================
def process():

    print("[INFO] Loading data...")
    df = load_recent_data()

    if df.empty:
        print("[WARNING] No data")
        return pd.DataFrame()

    df = df.sort_values(by=['SYMBOL','EXP_DATE','TRADE_DATE'])

    df['PRICE_CHANGE'] = df.groupby(['SYMBOL','EXP_DATE'])['CLOSE_PRICE'].diff()
    df['OI_CHANGE'] = df.groupby(['SYMBOL','EXP_DATE'])['OPEN_INT'].diff()

    df['SIGNAL'] = df.apply(classify, axis=1)

    # Strength
    df['OI_STRENGTH'] = abs(df['OI_CHANGE']) / df['OPEN_INT'].shift(1)
    df['PRICE_STRENGTH'] = abs(df['PRICE_CHANGE']) / df['CLOSE_PRICE'].shift(1)

    df = df[df['OPEN_INT'] > 10000]

    df['SCORE'] = (
        df['OI_STRENGTH'].fillna(0)*0.7 +
        df['PRICE_STRENGTH'].fillna(0)*0.3
    )

    latest = df.groupby('SYMBOL').tail(1)

    # Keep all non-neutral
    latest = latest[latest['SIGNAL'] != 'NEUTRAL']

    # Direction mapping
    def map_dir(x):
        if x in ['LONG_BUILDUP','SHORT_COVERING']:
            return 1
        elif x in ['SHORT_BUILDUP','LONG_UNWINDING']:
            return -1
        return 0

    latest['DIR'] = latest['SIGNAL'].apply(map_dir)

    # Rank
    latest['RANK'] = latest['SCORE'].rank(pct=True)

    # FINAL SMART MONEY SCORE
    latest['SM_SCORE'] = latest['RANK'] * latest['DIR']

    return latest[['SYMBOL','SM_SCORE','SIGNAL']]

# =========================================================
def save(df):
    if df.empty:
        return

    today = datetime.now().strftime("%Y-%m-%d")
    file = OUTPUT_DIR / f"smart_money_{today}.csv"

    df.to_csv(file, index=False)
    print(f"[OK] Saved → {file}")

# =========================================================
if __name__ == "__main__":
    print("[START] SMART MONEY ENGINE")
    df = process()
    print(df.head(10))
    save(df)
    print("[DONE]")