@echo off
title NBU Platform — Servers
echo Starting NBU Platform...
echo.

:: Kill any existing processes on ports 8001 and 5173
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8001"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5173"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 1 >nul

:: Start Backend
start "NBU Backend :8001" cmd /k "cd /d "%~dp0backend" && C:\Users\mukha\AppData\Local\Programs\Python\Python310\python.exe -m uvicorn app.main:app --port 8001"

:: Wait for backend to start
timeout /t 4 >nul

:: Start Frontend
start "NBU Frontend :5173" cmd /k "cd /d "%~dp0frontend" && set PATH=C:\Program Files\nodejs;%PATH% && npm run dev"

echo.
echo Both servers starting...
echo  Backend:  http://localhost:8001
echo  Frontend: http://localhost:5173
echo.
timeout /t 6 >nul
start http://localhost:5173
