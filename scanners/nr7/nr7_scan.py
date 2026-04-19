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
    "[bold magenta]NR7 SCANNER[/bold magenta]\n[white]Volatility Contraction Engine[/white]",
    border_style="magenta"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\nr7")
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
for sym in symbols:

    file = EQUITY_DIR / f"{sym}.csv"

    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.upper()

        if not {"DATE","HIGH","LOW","CLOSE"}.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 30:
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        if "TOTTRDQTY" not in df.columns:
            df["TOTTRDQTY"] = 0

        # =====================================================
        # CALCULATIONS
        # =====================================================
        df["RANGE"] = df["HIGH"] - df["LOW"]
        df["MA20"] = df["CLOSE"].rolling(20).mean()
        df["VOL_AVG"] = df["TOTTRDQTY"].rolling(20).mean()

        df = df.dropna()

        if len(df) < 7:
            continue

        last7 = df.tail(7)

        today = last7.iloc[-1]
        prev6 = last7.iloc[:-1]

        # =====================================================
        # CONDITIONS
        # =====================================================
        is_nr7 = today["RANGE"] < prev6["RANGE"].min()
        trend = today["CLOSE"] > today["MA20"]
        vol_contract = today["TOTTRDQTY"] < today["VOL_AVG"]

        if is_nr7 and vol_contract:

            compression = today["RANGE"] / prev6["RANGE"].mean()
            strength = "STRONG" if compression < 0.6 else "NORMAL"
            direction = "UP" if trend else "DOWN"

            results.append({
                "Symbol": sym,
                "Date": today["DATE"].strftime("%Y-%m-%d"),
                "Close": round(today["CLOSE"], 2),
                "Compression": round(compression, 2),
                "Direction": direction,
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

OUT_FILE = OUT_DIR / f"fno_nr7_filtered_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold magenta]NR7 SUMMARY[/bold magenta]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[magenta]🔥 Signals Found:[/magenta] {len(results)}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("Compression")

    table = Table(title="🟣 NR7 (VOLATILITY COMPRESSION)")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Compression", justify="center")
    table.add_column("Dir", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "green" if row["Direction"] == "UP" else "red"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["Date"],
            str(row["Close"]),
            str(row["Compression"]),
            row["Direction"],
            row["Strength"]
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold magenta]✔ Saved → {OUT_FILE}[/bold magenta]")

    console.rule("[bold magenta]ACTION LIST[/bold magenta]")

    console.print("\n[green]🟢 Breakout Candidates[/green]")
    for s in df_out[df_out["Direction"]=="UP"]["Symbol"].head(5):
        console.print(f"  → {s}")

    console.print("\n[red]🔴 Breakdown Candidates[/red]")
    for s in df_out[df_out["Direction"]=="DOWN"]["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[yellow]⚠ No NR7 Found[/yellow]")

# =====================================================
# FINAL NOTE
# =====================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 NR7 = lowest volatility → big move coming")