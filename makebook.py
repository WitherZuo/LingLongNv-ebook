#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

# 路径：资源目录、字体目录、样式目录、输出目录
SRC_DIR = Path("src")
FONTS_DIR = Path("fonts")
STYLES_DIR = Path("styles")
OUT_DIR = Path("out")
# 书籍元数据文件
BOOK_METADATA = Path("book.yaml")
# 主要/正文字体+子集化字体、woff2 字体
FONT_MAIN = FONTS_DIR / "JingHuaLaoSongTi.ttf"
FONT_MAIN_SUBSET = FONTS_DIR / "JingHuaLaoSongTi-subset.ttf"
FONT_MAIN_WOFF2 = FONTS_DIR / "JingHuaLaoSongTi.woff2"
# 标题字体+子集化字体、woff2 字体
FONT_TITLE = FONTS_DIR / "SimHei.ttf"
FONT_TITLE_SUBSET = FONTS_DIR / "SimHei-subset.ttf"
FONT_TITLE_WOFF2 = FONTS_DIR / "SimHei.woff2"
# 诗歌字体+子集化字体、woff2 字体
FONT_POEM = FONTS_DIR / "FangSong.ttf"
FONT_POEM_SUBSET = FONTS_DIR / "FangSong-subset.ttf"
FONT_POEM_WOFF2 = FONTS_DIR / "FangSong.woff2"
# 子集化字体所需的文本文件
FULL_TEXT = FONTS_DIR / "full.txt"
TITLE_TEXT = FONTS_DIR / "title.txt"
POEM_TEXT = FONTS_DIR / "poem.txt"
# 输出的 EPUB 文件
OUTPUT_EPUB = OUT_DIR / "玲珑女 - 高锋.epub"


def check_pandoc():
    print("检查 Pandoc 是否已安装和配置...")
    # 检查 Pandoc 是否存在
    if shutil.which("pandoc") is None:
        raise RuntimeError(
            "Pandoc 未安装或不在 PATH 中，请先安装 Pandoc: https://pandoc.org/installing.html"
        )


def collect_chapters():
    print("收集章节文件...")
    # 获取排序后的章节列表
    chapters = sorted(SRC_DIR.glob("*.md"))
    return chapters


def build_full_text(chapters):
    print("构建完整的正文文本...")
    # 拼接所有章节文本
    with FULL_TEXT.open("w", encoding="utf-8") as outfile:
        for chapter in chapters:
            with chapter.open("r", encoding="utf-8") as f:
                outfile.write(f.read())


def subset_font(font_path, text_file, output_path):
    print(f"子集化字体: {font_path}")
    # 使用 fonttools API 进行字体子集化
    options = subset.Options()
    options.set(layout_features="*")
    options.flavor = None

    font = subset.load_font(font_path, options)

    subsetter = subset.Subsetter(options)

    with open(text_file, encoding="utf-8") as f:
        text = f.read()

    subsetter.populate(text=text)
    subsetter.subset(font)

    subset.save_font(font, output_path, options)


def compress_to_woff2(input_font, output_font):
    print(f"压缩字体为 woff2: {input_font} -> {output_font}")
    # 压缩字体为 woff2
    font = TTFont(input_font)
    font.flavor = "woff2"
    font.save(output_font)


def run_pandoc(chapters):
    print("调用 Pandoc 生成 EPUB...")
    # 调用 Pandoc 生成 EPUB
    OUT_DIR.mkdir(exist_ok=True)

    cmd = [
        "pandoc",
        "-o",
        str(OUTPUT_EPUB),
        str(BOOK_METADATA),
        "--epub-title-page=false",
        f"--css={STYLES_DIR / 'book.css'}",
        f"--epub-embed-font={FONT_MAIN_WOFF2}",
        f"--epub-embed-font={FONT_TITLE_WOFF2}",
        f"--epub-embed-font={FONT_POEM_WOFF2}",
    ]

    cmd.extend(str(ch) for ch in chapters)

    subprocess.run(cmd, check=True)


def cleanup():
    print("清理临时文件...")
    # 删除临时文件
    for path in [
        FULL_TEXT,
        FONT_MAIN_SUBSET,
        FONT_TITLE_SUBSET,
        FONT_POEM_SUBSET,
        FONT_MAIN_WOFF2,
        FONT_TITLE_WOFF2,
        FONT_POEM_WOFF2,
    ]:
        if path.exists():
            path.unlink()


def main():
    check_pandoc()

    chapters = collect_chapters()

    if not chapters:
        raise RuntimeError("未找到任何章节文件 (src/*.md)")

    build_full_text(chapters)

    subset_font(FONT_MAIN, FULL_TEXT, FONT_MAIN_SUBSET)
    subset_font(FONT_TITLE, TITLE_TEXT, FONT_TITLE_SUBSET)
    subset_font(FONT_POEM, POEM_TEXT, FONT_POEM_SUBSET)

    compress_to_woff2(FONT_MAIN_SUBSET, FONT_MAIN_WOFF2)
    compress_to_woff2(FONT_TITLE_SUBSET, FONT_TITLE_WOFF2)
    compress_to_woff2(FONT_POEM_SUBSET, FONT_POEM_WOFF2)

    run_pandoc(chapters)

    cleanup()


if __name__ == "__main__":
    main()
