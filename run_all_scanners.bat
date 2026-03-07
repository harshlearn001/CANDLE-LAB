@echo off
echo ===============================
echo  CANDLE-LAB DAILY RUN STARTED
echo ===============================

call conda activate tradesense

REM ---------- BUILD F&O LIST ----------
cd /d H:\CANDLE-LAB\scanners\setup
python 00_build_fno_symbol_list.py
python 01_extract_last_row_equity.py


REM ---------- ENGULFING ----------
cd /d H:\CANDLE-LAB\scanners\engulfing_candle_1
python 01_bullish_engulfing_exact.py
python 02_bearish_engulfing_exact.py


REM ---------- 4 DAY GREEN ----------
cd /d H:\CANDLE-LAB\scanners\green_candle_fourday
python 01_4day_green_volume_rising_ok.py
python 00_4day_green_volume_confirmed.py


REM ---------- 4 DAY RED ----------
cd /d H:\CANDLE-LAB\scanners\red_candle_fourday
python 01_4day_red_volume_rising_ok.py
python 02_4day_red_volume_confirmed.py


REM ---------- GRAVESTONE ----------
cd /d H:\CANDLE-LAB\scanners\grevystone_candle
python 01_gravestone_doji_in_uptrend.py


REM ---------- HAMMER ----------
cd /d H:\CANDLE-LAB\scanners\Hammer
python step_07_detect_hammer.py


echo ===============================
echo  ALL SCANNERS COMPLETED
echo ===============================

REM pause