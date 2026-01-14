@echo off
chcp 65001 >nul
echo 😊 启动笑容检测器...
echo.
echo 提示：
echo   - 确保摄像头已连接并可用
echo   - 按 'q' 键退出程序
echo.
python smile_detector.py
pause

