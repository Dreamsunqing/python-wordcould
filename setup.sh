#!/usr/bin/env bash
set -euo pipefail

# 跨平台（Linux/macOS）一键环境配置脚本
# 用法：
#   chmod +x setup.sh
#   ./setup.sh

VENV_DIR=".venv"
PY_BIN="python3"
PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"

if ! command -v ${PY_BIN} >/dev/null 2>&1; then
	PY_BIN="python"
fi

echo "[info] 使用 Python 解释器: ${PY_BIN}"

if [ ! -d "${VENV_DIR}" ]; then
	echo "[info] 创建虚拟环境 ${VENV_DIR} ..."
	${PY_BIN} -m venv "${VENV_DIR}"
else
	echo "[info] 检测到已存在的虚拟环境 ${VENV_DIR}"
fi

VENV_PY="${VENV_DIR}/bin/python"
VENV_PIP="${VENV_DIR}/bin/pip"

# macOS/Linux 下升级 pip 并安装依赖
"${VENV_PIP}" install -U pip -i "${PIP_INDEX}"
"${VENV_PIP}" install -r requirements.txt -i "${PIP_INDEX}"

echo "[ok] 依赖安装完成。"
echo "[hint] 运行脚本示例："
echo "       ${VENV_PY} wordcloud_cn.py --text data/input.txt --font /System/Library/Fonts/PingFang.ttc --output output.png"
echo "[hint] 或运行交互式助手："
echo "       ${VENV_PY} manage.py"
