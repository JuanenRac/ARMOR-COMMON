@echo off
REM *****************************************************************************
REM A.R.M.O.R. - armor-project.bat
REM Standard Windows project workflow launcher.
REM Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
REM GPL-3.0-or-later - see LICENSE
REM *****************************************************************************
setlocal
set "ACTION=%~1"
REM Normalize the incoming directory.  A path ending in a backslash used with
REM CALL can otherwise retain a literal closing quote on Windows.
set "PROJECT=%~2"
for %%I in ("%PROJECT%\.") do set "PROJECT=%%~fI"
if "%ACTION%"=="" set "ACTION=build-test"
if "%PROJECT%"=="" set "PROJECT=%~dp0.."
for /f "usebackq delims=" %%P in (`python -c "import json,sys; print(json.load(open(r'%PROJECT%\armor.project.json',encoding='utf-8'))['name'])"`) do set "PROJECT_NAME=%%P"
echo.
echo *****************************************************************************
echo * %PROJECT_NAME% - %ACTION%
echo * Mode      : %ACTION%
echo * Author    : JuanenRac (Electro Hobby 3D)
echo * Email     : electrohobby3d@gmail.com
echo * Copyright : (C) 2026 JuanenRac
echo * License   : GPL-3.0-or-later - see LICENSE
echo * 1. Validate the real stack commands for this project.
echo * 2. Version and CHANGELOG change only after a successful build.
echo * 3. Keep this terminal open for the final result.
echo *****************************************************************************
python "%~dp0..\tools\armor_project_tool.py" "%ACTION%" "%PROJECT%"
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (echo ARMOR_WORKFLOW=PASS) else (echo ARMOR_WORKFLOW=FAIL)
pause
exit /b %RESULT%
