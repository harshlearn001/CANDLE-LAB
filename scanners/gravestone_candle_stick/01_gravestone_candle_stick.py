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
    "[bold magenta]GRAVESTONE + STICK SCANNER[/bold magenta]\n[cyan]Supply Rejection Engine[/cyan]",
    border_style="magenta"
))

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\gravestone_stick")
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

        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        c = df.iloc[-1]

        o, h, l, cl = c["OPEN"], c["HIGH"], c["LOW"], c["CLOSE"]

        rng = h - l
        if rng <= 0:
            continue

        body = abs(cl - o)
        upper = h - max(o, cl)
        lower = min(o, cl) - l

        body_pct  = body / rng
        upper_pct = upper / rng
        lower_pct = lower / rng

        # --------------------------------------------------
        # RANGE QUALITY (RELAXED)
        # --------------------------------------------------
        recent_ranges = df.iloc[-10:-1]["HIGH"] - df.iloc[-10:-1]["LOW"]
        if rng < np.percentile(recent_ranges, 40):
            continue

        # --------------------------------------------------
        # GRAVESTONE + STICK (RELAXED REAL MARKET)
        # --------------------------------------------------
        if (
            body_pct <= 0.40 and
            upper_pct >= 0.45 and
            lower_pct <= 0.40
        ):

            if upper_pct > (lower_pct * 1.2):

                body_position = (max(o, cl) - l) / rng

                if body_position <= 0.50:

                    strength = "STRONG" if upper_pct >= 0.65 else "NORMAL"

                    results.append({
                        "Symbol": symbol,
                        "Date": c["DATE"].strftime("%Y-%m-%d"),
                        "Close": round(cl, 2),
                        "UpperWick%": round(upper_pct * 100, 2),
                        "LowerWick%": round(lower_pct * 100, 2),
                        "Strength": strength
                    })

        # --------------------------------------------------
        # DEBUG (OPTIONAL - uncomment if needed)
        # --------------------------------------------------
        # if upper_pct >= 0.40:
        #     print(symbol, "Upper:", round(upper_pct,2), "Lower:", round(lower_pct,2))

    except:
        continue

# =================================================
# FINAL DATE
# =================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"gravestone_stick_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =================================================
# SUMMARY
# =================================================
console.rule("[bold cyan]GRAVESTONE + STICK SUMMARY[/bold cyan]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[magenta]🔥 Signals Found:[/magenta] {len(results)}")

# =================================================
# OUTPUT
# =================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("UpperWick%", ascending=False).reset_index(drop=True)

    table = Table(title="🟣 GRAVESTONE + STICK (SUPPLY REJECTION)")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("UpperWick%", justify="center")
    table.add_column("LowerWick%", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "magenta" if row["Strength"] == "STRONG" else "yellow"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            f"[{color}]{row['Date']}[/{color}]",
            f"[{color}]{row['Close']}[/{color}]",
            f"[{color}]{row['UpperWick%']}[/{color}]",
            f"[{color}]{row['LowerWick%']}[/{color}]",
            f"[{color}]{row['Strength']}[/{color}]"
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold magenta]✔ Saved → {OUT_FILE}[/bold magenta]")

    console.rule("[bold red]ACTION LIST[/bold red]")

    console.print("\n[red]🔴 Potential Reversal Shorts[/red]")
    for s in df_out["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[green]✔ No Gravestone Stick Found[/green]")

# =================================================
# FINAL NOTE
# =================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Works best near resistance / supply zones")