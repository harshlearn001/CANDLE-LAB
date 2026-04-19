#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import pandas as pd
from pathlib import Path
from datetime import datetime

console = Console()

# =====================================================
# HEADER
# =====================================================
console.print(Panel.fit(
    "[bold cyan]INSIDE BAR SCANNER[/bold cyan]\n[white]Volatility Compression Engine[/white]",
    border_style="cyan"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\inside_bar")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.strip().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

results = []
checked = 0
all_dates = []   # ✅ collect data dates

# =====================================================
# MAIN LOOP
# =====================================================
for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.upper()

        if not {"DATE","HIGH","LOW","CLOSE"}.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 5:
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        today = df.iloc[-1]
        prev  = df.iloc[-2]

        # =====================================================
        # INSIDE BAR CONDITION
        # =====================================================
        if today["HIGH"] < prev["HIGH"] and today["LOW"] > prev["LOW"]:

            today_range = today["HIGH"] - today["LOW"]
            prev_range  = prev["HIGH"] - prev["LOW"]

            if prev_range == 0:
                continue

            compression = today_range / prev_range

            # TREND
            df["EMA20"] = df["CLOSE"].ewm(span=20).mean()
            trend = "UP" if today["CLOSE"] > df["EMA20"].iloc[-1] else "DOWN"

            strength = "STRONG" if compression < 0.5 else "NORMAL"

            results.append({
                "Symbol": symbol,
                "Date": today["DATE"].strftime("%Y-%m-%d"),
                "Close": round(today["CLOSE"], 2),
                "Compression": round(compression, 2),
                "Trend": trend,
                "Strength": strength
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

OUT_FILE = OUT_DIR / f"fno_inside_bar_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold cyan]INSIDE BAR SUMMARY[/bold cyan]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[blue]🔥 Signals Found:[/blue] {len(results)}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("Compression")

    table = Table(title="🔵 INSIDE BAR (BREAKOUT SETUPS)")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Compression", justify="center")
    table.add_column("Trend", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "green" if row["Trend"] == "UP" else "red"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["Date"],
            str(row["Close"]),
            str(row["Compression"]),
            row["Trend"],
            row["Strength"]
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold cyan]✔ Saved → {OUT_FILE}[/bold cyan]")

    console.rule("[bold cyan]ACTION LIST[/bold cyan]")

    console.print("\n[green]🟢 Breakout Up Candidates[/green]")
    for s in df_out[df_out["Trend"]=="UP"]["Symbol"].head(5):
        console.print(f"  → {s}")

    console.print("\n[red]🔴 Breakdown Candidates[/red]")
    for s in df_out[df_out["Trend"]=="DOWN"]["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[yellow]⚠ No Inside Bar Found[/yellow]")

# =====================================================
# FINAL NOTE
# =====================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Inside Bar = compression → breakout coming")