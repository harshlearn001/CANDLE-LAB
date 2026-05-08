@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ======================================
REM FORCE AUTO MODE DEFAULT
REM ======================================
if "%AUTO_MODE%"=="" set AUTO_MODE=1

REM ======================================
REM PAUSE CONTROL (SAFE)
REM ======================================
if "%AUTO_MODE%"=="1" (
    set PAUSE_CMD=timeout /t 3 >nul
) else (
    set PAUSE_CMD=pause
)

REM ======================================
REM PYTHON PATH
REM ======================================
set PYTHON=C:\Users\Harshal\anaconda3\python.exe

echo ======================================
echo   CANDLE-LAB MASTER PIPELINE STARTED
echo ======================================

echo Running from: %cd%
echo Python: %PYTHON%

set start=%time%

REM ======================================
REM SETUP
REM ======================================
cd /d H:\CANDLE-LAB\scanners\setup
if not exist 00_build_fno_symbol_list.py goto :error
%PYTHON% 00_build_fno_symbol_list.py || goto :error

if not exist 01_extract_last_row_equity.py goto :error
%PYTHON% 01_extract_last_row_equity.py || goto :error

REM ======================================
REM CORE SCANNERS (ALPHABETICAL ORDER)
REM ======================================

echo.
echo ==============================
echo   RUNNING SCANNERS (A → Z)
echo ==============================
echo Total scanners running...
cd /d H:\CANDLE-LAB\scanners

REM ===== A =====
cd adx
%PYTHON% 01_adx_scan.py || goto :error

REM ===== B =====
cd ..\breadth
%PYTHON% 01_breadth_scan.py || goto :error

REM ===== D =====
cd ..\doji
%PYTHON% 01_doji_scan.py || goto :error

REM ===== E =====
cd ..\engulfing_candle
%PYTHON% 01_bullish_engulfing.py || goto :error
%PYTHON% 02_bearish_engulfing.py || goto :error

REM ===== G =====
cd ..\gravestone_candle
%PYTHON% 01_gravestone_doji_in_uptrend.py || goto :error

cd ..\gravestone_candle_stick
%PYTHON% 01_gravestone_candle_stick.py || goto :error

cd ..\green_candle_fourday
%PYTHON% 01_4day_green_priceup_volume_rising.py || goto :error

REM ===== H =====
cd ..\hammer
%PYTHON% hammer_confirmation.py || goto :error

cd ..\hangingman
%PYTHON% 01_hanging_man_scan.py || goto :error

cd ..\harami
%PYTHON% 01_harami_scan.py || goto :error

REM ===== I =====
cd ..\inside_bar
%PYTHON% inside_bar_scan.py || goto :error

REM ===== L =====
cd ..\long_leg_doji
%PYTHON% 01_long_leg_doji.py || goto :error

REM ===== M =====
cd ..\marubozu
%PYTHON% 01_marubozu_bullish_bearish.py || goto :error

cd ..\marubozu_tolerance_scaner
%PYTHON% 01_marubozu_tolerance_scaner.py || goto :error

cd ..\morning_evening_star
%PYTHON% 01_morning_star_scanner.py || goto :error
%PYTHON% 02_evening_star_scanner.py || goto :error

REM ===== N =====
cd ..\nr7
%PYTHON% nr7_scan.py || goto :error

REM ===== O =====
cd ..\open_high_low
%PYTHON% 01_open_high_low_scanner.py || goto :error

REM ===== P =====
cd ..\pcr_options
%PYTHON% 01_pcr_engine.py || goto :error

REM ===== R =====
cd ..\red_candle_fourday
%PYTHON% 01_4day_red_priceup_volume_rising.py || goto :error

cd ..\rsi
%PYTHON% 01_rsi_scan.py || goto :error

cd ..\rsi_divergence
%PYTHON% 02_rsi_divergence_scan.py || goto :error

REM ===== S =====
cd ..\shooting_star
%PYTHON% 01_shooting_star_uptrend.py || goto :error

REM ===== V =====
cd ..\volume
%PYTHON% 01_volume_scan.py || goto :error

cd ..\vwap
%PYTHON% 01_vwap_scan.py || goto :error

REM ======================================
REM ENGINES
REM ======================================

cd /d H:\CANDLE-LAB\engines\smart_money_engine
%PYTHON% smart_money_engine.py || goto :error

cd /d H:\CANDLE-LAB\engines\master_engine
%PYTHON% master_engine.py || goto :error

cd /d H:\CANDLE-LAB\engines
%PYTHON% filter_engine.py || goto :error

REM ======================================
REM END
REM ======================================

echo.
echo ======================================
echo   FULL PIPELINE COMPLETED
echo ======================================

set end=%time%
echo Started at: %start%
echo Ended at  : %end%

%PAUSE_CMD%
exit /b 0

REM ======================================
REM ERROR HANDLER
REM ======================================
:error
echo.
echo ERROR: PIPELINE FAILED
echo Check above step

%PAUSE_CMD%
exit /b 1