@echo off
echo ===============================
echo  CANDLE-LAB DAILY RUN STARTED
echo ===============================

call conda activate tradesense

REM ============================================
REM SETUP
REM ============================================
cd /d H:\CANDLE-LAB\scanners\setup
python 00_build_fno_symbol_list.py
python 01_extract_last_row_equity.py

REM ============================================
REM ENGULFING
REM ============================================
cd /d H:\CANDLE-LAB\scanners\engulfing_candle_1
python 01_bullish_engulfing_exact.py
python 02_bearish_engulfing_exact.py

REM ============================================
REM VOLUME (GREEN)
REM ============================================
cd /d H:\CANDLE-LAB\scanners\green_candle_fourday
python 01_4day_green_volume_rising_ok.py
python 00_4day_green_volume_confirmed.py

REM ============================================
REM VOLUME (RED)
REM ============================================
cd /d H:\CANDLE-LAB\scanners\red_candle_fourday
python 01_4day_red_volume_rising_ok.py
python 02_4day_red_volume_confirmed.py

REM ============================================
REM GRAVESTONE
REM ============================================
cd /d H:\CANDLE-LAB\scanners\grevystone_candle
python 01_gravestone_doji_in_uptrend.py

REM ============================================
REM HAMMER
REM ============================================
cd /d H:\CANDLE-LAB\scanners\Hammer
python step_07_detect_hammer.py

REM ============================================
REM SHOOTING STAR
REM ============================================
cd /d H:\CANDLE-LAB\scanners\shooting_star
python 01_shooting_star_uptrend.py

REM ============================================
REM HARAMI
REM ============================================
cd /d H:\CANDLE-LAB\scanners\harami
python 01_harami_scan.py

REM ============================================
REM NR7
REM ============================================
cd /d H:\CANDLE-LAB\scanners\nr7
python fno_nr7_scan.py

REM ============================================
REM RSI
REM ============================================
cd /d H:\CANDLE-LAB\scanners\rsi
python 01_rsi_scan.py

echo ===============================
echo  ALL SCANNERS COMPLETED
echo ===============================

pause