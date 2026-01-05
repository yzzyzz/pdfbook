#!/bin/bash

# 定义A5竖版尺寸（标准A5：595×842像素，300DPI）
A5_WIDTH=595
A5_HEIGHT=842

# 输出目录（自动创建）
OUTPUT_DIR="test_images"
mkdir -p "$OUTPUT_DIR"

# 循环生成1-120号图片，文件名格式为0001.jpg、0002.jpg…0120.jpg
for ((num=1; num<=120; num++)); do
    # 核心：用printf格式化数字为4位，不足补零
    FILE_NAME="${OUTPUT_DIR}/$(printf "%04d" $num).jpg"
    
    # 生成随机背景色（RGB值在0-255之间）
    R=$((RANDOM % 256))
    G=$((RANDOM % 256))
    B=$((RANDOM % 256))
    
    # 生成图片 - 背景随机色，字体为白色
    convert -size "${A5_WIDTH}x${A5_HEIGHT}" \
            -fill black \
            -gravity center \
            -pointsize 100 \
            label:"$num" \
            "$FILE_NAME"
    
    # 输出进度（可选）
    echo "已生成：$FILE_NAME (背景色: RGB($R,$G,$B))"
done

echo "✅ 全部生成完成！共120张A5竖版图片，存放于：$(pwd)/$OUTPUT_DIR"