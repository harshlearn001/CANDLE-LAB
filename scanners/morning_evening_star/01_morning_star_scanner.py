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
    "[bold yellow]MORNING STAR SCANNER[/bold yellow]\n[white]Reversal Bottom Engine[/white]",
    border_style="yellow"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\morning_star")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
fno = pd.read_csv(FNO_FILE)

symbol_col = None
for col in ["Symbol","symbol","SYMBOL","tradingsymbol"]:
    if col in fno.columns:
        symbol_col = col
        break

if symbol_col is None:
    raise ValueError(f"No symbol column found: {fno.columns}")

symbols = fno[symbol_col].dropna().astype(str).str.strip().unique()

console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

results = []
checked = 0
all_dates = []   # ✅ collect data dates

# =====================================================
# MAIN LOOP
# =====================================================
for sym in symbols:

    file = EQUITY_DIR / f"{sym}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)

        df.columns = df.columns.str.strip().str.upper()

        if not {"DATE","OPEN","HIGH","LOW","CLOSE"}.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 5:
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]

        # =====================================================
        # MORNING STAR LOGIC
        # =====================================================
        cond1 = c1["CLOSE"] < c1["OPEN"]

        body2 = abs(c2["CLOSE"] - c2["OPEN"])
        range2 = c2["HIGH"] - c2["LOW"]
        cond2 = range2 > 0 and body2 < (0.3 * range2)

        cond3 = (
            c3["CLOSE"] > c3["OPEN"] and
            c3["CLOSE"] > (c1["OPEN"] + c1["CLOSE"]) / 2
        )

        if cond1 and cond2 and cond3:

            strength = abs(c3["CLOSE"] - c1["CLOSE"])
            level = "STRONG" if strength > (0.02 * c3["CLOSE"]) else "NORMAL"

            results.append({
                "Symbol": sym,
                "Date": c3["DATE"].strftime("%Y-%m-%d"),
                "Close": round(c3["CLOSE"], 2),
                "StrengthPts": round(strength, 2),
                "Strength": level
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

OUT_FILE = OUT_DIR / f"fno_morning_star_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold yellow]MORNING STAR SUMMARY[/bold yellow]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[yellow]🔥 Signals Found:[/yellow] {len(results)}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("StrengthPts", ascending=False)

    table = Table(title="🌅 MORNING STAR (REVERSAL SETUPS)")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("StrengthPts", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(10).iterrows():

        color = "green" if row["Strength"] == "STRONG" else "white"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["Date"],
            str(row["Close"]),
            str(row["StrengthPts"]),
            row["Strength"]
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold yellow]✔ Saved → {OUT_FILE}[/bold yellow]")

    console.rule("[bold yellow]ACTION LIST[/bold yellow]")

    console.print("\n[green]🟢 Reversal Buy Candidates[/green]")
    for s in df_out["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[yellow]⚠ No Morning Star Found[/yellow]")

# =====================================================
# FINAL NOTE
# =====================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Morning Star = bottom reversal after sell-off")