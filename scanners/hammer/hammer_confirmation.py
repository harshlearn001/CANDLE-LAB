#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

console = Console()

# =====================================================
# HEADER
# =====================================================
console.print(Panel.fit(
    "[bold green]HAMMER + CONFIRMATION[/bold green]\n[cyan]Reversal Entry Engine[/cyan]",
    border_style="green"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\hammer")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.strip().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

# =====================================================
# HAMMER DETECTION
# =====================================================
def detect_hammer(df):

    df = df.copy()

    df['range'] = df['High'] - df['Low']
    df = df[df['range'] > 0]

    df['body'] = abs(df['Close'] - df['Open'])
    df['upper_shadow'] = df['High'] - df[['Open','Close']].max(axis=1)
    df['lower_shadow'] = df[['Open','Close']].min(axis=1) - df['Low']

    df['body_pct'] = df['body'] / df['range']
    df['lower_shadow_pct'] = df['lower_shadow'] / df['range']
    df['upper_shadow_pct'] = df['upper_shadow'] / df['range']

    structure = (
        (df['body_pct'] <= 0.30) &
        (df['lower_shadow_pct'] >= 0.60) &
        (df['upper_shadow_pct'] <= 0.10)
    )

    df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
    trend = df['Close'] < df['EMA5']

    df['Hammer'] = structure & trend

    return df

# =====================================================
# MAIN LOOP
# =====================================================
signals = []
checked = 0
all_dates = []   # ✅ collect data dates

for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)

        if df.empty:
            continue

        df.columns = [c.strip().capitalize() for c in df.columns]

        required = {'Date','Open','High','Low','Close'}
        if not required.issubset(df.columns):
            continue

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        if len(df) < 10:
            continue

        # ✅ collect latest date
        if not df.empty:
            all_dates.append(df["Date"].max())

        checked += 1

        df = detect_hammer(df)

        hammer = df.iloc[-2]
        confirm = df.iloc[-1]

        if hammer['Hammer']:

            breakout = confirm['Close'] > hammer['High']
            bullish = confirm['Close'] > confirm['Open']

            if breakout and bullish:

                strength = confirm['Close'] - hammer['High']
                rating = "STRONG" if strength > (hammer['High'] * 0.01) else "NORMAL"

                signals.append({
                    "Symbol": symbol,
                    "Date": confirm['Date'].strftime("%Y-%m-%d"),
                    "Close": round(confirm['Close'], 2),
                    "Strength": round(strength, 2),
                    "Type": rating
                })

    except:
        continue

# =====================================================
# FINAL DATE (FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_hammer_confirmation_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold green]HAMMER SUMMARY[/bold green]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[green]🔥 Signals Found:[/green] {len(signals)}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(signals)

if not df_out.empty:

    df_out = df_out.sort_values("Strength", ascending=False)

    table = Table(title="🟢 HAMMER + CONFIRMATION")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Strength", justify="center")
    table.add_column("Type", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "green" if row["Type"] == "STRONG" else "yellow"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["Date"],
            str(row["Close"]),
            str(row["Strength"]),
            row["Type"]
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold green]✔ Saved → {OUT_FILE}[/bold green]")

    console.rule("[bold green]ACTION LIST[/bold green]")

    console.print("\n[green]🟢 Long Candidates[/green]")
    for s in df_out["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[red]❌ No Hammer Confirmation Found[/red]")

# =====================================================
# FINAL NOTE
# =====================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Best after downtrend + support bounce")