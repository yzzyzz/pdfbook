from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5, A4, A6, A3, landscape
from reportlab.lib.units import mm
from PIL import Image
from reportlab.pdfbase import pdfmetrics

import os
import sys
import re

zhongxianspace = 18
book_name = "脚气"
pagesize = A4
def split_text_for_vertical_display(text):
    """
    将文本拆分为垂直显示的元素，但保持数字作为一个整体
    """
    import re
    # 使用正则表达式将数字组合和非数字字符分开
    parts = re.split(r'(\d+)', text)
    result = []
    for part in parts:
        if part.isdigit():
            # 如果是数字，作为一个整体添加
            result.append(part)
        else:
            # 如果不是数字，按字符拆分
            result.extend(list(part))
    return result


# 注册中文字体
try:
    # 尝试使用系统字体
    from reportlab.pdfbase.pdfmetrics import registerFont
    from reportlab.pdfbase.ttfonts import TTFont

    # 尝试注册常见中文字体
    font_registered = False
    common_fonts = [
        # "AlibabaPuHuiTi-3-55-RegularL3.ttf",  # macOS
        "FZXSS-Lusitana-Hybrid.ttf",  # macOS
    ]

    for font_path in common_fonts:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
            font_registered = True
            print(f"提示：已自动注册字体 '{font_path}'")
            break
    if not font_registered:
        # 如果没有找到合适的字体，使用默认字体
        DEFAULT_FONT = "Helvetica"
    else:
        DEFAULT_FONT = "ChineseFont"

except:
    DEFAULT_FONT = "Helvetica"


def generate_pdf_from_images(input_path: str, output_pdf: str, pagesize=A4):
    """
    在横版A4纸上绘制图片
    :param input_path: 输入路径（可以是单个图片文件或图片文件夹）
    :param output_pdf: 输出PDF文件的完整路径
    :param pagesize: PDF页面尺寸，默认A4横版
    """
    # --------------- 第一步：参数校验 ---------------
    if not os.path.exists(input_path):
        raise ValueError(f"错误：输入路径 '{input_path}' 不存在！")

    # A5高度和宽度作为参考尺寸
    a6_height = A6[1]  # A5竖版的高度
    a6_width = A6[0]  # A5的宽度

    landscape_pagesize = landscape(pagesize)  # 横向A4: 297mm x 210mm
    page_width, page_height = landscape_pagesize  # 获取页面尺寸（单位：点，1点=1/72英寸）
    # 检查输出PDF路径的父目录是否存在（不存在则创建）
    output_dir = os.path.dirname(output_pdf)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"提示：已自动创建输出目录 '{output_dir}'")
        # 初始化PDF画布
    c = canvas.Canvas(output_pdf, pagesize=landscape_pagesize)
    # 设置页面边距
    margin = 0  # 页面边距
    current_x = margin  # 当前绘制的x坐标
    current_y = page_height - margin  # 当前绘制的y坐标（从页面顶部开始）

    # 检查输入路径是文件夹还是单个图片文件
    if os.path.isdir(input_path):
        image_folder = input_path
        # 检查输出PDF路径的父目录是否存在（不存在则创建）
        output_dir = os.path.dirname(output_pdf)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"提示：已自动创建输出目录 '{output_dir}'")

        # --------------- 第二步：筛选有效图片（从文件夹） ---------------
        # 支持的图片格式
        valid_image_ext = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp',
                           '.webp')
        # 遍历文件夹，筛选图片文件并按文件名排序
        image_files = []
        for filename in os.listdir(image_folder):
            file_path = os.path.join(image_folder, filename)
            # 跳过目录，只处理文件
            if os.path.isfile(file_path) and filename.lower().endswith(
                    valid_image_ext):
                image_files.append(file_path)

        # 按文件名自然排序（保证图片顺序可控）
        image_files.sort(key=lambda x: os.path.basename(x))

        # 检查是否有有效图片
        if not image_files:
            raise RuntimeError(f"错误：文件夹 '{image_folder}' 中未找到任何有效图片！")
        print(f"提示：从文件夹中找到 {len(image_files)} 张有效图片")

        text_x = 0
        # 处理所有图片
        for i, image_file in enumerate(image_files):
            # 打开图片并获取尺寸（自动处理EXIF旋转）
            with Image.open(image_file) as img:
                # 修正图片旋转（解决部分手机拍摄图片旋转问题）
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif is not None:
                        orientation = exif.get(0x0112, 1)
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)

                img_w, img_h = img.size

            # 计算缩放比例，保持宽高比
            scale_w = a6_width / img_w
            scale_h = a6_height / img_h
            scale = min(scale_w, scale_h)
            scaled_w = img_w * scale
            scaled_h = img_h * scale

            # 绘制图片
            c.drawImage(
                image_file,
                x=current_x,
                y=(a6_height - scaled_h) / 2,  # 从当前y位置向下绘制
                width=scaled_w,
                height=scaled_h,
                preserveAspectRatio=True,
                mask='auto')

            print(
                f"绘制第 {i+1} 张图片: {os.path.basename(image_file)} 位置: x={current_x:.2f}, y={current_y - scaled_h:.2f}"
            )

            # 更新下一个图片的x坐标
            space_points = zhongxianspace * 72 / 25.4
            if text_x == 0:
                text_x = a6_width + 5
            current_x += (a6_width + space_points)  # 加10点间距

        # 保存PDF文件

        # 绘制文字：
        # 绘制垂直方向的文字
        text_elements = split_text_for_vertical_display(book_name)
        font_size = int(zhongxianspace * 1.4)
        char_height = font_size + 2  # 字体大小 + 行间距
        c.setFont(DEFAULT_FONT, font_size)
        # 计算起始y坐标，考虑数字组合可能占用更多垂直空间
        start_y = (scaled_h / 2) + (len(text_elements) * char_height / 2) - 14

        # 绘制每个元素（数字组合或单个字符）
        print(text_elements)
        for j, element in enumerate(text_elements):
            char_y = start_y - j * char_height
            centered_x = text_x
            c.drawString(centered_x, char_y, element)

        c.save()
        print(f"\n✅ PDF生成完成！")
        print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
        print(f"📄 页面尺寸：A4横版")

    elif os.path.isfile(input_path):
        # 输入是单个图片文件
        file_ext = os.path.splitext(input_path)[1].lower()
        valid_image_ext = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp',
                           '.webp')

        if file_ext not in valid_image_ext:
            raise ValueError(f"错误：输入文件 '{input_path}' 不是有效的图片格式！")

        with Image.open(input_path) as img:
            img_w, img_h = img.size
            # 计算缩放比例，保持宽高比
            scale_h = a6_height / img_h
            scaled_w = img_w * scale_h
            scaled_h = img_h * scale_h
            # 绘制图片
            c.drawImage(
                input_path,
                x=current_x,
                y=(a6_height - scaled_h) / 2,  # 从当前y位置向下绘制
                width=scaled_w,
                height=scaled_h,
                preserveAspectRatio=True,
                mask='auto')

        c.save()

    else:
        raise ValueError(f"错误：输入路径 '{input_path}' 既不是文件夹也不是文件！")


# --------------- 命令行调用入口 ---------------
if __name__ == "__main__":
    # 检查命令行参数数量
    if len(sys.argv) != 3:
        print("❌ 参数错误！正确用法：")
        print(f"1. python {os.path.basename(__file__)} <图片文件夹路径> <输出PDF文件路径>")
        print(f"2. python {os.path.basename(__file__)} <单个图片文件路径> <输出PDF文件路径>")
        print("示例：")
        print(f"python {os.path.basename(__file__)} ./images ./output.pdf")
        print(f"python {os.path.basename(__file__)} ./image.jpg ./output.pdf")
        sys.exit(1)

    # 获取命令行参数
    input_path = sys.argv[1]
    output_file = sys.argv[2]

    # 执行PDF生成
    try:
        generate_pdf_from_images(input_path, output_file)
    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)}")
        sys.exit(1)
