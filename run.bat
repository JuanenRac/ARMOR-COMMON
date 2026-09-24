@echo off
REM A.R.M.O.R. runtime launcher. GPL-3.0-or-later.
call "%~dp0scripts\armor-project.bat" run "%~dp0."
exit /b %ERRORLEVEL%
