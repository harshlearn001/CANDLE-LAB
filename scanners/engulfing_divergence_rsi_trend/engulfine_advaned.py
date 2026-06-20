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

# ================================
# HEADER
# ================================
console.print(Panel.fit(
    "[bold red]MARKETFORGE PRO ENGINE[/bold red]\n[cyan]Smart Ranked + Context Filter[/cyan]",
    border_style="red"
))

# ================================
# PATHS
# ================================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\Evening_star_advanced")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ================================
# SETTINGS
# ================================
RSI_LENGTH = 14
LOOKBACK = 5
MIN_BODY_RATIO = 0.40

# ================================
# RSI
# ================================
def calculate_rsi(df):
    delta = df["CLOSE"].diff()
    gain = delta.clip(lower=0).rolling(RSI_LENGTH).mean()
    loss = (-delta.clip(upper=0)).rolling(RSI_LENGTH).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

# ================================
# DIVERGENCE
# ================================
def detect_div(df):
    df["BearDiv"] = False
    df["BullDiv"] = False

    for i in range(LOOKBACK, len(df)):
        if df["HIGH"].iloc[i] > df["HIGH"].iloc[i-LOOKBACK] and df["RSI"].iloc[i] < df["RSI"].iloc[i-LOOKBACK]:
            df.loc[df.index[i], "BearDiv"] = True

        if df["LOW"].iloc[i] < df["LOW"].iloc[i-LOOKBACK] and df["RSI"].iloc[i] > df["RSI"].iloc[i-LOOKBACK]:
            df.loc[df.index[i], "BullDiv"] = True

    return df

# ================================
# SCORING
# ================================
def calculate_score(curr, prev, signal_type, trend):

    score = 0

    if signal_type == "SELL" and trend == "UP":
        score += 2
    if signal_type == "BUY" and trend == "DOWN":
        score += 2

    if curr["RSI"] > 65 or curr["RSI"] < 35:
        score += 2

    if curr["BearDiv"] or curr["BullDiv"]:
        score += 2

    body_curr = abs(curr["CLOSE"] - curr["OPEN"])
    body_prev = abs(prev["CLOSE"] - prev["OPEN"])

    score += 2 if body_curr > body_prev else 1

    return score

# ================================
# LOAD SYMBOLS
# ================================
symbols = pd.read_csv(FNO_FILE)["SYMBOL"].astype(str).str.upper().tolist()

results = []
checked = 0
all_dates = []

# ================================
# PROCESS
# ================================
for symbol in symbols:

    file = EQUITY_DIR / f"{symbol}.csv"
    if not file.exists():
        continue

    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.upper()

        df = df.rename(columns={"TOTTRDQTY": "VOLUME"})

        df["DATE"] = pd.to_datetime(df["DATE"], format="mixed", errors="coerce")
        df = df.dropna(subset=["DATE"]).sort_values("DATE").reset_index(drop=True)

        if len(df) < 50:
            continue

        df = calculate_rsi(df)
        df = detect_div(df)

        df["EMA50"] = df["CLOSE"].ewm(span=50).mean()
        df["Trend"] = df["CLOSE"] > df["EMA50"]

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        checked += 1
        all_dates.append(curr["DATE"])

        def body_ratio(c):
            rng = c["HIGH"] - c["LOW"]
            return abs(c["CLOSE"] - c["OPEN"]) / rng if rng > 0 else 0

        if body_ratio(prev) < MIN_BODY_RATIO or body_ratio(curr) < MIN_BODY_RATIO:
            continue

        bear_engulf = (
            prev["CLOSE"] > prev["OPEN"] and
            curr["CLOSE"] < curr["OPEN"] and
            curr["OPEN"] > prev["CLOSE"] and
            curr["CLOSE"] < prev["OPEN"]
        )

        bull_engulf = (
            prev["CLOSE"] < prev["OPEN"] and
            curr["CLOSE"] > curr["OPEN"] and
            curr["CLOSE"] > prev["OPEN"] and
            curr["OPEN"] < prev["CLOSE"]
        )

        if not (bear_engulf or bull_engulf):
            continue

        trend_label = "UP" if curr["Trend"] else "DOWN"
        signal_type = "SELL" if bear_engulf else "BUY"

        score = calculate_score(curr, prev, signal_type, trend_label)

        results.append({
            "Symbol": symbol,
            "Date": curr["DATE"].strftime("%Y-%m-%d"),
            "Close": round(curr["CLOSE"], 2),
            "RSI": round(curr["RSI"], 2),
            "Engulf": "YES",
            "Div": "YES" if (curr["BearDiv"] or curr["BullDiv"]) else "NO",
            "Trend": trend_label,
            "Type": signal_type,
            "Strength": "STRONG" if score >= 6 else "NORMAL",
            "Score": score
        })

    except Exception as e:
        console.print(f"[red]Error {symbol}: {e}[/red]")

# ================================
# OUTPUT
# ================================
df_out = pd.DataFrame(results)

console.rule("[bold cyan]SMART ENGINE[/bold cyan]")
console.print(f"Checked: {checked}")
console.print(f"Signals: {len(results)}")

if not df_out.empty:

    df_out = df_out.sort_values("Score", ascending=False)

    # 🔥 FINAL SMART FILTER
    high_prob = df_out[
        (df_out["Score"] >= 6) &
        (
            (
                (df_out["Type"] == "SELL") &
                (df_out["Trend"] == "UP") &
                (df_out["RSI"] >= 65) &
                ((df_out["Div"] == "YES") | (df_out["RSI"] >= 70))
            )
            |
            (
                (df_out["Type"] == "BUY") &
                (df_out["Trend"] == "DOWN") &
                (df_out["RSI"] <= 35) &
                ((df_out["Div"] == "YES") | (df_out["RSI"] <= 30))
            )
        )
    ]

    low_prob = df_out[~df_out.index.isin(high_prob.index)]

    # HIGH TABLE
    if not high_prob.empty:
        table1 = Table(title="🔥 HIGH PROBABILITY TRADES")
        for col in high_prob.columns:
            table1.add_column(col, justify="center")

        for _, row in high_prob.iterrows():
            color = "green" if row["Type"] == "BUY" else "red"
            table1.add_row(*[f"[{color}]{str(v)}[/{color}]" for v in row.values])

        console.print(table1)

    # LOW TABLE
    if not low_prob.empty:
        table2 = Table(title="⚠️ LOW QUALITY (IGNORE)")
        for col in low_prob.columns:
            table2.add_column(col, justify="center")

        for _, row in low_prob.iterrows():
            table2.add_row(*[str(v) for v in row.values])

        console.print(table2)

    final_date = max(all_dates).strftime("%Y-%m-%d")
    df_out.to_csv(OUT_DIR / f"final_signals_{final_date}.csv", index=False)

else:
    console.print("[yellow]No signals found[/yellow]")