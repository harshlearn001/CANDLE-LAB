CANDLE-LAB
==========

Purpose:
--------
F&O-only candle-based equity scanner for NSE.

Pipeline:
---------
1. setup/
   - Build F&O universe
   - Prepare equity last rows

2. scanners/
   - green_volume/ : bullish momentum scans
   - red_candle/   : bearish momentum scans

3. analysis/
   - last_row/ : derived base datasets
   - signals/  : final trade candidates

Philosophy:
-----------
Price + Volume + Structure
Low noise, high conviction.
