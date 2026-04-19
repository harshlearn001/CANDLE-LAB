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

# =================================================
# HEADER
# =================================================
console.print(Panel.fit(
    "[bold red]BEARISH ENGULFING SCANNER[/bold red]\n[cyan]Pure Price Action Engine[/cyan]",
    border_style="red"
))

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\engulfing")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =================================================
# PARAMETERS
# =================================================
MIN_BODY_RATIO = 0.40

# =================================================
# LOAD SYMBOLS
# =================================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.strip().str.upper().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

results = []
checked = 0
all_dates = []   # ✅ collect data dates

# =================================================
# PROCESS
# =================================================
for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)

        if len(df) < 2:
            continue

        df.columns = df.columns.str.strip().str.upper()

        required = {"DATE", "OPEN", "HIGH", "LOW", "CLOSE"}
        if not required.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 2:
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        # BODY SIZE
        def body_ratio(c):
            rng = c["HIGH"] - c["LOW"]
            if rng <= 0:
                return 0
            return abs(c["CLOSE"] - c["OPEN"]) / rng

        if body_ratio(prev) < MIN_BODY_RATIO:
            continue

        if body_ratio(curr) < MIN_BODY_RATIO:
            continue

        # BEARISH ENGULFING
        if (
            prev["CLOSE"] > prev["OPEN"] and
            curr["CLOSE"] < curr["OPEN"] and
            curr["OPEN"]  > prev["CLOSE"] and
            curr["CLOSE"] < prev["OPEN"]
        ):

            body_size = abs(curr["CLOSE"] - curr["OPEN"])
            prev_body = abs(prev["CLOSE"] - prev["OPEN"])
            strength = "STRONG" if body_size > prev_body else "NORMAL"

            results.append({
                "Symbol": symbol,
                "Date": curr["DATE"].strftime("%Y-%m-%d"),
                "Close": round(curr["CLOSE"], 2),
                "Strength": strength
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

OUT_FILE = OUT_DIR / f"bearish_engulfing_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =================================================
# SUMMARY
# =================================================
console.rule("[bold cyan]ENGULFING SUMMARY[/bold cyan]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[red]🔥 Signals Found:[/red] {len(results)}")

# =================================================
# OUTPUT
# =================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("Date", ascending=False).reset_index(drop=True)

    table = Table(title="🔴 BEARISH ENGULFING")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "red" if row["Strength"] == "STRONG" else "yellow"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            f"[{color}]{row['Date']}[/{color}]",
            f"[{color}]{row['Close']}[/{color}]",
            f"[{color}]{row['Strength']}[/{color}]"
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold red]✔ Saved → {OUT_FILE}[/bold red]")

    console.rule("[bold red]ACTION LIST[/bold red]")

    console.print("\n[red]🔴 Short Candidates[/red]")
    for s in df_out["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[green]✔ No Bearish Engulfing Found[/green]")

# =================================================
# FINAL NOTE
# =================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Use with RSI / ADX for confirmation")