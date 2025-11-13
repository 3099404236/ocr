#!/bin/bash
# 批量转换input目录下的所有PPT/PDF文件

INPUT_DIR="/input"
OUTPUT_DIR="/output"

echo "开始批量转换..."
echo "输入目录: $INPUT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 查找所有支持的文件
find "$INPUT_DIR" -type f \( -iname "*.ppt" -o -iname "*.pptx" -o -iname "*.pdf" \) | while read file; do
    echo "========================================"
    echo "处理文件: $(basename "$file")"
    echo "========================================"
    python /app/scripts/ppt_to_markdown.py "$file" "$OUTPUT_DIR"
    echo ""
done

echo "✅ 批量转换完成!"
