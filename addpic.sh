#!/bin/bash

# 检查参数数量
if [ $# -ne 2 ]; then
    echo "用法: $0 <src目录> <dst目录>"
    echo "示例: $0 /path/to/src /path/to/dst"
    exit 1
fi

# 获取参数
src_dir="$1"
dst_dir="$2"

# 检查源目录是否存在
if [ ! -d "$src_dir" ]; then
    echo "错误: 源目录 '$src_dir' 不存在"
    exit 1
fi

# 检查目标目录是否存在
if [ ! -d "$dst_dir" ]; then
    echo "错误: 目标目录 '$dst_dir' 不存在"
    exit 1
fi

# 支持的图片格式
image_extensions=("jpg" "jpeg" "png" "gif" "bmp" "tiff" "webp" "JPG" "JPEG" "PNG" "GIF" "BMP" "TIFF" "WEBP")

# 统计目标目录中的图片数量
dst_count=0
for ext in "${image_extensions[@]}"; do
    dst_count=$((dst_count + $(find "$dst_dir" -maxdepth 1 -name "*.$ext" -type f | wc -l)))
done

echo "目标目录 '$dst_dir' 中现有图片数量: $dst_count"

# 获取源目录中的所有图片文件并按名称排序
src_images=()
for ext in "${image_extensions[@]}"; do
    while IFS= read -r -d '' file; do
        src_images+=("$file")
    done < <(find "$src_dir" -maxdepth 1 -name "*.$ext" -type f -print0 | sort -z)
done

# 检查是否有图片需要移动
if [ ${#src_images[@]} -eq 0 ]; then
    echo "源目录 '$src_dir' 中没有找到图片文件"
    exit 0
fi

# 排序图片文件列表（确保顺序正确）
readarray -t src_images < <(printf '%s\n' "${src_images[@]}" | sort)

echo "源目录 '$src_dir' 中找到 ${#src_images[@]} 个图片文件"

# 开始移动和重命名图片
counter=$((dst_count + 20))
for src_image in "${src_images[@]}"; do
    # 获取源文件扩展名
    extension="${src_image##*.}"
    
    # 构建目标文件名，数字部分补齐到4位
    dst_filename="$(printf "%04d.%s" $counter $extension)"
    dst_path="$dst_dir/$dst_filename"
    
    # 移动文件
    echo "移动: $(basename "$src_image") -> $dst_filename"
    mv "$src_image" "$dst_path"
    
    # 增加计数器
    counter=$((counter + 1))
done

echo "完成！共移动了 ${#src_images[@]} 个文件到目标目录。"
echo "现在目标目录中总共有 $((dst_count + ${#src_images[@]})) 个图片文件。"