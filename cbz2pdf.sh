#!/bin/bash
set -e  # 出错时立即退出

# 函数：显示用法
usage() {
    echo "用法: $0 <输入图片文件夹路径> [输出PDF文件名]"
    echo "示例: $0 ~/comic/images ~/comic/my_comic_a4.pdf"
    exit 1
}

# 参数校验
if [ $# -lt 1 ]; then
    usage
fi

INPUT_DIR="$1"
OUTPUT_PDF="${2:-$(basename "$INPUT_DIR")_a4_2x2.pdf}"  # 默认输出名
TMP_DIR="./tmp/cbz2pdf_$(date +%s)"  # 临时目录，避免冲突

# 函数：清理临时文件
cleanup() {
    rm -rf "$TMP_DIR"
    echo "临时文件已清理"
}
# trap cleanup EXIT  # 脚本退出时自动执行清理

# 1. 创建临时目录并复制图片文件
mkdir -p "$TMP_DIR"
echo "正在复制图片文件从目录: $INPUT_DIR"
cp "$INPUT_DIR"/* "$TMP_DIR"/ 2>/dev/null || true

# 2. 将图片处理为适合打印的PDF页面（每页2张图，旋转90度）
echo "正在处理图片为适合打印的PDF页面..."
cd "$TMP_DIR"

# 获取所有图片文件并排序
IMAGE_LIST=$(ls -1 | sort -V | grep -E '\.(jpg|jpeg|png|gif)$')

# 计数器
count=0
page=1

# 临时存储图片列表
> temp_images.txt

for img in $IMAGE_LIST; do
    echo "$img" >> temp_images.txt
    count=$((count + 1))
    
    # 每两张图片生成一个PDF页面
    if [ $((count % 2)) -eq 0 ]; then
        # 获取两张图片
        img1=$(sed -n "$((count-1))p" temp_images.txt)
        img2=$(sed -n "${count}p" temp_images.txt)
        
        # 创建一个A4页面，将两张图片垂直排列并旋转90度
        CONVERT_CMD="magick \\( \"$img1\" -resize 2480x1754\\> -background white -gravity center -extent 2480x1754 \\) \\
                \\( \"$img2\" -resize 2480x1754\\> -background white -gravity center -extent 2480x1754 \\) \\
                -append -resize 1754x2480\\> -background white -gravity center -extent 1754x2480 \\
                -rotate 90 -page 2480x3508 -units PixelsPerInch -density 300x300 \\
                \"page_${page}.pdf\""
        
        echo "执行命令: $CONVERT_CMD"
        eval $CONVERT_CMD
        page=$((page + 1))
    fi
done


# 处理剩余的单张图片
if [ $((count % 2)) -eq 1 ]; then
    img1=$(tail -n 1 temp_images.txt)
    # 单张图片放在页面中央
    convert "$img1" -resize 2480x1754\> -background white -gravity center -extent 2480x1754 \
            -rotate 90 -page A4 -units PixelsPerInch -density 300x300 \
            "page_${page}.pdf"
fi

# 清理临时文件
rm -f temp_images.txt

# 3. 合并所有页面为最终PDF
echo "正在合并页面生成最终 PDF..."
cd - >/dev/null

# 检查是否有生成的 PDF 页面
if ! ls "$TMP_DIR"/page_*.pdf >/dev/null 2>&1; then
    echo "错误：未生成任何 PDF 页面"
    exit 1
fi

gs -dBATCH -dNOPAUSE -q \
    -sDEVICE=pdfwrite \
    -sPAPERSIZE=a4 \
    -dFIXEDMEDIA \
    -dNOSAFER \
    -sOutputFile="$OUTPUT_PDF" \
    "$TMP_DIR"/page_*.pdf

# 4. 验证输出 PDF 信息
if [ -f "$OUTPUT_PDF" ]; then
    echo "转换完成！最终 PDF 信息："
    pdfinfo "$OUTPUT_PDF" | grep -E "Title|Pages|Page size"
    echo "输出文件路径: $(realpath "$OUTPUT_PDF")"
else
    echo "错误：PDF 文件生成失败"
    exit 1
fi