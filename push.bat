@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Push sharing_go to GitHub

cd /d "%~dp0"

set "REPO_URL=https://github.com/iot-superman/sharing_go.git"
set "BRANCH=main"

echo.
echo ============================================================
echo   Push current project to GitHub
echo   %REPO_URL%
echo ============================================================
echo.

where git >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Git was not found in PATH.
    echo Install Git for Windows first:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

git --version
echo.

if not exist ".git" (
    echo [INFO] Initializing Git repository...
    git init
    if errorlevel 1 goto :FAIL
)

git branch -M %BRANCH%
if errorlevel 1 goto :FAIL

git remote get-url origin >nul 2>nul
if errorlevel 1 (
    echo [INFO] Adding origin...
    git remote add origin "%REPO_URL%"
    if errorlevel 1 goto :FAIL
) else (
    for /f "delims=" %%R in ('git remote get-url origin') do set "CURRENT_ORIGIN=%%R"
    echo [INFO] Current origin: !CURRENT_ORIGIN!
    if /I not "!CURRENT_ORIGIN!"=="%REPO_URL%" (
        echo [INFO] Updating origin...
        git remote set-url origin "%REPO_URL%"
        if errorlevel 1 goto :FAIL
    )
)

echo.
echo [INFO] Checking remote main branch...
git ls-remote --exit-code --heads origin %BRANCH% >nul 2>nul
if not errorlevel 1 (
    echo [INFO] Remote main exists. Fetching...
    git fetch origin %BRANCH%
    if errorlevel 1 goto :FAIL

    git rev-parse --verify HEAD >nul 2>nul
    if not errorlevel 1 (
        echo [INFO] Rebasing local commits on origin/%BRANCH% ...
        git pull --rebase origin %BRANCH%
        if errorlevel 1 (
            echo.
            echo [ERROR] Rebase failed or has conflicts.
            echo Resolve conflicts, then run push.bat again.
            echo.
            pause
            exit /b 1
        )
    )
) else (
    echo [INFO] Remote main does not exist yet. First push will create it.
)

echo.
echo [INFO] Staging all files...
git add -A
if errorlevel 1 goto :FAIL

echo.
git status --short
echo.

git diff --cached --quiet
if not errorlevel 1 goto :PUSH_ONLY

set "COMMIT_MSG="
set /p "COMMIT_MSG=Commit message [Update sharing_go]: "
if not defined COMMIT_MSG set "COMMIT_MSG=Update sharing_go"

git commit -m "%COMMIT_MSG%"
if errorlevel 1 goto :FAIL

:PUSH_ONLY
echo.
echo [INFO] Pushing to GitHub...
git push -u origin %BRANCH%
if errorlevel 1 goto :FAIL

echo.
echo ============================================================
echo [SUCCESS] Push completed.
echo https://github.com/iot-superman/sharing_go
echo ============================================================
echo.
pause
exit /b 0

:FAIL
echo.
echo ============================================================
echo [ERROR] Push failed.
echo No force push was used.
echo ============================================================
echo.
pause
exit /b 1
