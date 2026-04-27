#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FILTER ENGINE (PRO VERSION)

✔ Tier 1 (Elite trades)
✔ Tier 2 (Strong trades)
✔ Avoids empty output
✔ Candle = confirmation (not filter)
✔ Clean ranking

Author: Harshal System 🚀
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =========================================================
# PATHS
# =========================================================
MASTER_PATH = Path(r"H:\CANDLE-LAB\analysis\equity\master")
INSIDE_BAR_PATH = Path(r"H:\CANDLE-LAB\analysis\equity\signals\inside_bar")
ENGULF_PATH = Path(r"H:\CANDLE-LAB\analysis\equity\signals\engulfing")

OUTPUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\filtered")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# HELPERS
# =========================================================
def load_latest(folder):
    files = sorted(folder.glob("*.csv"))
    if not files:
        return pd.DataFrame()
    return pd.read_csv(files[-1])

def normalize(df):
    if df.empty:
        return df

    df.columns = df.columns.str.upper().str.strip()

    for col in df.columns:
        if col.lower() == "symbol":
            df.rename(columns={col: "SYMBOL"}, inplace=True)

    return df

# =========================================================
# LOAD DATA
# =========================================================
def load_all():
    master = normalize(load_latest(MASTER_PATH))
    inside = normalize(load_latest(INSIDE_BAR_PATH))
    engulf = normalize(load_latest(ENGULF_PATH))

    return master, inside, engulf

# =========================================================
# FILTER LOGIC
# =========================================================
def apply_filter(master, inside, engulf):

    if master.empty:
        return pd.DataFrame()

    df = master.copy()

    required = ['SYMBOL','FINAL_SCORE','SM_SCORE','ADX_SCORE']
    for col in required:
        if col not in df.columns:
            print(f"⚠ Missing column: {col}")
            return pd.DataFrame()

    # =====================================================
    # 🧠 PASS COUNT LOGIC (CORE FIX)
    # =====================================================
    conditions = [
        df['SM_SCORE'] > 0.7,
        df['FINAL_SCORE'] > 0.4,
        df['ADX_SCORE'] > 0.3
    ]

    df['PASS_COUNT'] = sum(conditions)

    # =====================================================
    # 🟢 TIER 1: ELITE
    # =====================================================
    elite = df[
        (df['SM_SCORE'] > 0.85) &
        (df['FINAL_SCORE'] > 0.55)
    ]

    # =====================================================
    # 🟡 TIER 2: STRONG
    # =====================================================
    strong = df[
        (df['PASS_COUNT'] >= 2)
    ]

    # =====================================================
    # 🧩 FALLBACK (VERY IMPORTANT)
    # =====================================================
    if elite.empty and strong.empty:
        print("⚠ No strict matches → using fallback")

        strong = df[
            (df['SM_SCORE'] > 0.6)
        ]

    # Combine
    df = pd.concat([elite, strong]).drop_duplicates()

    # =====================================================
    # 🔥 CANDLE CONFIRMATION (NOT FILTER)
    # =====================================================
    valid_symbols = set()

    if not inside.empty and 'SYMBOL' in inside.columns:
        valid_symbols.update(inside['SYMBOL'].unique())

    if not engulf.empty and 'SYMBOL' in engulf.columns:
        valid_symbols.update(engulf['SYMBOL'].unique())

    df['CANDLE_CONFIRM'] = df['SYMBOL'].isin(valid_symbols)

    # =====================================================
    # 🧠 FINAL SCORE BOOST (SMART RANKING)
    # =====================================================
    df['FINAL_RANK_SCORE'] = (
        df['FINAL_SCORE'] * 0.5 +
        df['SM_SCORE'] * 0.3 +
        df['ADX_SCORE'] * 0.2
    )

    # Boost if candle confirmation
    df.loc[df['CANDLE_CONFIRM'] == True, 'FINAL_RANK_SCORE'] += 0.1

    # =====================================================
    # SORT
    # =====================================================
    df = df.sort_values(
        by=['FINAL_RANK_SCORE'],
        ascending=False
    )

    return df
    # =====================================================
    # 🟡 TIER 2: STRONG
    # =====================================================
    strong = df[
        (df['SM_SCORE'] > 0.75) &
        (df['FINAL_SCORE'] > 0.4)
    ]

    # Combine
    df = pd.concat([elite, strong]).drop_duplicates()

    # =====================================================
    # 🔥 CANDLE CONFIRMATION (NOT FILTER)
    # =====================================================
    valid_symbols = set()

    if not inside.empty and 'SYMBOL' in inside.columns:
        valid_symbols.update(inside['SYMBOL'].unique())

    if not engulf.empty and 'SYMBOL' in engulf.columns:
        valid_symbols.update(engulf['SYMBOL'].unique())

    if valid_symbols:
        df['CANDLE_CONFIRM'] = df['SYMBOL'].isin(valid_symbols)
    else:
        df['CANDLE_CONFIRM'] = False

    # =====================================================
    # SORTING LOGIC
    # =====================================================
    df = df.sort_values(
        by=['CANDLE_CONFIRM', 'FINAL_SCORE', 'SM_SCORE'],
        ascending=False
    )

    return df

# =========================================================
# SAVE
# =========================================================
def save(df):
    today = datetime.now().strftime("%Y-%m-%d")
    path = OUTPUT_DIR / f"filtered_trades_{today}.csv"

    df.to_csv(path, index=False)
    print(f"\n✔ Saved → {path}")

# =========================================================
# MAIN
# =========================================================
def main():
    print("🎯 FILTER ENGINE (PRO) STARTED")

    master, inside, engulf = load_all()

    result = apply_filter(master, inside, engulf)

    print("\n🔥 FILTERED TRADES")
    print(result.head(15)[[
        'SYMBOL',
        'FINAL_SCORE',
        'SM_SCORE',
        'ADX_SCORE',
        'CANDLE_CONFIRM'
    ]])

    save(result)

    print("\n🚀 FILTER ENGINE COMPLETED")

# =========================================================
if __name__ == "__main__":
    main()