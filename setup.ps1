#requires -Version 5.1
param()
$ErrorActionPreference = 'Stop'

# Windows 一键环境配置脚本
# 用法：
#   PowerShell 以当前目录执行：
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   .\setup.ps1

$VenvDir = ".venv"
$PipIndex = "https://pypi.tuna.tsinghua.edu.cn/simple"

# 选择 Python 解释器
$py = (Get-Command py -ErrorAction SilentlyContinue)
if ($py) {
	$python = "py -3"
} else {
	$python = "python"
}

Write-Host "[info] 使用 Python 解释器: $python"

if (-not (Test-Path $VenvDir)) {
	Write-Host "[info] 创建虚拟环境 $VenvDir ..."
	& $python -m venv $VenvDir | Out-Null
} else {
	Write-Host "[info] 检测到已存在的虚拟环境 $VenvDir"
}

$venvPip = Join-Path $VenvDir 'Scripts\pip.exe'
$venvPy = Join-Path $VenvDir 'Scripts\python.exe'

& $venvPip install -U pip -i $PipIndex
& $venvPip install -r requirements.txt -i $PipIndex

Write-Host "[ok] 依赖安装完成。"
Write-Host "[hint] 运行脚本示例："
Write-Host "       $venvPy .\wordcloud_cn.py --text .\data\input.txt --font C:\Windows\Fonts\msyh.ttc --output .\output.png"
Write-Host "[hint] 或运行交互式助手："
Write-Host "       $venvPy .\manage.py"
