#!/usr/bin/env python3
"""
PPT/PDF 转 Markdown 工具 - GPU版本 (2025年最新)

使用GOT-OCR 2.0作为主引擎:
- 580M参数，仅需4GB显存
- 新一代OCR-2.0架构，端到端处理
- 原生支持Markdown格式输出
- 中英文识别优秀
- GPU加速，速度快

PaddleOCR GPU版作为备选引擎
"""

import os
import sys
import subprocess
import torch
from pathlib import Path
from transformers import AutoModel, AutoTokenizer
from pdf2image import convert_from_path
from PIL import Image


def ppt_to_pdf(ppt_path, pdf_path):
    """使用LibreOffice将PPT转换为PDF"""
    print(f"📄 正在将 {ppt_path} 转换为PDF...")
    cmd = [
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', os.path.dirname(pdf_path),
        ppt_path
    ]
    subprocess.run(cmd, check=True)
    print(f"✓ PDF已生成: {pdf_path}")


def check_gpu():
    """检查GPU是否可用"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🎮 检测到GPU: {gpu_name}")
        print(f"💾 显存: {gpu_memory:.1f} GB")
        return True
    else:
        print("⚠️  未检测到GPU，将使用CPU模式 (较慢)")
        return False


def pdf_to_markdown_got_ocr(pdf_path, output_path):
    """
    使用GOT-OCR 2.0将PDF转换为Markdown (推荐方法 - GPU加速)

    GOT-OCR 2.0特点:
    - 580M参数，轻量高效
    - OCR-2.0新架构：高压缩编码器 + 长上下文解码器
    - 原生支持格式化输出 (Markdown, LaTeX)
    - 支持中英文、数学公式、表格、手写等
    - GPU优化，速度快
    """
    print(f"🚀 正在使用 GOT-OCR 2.0 (GPU加速) 处理 {pdf_path}...")

    has_gpu = check_gpu()
    device = 'cuda' if has_gpu else 'cpu'

    try:
        # 加载GOT-OCR 2.0模型
        print("📦 正在加载 GOT-OCR 2.0 模型...")
        model_name = "stepfun-ai/GOT-OCR2_0"

        # 使用cache_dir缓存模型到/models目录
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir="/models"
        )
        model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            device_map=device,
            use_safetensors=True,
            cache_dir="/models"
        )

        if has_gpu:
            model = model.eval().cuda()
            print(f"✓ 模型已加载到GPU")
        else:
            model = model.eval()
            print(f"✓ 模型已加载到CPU")

        # 将PDF转换为图片
        print("📷 正在将PDF转换为图片...")
        images = convert_from_path(pdf_path, dpi=200)  # GPU版可以用更高DPI
        print(f"✓ 已转换 {len(images)} 页")

        markdown_content = []
        markdown_content.append(f"# {Path(pdf_path).stem}\n\n")

        # 对每一页进行OCR
        for i, image in enumerate(images, 1):
            print(f"🔍 正在处理第 {i}/{len(images)} 页...")

            # 保存临时图片
            temp_image_path = f"/tmp/page_{i}.png"
            image.save(temp_image_path, 'PNG')

            # 使用GOT-OCR 2.0进行OCR识别，直接输出Markdown
            # GOT-OCR支持"plain"和"format"两种模式
            result = model.chat(
                tokenizer,
                temp_image_path,
                ocr_type='format'  # format模式会保留文档格式
            )

            # 添加到Markdown
            markdown_content.append(f"\n---\n## Page {i}\n\n")
            markdown_content.append(result + "\n")

            # 删除临时图片
            os.remove(temp_image_path)

            # 清理GPU缓存
            if has_gpu:
                torch.cuda.empty_cache()

        # 保存Markdown
        final_markdown = ''.join(markdown_content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)

        print(f"✓ GOT-OCR 2.0 转换成功!")
        print(f"✓ Markdown已生成: {output_path}")
        return True

    except Exception as e:
        print(f"⚠ GOT-OCR 2.0 转换失败: {e}")
        import traceback
        traceback.print_exc()
        print("将使用 PaddleOCR GPU版 作为备选方案...")
        return False


def pdf_to_markdown_paddleocr_gpu(pdf_path, output_path):
    """使用PaddleOCR GPU版将PDF转换为Markdown (备选方法)"""
    print(f"🔄 正在使用 PaddleOCR GPU版 处理 {pdf_path}...")

    try:
        from paddleocr import PaddleOCR

        # 初始化PaddleOCR (GPU模式)
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            use_gpu=True,  # 启用GPU
            show_log=False
        )

        # 将PDF转换为图片
        print("📷 正在将PDF转换为图片...")
        images = convert_from_path(pdf_path, dpi=300)

        markdown_content = []
        markdown_content.append(f"# {Path(pdf_path).stem}\n\n")

        # 对每一页进行OCR
        for i, image in enumerate(images, 1):
            print(f"🔍 正在处理第 {i}/{len(images)} 页...")

            # 保存临时图片
            temp_image_path = f"/tmp/page_{i}.jpg"
            image.save(temp_image_path, 'JPEG')

            # OCR识别
            result = ocr.ocr(temp_image_path, cls=True)

            # 提取文字并添加到Markdown
            markdown_content.append(f"\n---\n## 第 {i} 页\n\n")

            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    confidence = line[1][1]
                    # 只保留置信度较高的文本
                    if confidence > 0.6:
                        markdown_content.append(text + "\n\n")

            # 删除临时图片
            os.remove(temp_image_path)

        # 保存Markdown
        final_markdown = ''.join(markdown_content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)

        print(f"✓ PaddleOCR转换成功!")
        print(f"✓ Markdown已生成: {output_path}")
        return True

    except Exception as e:
        print(f"❌ PaddleOCR转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False


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

    # 先尝试使用GOT-OCR 2.0 (GPU加速，更准确)
    if not pdf_to_markdown_got_ocr(str(input_pdf), str(markdown_path)):
        # 如果GOT-OCR失败，使用PaddleOCR GPU版
        if not pdf_to_markdown_paddleocr_gpu(str(input_pdf), str(markdown_path)):
            print("\n❌ 所有OCR引擎都失败了！")
            return

    print(f"\n✅ 转换完成!")
    print(f"📄 输出文件: {markdown_path}")

    # 显示文件大小
    file_size = markdown_path.stat().st_size / 1024
    print(f"📊 文件大小: {file_size:.1f} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ppt_to_markdown_gpu.py <输入文件路径> [输出目录]")
        print("示例: python ppt_to_markdown_gpu.py /input/lecture.pptx /output")
        sys.exit(1)

    input_file = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else "/output"

    convert_file(input_file, output_directory)
