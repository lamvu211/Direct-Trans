@echo off
echo === DirectTrans Build ===
echo.

REM Stop running DirectTrans instances so dist\*.exe is not locked (WinError 5)
echo Stopping any running DirectTrans processes...
taskkill /F /IM DirectTrans_v2.0.3.exe >nul 2>&1
taskkill /F /IM DirectTrans_v2.0.2.exe >nul 2>&1
taskkill /F /IM DirectTrans_v2.0.1.exe >nul 2>&1
taskkill /F /IM DirectTrans.exe >nul 2>&1
powershell -NoProfile -Command "Get-Process -Name 'DirectTrans*' -ErrorAction SilentlyContinue | Stop-Process -Force" >nul 2>&1
ping -n 3 127.0.0.1 >nul

REM Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM Build exe using spec file (single source of truth for build config)
echo Building DirectTrans v2.0.3...
python -m PyInstaller --clean --noconfirm DirectTrans.spec

echo.
echo Build done! File: dist\DirectTrans_v2.0.3.exe
