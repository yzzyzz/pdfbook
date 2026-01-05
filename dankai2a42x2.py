#  单开图转a4 打印 booklet 模式 (4合一漫画)
#  输入：图片文件夹路径
#  输出：生成的PDF文件（ booklet 模式）

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from PIL import Image
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import configparser
from reportlab.lib.pagesizes import landscape

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import util


def load_config(config_file):
    """
    从配置文件加载配置
    :param config_file: 配置文件路径
    :return: 配置对象
    """
    config = configparser.ConfigParser()

    # 设置默认值
    config['page'] = {
        'print_page_size': 'A5',
        'current_a5_image_count': '1',
        'line_width': '1',
        'lr_padding': '16',
        'center_padding': '16',
        'pre_none': '0',
        'start_index_offset': '0',
        'print_page_index': 'true',
        'color_mode': '0'
    }

    # 读取配置文件
    if os.path.exists(config_file):
        config.read(config_file, encoding='utf-8')
    else:
        raise FileNotFoundError(f"配置文件 {config_file} 不存在")

    # 从配置中读取参数
    global print_page_size, CURRENT_A5_IMAGE_COUNT
    global LINE_WIDTH, lr_padding, center_padding, PRE_NONE, start_index_offset
    global print_page_index, fold_mode, A5_SEQ_MAP, color_mode

    # 读取配置参数
    page_size_name = config.get('page', 'print_page_size', fallback='A5')
    if page_size_name == 'A5':
        print_page_size = A5
    else:
        print_page_size = A4  # 默认为A4

    CURRENT_A5_IMAGE_COUNT = config.getint('page',
                                           'current_a5_image_count',
                                           fallback=1)
    LINE_WIDTH = config.getint('page', 'line_width', fallback=1)
    lr_padding = config.getint('page', 'lr_padding', fallback=16)
    center_padding = config.getint('page', 'center_padding', fallback=16)
    PRE_NONE = config.getint('page', 'pre_none', fallback=0)
    start_index_offset = config.getint('page',
                                       'start_index_offset',
                                       fallback=0)
    print_page_index = config.getboolean('page',
                                         'print_page_index',
                                         fallback=True)
    fold_mode = config.getint('page', 'fold_mode', fallback=2)
    color_mode = config.getint('page', 'color_mode', fallback=0)

    print(f"配置信息：")
    print(f"  - 页面尺寸: {page_size_name}")
    print(f"  - 每个A5页面图片数: {CURRENT_A5_IMAGE_COUNT}")
    print(f"  - 边距: 左右={lr_padding}, 中心={center_padding}")
    print(f"  - 打印页码: {print_page_index}")
    print(f"  - 页码偏移: {start_index_offset}")
    return config


def is_landscape_image(image_path):
    """
    判断图片是否为横图
    :param image_path: 图片路径
    :return: True表示横图，False表示竖图或正方形图
    """
    try:
        with Image.open(image_path) as img:
            return img.width > img.height
    except Exception as e:
        print(f"无法读取图片 {image_path}: {e}")
        return False


def split_landscape_to_portrait(image_path, output_prefix="split"):
    """
    将横图分割为两张竖图
    :param image_path: 原始横图路径
    :param output_prefix: 输出文件前缀
    :return: 两个分割后的图片路径
    """
    try:
        # 创建临时目录
        temp_dir = "temp_split_images"
        os.makedirs(temp_dir, exist_ok=True)
        with Image.open(image_path) as img:
            # 确保图片是RGB模式，以便可以保存为PNG
            if img.mode in ('P', 'PA'):
                # P模式(调色板)和PA模式(带alpha通道的调色板)需要特殊处理
                img = img.convert(
                    'RGBA') if 'transparency' in img.info else img.convert(
                        'RGB')
            elif img.mode == 'RGBA' or img.mode == 'RGB':
                # 已经是合适的模式
                pass
            else:
                # 其他模式统一转换为RGB
                img = img.convert('RGB')

            width, height = img.size
            # 计算分割点（中间位置）
            mid_point = width // 2
            # 左半部分
            left_box = (0, 0, mid_point, height)
            left_img = img.crop(left_box)
            # 生成唯一的临时文件名
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            left_path = os.path.join(temp_dir, f"{base_name}_left_temp.png")
            left_img.save(left_path, 'PNG')
            # 右半部分
            right_box = (mid_point, 0, width, height)
            right_img = img.crop(right_box)
            right_path = os.path.join(temp_dir, f"{base_name}_right_temp.png")
            right_img.save(right_path, 'PNG')
            return right_path, left_path
    except Exception as e:
        print(f"分割图片时出错 {image_path}: {e}")
        return None, None


# ==================== 配置常量 ====================
fold_mode = 2  # 1 左翻页，2 右翻页
# A5页面包含的图片数量
A5_IMAGES_1 = 1  # 每个A5页面1张图片
A5_IMAGES_2 = 2  # 每个A5页面2张图片（上下排列）
A5_IMAGES_4 = 4  # 每个A5页面4张图片（2x2排列）
# A5_SEQ_MAP = [4, 1, 2, 3]  # 左侧开始翻页
A5_SEQ_MAP = [1, 4, 3, 2]  # 右侧开始翻页
if fold_mode == 1:
    A5_SEQ_MAP = [1, 4, 3, 2]
else:
    A5_SEQ_MAP = [4, 1, 2, 3]

# 当前配置
print_page_size = A5
pagenumber_font_size = 6
CURRENT_A5_IMAGE_COUNT = A5_IMAGES_1  # 当前每个A5页面的图片数量
LINE_WIDTH = 1
lr_padding = 16
center_padding = 16
PRE_NONE = 0
start_index_offset = 0
print_page_index = True
need_A4_pages = 0
color_mode = 0  # 0 灰度模式，1 彩色模式


# 在页面中央绘制一条黑色虚线，分隔两个A5区域
def draw_center_divider_line(canvas_obj, page_width, page_height):
    """
    在页面中央绘制一条黑色虚线，用于分隔两个A5区域
    :param canvas_obj: PDF画布对象
    :param page_width: 页面宽度
    :param page_height: 页面高度
    """
    # 设置线条样式为虚线
    canvas_obj.setDash(5, 3)  # 5点实线，3点间隔

    # 设置线条颜色为黑色
    canvas_obj.setStrokeColorRGB(0, 0, 0)

    # 设置线条宽度
    clip_line_width = LINE_WIDTH
    canvas_obj.setLineWidth(clip_line_width)

    # 计算中心线的X坐标（在两个A5区域之间）
    center_x = page_width / 2 - clip_line_width // 2
    # 绘制垂直虚线
    canvas_obj.line(center_x, 0, center_x, page_height)

    # 重置线条样式为实线
    canvas_obj.setDash()


# 在适当的位置调用这个函数
def generate_pdf_from_images(image_folder: str, output_pdf: str, pagesize=A4):
    """
    基于reportlab生成适合打印成册的PDF文件（4合一漫画模式）
    :param image_folder: 存放图片的文件夹路径（必填）
    :param output_pdf: 输出PDF文件的完整路径（必填）
    :param pagesize: PDF页面尺寸，默认A4横向（297mm×210mm）
    """
    # --------------- 第一步：参数校验 ---------------
    # 检查图片文件夹是否存在
    if not os.path.isdir(image_folder):
        raise ValueError(f"错误：图片文件夹 '{image_folder}' 不存在或不是有效目录！")

    # 检查输出PDF路径的父目录是否存在（不存在则创建）
    output_dir = os.path.dirname(output_pdf)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"提示：已自动创建输出目录 '{output_dir}'")

    # --------------- 第二步：筛选有效图片 ---------------
    # 支持的图片格式（可根据需要扩展）
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

    # 检查是否有有效图片
    if not image_files:
        raise RuntimeError(f"错误：文件夹 '{image_folder}' 中未找到任何有效图片！")
    # 按文件名自然排序（保证图片顺序可控）
    image_files.sort(key=lambda x: os.path.basename(x))

    # 重新组织图片：
    # 如果是 A5_IMAGES_1 或者 A5_IMAGES_4 ，如果原始图片里面有横图，则将图片分割为2张竖图
    if CURRENT_A5_IMAGE_COUNT in [A5_IMAGES_1, A5_IMAGES_4]:
        print("检查并处理横图...")
        new_image_files = []
        for img_path in image_files:
            if is_landscape_image(img_path):
                # 如果是横图，分割为两张竖图
                left_path, right_path = split_landscape_to_portrait(img_path)
                if left_path and right_path:
                    # 添加分割后的两张图片
                    new_image_files.extend([left_path, right_path])
                    print(f"已将横图 {os.path.basename(img_path)} 分割为两张竖图")
                else:
                    # 如果分割失败，保留原图
                    new_image_files.append(img_path)
            else:
                # 竖图直接添加
                new_image_files.append(img_path)

        # 更新image_files列表
        image_files = new_image_files

    print(f"提示：共找到 {len(image_files)} 张有效图片（包含分割后的图片）")

    # 前面补None，方便后续处理
    image_files = [None] * PRE_NONE + image_files
    # --------------- 第三步：计算分组大小 ---------------
    # 根据配置计算每张A4纸包含的图片数量
    images_per_a5 = CURRENT_A5_IMAGE_COUNT
    images_per_a4_sheet = images_per_a5 * 4

    # 计算需要的总PDF页面数
    total_images = len(image_files)
    images_per_pdf_page = CURRENT_A5_IMAGE_COUNT * 2  # 每页PDF包含两个A5区域的图片
    global need_A4_pages
    need_A4_pages = (total_images + images_per_a4_sheet -
                     1) // (images_per_a4_sheet)
    total_pdf_pages_needed = need_A4_pages * 2

    print(f"配置信息：")
    print(f"  - 每个A5页面图片数: {images_per_a5}")
    print(f"  - 每张A4纸图片数: {images_per_a4_sheet}")
    print(f"  - 每页PDF图片数: {images_per_pdf_page}")
    print(f"  - 总图片数: {total_images}")
    print(f"  - 需要PDF页数: {total_pdf_pages_needed}")

    # --------------- 第四步：初始化PDF画布（横向A4） ---------------
    landscape_pagesize = landscape(pagesize)  # 横向A4: 297mm x 210mm
    c = canvas.Canvas(output_pdf, pagesize=landscape_pagesize)
    page_width, page_height = landscape_pagesize  # 获取页面尺寸（单位：点，1点=1/72英寸）

    # A5区域尺寸（每个A5区域是A4页面的一半）
    a5_width = page_width / 2
    a5_height = page_height

    # --------------- 第五步：处理每页PDF并添加到PDF ---------------
    # 迭代PDF页面而不是图片
    for pdf_page_index in range(total_pdf_pages_needed):
        draw_center_divider_line(c, page_width, page_height)

        # 确定当前页面的A5区域位置
        front_a5_x, front_a5_y = 0, 0
        back_a5_x, back_a5_y = a5_width, 0
        left_a5, right_a5 = 0, 1
        # 根据配置绘制图片
        draw_images_in_a5_region(
            canvas_obj=c,
            image_files=image_files,
            left_or_right=left_a5,  # 正面A5区域索引
            x_offset=front_a5_x,
            y_offset=front_a5_y,
            a5_width=a5_width,
            a5_height=a5_height,
            pdf_page_index=pdf_page_index)

        draw_images_in_a5_region(
            canvas_obj=c,
            image_files=image_files,
            left_or_right=right_a5,  # 背面A5区域索引
            x_offset=back_a5_x,
            y_offset=back_a5_y,
            a5_width=a5_width,
            a5_height=a5_height,
            pdf_page_index=pdf_page_index)
        print(
            f"进度：第 {pdf_page_index+1} 页PDF → 已处理PDF页面 {pdf_page_index + 1}/{total_pdf_pages_needed}"
        )
        c.showPage()

    # --------------- 第六步：保存PDF文件 ---------------
    c.showPage()
    c.save()
    print(f"\n✅ PDF生成完成！")
    print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
    print(f"📄 PDF页数：{total_pdf_pages_needed}")
    print(f"📘 打印说明：")
    print(f"   1. 横向打印A4纸张")
    print(f"   2. 每页PDF包含{images_per_pdf_page}张图片")
    print(f"   3. 打印完成后对折装订成A5册子")


# ==================== 绘图函数 ====================


def draw_images_in_a5_region(canvas_obj, image_files, left_or_right, x_offset,
                             y_offset, a5_width, a5_height, pdf_page_index):
    """
    在指定的A5区域内绘制图片，根据配置自动选择绘制方式
    :param canvas_obj: PDF画布对象
    :param image_files: 所有图片文件列表
    :param left_or_right: 0=左边A5区域, 1=右边A5区域
    :param x_offset: X偏移量
    :param y_offset: Y偏移量
    :param a5_width: A5区域宽度
    :param a5_height: A5区域高度
    :param pdf_page_index: 当前PDF页面索引
    :param images_per_pdf_page: 每页PDF包含的图片数量
    """
    global need_A4_pages
    # 根据配置选择绘制方式
    if CURRENT_A5_IMAGE_COUNT == A5_IMAGES_1:
        if color_mode == 0:  # 灰度模式
            if pdf_page_index % 2 == 0:  # 正面
                if left_or_right == 1:  # 右边
                    img_index = int(pdf_page_index)
                else:
                    img_index = need_A4_pages * 4 - int(pdf_page_index) - 1
            else:  # 反面
                if left_or_right == 1:  # 右边
                    img_index = need_A4_pages * 4 - int(pdf_page_index) - 1
                else:
                    img_index = int(pdf_page_index)
        else:  # 彩色模式
            if pdf_page_index % 2 == 0:  # 正面
                if left_or_right == 1:  # 右边
                    img_index = (pdf_page_index // 2) * 4
                else:
                    img_index = (pdf_page_index // 2) * 4 + 3
            else:  # 反面
                if left_or_right == 1:  # 右边
                    img_index = (pdf_page_index // 2) * 4 + 2
                else:
                    img_index = (pdf_page_index // 2) * 4 + 1
        img_path = image_files[img_index] if img_index < len(
            image_files) else None
        page_number = img_index + 1
        if img_path and os.path.exists(img_path):
            with Image.open(img_path) as img:
                img_w, img_h = img.size
            # 计算缩放比例（填满A5区域）
            scale_w = (a5_width - lr_padding - center_padding) / img_w
            scale_h = a5_height / img_h
            scale = min(scale_w, scale_h)
            scaled_w = img_w * scale
            scaled_h = img_h * scale

            if left_or_right == 1:
                # 背面A5区域，图片向右偏移
                x = x_offset + (a5_width - lr_padding - center_padding -
                                scaled_w) / 2 + center_padding
            else:
                # 正面A5区域，图片向左偏移
                x = x_offset + (a5_width - lr_padding - center_padding -
                                scaled_w) / 2 + lr_padding

            y = y_offset + (a5_height - scaled_h) / 2

            canvas_obj.drawImage(img_path,
                                 x=x,
                                 y=y,
                                 width=scaled_w,
                                 height=scaled_h,
                                 preserveAspectRatio=True)

            # 添加页码（如果提供了页码）
            if page_number is not None and print_page_index:
                # 设置字体和大小
                show_number = page_number - PRE_NONE + start_index_offset
                if show_number > 0:
                    canvas_obj.setFont("Helvetica", pagenumber_font_size)
                    # 设置字体颜色为黑色
                    canvas_obj.setFillColorRGB(0, 0, 0)
                    page_number_text = str(page_number - PRE_NONE +
                                           start_index_offset)
                    text_width = canvas_obj.stringWidth(
                        page_number_text, "Helvetica", pagenumber_font_size)
                    if fold_mode == 1:
                        if left_or_right == 1:
                            page_x = x_offset + 12
                        else:
                            page_x = x_offset + a5_width - text_width - 12
                    else:
                        if left_or_right == 1:
                            page_x = x_offset + 4 + center_padding
                        else:
                            page_x = x_offset + a5_width - text_width - 4 - center_padding
                    page_y = y_offset + 8
                    canvas_obj.drawString(page_x, page_y, page_number_text)

    elif CURRENT_A5_IMAGE_COUNT == A5_IMAGES_2:
        # 每个A5区域2张图片（上下排列）
        img_paths = []
        page_numbers = []

        # 计算当前A5区域对应的图片索引
        base_index = (pdf_page_index) * 2
        for i in range(2):
            img_index = base_index + i
            img_path = image_files[img_index] if img_index < len(
                image_files) else None
            img_paths.append(img_path)
            page_numbers.append(img_index if img_path else None)

        # 每个小图片区域的尺寸（上下排列）
        small_width = a5_width
        small_height = a5_height / 2

        # 上下排列的位置
        positions = [
            (0, small_height),  # 上半部分
            (0, 0)  # 下半部分
        ]

        for i, (img_path, pos,
                page_num) in enumerate(zip(img_paths, positions,
                                           page_numbers)):
            if img_path and os.path.exists(img_path):
                with Image.open(img_path) as img:
                    img_w, img_h = img.size

                # 计算缩放比例（填满小区域）
                scale_w = small_width / img_w
                scale_h = small_height / img_h
                scale = min(scale_w, scale_h)

                scaled_w = img_w * scale
                scaled_h = img_h * scale

                # 在小区域内居中
                x = x_offset + pos[0] + (small_width - scaled_w) / 2
                y = y_offset + pos[1] + (small_height - scaled_h) / 2

                canvas_obj.drawImage(img_path,
                                     x=x,
                                     y=y,
                                     width=scaled_w,
                                     height=scaled_h,
                                     preserveAspectRatio=True)

            # # 添加页码（如果提供了页码）
            # if page_num is not None:
            #     # 设置字体和大小
            #     canvas_obj.setFont("Helvetica", 10)
            #     # 设置字体颜色为黑色
            #     canvas_obj.setFillColorRGB(0, 0, 0)

            #     page_number_text = str(page_num)
            #     text_width = canvas_obj.stringWidth(page_number_text, "Helvetica", 10)

            #     # 页码放在每个小图片的右下角
            #     page_x = x_offset + pos[0] + small_width - text_width - 5
            #     page_y = y_offset + pos[1] + 5

            #     canvas_obj.drawString(page_x, page_y, page_number_text)

    elif CURRENT_A5_IMAGE_COUNT == A5_IMAGES_4:
        # 每个A5区域4张图片（2x2排列）- 使用第一张图片的4倍分辨率
        img_paths = []
        page_numbers = []

        # 计算当前A5区域对应的图片索引
        base_index = (pdf_page_index - 1) * 4
        for i in range(4):
            img_index = base_index + i
            img_path = image_files[img_index] if img_index < len(
                image_files) else None
            img_paths.append(img_path)
            page_numbers.append(img_index + 1 if img_path else None)

        print(page_numbers)
        # 每个小图片区域的尺寸（2x2网格）
        small_width = (a5_width - lr_padding - center_padding) / 2
        small_height = (a5_height) / 2

        if left_or_right == 1:
            positions = [
                (small_width + center_padding, small_height),  # 右上
                (center_padding, small_height),
                (small_width + center_padding, 0),  # 右下
                (center_padding, 0),  # 左下
            ]
        else:
            positions = [
                (small_width + lr_padding, small_height),  # 右上
                (lr_padding, small_height),
                (small_width + lr_padding, 0),  # 右下
                (lr_padding, 0),  # 左下
            ]

        # 绘制4张图片
        for i, (img_path, pos,
                page_num) in enumerate(zip(img_paths, positions,
                                           page_numbers)):
            if img_path and os.path.exists(img_path):
                with Image.open(img_path) as img:
                    img_w, img_h = img.size

                # 计算缩放比例（填满小区域）
                scale_w = small_width / img_w
                scale_h = small_height / img_h
                scale = min(scale_w, scale_h)
                scaled_w = img_w * scale
                scaled_h = img_h * scale
                # 在小区域内居中
                x = x_offset + pos[0] + (small_width - scaled_w) / 2
                y = y_offset + pos[1] + (small_height - scaled_h) / 2

                canvas_obj.drawImage(img_path,
                                     x=x,
                                     y=y,
                                     width=scaled_w,
                                     height=scaled_h,
                                     preserveAspectRatio=True)

                # 添加页码（如果提供了页码）
                if page_num is not None and print_page_index:
                    # 设置字体和大小
                    canvas_obj.setFont("Helvetica", 8)
                    # 设置字体颜色为黑色
                    canvas_obj.setFillColorRGB(0, 0, 0)
                    page_number_text = str(page_num)
                    text_width = canvas_obj.stringWidth(
                        page_number_text, "Helvetica", 8)
                    # 页码放在每个小图片的右下角
                    if left_or_right == 1:
                        page_x = x_offset + pos[0] + 5
                    else:
                        page_x = x_offset + pos[
                            0] + small_width - text_width - 5

                    page_y = y_offset + pos[1] + 3

                    canvas_obj.drawString(page_x, page_y, page_number_text)

        # 绘制分割线
        if LINE_WIDTH > 0:
            # 设置线条颜色为黑色
            canvas_obj.setStrokeColorRGB(0, 0, 0)
            # 设置线条宽度
            canvas_obj.setLineWidth(LINE_WIDTH)

            # 绘制垂直分割线
            if left_or_right == 1:
                v_line_x = x_offset + center_padding + small_width - LINE_WIDTH / 2
            else:
                v_line_x = x_offset + lr_padding + small_width - LINE_WIDTH / 2
            canvas_obj.line(v_line_x, y_offset, v_line_x, y_offset + a5_height)
            # 绘制水平分割线
            h_line_y = y_offset + small_height + LINE_WIDTH / 2
            canvas_obj.line(x_offset, h_line_y, x_offset + a5_width, h_line_y)


# --------------- 命令行调用入口 ---------------
if __name__ == "__main__":
    # 检查命令行参数数量
    if len(sys.argv) != 4:
        print("❌ 参数错误！正确用法：")
        print(
            f"python {os.path.basename(__file__)} <图片文件夹路径> <输出PDF文件路径> <配置文件路径>"
        )
        print("示例：")
        print(
            f"python {os.path.basename(__file__)} ./images ./output.pdf config.ini"
        )
        sys.exit(1)

    # 获取命令行参数
    input_folder = sys.argv[1]
    output_file = sys.argv[2]
    config_file = sys.argv[3]

    # 加载配置
    config = load_config(config_file)

    # 执行PDF生成
    try:
        generate_pdf_from_images(input_folder, output_file, print_page_size)
    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)}")
        sys.exit(1)
