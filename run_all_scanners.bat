@echo off
setlocal enabledelayedexpansion

echo ======================================
echo   CANDLE-LAB MASTER PIPELINE STARTED
echo ======================================

REM Track time
set start=%time%

REM ======================================
REM SETUP
REM ======================================
echo.
echo [SETUP]
cd /d H:\CANDLE-LAB\scanners\setup
call python 00_build_fno_symbol_list.py
call python 01_extract_last_row_equity.py

REM ======================================
REM PCR ENGINE
REM ======================================
echo.
echo [PCR ENGINE]
cd /d H:\CANDLE-LAB\scanners\pcr_options
call python 01_pcr_engine.py

REM ======================================
REM ADX
REM ======================================
echo.
echo [ADX]
cd /d H:\CANDLE-LAB\scanners\adx
call python 01_adx_scan.py

REM ======================================
REM ENGULFING
REM ======================================
echo.
echo [ENGULFING]
cd /d H:\CANDLE-LAB\scanners\engulfing_candle
call python 01_bullish_engulfing.py
call python 02_bearish_engulfing.py

REM ======================================
REM VOLUME
REM ======================================
echo.
echo [VOLUME GREEN]
cd /d H:\CANDLE-LAB\scanners\green_candle_fourday
call python 01_4day_green_priceup_volume_rising.py

echo.
echo [VOLUME RED]
cd /d H:\CANDLE-LAB\scanners\red_candle_fourday
call python 01_4day_red_priceup_volume_rising.py

REM ======================================
REM CANDLE PATTERNS
REM ======================================
echo.
echo [GRAVESTONE]
cd /d H:\CANDLE-LAB\scanners\gravestone_candle
call python 01_gravestone_doji_in_uptrend.py

echo.
echo [HAMMER]
cd /d H:\CANDLE-LAB\scanners\hammer
call python hammer_confirmation.py

echo.
echo [SHOOTING STAR]
cd /d H:\CANDLE-LAB\scanners\shooting_star
call python 01_shooting_star_uptrend.py

echo.
echo [HANGING MAN]
cd /d H:\CANDLE-LAB\scanners\hangingman
call python 01_hanging_man_scan.py

echo.
echo [HARAMI]
cd /d H:\CANDLE-LAB\scanners\harami
call python 01_harami_scan.py

echo.
echo [INSIDE BAR]
cd /d H:\CANDLE-LAB\scanners\inside_bar
call python inside_bar_scan.py

echo.
echo [NR7]
cd /d H:\CANDLE-LAB\scanners\nr7
call python nr7_scan.py

REM ======================================
REM MOMENTUM
REM ======================================
echo.
echo [RSI]
cd /d H:\CANDLE-LAB\scanners\rsi
call python 01_rsi_scan.py

echo.
echo [RSI DIVERGENCE]
cd /d H:\CANDLE-LAB\scanners\rsi_divergence
call python 02_rsi_divergence_scan.py

REM ======================================
REM MORNING / EVENING
REM ======================================
echo.
echo [MORNING STAR]
cd /d H:\CANDLE-LAB\scanners\morning_evening_star
call python 01_morning_star_scanner.py

echo.
echo [EVENING STAR]
call python 02_evening_star_scanner.py

REM ======================================
REM END
REM ======================================
echo.
echo ======================================
echo   ALL SCANNERS COMPLETED ✅
echo ======================================

REM Time taken
set end=%time%
echo Started at: %start%
echo Ended at  : %end%

pause