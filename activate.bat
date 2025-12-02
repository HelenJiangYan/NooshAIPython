@echo off
REM 激活虚拟环境的便捷脚本

echo ========================================
echo NooshAI 测试框架 - 虚拟环境激活
echo ========================================
echo.

REM 检查venv是否存在
if not exist venv (
    echo [错误] 虚拟环境不存在！
    echo 请先运行: python -m venv venv
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo [成功] 虚拟环境已激活！
echo.
echo 提示:
echo   - 安装依赖: pip install -r requirements.txt
echo   - 安装Playwright: playwright install chromium
echo   - 运行测试: pytest -v
echo   - 退出环境: deactivate
echo.
