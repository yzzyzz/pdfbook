#!/bin/bash

# 检查是否传入了3个必传参数
if [ $# -ne 3 ]; then
    echo -e "\033[31m【错误】参数输入错误！正确用法如下：\033[0m"
    echo "bash $0 [图片源目录src] [目标保存目录dst] [旋转度数]"
    echo "示例：bash $0 ./my_images ./rotated_images 90"
    echo "支持的旋转度数：任意整数（如90、180、270、-90、45 均可）"
    exit 1
fi

# 接收传入的三个参数
SRC_DIR="$1"
DST_DIR="$2"
ROTATE_DEG="$3"

# 检查 imagemagick 的 convert 命令是否安装
if ! command -v convert &> /dev/null; then
    echo -e "\033[31m【错误】未检测到 imagemagick！请先安装：\033[0m"
    echo "Ubuntu/Debian 安装：sudo apt update && sudo apt install imagemagick -y"
    echo "CentOS/RHEL 安装：sudo yum install ImageMagick -y"
    echo "Mac 安装：brew install imagemagick"
    exit 1
fi

# 检查源目录是否存在
if [ ! -d "$SRC_DIR" ]; then
    echo -e "\033[31m【错误】源目录 $SRC_DIR 不存在！\033[0m"
    exit 1
fi

# 自动创建目标目录（包含父目录，不存在则创建，存在则无操作）
mkdir -p "$DST_DIR"

# 核心逻辑：递归遍历源目录所有图片 + 批量旋转 + 输出到目标目录
# 支持的图片格式：jpg jpeg png bmp gif webp tiff 主流格式全覆盖
# 核心逻辑：递归遍历源目录所有图片 + 批量旋转 + 输出到目标目录并转换为PNG
# 支持的图片格式：jpg jpeg png bmp gif webp tiff 主流格式全覆盖
find "$SRC_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" -o -iname "*.gif" -o -iname "*.webp" -o -iname "*.tiff" \) | while read -r img_path
do
    # 获取图片的纯文件名（不含扩展名）
    img_name_no_ext=$(basename "$img_path" .${img_path##*.})
    # 目标文件完整路径（强制使用.png扩展名）
    dst_img="$DST_DIR/${img_name_no_ext}.png"
    
    # 使用 imagemagick 的 convert 命令旋转图片并转换为PNG，核心命令
    # -rotate $ROTATE_DEG ：旋转指定度数，正数顺时针，负数逆时针
    # -define png:compression-level=1 : 设置PNG压缩级别为1(较高质量)
    # 旋转后自动适配画布大小，不会裁剪图片
    convert "$img_path" -rotate "$ROTATE_DEG" -define png:compression-level=1 "$dst_img"
    
    # 输出成功日志
    if [ $? -eq 0 ]; then
        echo -e "\033[32m✅ 处理成功：\033[0m $(basename "$img_path")  ->  $(basename "$dst_img") (旋转 $ROTATE_DEG 度数，转为PNG)"
    else
        echo -e "\033[31m❌ 处理失败：\033[0m $img_path"
    fi
done

# 执行完成提示
echo -e "\n\033[36m============================================\033[0m"
echo -e "\033[32m🎉 批量旋转完成！所有图片已保存至：$DST_DIR \033[0m"
echo -e "\033[36m============================================\033[0m"
