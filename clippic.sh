#!/bin/bash

# 裁剪图片上下纯白部分的函数，保存为PNG格式
crop_white_borders() {
    local input_dir="$1"
    local output_dir="$2"
    
    # 检查输入参数
    if [ -z "$input_dir" ]; then
        echo "错误: 请输入源图片文件夹路径"
        echo "用法: crop_white_borders <源文件夹> [输出文件夹]"
        return 1
    fi
    
    # 如果没有指定输出目录，则在源目录下创建cropped子目录
    if [ -z "$output_dir" ]; then
        output_dir="${input_dir}/cropped"
    fi
    
    # 检查源目录是否存在
    if [ ! -d "$input_dir" ]; then
        echo "错误: 源目录 '$input_dir' 不存在"
        return 1
    fi
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    # 支持的图片格式
    local image_extensions=("jpg" "jpeg" "png" "bmp" "tiff" "webp")
    
    echo "开始处理图片..."
    echo "源目录: $input_dir"
    echo "输出目录: $output_dir"
    
    local processed_count=0
    local failed_count=0
    
    # 遍历所有支持的图片格式
    for ext in "${image_extensions[@]}"; do
        # 查找当前格式的所有图片文件
        while IFS= read -r -d '' file; do
            if [ -f "$file" ]; then
                local filename=$(basename "$file")
                # 更改扩展名为.png
                local basename="${filename%.*}"
                local output_file="$output_dir/${basename}.png"
                
                echo "正在处理: $filename -> ${basename}.png"
                
                # 使用ImageMagick裁剪掉上下纯白部分，保存为PNG格式
                # -trim 裁剪边缘的相同颜色
                # -fuzz 5% 容忍轻微的颜色差异
                if magick "$file" -fuzz 30% -trim +repage PNG:"$output_file"; then
                    echo "  ✓ 处理成功: $filename -> ${basename}.png"
                    ((processed_count++))
                else
                    echo "  ✗ 处理失败: $filename"
                    ((failed_count++))
                fi
            fi
        done < <(find "$input_dir" -iname "*.$ext" -print0 2>/dev/null)
    done
    
    echo ""
    echo "处理完成!"
    echo "成功处理: $processed_count 张图片"
    echo "处理失败: $failed_count 张图片"
    echo "输出目录: $(realpath "$output_dir")"
}

# 只裁剪顶部和底部白色边框的函数，保存为PNG格式
crop_top_bottom_whitespace() {
    local input_dir="$1"
    local output_dir="$2"
    local fuzz_value="${3:-5%}"  # 默认容差为5%
    
    # 检查输入参数
    if [ -z "$input_dir" ]; then
        echo "错误: 请输入源图片文件夹路径"
        echo "用法: crop_top_bottom_whitespace <源文件夹> [输出文件夹] [容差值]"
        return 1
    fi
    
    # 如果没有指定输出目录，则在源目录下创建cropped子目录
    if [ -z "$output_dir" ]; then
        output_dir="${input_dir}/cropped"
    fi
    
    # 检查源目录是否存在
    if [ ! -d "$input_dir" ]; then
        echo "错误: 源目录 '$input_dir' 不存在"
        return 1
    fi
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    echo "开始处理图片 (仅裁剪上下白色边框)..."
    echo "源目录: $input_dir"
    echo "输出目录: $output_dir"
    echo "容差值: $fuzz_value"
    
    local processed_count=0
    local failed_count=0
    
    # 查找所有图片文件
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            # 更改扩展名为.png
            local basename="${filename%.*}"
            local output_file="$output_dir/${basename}.png"
            
            echo "正在处理: $filename -> ${basename}.png"
            
            # 只裁剪顶部和底部的白色区域，保存为PNG格式
            if magick "$file" \
                -fuzz "$fuzz_value" \
                -set option:area "%[fx:w*h]" \
                -trim \
                -set option:trim:area "%[fx:w*h]" \
                -format "%[h]\n" \
                info: >/dev/null 2>&1; then
                
                # 获取原始尺寸和裁剪后尺寸
                local orig_height=$(magick "$file" -format "%h" info:)
                local trimmed_height=$(magick "$file" -fuzz "$fuzz_value" -trim -format "%h" info: 2>/dev/null)
                
                if [ -n "$trimmed_height" ] && [ "$trimmed_height" -lt "$orig_height" ]; then
                    # 如果高度减小了，说明有白色边框被裁剪
                    magick "$file" -fuzz "$fuzz_value" -trim +repage PNG:"$output_file"
                    echo "  ✓ 裁剪完成: $filename -> ${basename}.png"
                else
                    # 没有白色边框，直接转换为PNG
                    magick "$file" PNG:"$output_file"
                    echo "  → 转换格式: $filename -> ${basename}.png"
                fi
                
                ((processed_count++))
            else
                echo "  ✗ 处理失败: $filename"
                ((failed_count++))
            fi
        fi
    done < <(find "$input_dir" \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.webp" \) -print0 2>/dev/null)
    
    echo ""
    echo "处理完成!"
    echo "成功处理: $processed_count 张图片"
    echo "处理失败: $failed_count 张图片"
    echo "输出目录: $(realpath "$output_dir")"
}

# 更精确的上下白边裁剪函数，保存为PNG格式
precise_crop_white_borders() {
    local input_dir="$1"
    local output_dir="$2"
    local fuzz_value="${3:-3%}"  # 默认容差为3%
    
    # 检查输入参数
    if [ -z "$input_dir" ]; then
        echo "错误: 请输入源图片文件夹路径"
        echo "用法: precise_crop_white_borders <源文件夹> [输出文件夹] [容差值]"
        return 1
    fi
    
    # 如果没有指定输出目录，则在源目录下创建cropped子目录
    if [ -z "$output_dir" ]; then
        output_dir="${input_dir}/cropped"
    fi
    
    # 检查源目录是否存在
    if [ ! -d "$input_dir" ]; then
        echo "错误: 源目录 '$input_dir' 不存在"
        return 1
    fi
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    echo "开始精确裁剪上下白色边框..."
    echo "源目录: $input_dir"
    echo "输出目录: $output_dir"
    echo "容差值: $fuzz_value"
    
    local processed_count=0
    local failed_count=0
    
    # 查找所有图片文件
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            # 更改扩展名为.png
            local basename="${filename%.*}"
            local output_file="$output_dir/${basename}.png"
            
            echo "正在处理: $filename -> ${basename}.png"
            
            # 使用更精确的方法裁剪上下白边，保存为PNG格式
            if magick "$file" \
                -fuzz "$fuzz_value" \
                -bordercolor white \
                -border 1x0 \
                -trim \
                -shave 1x0 \
                +repage \
                PNG:"$output_file"; then
                
                echo "  ✓ 裁剪完成: $filename -> ${basename}.png"
                ((processed_count++))
            else
                echo "  ✗ 处理失败: $filename"
                ((failed_count++))
            fi
        fi
    done < <(find "$input_dir" \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.webp" \) -print0 2>/dev/null)
    
    echo ""
    echo "处理完成!"
    echo "成功处理: $processed_count 张图片"
    echo "处理失败: $failed_count 张图片"
    echo "输出目录: $(realpath "$output_dir")"
}

# 裁剪四周白色空白部分的函数，保存为PNG格式
crop_all_white_borders() {
    local input_dir="$1"
    local output_dir="$2"
    local fuzz_value="${3:-5%}"  # 默认容差为5%
    
    # 检查输入参数
    if [ -z "$input_dir" ]; then
        echo "错误: 请输入源图片文件夹路径"
        echo "用法: crop_all_white_borders <源文件夹> [输出文件夹] [容差值]"
        return 1
    fi
    
    # 如果没有指定输出目录，则在源目录下创建cropped子目录
    if [ -z "$output_dir" ]; then
        output_dir="${input_dir}/cropped"
    fi
    
    # 检查源目录是否存在
    if [ ! -d "$input_dir" ]; then
        echo "错误: 源目录 '$input_dir' 不存在"
        return 1
    fi
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    echo "开始裁剪图片四周白色边框..."
    echo "源目录: $input_dir"
    echo "输出目录: $output_dir"
    echo "容差值: $fuzz_value"
    
    local processed_count=0
    local failed_count=0
    
    # 查找所有图片文件
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            # 更改扩展名为.png
            local basename="${filename%.*}"
            local output_file="$output_dir/${basename}.png"
            
            echo "正在处理: $filename -> ${basename}.png"
            
            # 裁剪四周的白色区域，保存为PNG格式
            if magick "$file" \
                -fuzz "$fuzz_value" \
                -trim \
                +repage \
                PNG:"$output_file"; then
                
                echo "  ✓ 裁剪完成: $filename -> ${basename}.png"
                ((processed_count++))
            else
                echo "  ✗ 处理失败: $filename"
                ((failed_count++))
            fi
        fi
    done < <(find "$input_dir" \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.webp" \) -print0 2>/dev/null)
    
    echo ""
    echo "处理完成!"
    echo "成功处理: $processed_count 张图片"
    echo "处理失败: $failed_count 张图片"
    echo "输出目录: $(realpath "$output_dir")"
}

# 调用函数处理图片
crop_white_borders $1 $2