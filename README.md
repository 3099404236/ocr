# PPT/PDF 转 Markdown OCR 工具

这个Docker容器可以将PPT和PDF文件转换为Markdown格式，方便喂给AI处理。

## 🎮 两个版本可选

### GPU版 (推荐 - 如果你有NVIDIA GPU) ⚡
- 使用 **GOT-OCR 2.0** (580M参数，OCR-2.0架构)
- 速度快10-15倍
- 仅需4GB显存，22GB完全够用
- 详见 `QUICKSTART_GPU.md`

### CPU版 (无GPU时使用)
- 使用 **Marker + Surya OCR**
- 不需要GPU，通用性好
- 详见 `QUICKSTART.md`

## 功能特点

- ✅ PPT/PPTX → PDF → Markdown 全流程转换
- ✅ **GPU版**: GOT-OCR 2.0 (主) + PaddleOCR GPU (备选)
- ✅ **CPU版**: Marker + Surya (主) + PaddleOCR (备选)
- ✅ 支持中英文识别，中文识别准确率高
- ✅ Docker容器化，不污染主机环境
- ✅ 支持单文件和批量转换

## 快速开始

### GPU版 (推荐 - 如果有NVIDIA GPU)

```bash
cd /path/to/ocr

# 安装NVIDIA Container Toolkit (一次性)
# 详见 QUICKSTART_GPU.md

# 构建GPU版镜像
docker-compose -f docker-compose.gpu.yml build

# 转换文件
docker-compose -f docker-compose.gpu.yml run --rm ocr-converter-gpu \
    python /app/scripts/ppt_to_markdown_gpu.py /input/课件.pptx /output
```

### CPU版 (无GPU时使用)

```bash
cd /path/to/ocr

# 构建CPU版镜像
docker-compose build

# 转换文件
docker-compose run --rm ocr-converter \
    python /app/scripts/ppt_to_markdown.py /input/课件.pptx /output
```

### 2. 准备文件

将你的PPT或PDF文件放入 `input` 目录:

```bash
mkdir -p input output
cp 你的课件.pptx input/
```

### 3. 运行转换

#### 方式A: 转换单个文件

```bash
docker-compose run --rm ocr-converter python /app/scripts/ppt_to_markdown.py /input/你的课件.pptx /output
```

#### 方式B: 批量转换所有文件

```bash
docker-compose run --rm ocr-converter bash /app/scripts/batch_convert.sh
```

#### 方式C: 进入容器交互式操作

```bash
docker-compose run --rm ocr-converter bash

# 在容器内执行
python /app/scripts/ppt_to_markdown.py /input/lecture.pptx /output
```

### 4. 查看结果

转换完成后，Markdown文件会出现在 `output` 目录:

```bash
ls -lh output/
cat output/你的课件.md
```

## 目录结构

```
ocr/
├── Dockerfile              # Docker镜像定义
├── docker-compose.yml      # Docker Compose配置
├── README.md              # 本文件
├── scripts/
│   ├── ppt_to_markdown.py # 转换脚本
│   └── batch_convert.sh   # 批量转换脚本
├── input/                 # 放入你的PPT/PDF文件
└── output/                # 输出的Markdown文件
```

## OCR引擎说明 (2025年最新)

### Marker + Surya OCR (主引擎) ⭐
- 🏆 **2025年最佳PDF→Markdown开源方案**
- 🎯 专门为PDF转Markdown设计，原生支持
- 🧠 内置Surya OCR引擎 (2025年SOTA开源OCR)
- 📊 能识别文档布局、表格、数学公式
- 🌐 支持90+语言，包括中英文
- ⚡ 4倍速于Nougat，准确率与Google Cloud Vision相当
- 📈 Benchmark表现优异 (详见 OCR_COMPARISON.md)

**为什么选择Surya OCR?**
- 比Tesseract更准确 (特别是复杂布局)
- 支持多语言，中英文识别优秀
- 实际测试中在各种格式和扫描文档上表现稳定
- CPU友好 (虽然较慢，但准确率高)

### PaddleOCR (备选引擎)
- 🇨🇳 百度开源，中文识别特别强
- 🌐 支持80+语言
- 💪 在Marker失败时自动启用
- 📄 逐页处理，适合复杂文档
- 🔒 适合隐私敏感场景 (本地部署)

**双引擎策略**: Marker优先，失败时自动切换PaddleOCR，确保成功率

💡 **想了解更多?** 查看 `OCR_COMPARISON.md` 了解2025年OCR模型详细对比

## 常见问题

### Q: 转换速度慢？
A: OCR是计算密集型任务。可以：
- 减少PDF页数
- 降低图片DPI (修改 `pdf2image` 的 `dpi` 参数)
- 如果有GPU，可以修改Dockerfile启用GPU加速

### Q: 识别准确率不高？
A: 确保：
- 原始文件清晰度足够
- 中文文档使用了中文OCR模型
- 尝试调整 `confidence` 阈值 (在脚本中)

### Q: 需要GPU加速？
A: 修改 `docker-compose.yml` 添加:
```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

并在Dockerfile中安装GPU版本的PaddlePaddle。

## 命令速查表

```bash
# 构建镜像
docker-compose build

# 转换单个文件
docker-compose run --rm ocr-converter python /app/scripts/ppt_to_markdown.py /input/file.pptx /output

# 批量转换
docker-compose run --rm ocr-converter bash /app/scripts/batch_convert.sh

# 进入容器
docker-compose run --rm ocr-converter bash

# 停止并清理
docker-compose down

# 查看镜像大小
docker images | grep ocr
```

## 技术栈

- **LibreOffice**: PPT转PDF
- **Marker + Surya OCR**: PDF转Markdown (主引擎，2025年SOTA)
- **PaddleOCR**: OCR识别 (备选引擎)
- **pdf2image**: PDF转图片
- **PyTorch**: 深度学习框架
- **Python 3.11**: 主要编程语言

## 为什么这个方案是2025年最佳选择?

根据最新的OCR模型benchmark (详见 `OCR_COMPARISON.md`):

1. ✅ **使用最先进的开源OCR引擎** - Surya OCR (2025年SOTA)
2. ✅ **专为PDF→Markdown优化** - Marker是这个任务的最佳工具
3. ✅ **双引擎保障** - Marker失败时自动切换PaddleOCR
4. ✅ **中英文支持优秀** - 特别适合中文课件
5. ✅ **Docker容器化** - 不污染主机环境
6. ✅ **开源免费** - 可本地部署，保护隐私

## License

MIT
