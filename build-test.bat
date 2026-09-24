@echo off
REM A.R.M.O.R. non-mutating build verification launcher. GPL-3.0-or-later.
call "%~dp0scripts\armor-project.bat" build-test "%~dp0."
exit /b %ERRORLEVEL%
