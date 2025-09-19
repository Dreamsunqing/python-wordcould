"""
中文词云生成脚本

功能概述：
- 使用 jieba 进行中文分词
- 支持停用词过滤（可配置文件 data/stopwords.txt）
- 支持遮罩图（mask.png）以生成特定形状的词云
- 自动探测常见中文字体（可通过 --font 手动指定）
- 支持从 .txt 与 .docx（Word）读取文本

用法示例（Windows PowerShell）：
.venv\Scripts\python .\wordcloud_cn.py --text .\data\input.txt --font C:\Windows\Fonts\msyh.ttc --output .\output.png
"""

import argparse
import os
import re
from pathlib import Path
from typing import Optional, Set

# 导入库
import jieba  
import numpy as np  
from PIL import Image  
from wordcloud import WordCloud  
from docx import Document 


# 默认参数（可通过命令行覆盖）
# 输入文本路径
DEFAULT_TEXT_PATH = Path("data/input.txt")
# 停用词路径
DEFAULT_STOPWORDS_PATH = Path("data/stopwords.txt")
# 遮罩图片路径
DEFAULT_MASK_PATH = Path("data/mask.png")
# 输出图片路径
DEFAULT_OUTPUT_PATH = Path("output.png")
# 画布大小
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 800
# 背景色
DEFAULT_BACKGROUND = "white"
# 最大词数
DEFAULT_MAX_WORDS = 300
# 最短词长度
DEFAULT_MIN_WORD_LENGTH = 2


def detect_chinese_font() -> Optional[str]:
	"""在常见路径中自动探测中文字体，找不到则返回 None。

	优先探测：
	- Windows: 微软雅黑、黑体、宋体
	- macOS: STHeiti/PingFang
	- Linux: 常见中文字体包
	"""
	common_fonts = [
		# Windows
		str(Path(os.environ.get("WINDIR", r"C:\\Windows")) / "Fonts" / "msyh.ttc"),  # 微软雅黑
		str(Path(os.environ.get("WINDIR", r"C:\\Windows")) / "Fonts" / "simhei.ttf"),  # 黑体
		str(Path(os.environ.get("WINDIR", r"C:\\Windows")) / "Fonts" / "simsun.ttc"),  # 宋体
		# macOS
		"/System/Library/Fonts/STHeiti Light.ttc",
		"/System/Library/Fonts/STHeiti Medium.ttc",
		"/System/Library/Fonts/PingFang.ttc",
		# Linux (常见中文字体包)
		"/usr/share/fonts/truetype/arphic/ukai.ttc",
		"/usr/share/fonts/truetype/arphic/uming.ttc",
	]
	for font in common_fonts:
		if Path(font).exists():
			return font
	return None


def read_text(path: Path) -> str:
	"""读取文本内容：支持 .txt 与 .docx。

	参数：
	- path: 文本或 Word 文件路径
	"""
	if not path.exists():
		raise FileNotFoundError(f"找不到文本文件: {path}")
	lower = path.suffix.lower()
	if lower == ".docx":
		# 读取 Word 段落与表格中的文本
		doc = Document(str(path))
		paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
		cells = []
		for table in getattr(doc, "tables", []):
			for row in table.rows:
				for cell in row.cells:
					text = cell.text.strip()
					if text:
						cells.append(text)
		return "\n".join(paras + cells)
	# 默认按 UTF-8 文本读取
	return path.read_text(encoding="utf-8", errors="ignore")

def read_stopwords(path: Path) -> Set[str]:
	"""从文件读取过滤词集合（若文件不存在则返回空集合）。"""
	stopwords: Set[str] = set()
	if path.exists():
		for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
			word = line.strip()
			if word:
				stopwords.add(word)
	return stopwords


def tokenize(text: str, min_word_length: int) -> str:
	"""对文本进行清洗与分词，过滤长度小于最短长度的词，返回以空格连接的分词结果。"""
	# 仅保留中英文与数字，其他字符替换为空格作为分隔符
	clean = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]+", " ", text)
	# 使用 jieba.cut 分词，并按最短词长度过滤
	tokens = [w.strip() for w in jieba.cut(clean) if len(w.strip()) >= min_word_length]
	return " ".join(tokens)


def load_mask(mask_path: Path) -> Optional[np.ndarray]:
	"""加载遮罩图片为灰度 numpy 数组；若文件不存在则返回 None。"""
	if mask_path.exists():
		img = Image.open(mask_path).convert("L")  # 单通道灰度
		return np.array(img)
	return None

# 词云配置
def build_wordcloud(
		text_tokens: str,
		font_path: Optional[str],
		stopwords: Set[str],
		mask_array: Optional[np.ndarray],
		width: int,
		height: int,
		background_color: str,
		max_words: int,
) -> WordCloud:
	"""根据分词结果与配置构建 WordCloud 对象并生成词云。"""
	wc = WordCloud(
		font_path=font_path,
		width=width,
		height=height,
		background_color=background_color,
		max_words=max_words,
		mask=mask_array,
		stopwords=stopwords or None,
		collocations=False,
	)
	wc.generate(text_tokens)
	return wc

# 主函数
def main():
	"""命令行入口：解析参数、读取数据、生成并保存词云图片。"""
	parser = argparse.ArgumentParser(description="中文词云生成器")
	# 基本 I/O 配置
	parser.add_argument("--text", type=str, default=str(DEFAULT_TEXT_PATH), help="输入文本文件路径（支持 .txt/.docx）")
	parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_PATH), help="输出图片路径")
	# 画布与外观
	parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="词云宽度")
	parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="词云高度")
	parser.add_argument("--background", type=str, default=DEFAULT_BACKGROUND, help="背景色，如 white 或 #000000")
	parser.add_argument("--max_words", type=int, default=DEFAULT_MAX_WORDS, help="最大词数")
	# 分词过滤与资源
	parser.add_argument("--min_word_length", type=int, default=DEFAULT_MIN_WORD_LENGTH, help="最短词长度过滤")
	parser.add_argument("--font", type=str, default="", help="中文字体路径。若留空将自动探测")
	parser.add_argument("--stopwords", type=str, default=str(DEFAULT_STOPWORDS_PATH), help="停用词表路径，可选")
	parser.add_argument("--mask", type=str, default=str(DEFAULT_MASK_PATH), help="遮罩图片路径，可选")

	args = parser.parse_args()

	# 路径解析
	text_path = Path(args.text)
	output_path = Path(args.output)
	stopwords_path = Path(args.stopwords) if args.stopwords else DEFAULT_STOPWORDS_PATH
	mask_path = Path(args.mask) if args.mask else DEFAULT_MASK_PATH

	# 读取数据与资源
	text = read_text(text_path)
	stopwords = read_stopwords(stopwords_path)
	mask_array = load_mask(mask_path)

	# 字体探测（或手动指定）
	font_path = args.font.strip() or detect_chinese_font()
	if not font_path:
		raise RuntimeError("未找到可用的中文字体，请通过 --font 指定字体文件路径")

	print(f"使用字体: {font_path}")
	print(f"分词中，最短词长: {args.min_word_length} ...")
	text_tokens = tokenize(text, args.min_word_length)

	# 生成词云
	print("生成词云...")
	wc = build_wordcloud(
		text_tokens=text_tokens,
		font_path=font_path,
		stopwords=stopwords,
		mask_array=mask_array,
		width=args.width,
		height=args.height,
		background_color=args.background,
		max_words=args.max_words,
	)

	# 保存图片
	wc.to_file(str(output_path))
	print(f"已生成: {output_path.resolve()}")


if __name__ == "__main__":
	main()
