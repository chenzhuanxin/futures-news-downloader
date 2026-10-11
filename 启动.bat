@echo off
chcp 65001 >nul
title 期货品种资讯下载器

set "PY=C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo ============================================================
echo   期货品种资讯下载器
echo   正在启动本地服务，稍后会自动打开浏览器…
echo   关闭此窗口即可停止服务
echo ============================================================

cd /d "%~dp0"
start "" http://127.0.0.1:8899
"%PY%" app.py
pause
