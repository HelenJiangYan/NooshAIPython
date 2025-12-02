@echo off
REM NooshAI 测试框架 - 快速运行脚本

echo ============================================================
echo NooshAI 自动化测试框架
echo ============================================================
echo.

REM 检查是否在项目目录
if not exist "venv" (
    echo [错误] 请在项目根目录运行此脚本！
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo [信息] 虚拟环境已激活
echo.

REM 检查参数
if "%1"=="" (
    echo [运行] 执行所有登录测试...
    python -m pytest tests/test_authentication/test_login.py -v
) else if "%1"=="all" (
    echo [运行] 执行所有测试...
    python -m pytest -v
) else if "%1"=="login" (
    echo [运行] 执行登录测试...
    python -m pytest tests/test_authentication/test_login.py -v
) else if "%1"=="chatbot" (
    echo [运行] 执行Chatbot测试...
    python -m pytest tests/test_chatbot/test_basic_chat.py -v
) else if "%1"=="smoke" (
    echo [运行] 执行冒烟测试...
    python -m pytest -m smoke -v
) else (
    echo [运行] 执行指定测试: %*
    python -m pytest %*
)

echo.
echo ============================================================
echo 测试完成！
echo HTML报告: reports\html\report.html
echo ============================================================
pause
