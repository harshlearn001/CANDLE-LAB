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

# =================================================
# HEADER
# =================================================
console.print(Panel.fit(
    "[bold magenta]DOJI SCANNER[/bold magenta]\n[cyan]Reversal Exhaustion Engine[/cyan]",
    border_style="magenta"
))

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\doji")
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

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)

        if df.empty:
            continue

        df.columns = df.columns.str.strip().str.upper()

        required = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}
        if not required.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 10:
            continue

        # Collect latest date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        # Uptrend check (optional)
        if df.iloc[-3]["CLOSE"] <= df.iloc[-6]["CLOSE"]:
            continue

        c = df.iloc[-1]
        o, h, l, cl = c["OPEN"], c["HIGH"], c["LOW"], c["CLOSE"]
        rng = h - l
        if rng <= 0:
            continue

        body = abs(cl - o)
        body_pct = body / rng

        # Doji pattern criteria
        if body_pct <= 0.10:  # Body less than or equal to 10%
            results.append({
                "Symbol": symbol,
                "Date": c["DATE"].strftime("%Y-%m-%d"),
                "Close": round(cl, 2),
                "Body%": round(body_pct * 100, 2)
            })

    except:
        continue

# =================================================
# FINAL DATE (FIX)
# =================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"doji_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =================================================
# SUMMARY
# =================================================
console.rule("[bold cyan]DOJI SUMMARY[/bold cyan]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[magenta]🔥 Signals Found:[/magenta] {len(results)}")

# =================================================
# OUTPUT
# =================================================
df_out = pd.DataFrame(results)

if not df_out.empty:
    df_out = df_out.sort_values("Body%", ascending=True).reset_index(drop=True)

    table = Table(title="🟣 DOJI")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Body%", justify="center")

    for _, row in df_out.head(15).iterrows():
        table.add_row(
            f"[yellow]{row['Symbol']}[/yellow]",
            f"[yellow]{row['Date']}[/yellow]",
            f"[yellow]{row['Close']}[/yellow]",
            f"[yellow]{row['Body%']}[/yellow]"
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold magenta]✔ Saved → {OUT_FILE}[/bold magenta]")
else:
    console.print("\n[green]✔ No Doji Found[/green]")

# =================================================
# FINAL NOTE
# =================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Indicates market indecision with very small body candles.")