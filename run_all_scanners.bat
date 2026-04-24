@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ======================================
echo   CANDLE-LAB MASTER PIPELINE STARTED
echo ======================================

set start=%time%

REM ======================================
REM ACTIVATE PYTHON (OPTIONAL IF NEEDED)
REM ======================================
call C:\Users\Harshal\anaconda3\Scripts\activate.bat base

REM ======================================
REM SETUP
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
cd /d H:\CANDLE-LAB\scanners\pcr_options
python 01_pcr_engine.py

REM ======================================
REM ADX
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
cd /d H:\CANDLE-LAB\scanners\engulfing_candle
python 01_bullish_engulfing.py
python 02_bearish_engulfing.py

REM ======================================
REM VOLUME
REM ======================================
echo.
echo [VOLUME GREEN]
cd /d H:\CANDLE-LAB\scanners\green_candle_fourday
python 01_4day_green_priceup_volume_rising.py

echo.
echo [VOLUME RED]
cd /d H:\CANDLE-LAB\scanners\red_candle_fourday
python 01_4day_red_priceup_volume_rising.py

REM ======================================
REM CANDLE PATTERNS
REM ======================================
echo.
echo [GRAVESTONE]
cd /d H:\CANDLE-LAB\scanners\gravestone_candle
python 01_gravestone_doji_in_uptrend.py

echo.
echo [HAMMER]
cd /d H:\CANDLE-LAB\scanners\hammer
python hammer_confirmation.py

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
echo [INSIDE BAR]
cd /d H:\CANDLE-LAB\scanners\inside_bar
python inside_bar_scan.py

echo.
echo [NR7]
cd /d H:\CANDLE-LAB\scanners\nr7
python nr7_scan.py

echo.
echo [VWAP]
cd /d H:\CANDLE-LAB\scanners\vwap
python 01_vwap_scan.py

echo.
echo [DOJI]
cd /d H:\CANDLE-LAB\scanners\doji
python 01_doji_scan.py

echo.
echo [LONG LEG DOJI]
cd /d H:\CANDLE-LAB\scanners\long_leg_doji
python 01_long_leg_doji.py

echo.
echo [VOLUME SCAN]
cd /d H:\CANDLE-LAB\scanners\volume
python 01_volume_scan.py

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
REM MORNING / EVENING
REM ======================================
echo.
echo [MORNING STAR]
cd /d H:\CANDLE-LAB\scanners\morning_evening_star
python 01_morning_star_scanner.py

echo.
echo [EVENING STAR]
python 02_evening_star_scanner.py

REM ======================================
REM 🔥 SMART MONEY ENGINE
REM ======================================
echo.
echo [SMART MONEY ENGINE]
cd /d H:\CANDLE-LAB\engines\smart_money_engine
python smart_money_engine.py || goto :error

REM ======================================
REM MASTER ENGINE
REM ======================================
echo.
echo [MASTER ENGINE]
cd /d H:\CANDLE-LAB\engines\master_engine
python master_engine.py || goto :error

REM ======================================
REM FILTER ENGINE
REM ======================================
echo.
echo [FILTER ENGINE]
cd /d H:\CANDLE-LAB\engines
echo Running from: %cd%
python filter_engine.py || goto :error

REM ======================================
REM END
REM ======================================
echo.
echo ======================================
echo   FULL PIPELINE COMPLETED ✅
echo ======================================

set end=%time%
echo Started at: %start%
echo Ended at  : %end%

pause
exit /b 0

REM ======================================
REM ERROR HANDLER
REM ======================================
:error
echo.
echo ❌ PIPELINE FAILED
echo Check above step for error
pause
exit /b 1