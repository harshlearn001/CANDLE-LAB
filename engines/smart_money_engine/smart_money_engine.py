#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMART MONEY ENGINE (ULTIMATE VERSION)

✔ Multi-day OI + Price analysis
✔ Expiry-safe (SYMBOL + EXP_DATE)
✔ Filters low OI noise
✔ Clips extreme values (no spikes)
✔ Weighted scoring system
✔ Relative ranking (RANK_SCORE)
✔ Outputs only actionable trades

Author: Harshal System 🚀
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
INPUT_DIR = Path(r"H:\MarketForge\data\processed\futures_daily\STOCKS")
OUTPUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\smart_money")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD LAST N DAYS
# =========================================================
def load_last_n_days(folder, n=3):
    files = sorted(folder.glob("futstk*.csv"))

    if len(files) < 2:
        raise ValueError("Need at least 2 days data")

    selected_files = files[-n:]

    df_list = []
    for f in selected_files:
        temp = pd.read_csv(f)
        temp['SOURCE_FILE'] = f.name
        df_list.append(temp)

    return pd.concat(df_list, ignore_index=True)

# =========================================================
# CLASSIFICATION
# =========================================================
def classify_smart_money(row):
    if row['PRICE_CHANGE'] > 0 and row['OI_CHANGE'] > 0:
        return 'LONG_BUILDUP'
    elif row['PRICE_CHANGE'] < 0 and row['OI_CHANGE'] > 0:
        return 'SHORT_BUILDUP'
    elif row['PRICE_CHANGE'] > 0 and row['OI_CHANGE'] < 0:
        return 'SHORT_COVERING'
    elif row['PRICE_CHANGE'] < 0 and row['OI_CHANGE'] < 0:
        return 'LONG_UNWINDING'
    else:
        return 'NEUTRAL'

# =========================================================
# MAIN ENGINE
# =========================================================
def process_smart_money():

    print("\n📊 Loading multi-day data...")
    df = load_last_n_days(INPUT_DIR, n=3)

    # Normalize
    df.columns = df.columns.str.upper()

    price_col = 'CLOSE_PRICE'
    oi_col = 'OPEN_INT'

    required_cols = ['SYMBOL', 'EXP_DATE', price_col, oi_col]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Sort properly
    df = df.sort_values(by=['SYMBOL', 'EXP_DATE', 'SOURCE_FILE']).copy()

    # =====================================================
    # CALCULATE CHANGES
    # =====================================================
    df['PRICE_CHANGE'] = df.groupby(['SYMBOL', 'EXP_DATE'])[price_col].diff()
    df['OI_CHANGE'] = df.groupby(['SYMBOL', 'EXP_DATE'])[oi_col].diff()

    # =====================================================
    # CLASSIFY
    # =====================================================
    df['SMART_SIGNAL'] = df.apply(classify_smart_money, axis=1)

    # =====================================================
    # STRENGTH CALCULATION
    # =====================================================
    df['OI_STRENGTH'] = abs(df['OI_CHANGE']) / df.groupby(['SYMBOL', 'EXP_DATE'])[oi_col].shift(1)
    df['PRICE_STRENGTH'] = abs(df['PRICE_CHANGE']) / df.groupby(['SYMBOL', 'EXP_DATE'])[price_col].shift(1)

    # =====================================================
    # FILTER LOW OI (REMOVE NOISE)
    # =====================================================
    df = df[df[oi_col] > 10000]

    # =====================================================
    # CLIP EXTREME VALUES
    # =====================================================
    df['OI_STRENGTH'] = df['OI_STRENGTH'].clip(lower=0, upper=1)
    df['PRICE_STRENGTH'] = df['PRICE_STRENGTH'].clip(lower=0, upper=0.2)

    # =====================================================
    # FINAL WEIGHTED SCORE
    # =====================================================
    df['SMART_SCORE'] = (
        (df['OI_STRENGTH'].fillna(0) * 0.7) +
        (df['PRICE_STRENGTH'].fillna(0) * 0.3)
    )

    # =====================================================
    # GET LATEST DATA PER SYMBOL
    # =====================================================
    latest_df = (
        df.sort_values(by=['EXP_DATE', 'SOURCE_FILE'])
          .groupby('SYMBOL')
          .tail(1)
          .copy()
    )

    # =====================================================
    # KEEP ONLY ACTIONABLE SIGNALS
    # =====================================================
    actionable = ['SHORT_COVERING', 'LONG_BUILDUP']
    latest_df = latest_df[latest_df['SMART_SIGNAL'].isin(actionable)]

    latest_df = latest_df[latest_df['SMART_SCORE'] > 0]

    # =====================================================
    # 🔥 RELATIVE RANKING (VERY IMPORTANT)
    # =====================================================
    latest_df['RANK_SCORE'] = latest_df['SMART_SCORE'].rank(pct=True)

    # Sort by rank
    latest_df = latest_df.sort_values(by='RANK_SCORE', ascending=False)

    # =====================================================
    # OUTPUT
    # =====================================================
    output_df = latest_df[['SYMBOL', price_col, 'SMART_SIGNAL', 'SMART_SCORE', 'RANK_SCORE']]
    output_df = output_df.rename(columns={price_col: 'PRICE'})

    return output_df

# =========================================================
# SAVE OUTPUT
# =========================================================
def save_output(df):
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"smart_money_{today}.csv"

    df.to_csv(output_file, index=False)
    print(f"\n✔ Saved → {output_file}")

# =========================================================
# MAIN
# =========================================================
def main():
    print("🔥 SMART MONEY ENGINE (ULTIMATE) STARTED 🔥")

    result_df = process_smart_money()

    print("\n📊 TOP SMART MONEY SIGNALS")
    print(result_df.head(20))

    save_output(result_df)

    print("\n🚀 SMART MONEY ENGINE COMPLETED")

# =========================================================
if __name__ == "__main__":
    main()