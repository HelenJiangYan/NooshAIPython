@echo off
REM 清除所有缓存和旧路径引用

echo 正在清除缓存...

REM 清除 Python 缓存
echo [1/5] 清除 Python 缓存...
if exist __pycache__ rd /s /q __pycache__
if exist .pytest_cache rd /s /q .pytest_cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM 清除 pytest 缓存
echo [2/5] 清除 pytest 缓存...
del /q .pytest_cache\* 2>nul

REM 清除测试报告（包含旧路径）
echo [3/5] 清除旧报告...
if exist reports\allure-results\*.json del /q reports\allure-results\*.json
if exist reports\system_exploration.json del /q reports\system_exploration.json

REM 清除 VSCode 缓存
echo [4/5] 清除 VSCode Python 缓存...
if exist .vscode\.ropeproject rd /s /q .vscode\.ropeproject

REM 重新生成 .pyc 文件
echo [5/5] 清理完成！

echo.
echo ✅ 所有缓存已清除！
echo.
echo 现在可以运行:
echo   venv\Scripts\activate
echo   pytest tests/test_authentication/test_login.py -v
echo.
pause
