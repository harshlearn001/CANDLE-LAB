#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich import print
from rich.console import Console
from rich.panel import Panel

from pathlib import Path
import pandas as pd
from datetime import datetime

console = Console()

# =================================================
# HEADER
# =================================================
console.print(Panel.fit(
    "[bold cyan]MARKET BREADTH ENGINE[/bold cyan]\n[green]Advance Decline Ratio[/green]",
    border_style="cyan"
))

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\breadth")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =================================================
# LOAD SYMBOLS
# =================================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.strip().str.upper().tolist()

console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

advances = 0
declines = 0
unchanged = 0
checked = 0

all_dates = []  # ✅ collect data dates

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

        if not {"DATE", "CLOSE"}.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 2:
            continue

        # ✅ collect latest date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        checked += 1

        if latest["CLOSE"] > prev["CLOSE"]:
            advances += 1
        elif latest["CLOSE"] < prev["CLOSE"]:
            declines += 1
        else:
            unchanged += 1

    except:
        continue

# =================================================
# FINAL DATE (IMPORTANT FIX)
# =================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"breadth_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =================================================
# CALCULATION
# =================================================
adr = advances / declines if declines != 0 else 0

# =================================================
# OUTPUT
# =================================================
console.rule("[bold cyan]BREADTH SUMMARY[/bold cyan]")

console.print(f"[cyan]Checked:[/cyan] {checked}")
console.print(f"[green]Advances:[/green] {advances}")
console.print(f"[red]Declines:[/red] {declines}")
console.print(f"[yellow]Unchanged:[/yellow] {unchanged}")
console.print(f"[bold]ADR:[/bold] {round(adr,2)}")

# =================================================
# INTERPRETATION
# =================================================
console.rule("[bold green]MARKET INSIGHT[/bold green]")

if adr > 2:
    insight = "🔥 Strong Bullish Breadth"
elif adr > 1.2:
    insight = "🟢 Bullish Breadth"
elif adr < 0.5:
    insight = "💀 Strong Bearish Breadth"
elif adr < 0.8:
    insight = "🔴 Bearish Breadth"
else:
    insight = "⚖ Neutral Breadth"

console.print(insight)

# =================================================
# SAVE
# =================================================
df_out = pd.DataFrame([{
    "Date": final_date,
    "Checked": checked,
    "Advances": advances,
    "Declines": declines,
    "Unchanged": unchanged,
    "ADR": round(adr, 2),
    "Insight": insight
}])

df_out.to_csv(OUT_FILE, index=False)

console.print(f"\n[bold green]✔ Saved → {OUT_FILE}[/bold green]")