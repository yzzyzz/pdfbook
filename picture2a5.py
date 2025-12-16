from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from PIL import Image
import os
import sys

def generate_pdf_from_images(image_folder: str, output_pdf: str, pagesize=A5):
    """
    基于reportlab生成每页一张或两张图片的PDF文件
    :param image_folder: 存放图片的文件夹路径（必填）
    :param output_pdf: 输出PDF文件的完整路径（必填）
    :param pagesize: PDF页面尺寸，默认A5（148mm×210mm）
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
    valid_image_ext = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp')
    # 遍历文件夹，筛选图片文件并按文件名排序
    image_files = []
    for filename in os.listdir(image_folder):
        file_path = os.path.join(image_folder, filename)
        # 跳过目录，只处理文件
        if os.path.isfile(file_path) and filename.lower().endswith(valid_image_ext):
            image_files.append(file_path)
    
    # 按文件名自然排序（保证图片顺序可控）
    image_files.sort(key=lambda x: os.path.basename(x))
    
    # 检查是否有有效图片
    if not image_files:
        raise RuntimeError(f"错误：文件夹 '{image_folder}' 中未找到任何有效图片！")
    print(f"提示：共找到 {len(image_files)} 张有效图片")

    # --------------- 第三步：初始化PDF画布 ---------------
    c = canvas.Canvas(output_pdf, pagesize=pagesize)
    page_width, page_height = pagesize  # 获取页面尺寸（单位：点，1点=1/72英寸）

    # --------------- 第四步：处理图片并添加到PDF ---------------
    i = 0
    page_count = 0
    
    while i < len(image_files):
        # 新页面（第一页无需showPage，后续页面需要）
        if page_count > 0:
            c.showPage()
        
        page_count += 1
        
        try:
            # 获取当前图片
            img_path = image_files[i]
            
            # 打开图片并获取尺寸（自动处理EXIF旋转）
            with Image.open(img_path) as img:
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
                img_px_w, img_px_h = img.size
            
            # 判断图片方向
            is_portrait = img_px_h > img_px_w
            
            if is_portrait:
                # 竖向图片，单独占一页
                draw_single_image(c, img_path, page_width, page_height)
                print(f"进度：第 {page_count} 页 → 已添加竖向图片：{os.path.basename(img_path)}")
                i += 1
            else:
                # 横向图片，尝试与下一张图片合并
                if i + 1 < len(image_files):
                    # 有下一张图片，检查下一张是否也是横向
                    next_img_path = image_files[i + 1]
                    with Image.open(next_img_path) as next_img:
                        next_img_w, next_img_h = next_img.size
                        next_is_landscape = next_img_w > next_img_h
                    
                    if next_is_landscape:
                        # 下一张也是横向图片，两张合并一页
                        draw_two_images(c, img_path, next_img_path, page_width, page_height)
                        print(f"进度：第 {page_count} 页 → 已添加两张横向图片：{os.path.basename(img_path)} + {os.path.basename(next_img_path)}")
                        i += 2
                    else:
                        # 下一张是竖向图片，当前图片单独一页
                        draw_single_image(c, img_path, page_width, page_height)
                        print(f"进度：第 {page_count} 页 → 已添加横向图片：{os.path.basename(img_path)}")
                        i += 1
                else:
                    # 没有下一张图片，当前图片单独一页
                    draw_single_image(c, img_path, page_width, page_height)
                    print(f"进度：第 {page_count} 页 → 已添加横向图片：{os.path.basename(img_path)}")
                    i += 1

        except Exception as e:
            print(f"警告：跳过图片处理 → 原因：{str(e)}")
            i += 1
            continue

    # --------------- 第七步：保存PDF文件 ---------------
    c.save()
    print(f"\n✅ PDF生成完成！")
    print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
    print(f"📄 总页数：{page_count}")

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
    canvas_obj.drawImage(
        img_path,
        x=x, y=y,
        width=scaled_w,
        height=scaled_h,
        preserveAspectRatio=True
    )

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

    canvas_obj.drawImage(
        img_path1,
        x=x1, y=y1,
        width=scaled_w1,
        height=scaled_h1,
        preserveAspectRatio=True
    )

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

    canvas_obj.drawImage(
        img_path2,
        x=x2, y=y2,
        width=scaled_w2,
        height=scaled_h2,
        preserveAspectRatio=True
    )

# --------------- 命令行调用入口 ---------------
if __name__ == "__main__":
    # 检查命令行参数数量
    if len(sys.argv) != 3:
        print("❌ 参数错误！正确用法：")
        print(f"python {os.path.basename(__file__)} <图片文件夹路径> <输出PDF文件路径>")
        print("示例：")
        print(f"python {os.path.basename(__file__)} ./images ./output.pdf")
        sys.exit(1)
    
    # 获取命令行参数
    input_folder = sys.argv[1]
    output_file = sys.argv[2]
    
    # 执行PDF生成
    try:
        generate_pdf_from_images(input_folder, output_file)
    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)}")
        sys.exit(1)