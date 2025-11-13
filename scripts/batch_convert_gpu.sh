#!/bin/bash
# GPU版批量转换脚本 - 使用GOT-OCR 2.0

INPUT_DIR="/input"
OUTPUT_DIR="/output"

echo "🚀 GPU加速批量转换 (GOT-OCR 2.0)"
echo "=================================="
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 检查GPU
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU信息:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
else
    echo "⚠️  未检测到nvidia-smi，可能无法使用GPU加速"
    echo ""
fi

# 查找所有支持的文件
find "$INPUT_DIR" -type f \( -iname "*.ppt" -o -iname "*.pptx" -o -iname "*.pdf" \) | while read file; do
    echo "========================================"
    echo "📄 处理文件: $(basename "$file")"
    echo "========================================"
    python /app/scripts/ppt_to_markdown_gpu.py "$file" "$OUTPUT_DIR"
    echo ""
done

echo "✅ 批量转换完成!"
echo ""
echo "📊 输出文件列表:"
ls -lh "$OUTPUT_DIR"/*.md 2>/dev/null || echo "未找到输出文件"
