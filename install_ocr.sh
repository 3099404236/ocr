#!/bin/bash
# OCR项目一键安装脚本
# 在你的Linux电脑上运行此脚本

set -e

echo "🚀 OCR项目一键安装"
echo "=================="
echo ""

# 1. 检查目录
if [ -d "ocr" ]; then
    echo "⚠️  ocr目录已存在，是否删除并重新创建？[y/N]"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf ocr
    else
        echo "❌ 安装取消"
        exit 1
    fi
fi

# 2. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p ocr/{scripts,input,output,models}
cd ocr

# 3. 初始化Git
echo "🔧 初始化Git仓库..."
git init
git remote add origin https://github.com/3099404236/ocr.git

# 4. 创建README.md
echo "📝 创建README.md..."
cat > README.md << 'EOFREADME'
# PPT/PDF 转 Markdown OCR 工具

Docker容器化的OCR工具，将PPT和PDF转换为Markdown格式。

## 🎮 GPU版 (推荐)

使用GOT-OCR 2.0 (580M参数，仅需4GB显存)

### 快速开始

```bash
# 构建镜像
docker-compose -f docker-compose.gpu.yml build

# 转换文件
docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu \
    python /app/scripts/ppt_to_markdown_gpu.py /input/your_file.pptx /output
```

详见 `QUICKSTART_GPU.md`
EOFREADME

# 5. 创建Dockerfile.gpu
echo "🐳 创建Dockerfile.gpu..."
cat > Dockerfile.gpu << 'EOFDOCKER'
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip libreoffice \
    libreoffice-writer libreoffice-impress \
    poppler-utils git wget \
    libgl1-mesa-glx libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.10 /usr/bin/python

RUN pip install --no-cache-dir \
    torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 \
    --index-url https://download.pytorch.org/whl/cu121

RUN pip install --no-cache-dir \
    transformers==4.37.2 tiktoken==0.6.0 verovio==4.3.1 \
    accelerate==0.28.0 Pillow pdf2image python-docx \
    paddlepaddle-gpu paddleocr

RUN mkdir -p /input /output /models

CMD ["/bin/bash"]
EOFDOCKER

# 6. 创建docker-compose.gpu.yml
echo "🐳 创建docker-compose.gpu.yml..."
cat > docker-compose.gpu.yml << 'EOFCOMPOSE'
version: '3.8'

services:
  ocr-converter-gpu:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    container_name: ocr-converter-gpu
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
      - PYTHONUNBUFFERED=1
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./input:/input
      - ./output:/output
      - ./scripts:/app/scripts
      - ./models:/models
    shm_size: '8gb'
    stdin_open: true
    tty: true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
EOFCOMPOSE

# 7. 创建转换脚本（简化版）
echo "🐍 创建Python转换脚本..."
cat > scripts/ppt_to_markdown_gpu.py << 'EOFPYTHON'
#!/usr/bin/env python3
"""GPU加速的PPT/PDF转Markdown工具 - 使用GOT-OCR 2.0"""

import os, sys, subprocess, torch
from pathlib import Path
from transformers import AutoModel, AutoTokenizer
from pdf2image import convert_from_path

def ppt_to_pdf(ppt_path, pdf_path):
    print(f"📄 转换PPT为PDF...")
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', os.path.dirname(pdf_path), ppt_path], check=True)
    print(f"✓ PDF生成: {pdf_path}")

def pdf_to_markdown_got_ocr(pdf_path, output_path):
    print(f"🚀 使用GOT-OCR 2.0处理 {pdf_path}...")

    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        device = 'cuda'
    else:
        print("⚠️ 未检测到GPU，使用CPU")
        device = 'cpu'

    try:
        print("📦 加载GOT-OCR 2.0模型...")
        tokenizer = AutoTokenizer.from_pretrained("stepfun-ai/GOT-OCR2_0",
                                                    trust_remote_code=True, cache_dir="/models")
        model = AutoModel.from_pretrained("stepfun-ai/GOT-OCR2_0",
                                          trust_remote_code=True, device_map=device,
                                          use_safetensors=True, cache_dir="/models")

        if device == 'cuda':
            model = model.eval().cuda()
        else:
            model = model.eval()

        print("📷 转换PDF为图片...")
        images = convert_from_path(pdf_path, dpi=200)

        markdown_content = [f"# {Path(pdf_path).stem}\n\n"]

        for i, image in enumerate(images, 1):
            print(f"🔍 处理第 {i}/{len(images)} 页...")
            temp_image = f"/tmp/page_{i}.png"
            image.save(temp_image, 'PNG')

            result = model.chat(tokenizer, temp_image, ocr_type='format')
            markdown_content.append(f"\n---\n## Page {i}\n\n{result}\n")

            os.remove(temp_image)
            if device == 'cuda':
                torch.cuda.empty_cache()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))

        print(f"✓ Markdown生成: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ppt_to_markdown_gpu.py <文件路径> [输出目录]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.suffix.lower() in ['.ppt', '.pptx']:
        pdf_path = output_dir / f"{input_path.stem}.pdf"
        ppt_to_pdf(str(input_path), str(pdf_path))
        input_pdf = pdf_path
    elif input_path.suffix.lower() == '.pdf':
        input_pdf = input_path
    else:
        print(f"❌ 不支持的格式: {input_path.suffix}")
        sys.exit(1)

    markdown_path = output_dir / f"{input_pdf.stem}.md"
    pdf_to_markdown_got_ocr(str(input_pdf), str(markdown_path))
EOFPYTHON

chmod +x scripts/ppt_to_markdown_gpu.py

# 8. 创建.gitignore
cat > .gitignore << 'EOFGITIGNORE'
input/*
output/*
models/*
__pycache__/
*.pyc
.DS_Store
EOFGITIGNORE

# 9. 提交到Git
echo "📤 提交到Git..."
git add .
git commit -m "Initial commit: GPU-accelerated OCR with GOT-OCR 2.0"
git branch -M main

echo ""
echo "✅ 安装完成！"
echo ""
echo "📋 下一步："
echo ""
echo "1. 推送到GitHub:"
echo "   cd ~/ocr"
echo "   git push -u origin main"
echo ""
echo "2. 安装NVIDIA Container Toolkit（如果还没装）:"
echo "   详见文档"
echo ""
echo "3. 构建Docker镜像:"
echo "   docker-compose -f docker-compose.gpu.yml build"
echo ""
echo "4. 开始使用:"
echo "   cp your_file.pptx input/"
echo "   docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu \\"
echo "       python /app/scripts/ppt_to_markdown_gpu.py /input/your_file.pptx /output"
echo ""
