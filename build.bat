@echo off
echo === DirectTrans Build ===
echo.

REM Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM Build exe using spec file (single source of truth for build config)
echo Building DirectTrans v1.0...
python -m PyInstaller --clean --noconfirm DirectTrans.spec

echo.
echo Build done! File: dist\DirectTrans_v1.0.exe
