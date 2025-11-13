# 基于Python 3.11镜像 (支持最新的OCR模型)
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    libreoffice-impress \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装最新的OCR引擎
# 1. Marker (with Surya OCR) - 最佳PDF转Markdown工具
# 2. PaddleOCR - 备选，中文支持好
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    marker-pdf \
    surya-ocr \
    paddlepaddle \
    paddleocr \
    pdf2image \
    pillow \
    pypandoc \
    python-docx \
    transformers \
    accelerate

# 创建输入输出目录
RUN mkdir -p /input /output

# 设置环境变量
ENV PYTHONUNBUFFERED=1

WORKDIR /app

CMD ["/bin/bash"]
