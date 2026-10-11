@echo off
chcp 65001 >nul
REM ============================================================
REM  打包为单文件 exe（Windows）
REM  依赖：pip install pyinstaller
REM  产物：dist\FuturesNewsDownloader.exe
REM ============================================================
cd /d "%~dp0"

echo [1/3] 生成图标 ...
python make_icon.py

echo [2/3] 清理旧产物 ...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo [3/3] PyInstaller 打包中 ...
python -m PyInstaller --noconfirm --clean --onefile ^
  --name FuturesNewsDownloader ^
  --icon app.ico ^
  --add-data "static;static" ^
  --collect-data docx ^
  app.py

echo.
echo 完成！可执行文件： dist\FuturesNewsDownloader.exe
pause
