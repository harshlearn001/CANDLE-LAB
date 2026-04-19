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
    "[bold blue]4-DAY GREEN + RISING VOLUME[/bold blue]\n[cyan]Accumulation Engine[/cyan]",
    border_style="blue"
))

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\green_candle")
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

        if df.empty:
            continue

        df.columns = df.columns.str.strip().str.upper()

        required = {"DATE", "OPEN", "CLOSE", "TOTTRDQTY"}
        if not required.issubset(df.columns):
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < 4:
            continue

        # ✅ collect latest date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        checked += 1

        last4 = df.tail(4)

        # --------------------------------------------------
        # 4 GREEN CANDLES
        # --------------------------------------------------
        if not (last4["CLOSE"] > last4["OPEN"]).all():
            continue

        # --------------------------------------------------
        # STRICT VOLUME RISE
        # --------------------------------------------------
        vols = last4["TOTTRDQTY"].values

        if not (vols[0] < vols[1] < vols[2] < vols[3]):
            continue

        # --------------------------------------------------
        # METRICS
        # --------------------------------------------------
        body = (last4["CLOSE"] - last4["OPEN"]).sum()
        vol_growth = vols[3] / vols[0]

        strength = "STRONG" if vol_growth > 2 else "NORMAL"

        results.append({
            "Symbol": symbol,
            "To": last4.iloc[-1]["DATE"].strftime("%Y-%m-%d"),
            "Close": round(last4.iloc[-1]["CLOSE"], 2),
            "VolGrowth": round(vol_growth, 2),
            "Momentum": round(body, 2),
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

OUT_FILE = OUT_DIR / f"fno_4day_green_volume_rising_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =================================================
# SUMMARY
# =================================================
console.rule("[bold cyan]ACCUMULATION SUMMARY[/bold cyan]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[blue]🔥 Signals Found:[/blue] {len(results)}")

# =================================================
# OUTPUT
# =================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("VolGrowth", ascending=False).reset_index(drop=True)

    table = Table(title="🔵 4-DAY GREEN + RISING VOLUME")

    table.add_column("Symbol", justify="center")
    table.add_column("To", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("VolGrowth", justify="center")
    table.add_column("Momentum", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "blue" if row["Strength"] == "STRONG" else "yellow"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["To"],
            str(row["Close"]),
            str(row["VolGrowth"]),
            str(row["Momentum"]),
            row["Strength"]
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold blue]✔ Saved → {OUT_FILE}[/bold blue]")

    console.rule("[bold blue]ACTION LIST[/bold blue]")

    console.print("\n[blue]🔵 Accumulation Candidates[/blue]")
    for s in df_out["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[red]❌ No Accumulation Setup Found[/red]")

# =================================================
# FINAL NOTE
# =================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Early stage accumulation before breakout")