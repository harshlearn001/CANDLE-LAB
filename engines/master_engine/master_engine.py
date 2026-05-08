#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
from datetime import datetime

BASE_PATH = Path(r"H:\CANDLE-LAB\analysis\equity\signals")

SMART = BASE_PATH / "smart_money"
PCR = BASE_PATH / "options_pcr"
ADX = BASE_PATH / "adx"
MARU = BASE_PATH / "marubozu_latest"
OHL = BASE_PATH / "open_high_low"

OUTPUT = Path(r"H:\CANDLE-LAB\analysis\equity\master")
OUTPUT.mkdir(parents=True, exist_ok=True)

def load_latest(p):
    f = sorted(p.glob("*.csv"))
    return pd.read_csv(f[-1]) if f else pd.DataFrame()

def norm(df):
    if df.empty: return df
    df.columns = df.columns.str.upper()
    if 'SYMBOL' not in df.columns:
        df.rename(columns={df.columns[0]:'SYMBOL'}, inplace=True)
    return df

def build():

    sm = norm(load_latest(SMART))
    pcr = norm(load_latest(PCR))
    adx = norm(load_latest(ADX))
    maru = norm(load_latest(MARU))
    ohl = norm(load_latest(OHL))

    df = sm[['SYMBOL','SM_SCORE']].copy()

    # PCR
    if 'PCR' in pcr.columns:
        pcr['PCR_SCORE'] = pcr['PCR'].apply(lambda x: 1 if x<0.5 else -1 if x>1 else 0)
        df = df.merge(pcr[['SYMBOL','PCR_SCORE']], on='SYMBOL', how='left')

    # ADX
    if 'SIGNAL' in adx.columns:
        adx['ADX_SCORE'] = adx['SIGNAL'].map({'UPTREND':1,'DOWNTREND':-1}).fillna(0)
        df = df.merge(adx[['SYMBOL','ADX_SCORE']], on='SYMBOL', how='left')

    # MARUBOZU
    if 'TYPE' in maru.columns:
        maru['MARU_SCORE'] = maru['TYPE'].map({'BULLISH':1,'BEARISH':-1})
        df = df.merge(maru[['SYMBOL','MARU_SCORE']], on='SYMBOL', how='left')

    # OPEN HL
    if 'TYPE' in ohl.columns:
        ohl['OHL_SCORE'] = ohl['TYPE'].apply(lambda x: 1 if 'LOW' in x else -1)
        df = df.merge(ohl[['SYMBOL','OHL_SCORE']], on='SYMBOL', how='left')

    df = df.fillna(0)

    # FINAL SCORE
    df['FINAL_SCORE'] = (
        df['SM_SCORE']*0.35 +
        df['PCR_SCORE']*0.25 +
        df['ADX_SCORE']*0.15 +
        df['MARU_SCORE']*0.15 +
        df['OHL_SCORE']*0.10
    )

    # DIRECTION (IMPROVED)
    def direction(x):
        if x > 0.3: return "LONG"
        elif x < -0.3: return "SHORT"
        else: return "SIDEWAYS"

    df['DIRECTION'] = df['FINAL_SCORE'].apply(direction)

    df['CONFIDENCE'] = (abs(df['FINAL_SCORE'])*100).round(2)

    df = df.sort_values(by='FINAL_SCORE', ascending=False)

    return df

def save(df):
    f = OUTPUT / f"master_trades_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(f,index=False)
    print("Saved →",f)

if __name__ == "__main__":
    print("MASTER ENGINE V2 RUNNING")
    df = build()
    print(df.head(10))
    save(df)