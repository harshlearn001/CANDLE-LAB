#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    "[bold red]HANGING MAN SCANNER[/bold red]\n[cyan]Top Reversal Exhaustion Engine[/cyan]",
    border_style="red"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\hangingman")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

signals = []
checked = 0
all_dates = []   # ✅ collect data dates

# =====================================================
# SWING HIGH FUNCTION
# =====================================================
def is_near_swing_high(df, i, lookback=10):
    if i - lookback < 0:
        return False
    recent_high = df['High'].iloc[i-lookback:i].max()
    current_high = df['High'].iloc[i]
    return current_high >= 0.95 * recent_high

# =====================================================
# MAIN LOOP
# =====================================================
for symbol in symbols:

    file_path = EQUITY_DIR / f"{symbol}.csv"
    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)
        df.columns = [c.strip().capitalize() for c in df.columns]

        if not {'Date','Open','High','Low','Close'}.issubset(df.columns):
            continue

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']).sort_values("Date")

        if len(df) < 220:
            continue

        # ✅ collect date
        if not df.empty:
            all_dates.append(df["Date"].max())

        checked += 1

        # INDICATORS
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()

        # LAST 5 CANDLES
        for i in range(-5, 0):

            row = df.iloc[i]

            open_ = row['Open']
            close = row['Close']
            high = row['High']
            low = row['Low']

            body = abs(close - open_)
            candle_range = high - low

            if candle_range == 0 or body == 0:
                continue

            upper = high - max(open_, close)
            lower = min(open_, close) - low

            structure = (
                lower >= 1.5 * body and
                upper <= body
            )

            body_top = max(open_, close)
            position = body_top >= (high - candle_range * 0.4)

            trend = (
                close > df['EMA50'].iloc[i] and
                df['EMA50'].iloc[i] > df['SMA200'].iloc[i]
            )

            location = is_near_swing_high(df, i)

            if structure and position and trend and location:

                strength = lower / body
                rating = "STRONG" if strength > 3 else "NORMAL"

                signals.append({
                    "Symbol": symbol,
                    "Date": row['Date'].strftime("%Y-%m-%d"),
                    "Close": round(close, 2),
                    "Strength": round(strength, 2),
                    "Type": rating
                })

                break

    except:
        continue

# =====================================================
# FINAL DATE (FIX)
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_hanging_man_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold red]HANGING MAN SUMMARY[/bold red]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[red]🔥 Signals Found:[/red] {len(signals)}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(signals)

if not df_out.empty:

    df_out = df_out.sort_values("Strength", ascending=False)

    table = Table(title="🔻 HANGING MAN (TOP REVERSAL)")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Strength", justify="center")
    table.add_column("Type", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "red" if row["Type"] == "STRONG" else "yellow"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["Date"],
            str(row["Close"]),
            str(row["Strength"]),
            row["Type"]
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold red]✔ Saved → {OUT_FILE}[/bold red]")

    console.rule("[bold red]ACTION LIST[/bold red]")

    console.print("\n[red]🔻 Potential Shorts[/red]")
    for s in df_out["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[green]✔ No Top Exhaustion Found (Trend Strong)[/green]")

# =====================================================
# FINAL NOTE
# =====================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Wait for breakdown confirmation before shorting")
