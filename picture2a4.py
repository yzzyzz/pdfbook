from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PIL import Image
import os
import sys

def generate_pdf_from_images(image_folder: str, output_pdf: str, pagesize=A4):
    """
    基于reportlab生成适合打印成册的PDF文件
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

    # --------------- 第三步：初始化PDF画布（横向A4） ---------------
    from reportlab.lib.pagesizes import landscape
    landscape_pagesize = landscape(pagesize)  # 横向A4: 297mm x 210mm
    c = canvas.Canvas(output_pdf, pagesize=landscape_pagesize)
    page_width, page_height = landscape_pagesize  # 获取页面尺寸（单位：点，1点=1/72英寸）
    
    # 每页分为左右两个A5区域
    a5_width = page_width / 2
    a5_height = page_height
    half_a5_height = a5_height / 2

    # --------------- 第四步：处理图片并添加到PDF ---------------
    i = 0
    page_count = 0
    
    while i < len(image_files):
        # 新页面（第一页无需showPage，后续页面需要）
        if page_count > 0:
            c.showPage()
        
        page_count += 1
        
        # 左侧A5页面（正面）
        left_x = 0
        # 右侧A5页面（背面）
        right_x = a5_width
        
        # 左侧A5页面添加两张上下排列的图片
        if i < len(image_files):
            draw_two_images_in_a5(canvas_obj=c, 
                                img_paths=image_files[i:i+2] if i+1 < len(image_files) else [image_files[i]], 
                                x_offset=left_x, 
                                y_offset=0, 
                                a5_width=a5_width, 
                                a5_height=a5_height)
            processed_count = min(2, len(image_files) - i)
            print(f"进度：第 {page_count} 页左侧A5 → 已添加 {processed_count} 张图片")
            i += processed_count
        
        # 右侧A5页面添加两张上下排列的图片
        if i < len(image_files):
            draw_two_images_in_a5(canvas_obj=c, 
                                img_paths=image_files[i:i+2] if i+1 < len(image_files) else [image_files[i]], 
                                x_offset=right_x, 
                                y_offset=0, 
                                a5_width=a5_width, 
                                a5_height=a5_height)
            processed_count = min(2, len(image_files) - i)
            print(f"进度：第 {page_count} 页右侧A5 → 已添加 {processed_count} 张图片")
            i += processed_count

    # --------------- 第五步：保存PDF文件 ---------------
    c.save()
    print(f"\n✅ PDF生成完成！")
    print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
    print(f"📄 总页数：{page_count}")
    print(f"📘 打印说明：横向打印A4纸张，对折装订成A5册子")

def draw_two_images_in_a5(canvas_obj, img_paths, x_offset, y_offset, a5_width, a5_height):
    """
    在指定的A5区域内绘制最多两张图片，上下排列
    """
    half_height = a5_height / 2
    
    for idx, img_path in enumerate(img_paths[:2]):  # 最多处理两张图片
        with Image.open(img_path) as img:
            img_w, img_h = img.size

        # 计算缩放比例
        scale_w = a5_width / img_w
        scale_h = half_height / img_h
        scale = min(scale_w, scale_h)
        
        scaled_w = img_w * scale
        scaled_h = img_h * scale
        
        # 根据索引确定位置（0=上半部分，1=下半部分）
        if idx == 0:
            # 上半部分
            x = x_offset + (a5_width - scaled_w) / 2
            y = y_offset + half_height + (half_height - scaled_h) / 2
        else:
            # 下半部分
            x = x_offset + (a5_width - scaled_w) / 2
            y = y_offset + (half_height - scaled_h) / 2

        canvas_obj.drawImage(
            img_path,
            x=x, y=y,
            width=scaled_w,
            height=scaled_h,
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