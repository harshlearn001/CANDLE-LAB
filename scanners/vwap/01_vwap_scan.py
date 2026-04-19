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
    "[bold cyan]VWAP SCANNER[/bold cyan]\n[green]Smart Entry Engine[/green]",
    border_style="cyan"
))

# =================================================
# PATHS
# =================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\vwap")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =================================================
# PARAMETERS
# =================================================
MIN_PRICE = 50
LOOKBACK = 20

# =================================================
# LOAD SYMBOLS
# =================================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.strip().str.upper().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

results = []
checked = 0
skipped = 0
all_dates = []   # ✅ collect data dates

# =================================================
# PROCESS
# =================================================
for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"

    if not file.exists():
        skipped += 1
        continue

    try:
        df = pd.read_csv(file)

        if df.empty:
            skipped += 1
            continue

        df.columns = df.columns.str.strip().str.upper()

        if not {"DATE", "HIGH", "LOW", "CLOSE"}.issubset(df.columns):
            skipped += 1
            continue

        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE")

        if len(df) < LOOKBACK + 5:
            skipped += 1
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["DATE"].max())

        # =================================================
        # VWAP
        # =================================================
        df["TP"] = (df["HIGH"] + df["LOW"] + df["CLOSE"]) / 3

        if "VOLUME" in df.columns:
            df["VOLUME"] = pd.to_numeric(df["VOLUME"], errors="coerce").fillna(0)

            vol_sum = df["VOLUME"].rolling(LOOKBACK).sum()

            df["VWAP"] = (
                (df["TP"] * df["VOLUME"]).rolling(LOOKBACK).sum()
            ) / vol_sum

            if df["VWAP"].isna().all():
                df["VWAP"] = df["TP"].rolling(LOOKBACK).mean()
        else:
            df["VWAP"] = df["TP"].rolling(LOOKBACK).mean()

        df = df.dropna(subset=["VWAP"])

        if df.empty:
            skipped += 1
            continue

        latest = df.iloc[-1]

        price = latest["CLOSE"]

        if price < MIN_PRICE:
            continue

        vwap = latest["VWAP"]
        distance = ((price - vwap) / vwap) * 100

        # =================================================
        # ZONE
        # =================================================
        if distance > 5:
            zone = "OVEREXTENDED"
        elif distance > 2:
            zone = "ABOVE_VWAP"
        elif distance < -5:
            zone = "DEEP_DISCOUNT"
        elif distance < -2:
            zone = "BELOW_VWAP"
        else:
            zone = "FAIR_VALUE"

        checked += 1

        results.append({
            "Symbol": symbol,
            "Date": latest["DATE"].strftime("%Y-%m-%d"),
            "Close": round(price, 2),
            "VWAP": round(vwap, 2),
            "Distance_%": round(distance, 2),
            "Zone": zone
        })

    except:
        skipped += 1
        continue

# =================================================
# FINAL DATE (FIX)
# =================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"vwap_scan_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =================================================
# SUMMARY
# =================================================
console.rule("[bold cyan]VWAP SUMMARY[/bold cyan]")

console.print(f"[cyan]📊 Checked:[/cyan] {checked}")
console.print(f"[yellow]⚠ Skipped:[/yellow] {skipped}")
console.print(f"[green]🔥 Results:[/green] {len(results)}")

# =================================================
# OUTPUT
# =================================================
df_out = pd.DataFrame(results)

if not df_out.empty:

    df_out = df_out.sort_values("Distance_%").reset_index(drop=True)

    table = Table(title="📊 VWAP BEST SETUPS")

    table.add_column("Symbol", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("VWAP", justify="center")
    table.add_column("Dist %", justify="center")
    table.add_column("Zone", justify="center")

    for _, row in df_out.head(15).iterrows():

        if row["Zone"] == "FAIR_VALUE":
            color = "cyan"
        elif row["Zone"] == "DEEP_DISCOUNT":
            color = "green"
        elif row["Zone"] == "OVEREXTENDED":
            color = "red"
        else:
            color = "yellow"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            f"[{color}]{row['Close']}[/{color}]",
            f"[{color}]{row['VWAP']}[/{color}]",
            f"[{color}]{row['Distance_%']}[/{color}]",
            f"[{color}]{row['Zone']}[/{color}]"
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold green]✔ Saved → {OUT_FILE}[/bold green]")

else:
    console.print("\n[red]❌ No VWAP results found[/red]")

# =================================================
# NOTE
# =================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Use with ADX + RSI + Candles for high probability trades")