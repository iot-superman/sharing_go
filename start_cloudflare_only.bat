@echo off
setlocal
title Cloudflare Quick Tunnel - Carpool Go

set "CLOUDFLARED="

where cloudflared >nul 2>nul
if not errorlevel 1 set "CLOUDFLARED=cloudflared"
if not defined CLOUDFLARED if exist "%ProgramFiles%\cloudflared\cloudflared.exe" set "CLOUDFLARED=%ProgramFiles%\cloudflared\cloudflared.exe"
if not defined CLOUDFLARED if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" set "CLOUDFLARED=%ProgramFiles(x86)%\cloudflared\cloudflared.exe"

if not defined CLOUDFLARED (
    echo [ERROR] cloudflared was not found.
    echo Run start_windows_cloudflare.bat first.
    pause
    exit /b 1
)

echo.
echo Django must already be running at:
echo http://127.0.0.1:8000
echo.
echo Starting Quick Tunnel...
echo Copy the generated https://xxxxx.trycloudflare.com URL.
echo.
"%CLOUDFLARED%" tunnel --url http://127.0.0.1:8000
pause
endlocal
