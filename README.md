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
  * `gravestone_candle/` → exhaustion signals

* **Structure / Compression**

  * `nr7/` → volatility contraction (breakout setup)
  * `inside_bar/` → consolidation zones
  * `harami/` → pause before expansion

* **Momentum Indicators**

  * `rsi/` → overbought / oversold detection

* **Pattern Recognition**

  * `price_action/engulfing/` → strong directional candles (moved from `engulfing_candle`)

---

### 3. Analysis Layer (`analysis/equity/`)

* `last_row/` → processed base datasets
* `signals/` → individual scanner outputs (daily signals by pattern type)
* `master/` → unified master_trades with all scoring metrics
* `filtered/` → high-quality filtered_trades (ADX + candle confirmation)
* `consolidated/` → **NEW** unified ranked output combining filtered + master trades

---

### 4. Ranking & Consolidation Engine (`engines/consolidation_engine.py`)

**Purpose**: Merge filtered and master trades into single prioritized output

**Output Structure** (`consolidated_analysis_YYYY-MM-DD.csv`):
- **RANK**: Opportunity ranking
- **SYMBOL**: Stock symbol
- **SOURCE**: FILTERED (priority 1) or MASTER (priority 2)
- **FINAL_SCORE**: Composite score (0.0-1.0)
- **DIRECTION**: LONG or SHORT bias
- Additional metrics from source files

**Priority Logic**:
1. Filtered trades listed first (higher quality - ADX trending + candle confirmed)
2. Master trades added after (broader coverage, lower barrier)
3. Sorted by FINAL_SCORE descending within each tier

---

### 5. Execution Pipeline

Run via:

```bash
run_all_scanners.bat
```

Flow:

```text
Setup 
  ↓
Scanners (30+ pattern engines) 
  ↓
Signal Files (individual pattern outputs)
  ↓
Smart Money Engine (scoring)
  ↓
Master Engine (unified trades)
  ↓
Filter Engine (ADX + candle confirmation)
  ↓
Consolidation Engine (FINAL RANKED OUTPUT)
```

**Final Output Locations**:
- ✅ **Primary**: `analysis/equity/consolidated/consolidated_analysis_YYYY-MM-DD.csv` (unified ranked)
- `analysis/equity/filtered/filtered_trades_YYYY-MM-DD.csv` (high-quality only)
- `analysis/equity/master/master_trades_YYYY-MM-DD.csv` (all opportunities)

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
