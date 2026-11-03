@echo off
:: =============================================================================
:: FaceForge - Single Command Launcher
:: Contributed by: Member 4 (System Integration, UI, Storage & Analytics)
:: Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur
::
:: Automatically launches the Python FastAPI server and opens the browser
:: =============================================================================
title FaceForge Application Server (Group G2 - Final Year Project)
cd /d "%~dp0"
echo ======================================================================
echo    FaceForge - Facial Emotion Recognition System
echo    B.Tech Final Year Project - Group G2 (IT) - SKIT Jaipur
echo ======================================================================
echo.
echo Starting FaceForge backend server on http://127.0.0.1:8000 ...
echo Opening your browser to FaceForge Dashboard...
echo.
start "" "http://127.0.0.1:8000"

if exist ".\.venv\Scripts\python.exe" (
    .\.venv\Scripts\python.exe app.py
) else (
    python app.py
)
pause
