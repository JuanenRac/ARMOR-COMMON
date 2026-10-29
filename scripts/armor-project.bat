@echo off
REM *****************************************************************************
REM A.R.M.O.R. - armor-project.bat
REM Standard Windows project workflow launcher.
REM Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
REM GPL-3.0-or-later - see LICENSE
REM *****************************************************************************
setlocal
rem Keep the window open for people, never in automation (CI / HYDRA_UMC_CI).
set "KEEP_OPEN=pause"
if defined CI set "KEEP_OPEN=ver >nul"
if "%HYDRA_UMC_CI%"=="1" set "KEEP_OPEN=ver >nul"
set "ACTION=%~1"
REM Normalize the incoming directory.  A path ending in a backslash used with
REM CALL can otherwise retain a literal closing quote on Windows.
set "PROJECT=%~2"
for %%I in ("%PROJECT%\.") do set "PROJECT=%%~fI"
if "%ACTION%"=="" set "ACTION=build-test"
if "%PROJECT%"=="" set "PROJECT=%~dp0.."
for /f "usebackq delims=" %%P in (`python -c "import json,sys; print(json.load(open(r'%PROJECT%\armor.project.json',encoding='utf-8'))['name'])"`) do set "PROJECT_NAME=%%P"
python "%~dp0..\tools\armor_project_tool.py" "%ACTION%" "%PROJECT%"
set "RESULT=%ERRORLEVEL%"
%KEEP_OPEN%
exit /b %RESULT%
