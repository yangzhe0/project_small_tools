@echo off
echo ========================================
echo    Arxiv 论文简报系统
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖包...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo 安装依赖包...
    pip install -r requirements.txt
)

REM 运行简报系统
echo.
echo 启动简报系统...
python arxiv_briefing.py

echo.
echo 按任意键退出...
pause >nul
