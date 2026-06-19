@echo off
taskkill /F /IM phantom-clock.exe >nul 2>&1
if %errorlevel%==0 (
    echo Phantom Clock stopped.
) else (
    echo Phantom Clock was not running.
)
