@echo off
chcp 65001 >nul
title 留痕 · 启动面板

echo ================================
echo   留痕 (LiuHen) - 启动面板
echo ================================
echo.

cd /d "%~dp0"

:: 启动后端 (FastAPI)
echo [1/2] 启动后端服务 (FastAPI + SQLite)...
start "留痕-后端" cmd /c "cd backend && python main.py"
echo        后端已启动: http://localhost:8000
echo        API 文档: http://localhost:8000/docs
echo.

:: 等待后端就绪
timeout /t 2 /nobreak >nul

:: 启动前端 (Vue3 + Vite)
echo [2/2] 启动前端服务 (Vue3 + Vite)...
start "留痕-前端" cmd /c "cd frontend && npm run dev"
echo        前端已启动: http://localhost:5173
echo.

echo ================================
echo   请在浏览器打开: http://localhost:5173
echo ================================
echo.
echo   关闭本窗口不会影响服务运行
echo   如需停止服务，请关闭"留痕-后端"和"留痕-前端"窗口
echo.

pause
