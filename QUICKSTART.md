# 快速使用指南 - 在你的Linux电脑上执行

## 📋 前置要求

确保你的Linux系统已安装Docker和Docker Compose:

```bash
# 检查Docker是否安装
docker --version
docker-compose --version

# 如果没装，Ubuntu/Debian系统执行:
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER  # 将当前用户加入docker组
# 然后重新登录或执行: newgrp docker
```

## 🚀 三步开始使用

### 第一步: 下载并构建

```bash
# 假设你已经把这些文件放到了 ~/ocr 目录
cd ~/ocr

# 创建必要的目录
mkdir -p input output

# 构建Docker镜像 (第一次需要5-10分钟)
docker-compose build
```

### 第二步: 放入文件

```bash
# 把你的PPT或PDF文件复制到input目录
cp /path/to/your/课件.pptx ~/ocr/input/
```

### 第三步: 转换

```bash
# 批量转换input目录下的所有文件
docker-compose run --rm ocr-converter bash /app/scripts/batch_convert.sh

# 或者转换单个文件
docker-compose run --rm ocr-converter python /app/scripts/ppt_to_markdown.py /input/课件.pptx /output
```

## ✅ 查看结果

```bash
# 查看生成的markdown文件
ls -lh output/

# 查看内容
cat output/课件.md

# 或使用你喜欢的编辑器
vim output/课件.md
# nano output/课件.md
```

## 💡 实际使用示例

```bash
# 示例1: 转换一个PPT
cp ~/Documents/机器学习第一课.pptx input/
docker-compose run --rm ocr-converter python /app/scripts/ppt_to_markdown.py /input/机器学习第一课.pptx /output
cat output/机器学习第一课.md

# 示例2: 批量转换多个文件
cp ~/Documents/*.pptx input/
docker-compose run --rm ocr-converter bash /app/scripts/batch_convert.sh
ls output/

# 示例3: 转换PDF文件
cp ~/Downloads/论文.pdf input/
docker-compose run --rm ocr-converter python /app/scripts/ppt_to_markdown.py /input/论文.pdf /output
```

## 🎯 一键脚本 (推荐)

创建一个便捷脚本:

```bash
# 创建快捷命令
cat > ~/ocr/convert.sh << 'EOF'
#!/bin/bash
cd ~/ocr
if [ -z "$1" ]; then
    echo "批量转换模式..."
    docker-compose run --rm ocr-converter bash /app/scripts/batch_convert.sh
else
    echo "转换文件: $1"
    filename=$(basename "$1")
    cp "$1" input/
    docker-compose run --rm ocr-converter python /app/scripts/ppt_to_markdown.py "/input/$filename" /output
fi
echo ""
echo "✅ 完成! 查看结果:"
ls -lh output/
EOF

chmod +x ~/ocr/convert.sh

# 使用方法:
~/ocr/convert.sh                           # 批量转换input目录下所有文件
~/ocr/convert.sh ~/Documents/课件.pptx     # 转换单个文件
```

## 🔧 高级选项

### 调整OCR准确率

编辑 `scripts/ppt_to_markdown.py`，修改这一行:

```python
if confidence > 0.5:  # 改为 0.7 提高准确率，但可能丢失一些文本
```

### 调整图片质量

编辑 `scripts/ppt_to_markdown.py`，修改这一行:

```python
images = convert_from_path(pdf_path, dpi=300)  # 改为 150 加快速度，改为 600 提高质量
```

### 启用GPU加速 (如果你有NVIDIA显卡)

编辑 `Dockerfile`，将:
```dockerfile
RUN pip install --no-cache-dir paddlepaddle
```
改为:
```dockerfile
RUN pip install --no-cache-dir paddlepaddle-gpu
```

并在 `docker-compose.yml` 中添加GPU支持 (详见README.md)。

## 🧹 清理

```bash
# 清理输出文件
rm -rf output/*

# 停止并删除容器
docker-compose down

# 删除Docker镜像 (如果不再使用)
docker rmi ocr-ocr-converter
```

## ❓ 遇到问题?

1. **Permission denied**: 执行 `sudo chmod +x scripts/*.sh`
2. **Docker权限问题**: 执行 `sudo usermod -aG docker $USER` 然后重新登录
3. **中文乱码**: 确保你的终端支持UTF-8编码
4. **转换失败**: 检查input目录的文件是否损坏，尝试手动打开看看

## 📊 性能参考

- 单页PPT转换: ~2-5秒
- 10页PPT转换: ~20-50秒
- 100页PDF: ~3-10分钟

(具体取决于你的CPU性能和文档复杂度)
