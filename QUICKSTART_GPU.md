# GPU版快速使用指南 - GOT-OCR 2.0

## 🎮 GPU版本优势

使用GOT-OCR 2.0 GPU版本，相比CPU版本：
- ⚡ **速度提升**: 10-50倍加速
- 🎯 **更高精度**: 可以使用更高DPI (200-300)
- 🚀 **批量处理**: 22GB显存可以处理更大的批量
- 🧠 **更先进**: GOT-OCR 2.0是2024年最新的OCR-2.0架构

## 📋 前置要求

1. **NVIDIA GPU** (你有22GB显存，完美！)
2. **NVIDIA驱动** (>= 525.60.13)
3. **Docker + NVIDIA Container Toolkit**

### 安装NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# 验证安装
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## 🚀 快速开始 (GPU版)

### 第一步: 构建GPU镜像

```bash
cd ~/ocr

# 构建GPU版本Docker镜像 (第一次需要10-15分钟)
docker-compose -f docker-compose.gpu.yml build

# 镜像会自动下载GOT-OCR 2.0模型 (~1.4GB)
```

### 第二步: 验证GPU可用

```bash
# 测试GPU是否可用
docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu nvidia-smi

# 应该能看到你的GPU信息
```

### 第三步: 转换文件

```bash
# 放入文件
mkdir -p input output
cp ~/Documents/课件.pptx input/

# 转换单个文件 (GPU加速)
docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu \
    python /app/scripts/ppt_to_markdown_gpu.py /input/课件.pptx /output

# 批量转换
docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu \
    bash /app/scripts/batch_convert_gpu.sh
```

### 第四步: 查看结果

```bash
ls -lh output/
cat output/课件.md
```

## ⚡ 性能对比

### CPU版本 (Marker + Surya):
- 单页: ~3-5秒
- 10页PPT: ~30-50秒
- 100页PDF: ~5-10分钟

### GPU版本 (GOT-OCR 2.0):
- 单页: ~0.3-0.8秒 ⚡
- 10页PPT: ~3-8秒 ⚡
- 100页PDF: ~30-80秒 ⚡

**速度提升约10-15倍！**

## 🎯 GOT-OCR 2.0 特点

### 技术优势:
1. **OCR-2.0架构**
   - 高压缩编码器 (处理高分辨率图像)
   - 长上下文解码器 (理解文档结构)

2. **原生格式输出**
   - 直接输出Markdown格式
   - 保留文档结构 (标题、列表、表格)
   - 支持数学公式 (LaTeX)

3. **多场景支持**
   - 印刷体文本
   - 手写文字
   - 数学公式
   - 表格和图表
   - 多语言 (中英文优秀)

4. **轻量高效**
   - 仅580M参数
   - 只需4GB显存
   - 你的22GB显存可以同时处理多个文件

## 🔧 高级配置

### 调整DPI (影响识别质量)

编辑 `scripts/ppt_to_markdown_gpu.py`:

```python
images = convert_from_path(pdf_path, dpi=200)  # 改为300提高质量，改为150加快速度
```

### 选择OCR模式

GOT-OCR 2.0支持两种模式:

```python
# 格式化模式 (推荐) - 保留文档格式
result = model.chat(tokenizer, image_path, ocr_type='format')

# 纯文本模式 - 只提取文字
result = model.chat(tokenizer, image_path, ocr_type='plain')
```

### 多GPU并行处理

如果你有多块GPU，可以修改 `docker-compose.gpu.yml`:

```yaml
environment:
  - CUDA_VISIBLE_DEVICES=0,1  # 使用GPU 0和1
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 2  # 使用2块GPU
          capabilities: [gpu]
```

## 📊 显存使用

| 任务 | GOT-OCR 2.0 | PaddleOCR GPU | 剩余显存 |
|------|-------------|---------------|----------|
| 模型加载 | ~4GB | ~2GB | ~16GB |
| 单页处理 | +0.5GB | +0.5GB | ~17.5GB |
| 峰值 | ~5GB | ~3GB | ~17GB |

你的22GB显存完全够用，还有很大余量！

## 🐛 故障排除

### 问题1: CUDA out of memory

虽然不太可能（GOT-OCR很轻量），但如果遇到：

```bash
# 降低DPI
images = convert_from_path(pdf_path, dpi=150)

# 或在每页处理后清理缓存（脚本中已包含）
torch.cuda.empty_cache()
```

### 问题2: 找不到GPU

```bash
# 检查Docker是否能访问GPU
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# 检查NVIDIA Container Toolkit
sudo systemctl status docker
nvidia-container-cli info
```

### 问题3: 模型下载慢

```bash
# 使用镜像站点 (中国大陆)
export HF_ENDPOINT=https://hf-mirror.com

# 然后重新构建
docker-compose -f docker-compose.gpu.yml build
```

## 💡 最佳实践

1. **首次运行**: 第一次会下载模型，需要等待
2. **模型缓存**: 模型会缓存在 `./models` 目录，下次启动更快
3. **批量处理**: 使用批量脚本一次处理多个文件
4. **监控GPU**: 使用 `nvidia-smi -l 1` 实时监控GPU使用

## 🎉 一键运行脚本

创建快捷脚本:

```bash
cat > ~/ocr/convert_gpu.sh << 'EOF'
#!/bin/bash
cd ~/ocr

# 检查GPU
echo "🎮 GPU信息:"
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader
echo ""

if [ -z "$1" ]; then
    echo "批量转换模式..."
    docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu bash /app/scripts/batch_convert_gpu.sh
else
    echo "转换文件: $1"
    filename=$(basename "$1")
    cp "$1" input/
    docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu \
        python /app/scripts/ppt_to_markdown_gpu.py "/input/$filename" /output
fi

echo ""
echo "✅ 完成! 查看结果:"
ls -lh output/*.md | tail -5
EOF

chmod +x ~/ocr/convert_gpu.sh

# 使用:
~/ocr/convert_gpu.sh                        # 批量转换
~/ocr/convert_gpu.sh ~/Documents/课件.pptx  # 转换单个文件
```

---

**性能**: GOT-OCR 2.0在你的22GB GPU上会非常快，享受⚡光速转换吧！
