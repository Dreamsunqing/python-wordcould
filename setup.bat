@echo off
setlocal enabledelayedexpansion

REM Windows 一键环境配置（批处理版）
REM 用法：双击运行或在 CMD 中执行: setup.bat

REM 启用 UTF-8 控制台以更好支持中文输出与中文路径
chcp 65001 >nul 2>nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set VENV_DIR=.venv
set PIP_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple

REM 选择 Python 解释器
where py >nul 2>nul
if %errorlevel%==0 (
	set PY=py -3
) else (
	set PY=python
)

echo [info] 使用 Python 解释器: %PY%

echo [info] 工作目录: %CD%
if not exist "%VENV_DIR%" (
	echo [info] 创建虚拟环境 %VENV_DIR% ...
	%PY% -m venv "%VENV_DIR%"
) else (
	echo [info] 检测到已存在的虚拟环境 %VENV_DIR%
)

set VENV_PIP=%VENV_DIR%\Scripts\pip.exe
set VENV_PY=%VENV_DIR%\Scripts\python.exe

"%VENV_PIP%" install -U pip -i %PIP_INDEX%
"%VENV_PIP%" install -r requirements.txt -i %PIP_INDEX%

echo [ok] 依赖安装完成。

echo [hint] 请运行交互式助手：
echo        python .\manage.py


pause   
