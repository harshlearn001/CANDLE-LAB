import pandas as pd
import os
from datetime import datetime

print("\nINSIDE BAR SCANNER STARTED\n")

symbols_file = r"H:\CANDLE-LAB\config\fno_symbols.csv"
data_dir = r"H:\MarketForge\data\master\Equity_stock_master"

today_date = str(datetime.today().date())

output_file = rf"H:\CANDLE-LAB\analysis\equity\signals\inside_bar\fno_inside_bar_{today_date}.csv"

# Automatically create folder if missing
os.makedirs(os.path.dirname(output_file), exist_ok=True)

symbols = pd.read_csv(symbols_file)["SYMBOL"].tolist()

results = []

for symbol in symbols:

    file_path = os.path.join(data_dir, f"{symbol}.csv")

    if not os.path.exists(file_path):
        continue

    try:
        df = pd.read_csv(file_path)
    except:
        continue

    if len(df) < 2:
        continue

    today = df.iloc[-1]
    prev = df.iloc[-2]

    if today["HIGH"] < prev["HIGH"] and today["LOW"] > prev["LOW"]:

        print("INSIDE BAR →", symbol)

        results.append({
            "SYMBOL": symbol,
            "DATE": today["DATE"],
            "HIGH": today["HIGH"],
            "LOW": today["LOW"],
            "PREV_HIGH": prev["HIGH"],
            "PREV_LOW": prev["LOW"]
        })

df_out = pd.DataFrame(results)

df_out.to_csv(output_file, index=False)

print("\nINSIDE BAR SCAN COMPLETED")
print("Stocks found:", len(df_out))
print("Saved →", output_file)