@echo off
REM A.R.M.O.R. project incremental release launcher. GPL-3.0-or-later.
call "%~dp0scripts\armor-project.bat" build "%~dp0."
exit /b %ERRORLEVEL%
