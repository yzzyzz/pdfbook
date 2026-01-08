#!/bin/bash

function splitpic() {
    local src_dir="$1"
    local dst_dir="$2"

    # 检查参数
    if [ -z "$src_dir" ] || [ -z "$dst_dir" ]; then
        echo "用法: splitpic <src_dir> <dst_dir>"
        return 1
    fi

    # 检查源目录是否存在
    if [ ! -d "$src_dir" ]; then
        echo "错误: 源目录 '$src_dir' 不存在"
        return 1
    fi

    # 创建目标目录
    mkdir -p "$dst_dir"

    # 检查ImageMagick是否已安装
    if ! command -v convert &> /dev/null && ! command -v magick &> /dev/null; then
        echo "错误: ImageMagick 未安装，请先安装ImageMagick"
        return 1
    fi

    # 定义支持的图片格式
    local img_extensions=("*.jpg" "*.jpeg" "*.png" "*.bmp" "*.tiff" "*.gif")

    # 设置fuzz值，用于定义"白色"的范围
    local fuzz_value="50%"

    # 遍历源目录中的所有图片文件，按文件名排序
    for img_ext in "${img_extensions[@]}"; do
        for img_file in $(find "$src_dir" -maxdepth 1 -name "$img_ext" -type f | sort); do
            if [ -f "$img_file" ]; then
                local filename=$(basename -- "$img_file")
                local filename_no_ext="${filename%.*}"
                
                echo "正在处理: $filename"

                # 获取图片尺寸
                local width=$(identify -format "%w" "$img_file")
                local height=$(identify -format "%h" "$img_file")
                
                # 判断是横图还是竖图（宽度大于高度为横图）
                if [ "$width" -le "$height" ]; then
                    echo "检测到竖图，仅复制: $filename"
                    cp "$img_file" "${dst_dir}/${filename}"
                else
                    # 横图进行分割处理
                    echo "检测到横图，进行分割处理: $filename"
                    
                    local half_width=$((width / 2))

                    # 分割图片为左右两部分，输出为PNG格式
                    local left_part="${dst_dir}/${filename_no_ext}-2.png"
                    local right_part="${dst_dir}/${filename_no_ext}-1.png"
                    
                    # 分割图片
                    convert "$img_file" -crop ${half_width}x+0+0 +repage "${dst_dir}/temp_left.png"
                    convert "$img_file" -crop ${half_width}x+${half_width}+0 +repage "${dst_dir}/temp_right.png"
                    
                    # 使用magick命令移除白色边缘并保存为PNG格式
                    if magick "${dst_dir}/temp_left.png" \
                        -fuzz "$fuzz_value" \
                        -trim \
                        +repage \
                        PNG:"$left_part"; then
                        echo "左半部分处理成功: $left_part"
                    else
                        echo "左半部分处理失败，使用默认输出"
                        mv "${dst_dir}/temp_left.png" "$left_part"
                    fi

                    if magick "${dst_dir}/temp_right.png" \
                        -fuzz "$fuzz_value" \
                        -trim \
                        +repage \
                        PNG:"$right_part"; then
                        echo "右半部分处理成功: $right_part"
                    else
                        echo "右半部分处理失败，使用默认输出"
                        mv "${dst_dir}/temp_right.png" "$right_part"
                    fi

                    # 清理临时文件
                    rm -f "${dst_dir}/temp_left.png" "${dst_dir}/temp_right.png"
                fi

                echo "完成处理: $filename"
            fi
        done
    done

    echo "所有图片处理完成！"
}

# 如果直接运行此脚本，执行splitpic函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -ne 2 ]; then
        echo "用法: $0 <src_dir> <dst_dir>"
        exit 1
    fi
    splitpic "$1" "$2"
fi