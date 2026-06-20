#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pathlib import Path
import pandas as pd
from datetime import datetime

console = Console()

# =====================================================
# HEADER
# =====================================================
console.print(Panel.fit(
    "[bold magenta]MARUBOZU SCANNER[/bold magenta]\n[cyan]Strong Momentum Candle Engine[/cyan]",
    border_style="magenta"
))

# =====================================================
# PATHS
# =====================================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\marubozu")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOAD SYMBOLS
# =====================================================
symbols = pd.read_csv(FNO_FILE).iloc[:, 0].astype(str).str.strip().tolist()
console.print(f"\n[cyan]Loaded Symbols:[/cyan] {len(symbols)}")

signals = []
checked = 0
all_dates = []

# =====================================================
# MARUBOZU LOGIC
# =====================================================
def detect_marubozu(df, tolerance=0.002):

    df = df.copy()

    body = abs(df['Close'] - df['Open'])
    range_ = df['High'] - df['Low']

    upper_wick = df['High'] - df[['Open', 'Close']].max(axis=1)
    lower_wick = df[['Open', 'Close']].min(axis=1) - df['Low']

    # Avoid division by zero
    df['Body_Ratio'] = body / range_.replace(0, 1)

    # Bullish Marubozu
    df['Bullish_Marubozu'] = (
        (df['Close'] > df['Open']) &
        (upper_wick <= tolerance * range_) &
        (lower_wick <= tolerance * range_) &
        (df['Body_Ratio'] > 0.9)
    )

    # Bearish Marubozu
    df['Bearish_Marubozu'] = (
        (df['Close'] < df['Open']) &
        (upper_wick <= tolerance * range_) &
        (lower_wick <= tolerance * range_) &
        (df['Body_Ratio'] > 0.9)
    )

    return df

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

        # collect date
        if not df.empty:
            all_dates.append(df["Date"].max())

        checked += 1

        df = detect_marubozu(df)

        latest = df.iloc[-1]

        # =============================
        # OPTIONAL TREND FILTER
        # =============================
        df['EMA20'] = df['Close'].ewm(span=20).mean()

        trend_up = latest['Close'] > df['EMA20'].iloc[-1]
        trend_down = latest['Close'] < df['EMA20'].iloc[-1]

        # =============================
        # SIGNAL
        # =============================
        if latest['Bullish_Marubozu'] and trend_up:

            strength = abs(latest['Close'] - latest['Open'])

            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'].strftime("%Y-%m-%d"),
                "Close": round(latest['Close'], 2),
                "Type": "BULLISH",
                "Strength": round(strength, 2)
            })

        elif latest['Bearish_Marubozu'] and trend_down:

            strength = abs(latest['Close'] - latest['Open'])

            signals.append({
                "Symbol": symbol,
                "Date": latest['Date'].strftime("%Y-%m-%d"),
                "Close": round(latest['Close'], 2),
                "Type": "BEARISH",
                "Strength": round(strength, 2)
            })

    except:
        continue

# =====================================================
# FINAL DATE
# =====================================================
if all_dates:
    final_date = max(all_dates).strftime("%Y-%m-%d")
else:
    final_date = datetime.now().strftime("%Y-%m-%d")

OUT_FILE = OUT_DIR / f"fno_marubozu_{final_date}.csv"

console.print(f"[yellow]📅 Data Date Used: {final_date}[/yellow]")

# =====================================================
# SUMMARY
# =====================================================
console.rule("[bold magenta]MARUBOZU SUMMARY[/bold magenta]")

console.print(f"[cyan]📊 Total Checked:[/cyan] {checked}")
console.print(f"[magenta]🔥 Signals Found:[/magenta] {len(signals)}")

# =====================================================
# OUTPUT
# =====================================================
df_out = pd.DataFrame(signals)

if not df_out.empty:

    df_out = df_out.sort_values("Strength", ascending=False)

    table = Table(title="🟣 MARUBOZU SIGNALS")

    table.add_column("Symbol", justify="center")
    table.add_column("Date", justify="center")
    table.add_column("Close", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Strength", justify="center")

    for _, row in df_out.head(15).iterrows():

        color = "green" if row["Type"] == "BULLISH" else "red"

        table.add_row(
            f"[{color}]{row['Symbol']}[/{color}]",
            row["Date"],
            str(row["Close"]),
            row["Type"],
            str(row["Strength"])
        )

    console.print(table)

    df_out.to_csv(OUT_FILE, index=False)
    console.print(f"\n[bold magenta]✔ Saved → {OUT_FILE}[/bold magenta]")

    console.rule("[bold magenta]ACTION LIST[/bold magenta]")

    console.print("\n[green]🟢 Bullish Watchlist[/green]")
    for s in df_out[df_out["Type"]=="BULLISH"]["Symbol"].head(5):
        console.print(f"  → {s}")

    console.print("\n[red]🔴 Bearish Watchlist[/red]")
    for s in df_out[df_out["Type"]=="BEARISH"]["Symbol"].head(5):
        console.print(f"  → {s}")

else:
    console.print("\n[yellow]⚠ No Marubozu Signals Found[/yellow]")

# =====================================================
# FINAL NOTE
# =====================================================
console.rule("[bold yellow]NOTE[/bold yellow]")
console.print("👉 Marubozu = strong momentum → best for breakout continuation trades")
