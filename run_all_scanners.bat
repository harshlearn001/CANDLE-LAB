@echo off

echo ======================================
echo   CANDLE-LAB MASTER PIPELINE STARTED
echo ======================================

call conda activate TradeSense

REM ======================================
REM SETUP (VERY IMPORTANT FIRST)
REM ======================================
echo.
echo [SETUP]
cd /d H:\CANDLE-LAB\scanners\setup
python 00_build_fno_symbol_list.py
python 01_extract_last_row_equity.py

REM ======================================
REM PCR ENGINE
REM ======================================
echo.
echo [PCR ENGINE]
cd /d H:\CANDLE-LAB\scanners\pcr_day
python 01_append_to_pcr_history_STOCKS_AND_INDICES.py
python 04_scan_pcr_rise_above_point_8_stocks_indices.py
python 03_check_last_5_pcr.py

REM ======================================
REM TREND STRENGTH (ADX 🔥)
REM ======================================
echo.
echo [ADX]
cd /d H:\CANDLE-LAB\scanners\adx
python 01_adx_scan.py

REM ======================================
REM ENGULFING
REM ======================================
echo.
echo [ENGULFING]
cd /d H:\CANDLE-LAB\scanners\engulfing_candle_1
python 01_bullish_engulfing_exact.py
python 02_bearish_engulfing_exact.py

REM ======================================
REM VOLUME
REM ======================================
echo.
echo [VOLUME GREEN]
cd /d H:\CANDLE-LAB\scanners\green_candle_fourday
python 01_4day_green_volume_rising_ok.py

echo.
echo [VOLUME RED]
cd /d H:\CANDLE-LAB\scanners\red_candle_fourday
python 01_4day_red_volume_rising_ok.py

REM ======================================
REM CANDLE PATTERNS
REM ======================================
echo.
echo [GRAVESTONE]
cd /d H:\CANDLE-LAB\scanners\grevystone_candle
python 02_gravestone_doji_in_uptrend.py

echo.
echo [HAMMER]
cd /d H:\CANDLE-LAB\scanners\Hammer
python step_07_detect_hammer.py

echo.
echo [SHOOTING STAR]
cd /d H:\CANDLE-LAB\scanners\shooting_star
python 01_shooting_star_uptrend.py

echo.
echo [HANGING MAN]
cd /d H:\CANDLE-LAB\scanners\hangingman
python 01_hanging_man_scan.py

echo.
echo [HARAMI]
cd /d H:\CANDLE-LAB\scanners\harami
python 01_harami_scan.py

echo.
echo [NR7]
cd /d H:\CANDLE-LAB\scanners\nr7
python fno_nr7_scan.py

REM ======================================
REM MOMENTUM
REM ======================================
echo.
echo [RSI]
cd /d H:\CANDLE-LAB\scanners\rsi
python 01_rsi_scan.py

echo.
echo [RSI DIVERGENCE]
cd /d H:\CANDLE-LAB\scanners\rsi_divergence
python 02_rsi_divergence_scan.py

REM ======================================
REM PATTERN CONFIRMATION
REM ======================================
echo.
echo [MORNING / EVENING STAR]
cd /d H:\CANDLE-LAB\scanners\morningstar
python 01_morning_star_scanner.py
python 02_evening_star_uptrend.py

echo.
echo ======================================
echo   ALL SCANNERS COMPLETED ✅
echo ======================================

pause