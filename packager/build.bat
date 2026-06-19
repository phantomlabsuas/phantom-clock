@echo off
rem Wrapper — calls build.ps1 which handles special chars in paths correctly
rem Usage: build.bat            (no console window)
rem        build.bat --console  (with console window)

set EXTRA=
if "%~1"=="--console" set EXTRA=-Console

powershell -ExecutionPolicy Bypass -File "%~dp0build.ps1" %EXTRA%
pause
