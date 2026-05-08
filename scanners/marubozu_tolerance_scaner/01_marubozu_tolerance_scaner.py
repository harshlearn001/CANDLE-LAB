#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pathlib import Path
import pandas as pd
from datetime import datetime

console = Console()

# =====================================================
# HEADER
# =====================================================
console.print(Panel.fit(
    "[bold yellow]MARUBOZU (LATEST ONLY)[/bold yellow]\n[cyan]Daily Momentum Scanner[/cyan]",
    border_style="yellow"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\marubozu_latest")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

signals = []
checked = 0
all_dates = []

# =====================================================
# MARUBOZU LOGIC (TOLERANCE)
# =====================================================
def detect_marubozu(df):

    df = df.copy()

    body = abs(df['Close'] - df['Open'])
    range_ = df['High'] - df['Low']

    upper_wick = df['High'] - df[['Open', 'Close']].max(axis=1)
    lower_wick = df[['Open', 'Close']].min(axis=1) - df['Low']

    df['Body_Ratio'] = body / range_.replace(0, 1)

    df['Bullish_Marubozu'] = (
        (df['Close'] > df['Open']) &
        (df['Body_Ratio'] > 0.6) &
        (lower_wick < body * 0.3)
    )

    df['Bearish_Marubozu'] = (
        (df['Close'] < df['Open']) &
        (df['Body_Ratio'] > 0.6) &
        (upper_wick < body * 0.3)
    )

    return df

# =====================================================
# MAIN LOOP
# =====================================================
for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)
        df.columns = [c.strip().capitalize() for c in df.columns]

        if not {'Date','Open','High','Low','Close'}.issubset(df.columns):
            continue

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        if len(df) < 20:
            continue

        # Collect latest date
        all_dates.append(df["Date"].max())

        checked += 1

        df = detect_marubozu(df)

        # =====================================================
        # 🔥 SCAN ONLY LATEST CANDLE
        # =====================================================
        latest = df.iloc[-1]

        if latest['Bullish_Marubozu']:

            strength = abs(latest['Close'] - latest['Open'])

            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'].strftime("%Y-%m-%d"),
                "Close": round(latest['Close'], 2),
                "Type": "BULLISH",
                "Strength": round(strength, 2)
            })

        elif latest['Bearish_Marubozu']:

            strength = abs(latest['Close'] - latest['Open'])

            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'].strftime("%Y-%m-%d"),
                "Close": round(latest['Close'], 2),
                "Type": "BEARISH",
                "Strength": round(strength, 2)
            })

    except:
        continue

# =====================================================
# FINAL DATE
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_marubozu_latest_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold yellow]LATEST MARUBOZU SUMMARY[/bold yellow]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[yellow]🔥 Signals Found:[/yellow] {len(signals)}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(signals)

if not df_out.empty:

    df_out = df_out.sort_values("Strength", ascending=False)

    table = Table(title="🟡 TODAY'S MARUBOZU SIGNALS")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "green" if row["Type"] == "BULLISH" else "red"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["Date"],
            str(row["Close"]),
            row["Type"],
            str(row["Strength"])
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold yellow]✔ Saved → {OUT_FILE}[/bold yellow]")

else:
    console.print("\n[yellow]⚠ No Signals Found[/yellow]")

# =====================================================
# NOTE
# =====================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Only latest candle signals (today's market setups)")