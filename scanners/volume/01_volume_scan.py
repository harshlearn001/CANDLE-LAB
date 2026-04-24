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
import matplotlib.pyplot as plt

console = Console()

# =================================================
# SETTINGS
# =================================================
DEBUG = False  # 🔥 Turn ON/OFF debug logs

# =================================================
# HEADER
# =================================================
console.print(Panel.fit(
    "[bold magenta]VOLUME INDICATOR[/bold magenta]\n[cyan]Volume Analysis Engine[/cyan]",
    border_style="magenta"
))

# =================================================
# PATHS
# =================================================
DATA_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")
OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\volume")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =================================================
# LOAD SYMBOLS
# =================================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.strip().str.upper().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

results = []
checked = 0
all_dates = []

# =================================================
# PROCESS
# =================================================
for symbol in symbols:

    if DEBUG:
        console.print(f"\nProcessing symbol: {symbol}")

    file = DATA_DIR / f"{symbol}.csv"

    if not file.exists():
        if DEBUG:
            console.print(f"[red]File not found:[/red] {file}")
        continue

    try:
        df = pd.read_csv(file)

        if df.empty:
            if DEBUG:
                console.print(f"[yellow]No data in file for {symbol}[/yellow]")
            continue

        # Clean column headers
        df.columns = df.columns.str.strip().str.upper()

        # Print columns only ONCE
        if DEBUG and checked == 0:
            console.print(f"[blue]Columns:[/blue] {df.columns.tolist()}")

        # Required columns
        required = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE", "TOTTRDQTY"}

        if not required.issubset(df.columns):
            if DEBUG:
                missing_cols = required - set(df.columns)
                console.print(f"[red]Missing columns for {symbol}:[/red] {missing_cols}")
            continue

        # Convert DATE
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 20:
            continue

        # Track latest date
        all_dates.append(df["DATE"].max())
        checked += 1

        # =================================================
        # VOLUME CALCULATION
        # =================================================
        df["VOL_20_MA"] = df["TOTTRDQTY"].rolling(window=20).mean()

        latest = df.iloc[-1]
        vol = latest["TOTTRDQTY"]
        vol_ma = latest["VOL_20_MA"]

        if DEBUG:
            console.print(f"{symbol} volume: {vol}")
            console.print(f"{symbol} MA20: {vol_ma}")

        # =================================================
        # STORE RESULT
        # =================================================
        results.append({
            "Symbol": symbol,
            "Date": latest["DATE"].strftime("%Y-%m-%d"),
            "Volume": int(vol),
            "Volume_MA20": float(vol_ma)
        })

    except Exception as e:
        console.print(f"[red]Error processing {symbol}: {e}[/red]")
        continue

# =================================================
# FINAL DATE
# =================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"volume_{final_date}.csv"

console.print(f"\n[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =================================================
# SUMMARY
# =================================================
console.rule("[bold cyan]VOLUME SUMMARY[/bold cyan]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[magenta]📈 Signals Found:[/magenta] {len(results)}")

# =================================================
# OUTPUT
# =================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("Volume", ascending=False).reset_index(drop=True)

    table = Table(title="Volume Analysis")
    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Volume", justify="center")
    table.add_column("20 MA Volume", justify="center")

    for _, row in df_out.head(15).iterrows():
        table.add_row(
            f"[yellow]{row['Symbol']}[/yellow]",
            f"[yellow]{row['Date']}[/yellow]",
            f"[yellow]{row['Volume']}[/yellow]",
            f"[yellow]{round(row['Volume_MA20'], 2)}[/yellow]"
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold magenta]✔ Saved → {OUT_FILE}[/bold magenta]")

else:
    console.print("\n[green]✔ No Volume Data Found[/green]")

# =================================================
# FINAL NOTE
# =================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Volume analysis with moving average indicates trading activity levels.")