from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5, A4 ,A6
from reportlab.lib.units import mm
from PIL import Image
import os
import sys

zhongxianspace = 20


def generate_pdf_from_images(input_path: str, output_pdf: str, pagesize=A4):
    """
    在横版A4纸上绘制单张图片
    :param input_path: 输入路径（单个图片文件）
    :param output_pdf: 输出PDF文件的完整路径
    :param pagesize: PDF页面尺寸，默认A4横版
    """
    # --------------- 第一步：参数校验 ---------------
    # 检查输入路径是否存在
    if not os.path.exists(input_path):
        raise ValueError(f"错误：输入路径 '{input_path}' 不存在！")

    # 检查输入路径是单个图片文件
    if os.path.isfile(input_path):
        file_ext = os.path.splitext(input_path)[1].lower()
        valid_image_ext = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp',
                           '.webp')

        if file_ext not in valid_image_ext:
            raise ValueError(f"错误：输入文件 '{input_path}' 不是有效的图片格式！")

        image_file = input_path
        print(f"提示：处理单个图片文件: {input_path}")

        # 检查输出PDF路径的父目录是否存在（不存在则创建）
        output_dir = os.path.dirname(output_pdf)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"提示：已自动创建输出目录 '{output_dir}'")
    else:
        raise ValueError(f"错误：输入路径 '{input_path}' 不是有效的图片文件！")

    # A5高度
    a5_height = A6[1]  # A5竖版的高度
    a5_width = A6[0]
    from reportlab.lib.pagesizes import landscape
    landscape_pagesize = landscape(pagesize)  # 横向A4: 297mm x 210mm
    c = canvas.Canvas(output_pdf, pagesize=landscape_pagesize)
    page_width, page_height = landscape_pagesize  # 获取页面尺寸（单位：点，1点=1/72英寸）

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

        # 获取图片原始像素尺寸
        # img_px_w, img_px_h = img.size

        img_w, img_h = img.size

        # 计算缩放比例（填满A5区域）
        scale_w = (a5_width) / img_w
        scale_h = a5_height / img_h
        scale = min(scale_w, scale_h)
        scaled_w = img_w * scale
        scaled_h = img_h * scale

    # 计算居中位置
    x = 0
    y = 0

    # 绘制图片
    c.drawImage(image_file,
                x=x,
                y=y,
                width=scaled_w,
                height=scaled_h,
                preserveAspectRatio=True,
                mask='auto')

    print(f"绘制位置：x={x:.2f}, y={y:.2f}")

    # 保存PDF文件
    c.save()
    print(f"\n✅ PDF生成完成！")
    print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
    print(f"📄 页面尺寸：A4横版")


def draw_single_image(canvas_obj, img_path, page_width, page_height):
    """
    在页面上绘制单张图片，填满整个页面
    """
    # 打开图片获取尺寸
    with Image.open(img_path) as img:
        img_px_w, img_px_h = img.size

    # 计算缩放比例（填满页面）
    scale_w = page_width / img_px_w
    scale_h = page_height / img_px_h
    scale = min(scale_w, scale_h)

    # 缩放后图片尺寸
    scaled_w = img_px_w * scale
    scaled_h = img_px_h * scale

    # 计算居中坐标
    x = (page_width - scaled_w) / 2
    y = (page_height - scaled_h) / 2

    # 绘制图片
    canvas_obj.drawImage(img_path,
                         x=x,
                         y=y,
                         width=scaled_w,
                         height=scaled_h,
                         preserveAspectRatio=True)


def draw_two_images(canvas_obj, img_path1, img_path2, page_width, page_height):
    """
    在页面上绘制两张图片，上下排列各占一半高度
    """
    half_height = page_height / 2

    # 处理第一张图片（上半部分）
    with Image.open(img_path1) as img1:
        img1_w, img1_h = img1.size

    scale_w1 = page_width / img1_w
    scale_h1 = half_height / img1_h
    scale1 = min(scale_w1, scale_h1)

    scaled_w1 = img1_w * scale1
    scaled_h1 = img1_h * scale1

    x1 = (page_width - scaled_w1) / 2
    y1 = half_height + (half_height - scaled_h1) / 2  # 在上半部分居中

    canvas_obj.drawImage(img_path1,
                         x=x1,
                         y=y1,
                         width=scaled_w1,
                         height=scaled_h1,
                         preserveAspectRatio=True)

    # 处理第二张图片（下半部分）
    with Image.open(img_path2) as img2:
        img2_w, img2_h = img2.size

    scale_w2 = page_width / img2_w
    scale_h2 = half_height / img2_h
    scale2 = min(scale_w2, scale_h2)

    scaled_w2 = img2_w * scale2
    scaled_h2 = img2_h * scale2

    x2 = (page_width - scaled_w2) / 2
    y2 = (half_height - scaled_h2) / 2  # 在下半部分居中

    canvas_obj.drawImage(img_path2,
                         x=x2,
                         y=y2,
                         width=scaled_w2,
                         height=scaled_h2,
                         preserveAspectRatio=True)


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
