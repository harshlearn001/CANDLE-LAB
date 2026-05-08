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

# =====================================================
# SETTINGS
# =====================================================
TOLERANCE_PCT = 0.001   # 0.1% tolerance (VERY STRICT)
BODY_RATIO_MIN = 0.7    # strong candle

# =====================================================
# HEADER
# =====================================================
console.print(Panel.fit(
    "[bold red]STRICT OPEN=HIGH / OPEN=LOW[/bold red]\n[cyan]True Control Candle Scanner[/cyan]",
    border_style="red"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\open_high_low")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()

signals = []
all_dates = []
checked = 0

# =====================================================
# MAIN LOOP
# =====================================================
for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"
    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)
        df.columns = [c.strip().capitalize() for c in df.columns]

        if not {'Date','Open','High','Low','Close'}.issubset(df.columns):
            continue

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        if len(df) < 20:
            continue

        checked += 1
        all_dates.append(df["Date"].max())

        latest = df.iloc[-1]

        O = latest['Open']
        H = latest['High']
        L = latest['Low']
        C = latest['Close']

        body = abs(C - O)
        range_ = H - L

        if range_ == 0:
            continue

        body_ratio = body / range_

        # 🔥 dynamic tolerance
        tol = C * TOLERANCE_PCT

        strength = abs(C - O)

        # 🟢 TRUE OPEN = LOW
        if (
            abs(O - L) <= tol and
            C > O and
            body_ratio >= BODY_RATIO_MIN
        ):
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'].strftime("%Y-%m-%d"),
                "Type": "OPEN=LOW (TRUE)",
                "Strength": round(strength, 2)
            })

        # 🔴 TRUE OPEN = HIGH
        elif (
            abs(O - H) <= tol and
            C < O and
            body_ratio >= BODY_RATIO_MIN
        ):
            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'].strftime("%Y-%m-%d"),
                "Type": "OPEN=HIGH (TRUE)",
                "Strength": round(strength, 2)
            })

    except:
        continue

# =====================================================
# OUTPUT
# =====================================================
final_date = max(all_dates).strftime("%Y-%m-%d") if all_dates else "NA"
OUT_FILE = OUT_DIR / f"open_high_low_{final_date}.csv"

console.print(f"\nChecked: {checked}")
console.print(f"Signals: {len(signals)}")

df_out = pd.DataFrame(signals)

if not df_out.empty:

    df_out = df_out.sort_values("Strength", ascending=False)

    table = Table(title="🔥 TRUE OPEN=HIGH / OPEN=LOW")

    table.add_column("Symbol")
    table.add_column("Date")
    table.add_column("Type")
    table.add_column("Strength")

    for _, row in df_out.head(15).iterrows():
        table.add_row(row["Symbol"], row["Date"], row["Type"], str(row["Strength"]))

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n✔ Saved → {OUT_FILE}")

else:
    console.print("\n⚠ No True Open=High/Low candles found")