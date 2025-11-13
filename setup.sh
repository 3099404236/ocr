#!/bin/bash
# 在你的Linux电脑上执行这个脚本来设置OCR项目

set -e

echo "🚀 开始设置OCR项目..."
echo ""

# 检查是否在ocr目录中
if [ ! -d ".git" ]; then
    echo "❌ 请先克隆GitHub仓库："
    echo "   cd ~"
    echo "   git clone https://github.com/3099404236/ocr.git"
    echo "   cd ocr"
    echo "   然后再运行此脚本"
    exit 1
fi

echo "📁 创建目录结构..."
mkdir -p scripts input output models

echo "📝 下载文件..."

# 下载所有文件
FILES=(
    "Dockerfile.gpu"
    "docker-compose.gpu.yml"
    "scripts/ppt_to_markdown_gpu.py"
    "scripts/batch_convert_gpu.sh"
    "README.md"
    "QUICKSTART_GPU.md"
    "OCR_COMPARISON.md"
    ".gitignore"
)

BRANCH="claude/linux-commands-help-011CV5EDUFPERGoDrUGuDPne"
BASE_URL="https://raw.githubusercontent.com/3099404236/ocr/$BRANCH"

for file in "${FILES[@]}"; do
    echo "  下载 $file ..."
    curl -fsSL "$BASE_URL/$file" -o "$file" 2>/dev/null || echo "    ⚠️  文件暂时无法下载，稍后重试"
done

echo ""
echo "✅ 设置完成！"
echo ""
echo "📋 下一步："
echo "1. 安装NVIDIA Container Toolkit（如果还没装）"
echo "2. 构建Docker镜像: docker-compose -f docker-compose.gpu.yml build"
echo "3. 开始使用！详见 QUICKSTART_GPU.md"
echo ""
