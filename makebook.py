#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


SRC_DIR = Path("src")
FONTS_DIR = Path("fonts")
STYLES_DIR = Path("styles")
OUT_DIR = Path("out")

BOOK_METADATA = Path("book.yaml")

FONT_MAIN = FONTS_DIR / "JingHuaLaoSongTi_v3.ttf"
FONT_MAIN_SUBSET = FONTS_DIR / "JingHuaLaoSongTi.ttf"

FONT_TITLE = FONTS_DIR / "simhei.ttf"
FONT_TITLE_SUBSET = FONTS_DIR / "simhei-subset.ttf"

FONT_MAIN_WOFF2 = FONTS_DIR / "JingHuaLaoSongTi.woff2"
FONT_TITLE_WOFF2 = FONTS_DIR / "SimHei.woff2"

FULL_TEXT = FONTS_DIR / "full.txt"
TITLE_TEXT = FONTS_DIR / "title.txt"

OUTPUT_EPUB = OUT_DIR / "linglongnv.epub"


def check_pandoc():
    """检查 Pandoc 是否存在"""
    if shutil.which("pandoc") is None:
        raise RuntimeError(
            "Pandoc 未安装或不在 PATH 中，请先安装 Pandoc: https://pandoc.org/installing.html"
        )


def collect_chapters():
    """获取排序后的章节列表"""
    chapters = sorted(SRC_DIR.glob("*.md"))
    return chapters


def build_full_text(chapters):
    """拼接所有章节文本"""
    with FULL_TEXT.open("w", encoding="utf-8") as outfile:
        for chapter in chapters:
            with chapter.open("r", encoding="utf-8") as f:
                outfile.write(f.read())


def subset_font(font_path, text_file, output_path):
    """使用 fontTools API 进行字体子集化"""

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
    """压缩字体为 woff2"""

    font = TTFont(input_font)
    font.flavor = "woff2"
    font.save(output_font)


def run_pandoc(chapters):
    """调用 Pandoc 生成 EPUB"""

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
    ]

    cmd.extend(str(ch) for ch in chapters)

    subprocess.run(cmd, check=True)


def cleanup():
    """删除临时文件"""
    for path in [
        FULL_TEXT,
        FONT_MAIN_SUBSET,
        FONT_TITLE_SUBSET,
        FONT_MAIN_WOFF2,
        FONT_TITLE_WOFF2,
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

    compress_to_woff2(FONT_MAIN_SUBSET, FONT_MAIN_WOFF2)
    compress_to_woff2(FONT_TITLE_SUBSET, FONT_TITLE_WOFF2)

    run_pandoc(chapters)

    cleanup()


if __name__ == "__main__":
    main()
