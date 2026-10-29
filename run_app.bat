@echo off
setlocal
title Expense Vision - Server Launcher
cd /d "%~dp0"

echo ======================================================================
echo                LAUNCHING EXPENSE VISION SYSTEM
echo ======================================================================
echo.

:: 1. Check & Start FastAPI Backend (Port 8000)
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/3] FastAPI Backend is ALREADY running on http://127.0.0.1:8000/
) else (
    echo [1/3] Starting Python FastAPI Backend Server on port 8000...
    start "Expense Vision - FastAPI Backend" cmd /k "cd /d ""%~dp0"" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
)

:: Brief pause without input redirection issues
timeout /t 2 >nul 2>&1 || ping 127.0.0.1 -n 3 >nul

:: 2. Check & Start React Vite Frontend (Port 5173)
netstat -ano | findstr :5173 | findstr LISTENING >nul 2>&1
if %errorlevel% equ 0 (
    echo [2/3] React Vite Frontend is ALREADY running on http://localhost:5173/
) else (
    echo [2/3] Starting React Vite Frontend Server on port 5173...
    start "Expense Vision - React Frontend" cmd /k "cd /d ""%~dp0"" && npm run dev"
)

:: Brief pause
timeout /t 2 >nul 2>&1 || ping 127.0.0.1 -n 3 >nul

:: 3. Start Telegram Bot Worker
echo [3/3] Starting Telegram Bot Worker...
start "Expense Vision - Telegram Bot" cmd /k "cd /d ""%~dp0"" && python -u backend/telegram_bot.py"

:: Open Dashboard
echo.
echo ======================================================================
echo Expense Vision System is Ready!
echo   - React Dashboard : http://localhost:5173/
echo   - FastAPI Backend : http://127.0.0.1:8000/
echo   - Swagger API Docs: http://127.0.0.1:8000/docs
echo ======================================================================
echo.
start http://localhost:5173/

echo Press any key to close this launcher window (servers will remain running).
pause >nul
