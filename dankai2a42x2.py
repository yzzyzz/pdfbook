#  单开图转a4 打印 booklet 模式 (4合一漫画)
#  输入：图片文件夹路径
#  输出：生成的PDF文件（ booklet 模式）

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from PIL import Image
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import util

# ==================== 配置常量 ====================
# 原始图片模式
IMAGE_MODE_LANDSCAPE = "landscape"  # 横版图片
IMAGE_MODE_PORTRAIT = "portrait"    # 竖版图片
IMAGE_MODE_AUTO = "auto"            # 自动检测
img_scale = 0.98                    # 图片缩放

# A5页面包含的图片数量
A5_IMAGES_1 = 1  # 每个A5页面1张图片
A5_IMAGES_2 = 2  # 每个A5页面2张图片（上下排列）
A5_IMAGES_4 = 4  # 每个A5页面4张图片（2x2排列）
A5_SEQ_MAP=[4,1,2,3]
# 当前配置
CURRENT_IMAGE_MODE = IMAGE_MODE_PORTRAIT  # 当前图片模式
CURRENT_A5_IMAGE_COUNT = A5_IMAGES_4      # 当前每个A5页面的图片数量
print_page_index = False
#  zhuangding_papge_size = 1
# ==================== 主要逻辑 ====================

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

    # --------------- 第三步：计算分组大小 ---------------
    # 根据配置计算每张A4纸包含的图片数量
    images_per_a5 = CURRENT_A5_IMAGE_COUNT
    a5_regions_per_a4_sheet = 4  # 每张A4纸有4个A5区域
    images_per_a4_sheet = images_per_a5 * a5_regions_per_a4_sheet
    
    # 每张A4纸生成的PDF页面数
    pdf_pages_per_a4_sheet = 2  # 正面和反面
    
    # 计算需要的总PDF页面数
    total_images = len(image_files)
    images_per_pdf_page = CURRENT_A5_IMAGE_COUNT * 2  # 每页PDF包含两个A5区域的图片
    
    need_A4_pages = (total_images + CURRENT_A5_IMAGE_COUNT*4 -1 ) // (CURRENT_A5_IMAGE_COUNT*4)
    total_pdf_pages_needed = need_A4_pages*2
    
    print(f"配置信息：")
    print(f"  - 图片模式: {CURRENT_IMAGE_MODE}")
    print(f"  - 每个A5页面图片数: {images_per_a5}")
    print(f"  - 每张A4纸图片数: {images_per_a4_sheet}")
    print(f"  - 每页PDF图片数: {images_per_pdf_page}")
    print(f"  - 总图片数: {total_images}")
    print(f"  - 需要PDF页数: {total_pdf_pages_needed}")

    # --------------- 第四步：初始化PDF画布（横向A4） ---------------
    from reportlab.lib.pagesizes import landscape
    landscape_pagesize = landscape(pagesize)  # 横向A4: 297mm x 210mm
    c = canvas.Canvas(output_pdf, pagesize=landscape_pagesize)
    page_width, page_height = landscape_pagesize  # 获取页面尺寸（单位：点，1点=1/72英寸）
    
    # A5区域尺寸（每个A5区域是A4页面的一半）
    a5_width = page_width / 2
    a5_height = page_height

    # --------------- 第五步：处理每页PDF并添加到PDF ---------------
    total_sheet_count = 0
    first_page = True
    
    # 迭代PDF页面而不是图片
    for pdf_page_index in range(total_pdf_pages_needed):
        # 检查当前PDF页面是否有内容
        # has_content = False
        # for i in range(images_per_pdf_page):
        #     img_index = pdf_page_index * images_per_pdf_page + i
        #     if img_index < len(image_files):
        #         has_content = True
        #         break
        
        # if not has_content:
        #     continue
            
        # 新页面（第一页无需showPage，后续页面需要）
        if not first_page:
            c.showPage()
        else:
            first_page = False
        
        total_sheet_count += 1
        
        # 确定当前页面的A5区域位置
        page_side = pdf_page_index % 2  # 0=正面, 1=反面
        sheet_index = pdf_page_index // 2  # 当前A4纸的索引
        
        front_a5_x, front_a5_y = 0, 0        # 左侧A5区域（正面内容）
        back_a5_x, back_a5_y = a5_width, 0
            
        
        a5lindex = (pdf_page_index // 2 ) *4 + A5_SEQ_MAP[page_side*2]
        a5rindex = (pdf_page_index // 2 ) *4 + A5_SEQ_MAP[page_side*2+1]
        # 根据配置绘制图片
        if CURRENT_A5_IMAGE_COUNT == A5_IMAGES_1:
            # 每个A5区域1张图片  
           
            draw_images_in_a5_region(
                canvas_obj=c,
                image_files=image_files,
                a5_index= a5lindex,  # 正面A5区域索引
                x_offset=front_a5_x,
                y_offset=front_a5_y,
                a5_width=a5_width,
                a5_height=a5_height,
                pdf_page_index=pdf_page_index,
                images_per_pdf_page=images_per_pdf_page
            )
            
            draw_images_in_a5_region(
                canvas_obj=c,
                image_files=image_files,
                a5_index=a5rindex,  # 背面A5区域索引
                x_offset=back_a5_x,
                y_offset=back_a5_y,
                a5_width=a5_width,
                a5_height=a5_height,
                pdf_page_index=pdf_page_index,
                images_per_pdf_page=images_per_pdf_page
            )
            
        elif CURRENT_A5_IMAGE_COUNT == A5_IMAGES_2:
            # 每个A5区域2张图片（上下排列）
            draw_images_in_a5_region(
                canvas_obj=c,
                image_files=image_files,
                a5_index=a5lindex,  # 正面A5区域索引
                x_offset=front_a5_x,
                y_offset=front_a5_y,
                a5_width=a5_width,
                a5_height=a5_height,
                pdf_page_index=pdf_page_index,
                images_per_pdf_page=images_per_pdf_page
            )
            
            draw_images_in_a5_region(
                canvas_obj=c,
                image_files=image_files,
                a5_index=a5rindex,  # 背面A5区域索引
                x_offset=back_a5_x,
                y_offset=back_a5_y,
                a5_width=a5_width,
                a5_height=a5_height,
                pdf_page_index=pdf_page_index,
                images_per_pdf_page=images_per_pdf_page
            )
            
        elif CURRENT_A5_IMAGE_COUNT == A5_IMAGES_4:
            # 每个A5区域4张图片（2x2排列）
            draw_images_in_a5_region(
                canvas_obj=c,
                image_files=image_files,
                a5_index=a5lindex,  # 正面A5区域索引
                x_offset=front_a5_x,
                y_offset=front_a5_y,
                a5_width=a5_width,
                a5_height=a5_height,
                pdf_page_index=pdf_page_index,
                images_per_pdf_page=images_per_pdf_page
            )
            
            draw_images_in_a5_region(
                canvas_obj=c,
                image_files=image_files,
                a5_index=a5rindex,  # 背面A5区域索引
                x_offset=back_a5_x,
                y_offset=back_a5_y,
                a5_width=a5_width,
                a5_height=a5_height,
                pdf_page_index=pdf_page_index,
                images_per_pdf_page=images_per_pdf_page
            )
        
        print(f"进度：第 {total_sheet_count} 页PDF → 已处理PDF页面 {pdf_page_index + 1}/{total_pdf_pages_needed}")

    # --------------- 第六步：保存PDF文件 ---------------
    c.save()
    print(f"\n✅ PDF生成完成！")
    print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
    print(f"📄 PDF页数：{total_sheet_count}")
    print(f"📘 打印说明：")
    print(f"   1. 横向打印A4纸张")
    print(f"   2. 每页PDF包含{images_per_pdf_page}张图片")
    print(f"   3. 打印完成后对折装订成A5册子")

# ==================== 绘图函数 ====================

def draw_images_in_a5_region(canvas_obj, image_files, a5_index, x_offset, y_offset, a5_width, a5_height, pdf_page_index, images_per_pdf_page):
    """
    在指定的A5区域内绘制图片，根据配置自动选择绘制方式
    :param canvas_obj: PDF画布对象
    :param image_files: 所有图片文件列表
    :param a5_index: A5区域索引（0-3）
    :param x_offset: X偏移量
    :param y_offset: Y偏移量
    :param a5_width: A5区域宽度
    :param a5_height: A5区域高度
    :param pdf_page_index: 当前PDF页面索引
    :param images_per_pdf_page: 每页PDF包含的图片数量
    """
    # 根据配置选择绘制方式
    if CURRENT_A5_IMAGE_COUNT == A5_IMAGES_1:
        # 每个A5区域1张图片
        img_index = a5_index - 1
        img_path = image_files[img_index] if img_index < len(image_files) else None
        page_number = a5_index if img_path else None
        
        if img_path and os.path.exists(img_path):
            with Image.open(img_path) as img:
                img_w, img_h = img.size

            # 计算缩放比例（填满A5区域）
            scale_w = a5_width / img_w
            scale_h = a5_height / img_h
            scale = min(scale_w, scale_h)
            
            scaled_w = img_w * scale
            scaled_h = img_h * scale
            
            # 在A5区域内居中
            x = x_offset + (a5_width - scaled_w) / 2
            y = y_offset + (a5_height - scaled_h) / 2

            canvas_obj.drawImage(
                img_path,
                x=x, y=y,
                width=scaled_w,
                height=scaled_h,
                preserveAspectRatio=True
            )
        
        # 添加页码（如果提供了页码）
        if page_number is not None and print_page_index:
            # 设置字体和大小
            canvas_obj.setFont("Helvetica", 12)
            # 设置字体颜色为黑色
            canvas_obj.setFillColorRGB(0, 0, 0)
            
            page_number_text = str(page_number)
            text_width = canvas_obj.stringWidth(page_number_text, "Helvetica", 12)
            
            # 页码放在A5区域的右下角
            page_x = x_offset + a5_width - text_width - 10
            page_y = y_offset + 10
            
            canvas_obj.drawString(page_x, page_y, page_number_text)
            
    elif CURRENT_A5_IMAGE_COUNT == A5_IMAGES_2:
        # 每个A5区域2张图片（上下排列）
        img_paths = []
        page_numbers = []
        
        # 计算当前A5区域对应的图片索引
        base_index = (a5_index - 1) * 2 
        for i in range(2):
            img_index = base_index + i
            img_path = image_files[img_index] if img_index < len(image_files) else None
            img_paths.append(img_path)
            page_numbers.append(img_index if img_path else None)
        
        # 每个小图片区域的尺寸（上下排列）
        small_width = a5_width
        small_height = a5_height / 2
        
        # 上下排列的位置
        positions = [
            (0, small_height),  # 上半部分
            (0, 0)             # 下半部分
        ]
        
        for i, (img_path, pos, page_num) in enumerate(zip(img_paths, positions, page_numbers)):
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

                canvas_obj.drawImage(
                    img_path,
                    x=x, y=y,
                    width=scaled_w,
                    height=scaled_h,
                    preserveAspectRatio=True
                )
            
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
        # 每个A5区域4张图片（2x2排列）
        img_paths = []
        page_numbers = []
        
        # 计算当前A5区域对应的图片索引
        base_index = (a5_index - 1) * 4
        for i in range(4):
            img_index = base_index + i
            img_path = image_files[img_index] if img_index < len(image_files) else None
            img_paths.append(img_path)
            page_numbers.append(img_index + 1 if img_path else None)
        
        # 每个小图片区域的尺寸（2x2网格）
        small_width = a5_width / 2
        small_height = a5_height / 2
        
        # 2x2排列的位置（从上到下，从左到右）
        positions = [
            (0, small_height),          # 左上
            (small_width, small_height), # 右上
            (0, 0),                     # 左下
            (small_width, 0)            # 右下
        ]
        
        for i, (img_path, pos, page_num) in enumerate(zip(img_paths, positions, page_numbers)):
            if img_path and os.path.exists(img_path):
                with Image.open(img_path) as img:
                    img_w, img_h = img.size

                # 计算缩放比例（填满小区域）
                scale_w = small_width / img_w
                scale_h = small_height / img_h
                scale = min(scale_w, scale_h)
                
                scaled_w = img_w * scale * img_scale
                scaled_h = img_h * scale * img_scale
                
                # 在小区域内居中
                x = x_offset + pos[0] + (small_width - scaled_w) / 2
                y = y_offset + pos[1] + (small_height - scaled_h) / 2

                canvas_obj.drawImage(
                    img_path,
                    x=x, y=y,
                    width=scaled_w,
                    height=scaled_h,
                    preserveAspectRatio=True
                )
            
            # 添加页码（如果提供了页码）
            if page_num is not None and print_page_index:
                # 设置字体和大小
                canvas_obj.setFont("Helvetica", 8)
                # 设置字体颜色为黑色
                canvas_obj.setFillColorRGB(0, 0, 0)
                
                page_number_text = str(page_num)
                text_width = canvas_obj.stringWidth(page_number_text, "Helvetica", 8)
                
                # 页码放在每个小图片的左下角
                page_x = x_offset + pos[0] + small_width - 14
                page_y = y_offset + pos[1] + 2
                
                canvas_obj.drawString(page_x, page_y, page_number_text)

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