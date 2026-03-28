import pandas as pd
from pathlib import Path
from datetime import datetime

print("🌇 EVENING STAR SCANNER (FNO) 🔥\n")

# ==============================
# PATHS (YOUR STANDARD)
# ==============================
EQUITY_DIR = Path(r"H:\MarketForge\data\master\Equity_stock_master")
FNO_FILE   = Path(r"H:\CANDLE-LAB\config\fno_symbols.csv")

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\equity\signals\evening_star")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"fno_evening_star_{today}.csv"

# ==============================
# LOAD FNO SYMBOLS
# ==============================
fno = pd.read_csv(FNO_FILE)

# 🔥 AUTO DETECT SYMBOL COLUMN
possible_cols = ["Symbol", "symbol", "SYMBOL", "tradingsymbol"]

symbol_col = None
for col in possible_cols:
    if col in fno.columns:
        symbol_col = col
        break

if symbol_col is None:
    raise ValueError(f"❌ No valid symbol column found. Columns: {fno.columns}")

print(f"📊 Using symbol column: {symbol_col}")

symbols = fno[symbol_col].dropna().unique()

results = []

# ==============================
# SCAN
# ==============================
for sym in symbols:
    file_path = EQUITY_DIR / f"{sym}.csv"

    if not file_path.exists():
        continue

    try:
        df = pd.read_csv(file_path)

        if len(df) < 3:
            continue

        df = df.tail(3)

        c1, c2, c3 = df.iloc[0], df.iloc[1], df.iloc[2]

        # Evening Star Logic
        cond1 = c1["close"] > c1["open"]

        body2 = abs(c2["close"] - c2["open"])
        range2 = c2["high"] - c2["low"]
        cond2 = body2 < (0.3 * range2)

        cond3 = (
            c3["close"] < c3["open"] and
            c3["close"] < (c1["open"] + c1["close"]) / 2
        )

        if cond1 and cond2 and cond3:
            print(f"🌇 {sym}")
            results.append({
                "Symbol": sym,
                "Pattern": "Evening Star"
            })

    except Exception as e:
        continue

# ==============================
# SAVE
# ==============================
pd.DataFrame(results).to_csv(OUT_FILE, index=False)

print(f"\n✅ FOUND: {len(results)}")
print(f"📁 Saved → {OUT_FILE}")