#!/usr/bin/env python3
"""
PPT/PDF 转 Markdown 工具 (2025年最新OCR引擎)

OCR引擎选择策略:
1. Marker (with Surya OCR) - 主引擎，2025年最佳PDF→Markdown工具
   - 使用先进的Surya OCR模型 (比Tesseract更准确)
   - 支持90+语言，包括中英文
   - 能识别复杂布局、表格、公式
   - 专门为PDF转Markdown优化

2. PaddleOCR - 备选引擎，当Marker失败时使用
   - 中文识别准确率高
   - 稳定可靠
"""

import os
import sys
import subprocess
from pathlib import Path
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from PIL import Image


def ppt_to_pdf(ppt_path, pdf_path):
    """使用LibreOffice将PPT转换为PDF"""
    print(f"正在将 {ppt_path} 转换为PDF...")
    cmd = [
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', os.path.dirname(pdf_path),
        ppt_path
    ]
    subprocess.run(cmd, check=True)
    print(f"✓ PDF已生成: {pdf_path}")


def pdf_to_markdown_marker(pdf_path, output_path):
    """
    使用Marker将PDF转换为Markdown (2025年推荐方法)

    Marker内部使用Surya OCR引擎:
    - Surya是2025年最先进的开源OCR引擎之一
    - 支持90+语言的行级文本检测和识别
    - 比Tesseract更准确，特别是对复杂布局
    - benchmark显示与Google Cloud Vision准确率相当
    """
    print(f"🚀 正在使用 Marker (with Surya OCR) 处理 {pdf_path}...")
    print(f"   Surya OCR: 2025年SOTA开源OCR引擎，支持90+语言")
    try:
        from marker.convert import convert_single_pdf
        from marker.models import load_all_models

        # 加载模型 (包括Surya OCR)
        print("   正在加载Surya OCR模型...")
        models = load_all_models()

        # 转换PDF
        print("   正在识别文字和布局...")
        full_text, images, out_meta = convert_single_pdf(pdf_path, models)

        # 保存Markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        print(f"✓ Marker转换成功!")
        print(f"✓ Markdown已生成: {output_path}")
        return True
    except Exception as e:
        print(f"⚠ Marker转换失败: {e}")
        print("将使用 PaddleOCR 作为备选方案...")
        return False


def pdf_to_markdown_paddleocr(pdf_path, output_path):
    """使用PaddleOCR将PDF转换为Markdown (备选方法)"""
    print(f"正在使用 PaddleOCR 处理 {pdf_path}...")

    # 初始化PaddleOCR (支持中英文)
    ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)

    # 将PDF转换为图片
    print("正在将PDF转换为图片...")
    images = convert_from_path(pdf_path, dpi=300)

    markdown_content = []

    # 对每一页进行OCR
    for i, image in enumerate(images, 1):
        print(f"正在处理第 {i}/{len(images)} 页...")

        # 保存临时图片
        temp_image_path = f"/tmp/page_{i}.jpg"
        image.save(temp_image_path, 'JPEG')

        # OCR识别
        result = ocr.ocr(temp_image_path, cls=True)

        # 提取文字并添加到Markdown
        markdown_content.append(f"\n## 第 {i} 页\n")

        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                # 只保留置信度较高的文本
                if confidence > 0.5:
                    markdown_content.append(text + "\n")

        # 删除临时图片
        os.remove(temp_image_path)

    # 保存Markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown_content))

    print(f"✓ Markdown已生成: {output_path}")


def convert_file(input_path, output_dir):
    """转换文件的主函数"""
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 确定文件类型
    ext = input_path.suffix.lower()

    if ext in ['.ppt', '.pptx']:
        # PPT -> PDF
        pdf_path = output_dir / f"{input_path.stem}.pdf"
        ppt_to_pdf(str(input_path), str(pdf_path))
        input_pdf = pdf_path
    elif ext == '.pdf':
        input_pdf = input_path
    else:
        print(f"❌ 不支持的文件格式: {ext}")
        print("支持的格式: .ppt, .pptx, .pdf")
        return

    # PDF -> Markdown
    markdown_path = output_dir / f"{input_pdf.stem}.md"

    # 先尝试使用Marker (更准确)
    if not pdf_to_markdown_marker(str(input_pdf), str(markdown_path)):
        # 如果Marker失败，使用PaddleOCR
        pdf_to_markdown_paddleocr(str(input_pdf), str(markdown_path))

    print(f"\n✅ 转换完成!")
    print(f"📄 输出文件: {markdown_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ppt_to_markdown.py <输入文件路径> [输出目录]")
        print("示例: python ppt_to_markdown.py /input/lecture.pptx /output")
        sys.exit(1)

    input_file = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else "/output"

    convert_file(input_file, output_directory)
