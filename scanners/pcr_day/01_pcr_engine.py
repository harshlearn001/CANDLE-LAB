import pandas as pd
from pathlib import Path
from datetime import datetime

print("📊 PCR ENGINE STARTED 🔥\n")

# ==============================
# PATHS
# ==============================
BASE_DIR = Path(r"H:\MarketForge\data\master\option_master")

INDEX_DIR = BASE_DIR / "INDICES"
STOCK_DIR = BASE_DIR / "STOCKS"

OUT_DIR = Path(r"H:\CANDLE-LAB\analysis\options\pcr")
OUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = OUT_DIR / f"pcr_{today}.csv"

# ==============================
# FUNCTION TO CALCULATE PCR
# ==============================
def calculate_pcr(file_path):

    try:
        if file_path.suffix == ".parquet":
            df = pd.read_parquet(file_path)
        else:
            df = pd.read_csv(file_path)

        if df.empty:
            return None

        # Ensure required columns
        required = ["SYMBOL", "OPT_TYPE", "OPEN_INT"]
        if not all(col in df.columns for col in required):
            return None

        symbol = df["SYMBOL"].iloc[0]

        ce_oi = df[df["OPT_TYPE"] == "CE"]["OPEN_INT"].sum()
        pe_oi = df[df["OPT_TYPE"] == "PE"]["OPEN_INT"].sum()

        if ce_oi == 0:
            return None

        pcr = pe_oi / ce_oi

        # Signal classification
        if pcr > 1.2:
            signal = "BULLISH"
        elif pcr < 0.8:
            signal = "BEARISH"
        else:
            signal = "NEUTRAL"

        return {
            "Symbol": symbol,
            "CE_OI": ce_oi,
            "PE_OI": pe_oi,
            "PCR": round(pcr, 2),
            "Signal": signal
        }

    except Exception as e:
        return None


# ==============================
# SCAN ALL FILES
# ==============================
results = []

all_files = list(INDEX_DIR.glob("*")) + list(STOCK_DIR.glob("*"))

for file in all_files:
    if file.suffix not in [".csv", ".parquet"]:
        continue

    res = calculate_pcr(file)

    if res:
        print(f"{res['Symbol']} → PCR: {res['PCR']} ({res['Signal']})")
        results.append(res)

# ==============================
# SAVE OUTPUT
# ==============================
df_out = pd.DataFrame(results)

df_out = df_out.sort_values("PCR", ascending=False)

df_out.to_csv(OUT_FILE, index=False)

print("\n📊 PCR ENGINE COMPLETED")
print(f"Total symbols: {len(df_out)}")
print(f"Saved → {OUT_FILE}")