#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

console = Console()

# =====================================================
# HEADER
# =====================================================
console.print(Panel.fit(
    "[bold green]ADX SCANNER[/bold green]\n[cyan]Trend Strength Engine[/cyan]",
    border_style="green"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\adx")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

signals = []
all_dates = []   # ✅ NEW: collect all data dates

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
uptrend_count = 0
downtrend_count = 0
weak_count = 0
checked = 0

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

        # ✅ COLLECT DATA DATE
        if not df.empty:
            all_dates.append(df["Date"].max())

        checked += 1

        df = calculate_adx(df)

        latest = df.iloc[-1]

        adx = latest['ADX']
        plus_di = latest['+DI']
        minus_di = latest['-DI']

        signal = None

        if adx < 20:
            signal = "WEAK"
            weak_count += 1

        elif adx > 25:
            if plus_di > minus_di:
                signal = "UPTREND"
                uptrend_count += 1
            elif minus_di > plus_di:
                signal = "DOWNTREND"
                downtrend_count += 1

        if signal:
            signals.append({
                "Symbol": symbol,
                "Close": round(latest['Close'], 2),
                "ADX": round(adx, 2),
                "+DI": round(plus_di, 2),
                "-DI": round(minus_di, 2),
                "Signal": signal
            })

    except:
        continue

# =====================================================
# FINAL DATE (IMPORTANT FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_adx_signals_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold cyan]ADX SUMMARY[/bold cyan]")

console.print(f"[green]🔥 Uptrend:[/green] {uptrend_count}")
console.print(f"[red]💀 Downtrend:[/red] {downtrend_count}")
console.print(f"[yellow]⚠ Weak Trend:[/yellow] {weak_count}")
console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")

# =====================================================
# MARKET STRUCTURE %
# =====================================================
total = uptrend_count + downtrend_count + weak_count

if total > 0:
    up_pct = (uptrend_count / total) * 100
    down_pct = (downtrend_count / total) * 100
    weak_pct = (weak_count / total) * 100

    console.print(f"\n[bold]📊 Market Structure:[/bold]")
    console.print(f"[green]Uptrend: {up_pct:.1f}%[/green]")
    console.print(f"[red]Downtrend: {down_pct:.1f}%[/red]")
    console.print(f"[yellow]Weak: {weak_pct:.1f}%[/yellow]")

# =====================================================
# DATAFRAME
# =====================================================
signals_df = pd.DataFrame(signals)

if not signals_df.empty:

    signals_df = signals_df.sort_values("ADX", ascending=False)

    signals_df.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold green]✔ Saved → {OUT_FILE}[/bold green]")