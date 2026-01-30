#!/bin/bash

# 检查是否提供了参数
if [ $# -ne 1 ]; then
    echo "用法: $0 <input_directory>"
    exit 1
fi

input_dir="$1"

# 检查输入目录是否存在
if [ ! -d "$input_dir" ]; then
    echo "错误: 输入目录 '$input_dir' 不存在"
    exit 1
fi

# 创建输出目录
mkdir -p output

# 处理输入目录中的所有图片文件
for img in "$input_dir"/*; do
    # 检查是否为文件且是图片格式
    if [ -f "$img" ] && [[ "$img" =~ \.(jpg|jpeg|png|gif|bmp|tiff)$ ]]; then
        filename=$(basename "$img")
        
        # 使用magick命令处理图片，保持白底黑线条
        magick "$img" \
            -modulate 100,80,120 \
            -level 5%,95%,1.2 \
            -colorspace Gray \
            "output/$filename.png"
        
        echo "已处理: $filename -> clean_$filename"
    fi
done

echo "批量处理完成！结果保存在 'output' 文件夹中。"