@echo off
echo === DirectTrans QA smoke ===
cd /d "%~dp0.."
python -m unittest discover -s tests -q
if errorlevel 1 exit /b 1
echo.
echo Optional: launch app, then run this again in another terminal (should exit immediately):
echo   cd src ^&^& python main.py
echo.
if exist dist\DirectTrans_v2.0.0.exe (echo EXE present: dist\DirectTrans_v2.0.0.exe) else (echo WARN: run build.bat for exe)
exit /b 0
