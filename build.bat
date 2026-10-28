@echo off
setlocal EnableExtensions

echo === DirectTrans Build ===
echo.

for /f "delims=" %%V in ('python -c "import sys; sys.path.insert(0,'src'); from constants import APP_VERSION; print(APP_VERSION)"') do set "APP_VERSION=%%V"
if not defined APP_VERSION (
  echo ERROR: Could not read APP_VERSION from src\constants.py
  exit /b 1
)
set "EXE_NAME=DirectTrans_v%APP_VERSION%.exe"

REM Unlock dist\*.exe if a running instance holds the file (WinError 5)
echo Stopping DirectTrans processes...
powershell -NoProfile -Command "Get-Process -Name 'DirectTrans*' -ErrorAction SilentlyContinue | Stop-Process -Force" >nul 2>&1
timeout /t 2 /nobreak >nul

pip install -r requirements.txt
pip install pyinstaller

echo Building DirectTrans v%APP_VERSION%...
python -m PyInstaller --clean --noconfirm DirectTrans.spec
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo.
echo Build done! File: dist\%EXE_NAME%
endlocal
