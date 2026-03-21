# CANDLE-LAB

## **Purpose**

F&O-only equity scanning system for NSE based on **price action, volume, and market structure**.
Designed to identify **high-probability trading setups with minimal noise**.

---

## **System Architecture**

### 1. Setup Engine (`scanners/setup/`)

* Build F&O universe dynamically
* Extract and maintain latest OHLC data
* Prepare base datasets for all scanners

---

### 2. Scanner Engine (`scanners/`)

Modular signal generators based on different market behaviors:

* **Momentum (Volume-Based)**

  * `green_candle_fourday/` → bullish continuation
  * `red_candle_fourday/` → bearish continuation

* **Reversal (Price Action)**

  * `Hammer/` → bottom reversal
  * `shooting_star/` → top rejection
  * `grevystone_candle/` → exhaustion signals

* **Structure / Compression**

  * `nr7/` → volatility contraction (breakout setup)
  * `inside_bar/` → consolidation zones
  * `harami/` → pause before expansion

* **Momentum Indicators**

  * `rsi/` → overbought / oversold detection

* **Pattern Recognition**

  * `engulfing_candle_1/` → strong directional candles

---

### 3. Analysis Layer (`analysis/`)

* `last_row/` → processed base datasets
* `signals/` → scanner outputs (daily signals)

---

### 4. Execution Pipeline

Run via:

```bash
run_all_scanners.bat
```

Flow:

```text
Setup → Scanners → Signal Files
```

---

## **Philosophy**

* Price leads everything
* Volume confirms intent
* Structure defines opportunity

Focus:

```text
Low Noise → High Conviction → Tradeable Signals
```

---

## **Next Evolution (Planned)**

* Master Signal Engine (multi-factor signal fusion)
* Signal ranking & scoring system
* Streamlit dashboard for monitoring
* Automated alerts (Zerodha API integration)

---

## **Author Vision**

Build a **modular, scalable, AI-assisted trading system**
focused on disciplined, rule-based decision making.
