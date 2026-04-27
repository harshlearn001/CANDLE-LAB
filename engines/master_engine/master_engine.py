#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MASTER ENGINE (PRO FINAL VERSION)

✔ Smart Money fix (RANK / RANK_SCORE handled)
✔ ADX signal mapping fixed
✔ Robust merging
✔ Clean scoring system
✔ Production ready

Author: Harshal System 🚀
"""

from pathlib import Path
import pandas as pd
from datetime import datetime

# =========================================================
# PATHS
# =========================================================
BASE_PATH = Path(r"H:\CANDLE-LAB\analysis\equity\signals")

SMART_MONEY_PATH = BASE_PATH / "smart_money"
PCR_PATH = BASE_PATH / "options_pcr"
ADX_PATH = BASE_PATH / "adx"

ENGULF_PATH = BASE_PATH / "engulfing"
INSIDE_PATH = BASE_PATH / "inside_bar"

OUTPUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\master")
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
    smart = normalize(load_latest(SMART_MONEY_PATH))
    pcr = normalize(load_latest(PCR_PATH))
    adx = normalize(load_latest(ADX_PATH))
    engulf = normalize(load_latest(ENGULF_PATH))
    inside = normalize(load_latest(INSIDE_PATH))

    return smart, pcr, adx, engulf, inside

# =========================================================
# SCORING
# =========================================================
def score_smart_money(df):
    if df.empty:
        return pd.DataFrame(columns=['SYMBOL','SM_SCORE'])

    df.columns = df.columns.str.upper()

    # 🔥 FIX: support both formats
    if 'RANK_SCORE' in df.columns:
        df['SM_SCORE'] = df['RANK_SCORE']
    elif 'RANK' in df.columns:
        df['SM_SCORE'] = df['RANK']
    else:
        print("⚠ Smart Money column missing")
        return pd.DataFrame(columns=['SYMBOL','SM_SCORE'])

    return df[['SYMBOL','SM_SCORE']]


def score_pcr(df):
    if df.empty or 'PCR' not in df.columns:
        return pd.DataFrame(columns=['SYMBOL','PCR_SCORE'])

    def logic(x):
        if x < 0.5:
            return 1
        elif x > 1:
            return -1
        else:
            return 0

    df['PCR_SCORE'] = df['PCR'].apply(logic)
    return df[['SYMBOL','PCR_SCORE']]


def score_adx(df):
    if df.empty:
        return pd.DataFrame(columns=['SYMBOL','ADX_SCORE'])

    df.columns = df.columns.str.upper()

    # Fix symbol column
    if 'SYMBOL' not in df.columns:
        for col in df.columns:
            if col.lower() == 'symbol':
                df.rename(columns={col: 'SYMBOL'}, inplace=True)

    if 'SIGNAL' not in df.columns:
        print("⚠ ADX SIGNAL missing")
        return pd.DataFrame(columns=['SYMBOL','ADX_SCORE'])

    def logic(x):
        if x == 'UPTREND':
            return 1
        elif x == 'DOWNTREND':
            return -1
        else:
            return 0

    df['ADX_SCORE'] = df['SIGNAL'].apply(logic)

    return df[['SYMBOL','ADX_SCORE']]


def score_candles(engulf, inside):
    frames = []

    if not engulf.empty and 'SYMBOL' in engulf.columns:
        engulf['CANDLE_SCORE'] = 1
        frames.append(engulf[['SYMBOL','CANDLE_SCORE']])

    if not inside.empty and 'SYMBOL' in inside.columns:
        inside['CANDLE_SCORE'] = 0.5
        frames.append(inside[['SYMBOL','CANDLE_SCORE']])

    if not frames:
        return pd.DataFrame(columns=['SYMBOL','CANDLE_SCORE'])

    df = pd.concat(frames)
    return df.groupby('SYMBOL').sum().reset_index()

# =========================================================
# MASTER BUILD
# =========================================================
def build_master():
    smart, pcr, adx, engulf, inside = load_all()

    sm = score_smart_money(smart)
    pc = score_pcr(pcr)
    ax = score_adx(adx)
    cd = score_candles(engulf, inside)

    df = sm.merge(pc, on='SYMBOL', how='outer') \
           .merge(ax, on='SYMBOL', how='outer') \
           .merge(cd, on='SYMBOL', how='outer')

    df = df.fillna(0)

    # =====================================================
    # FINAL SCORE
    # =====================================================
    df['FINAL_SCORE'] = (
        df['SM_SCORE'] * 0.4 +
        df['PCR_SCORE'] * 0.2 +
        df['ADX_SCORE'] * 0.2 +
        df['CANDLE_SCORE'] * 0.2
    )

    # Direction
    df['DIRECTION'] = df['FINAL_SCORE'].apply(
        lambda x: 'LONG' if x > 0 else 'SHORT'
    )

    # Confidence
    df['CONFIDENCE'] = (abs(df['FINAL_SCORE']) * 100).round(2)

    # =====================================================
    # SORTING
    # =====================================================
    df = df.sort_values(by='FINAL_SCORE', ascending=False)

    return df

# =========================================================
# SAVE
# =========================================================
def save(df):
    today = datetime.now().strftime("%Y-%m-%d")
    path = OUTPUT_DIR / f"master_trades_{today}.csv"

    df.to_csv(path, index=False)
    print(f"\n✔ Saved → {path}")

# =========================================================
# MAIN
# =========================================================
def main():
    print("🧠 MASTER ENGINE (PRO FINAL) STARTED")

    df = build_master()

    print("\n🎯 TOP TRADES")
    print(df.head(10)[[
        'SYMBOL','DIRECTION','FINAL_SCORE','CONFIDENCE'
    ]])

    save(df)

    print("\n🚀 MASTER ENGINE COMPLETED")

# =========================================================
if __name__ == "__main__":
    main()