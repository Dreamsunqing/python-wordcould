#!/usr/bin/env python
import os
import shutil
import sys
import subprocess
from pathlib import Path

# 交互式助手：引导安装依赖、选择文本/字体/遮罩并生成词云

PROJECT_ROOT = Path(__file__).parent
VENV_DIR = PROJECT_ROOT / '.venv'
PIP_INDEX = 'https://pypi.tuna.tsinghua.edu.cn/simple'


def run(cmd):
	print(f'[cmd] {cmd}')
	return subprocess.call(cmd, shell=True)


def ensure_venv_and_requirements():
	# 简单检测：若脚本不在虚拟环境中，提示并提供自动安装
	in_venv = (sys.prefix != sys.base_prefix) or (os.environ.get('VIRTUAL_ENV') is not None)
	if not in_venv:
		print('[info] 当前不在虚拟环境中。建议先运行一键脚本:')
		if os.name == 'nt':
			print('       powershell -ExecutionPolicy Bypass -File .\\setup.ps1')
		else:
			print('       bash ./setup.sh')
		choice = input('是否现在自动创建虚拟环境并安装依赖? [Y/n]: ').strip().lower() or 'y'
		if choice.startswith('y'):
			if os.name == 'nt':
				run('py -3 -m venv .venv' if shutil.which('py') else 'python -m venv .venv')
				pip_exe = str(VENV_DIR / 'Scripts' / 'pip.exe')
				run(f'"{pip_exe}" install -U pip -i {PIP_INDEX}')
				run(f'"{pip_exe}" install -r requirements.txt -i {PIP_INDEX}')
			else:
				run('python3 -m venv .venv || python -m venv .venv')
				pip_exe = str(VENV_DIR / 'bin' / 'pip')
				run(f'"{pip_exe}" install -U pip -i {PIP_INDEX}')
				run(f'"{pip_exe}" install -r requirements.txt -i {PIP_INDEX}')
			print('[ok] 虚拟环境与依赖安装完成。请使用虚拟环境内的 python 重新运行本脚本以获得最佳体验。')
			return False
	return True


def ask_path(prompt, default):
	val = input(f"{prompt} [{default}]: ").strip()
	return val or default


def main():
	print('=== 交互式词云助手 ===')
	if not ensure_venv_and_requirements():
		return

	text_path = ask_path('输入文本路径(支持 .txt/.docx)', str(PROJECT_ROOT / 'data' / 'input.txt'))
	font_path = ask_path('中文字体路径(留空尝试自动探测)', '')
	stopwords_path = ask_path('停用词路径(可留空)', str(PROJECT_ROOT / 'data' / 'stopwords.txt'))
	mask_path = ask_path('遮罩图片路径(可留空)', str(PROJECT_ROOT / 'data' / 'mask.png'))
	output_path = ask_path('输出图片路径', str(PROJECT_ROOT / 'output.png'))
	width = ask_path('词云宽度', '1200')
	height = ask_path('词云高度', '800')
	min_len = ask_path('最短词长度(过滤)', '2')
	max_words = ask_path('最大词数', '300')
	background = ask_path('背景色(如 white 或 #000000)', 'white')

	py = sys.executable
	cmd = (
		f'"{py}" "{PROJECT_ROOT / "wordcloud_cn.py"}" '
		f'--text "{text_path}" '
		f'--output "{output_path}" '
		f'--width {width} --height {height} '
		f'--background {background} --max_words {max_words} --min_word_length {min_len} '
		f'--stopwords "{stopwords_path}" '
		f'--mask "{mask_path}" '
	)
	if font_path:
		cmd += f'--font "{font_path}" '

	print('\n将执行命令:')
	print(cmd)
	ok = input('确认执行? [Y/n]: ').strip().lower() or 'y'
	if ok.startswith('y'):
		code = run(cmd)
		if code == 0:
			print('[ok] 词云已生成。')
		else:
			print('[error] 生成失败，请检查参数与依赖。')
	else:
		print('[cancel] 已取消执行。')


if __name__ == '__main__':
	main()
