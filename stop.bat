@echo off
set killed=0

taskkill /F /IM phantom-clock.exe >nul 2>&1
if %errorlevel%==0 set killed=1

powershell -NoProfile -Command ^
  "$p = Get-CimInstance Win32_Process -Filter 'name=''python.exe''' | Where-Object { $_.CommandLine -like '*phantom_clock*' }; if ($p) { $p | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }; exit 0 } else { exit 1 }" >nul 2>&1
if %errorlevel%==0 set killed=1

if "%killed%"=="1" (
    echo Phantom Clock stopped.
) else (
    echo Phantom Clock was not running.
)
