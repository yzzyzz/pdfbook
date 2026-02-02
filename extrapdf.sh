#!/bin/bash

# 配置参数
SRC_PDF=$1
DST_DIR=$2

rm -rf $DST_DIR/*
# 检查参数
if [ $# -ne 2 ]; then
    echo "用法: $0 <src_pdf> <dst_dir>"
    exit 1
fi

# 检查源文件是否存在
if [ ! -f "$SRC_PDF" ]; then
    echo "错误: 源PDF文件 '$SRC_PDF' 不存在"
    exit 1
fi

# 检查目标目录是否存在，不存在则创建
if [ ! -d "$DST_DIR" ]; then
    mkdir -p "$DST_DIR"
    if [ $? -ne 0 ]; then
        echo "错误: 无法创建目录 '$DST_DIR'"
        exit 1
    fi
fi

echo "开始从 '$SRC_PDF' 提取图片到目录 '$DST_DIR'..."

# 使用 pdfimages 工具提取图片
# -j 参数表示同时提取 JPEG 图片
pdfimages -all "$SRC_PDF" "$DST_DIR/pic"

# 检查是否成功执行
if [ $? -eq 0 ]; then
    # 统计提取的图片数量
    IMAGE_COUNT=$(ls "$DST_DIR" | grep -E "\.(ppm|jpg|png|pbm)$" | wc -l)
    echo "图片提取完成！"
    echo "源文件: $SRC_PDF"
    echo "目标目录: $DST_DIR"
    echo "提取图片数量: $IMAGE_COUNT"
    
    # 列出提取的所有图片
    echo "提取的图片列表:"
    ls -la "$DST_DIR" | grep -E "\.(ppm|jpg|png|pbm)$"
else
    echo "错误: 提取图片失败"
    exit 1
fi