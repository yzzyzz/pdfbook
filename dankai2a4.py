#  单开图转a4 打印 booklet 模式
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

def generate_pdf_from_images(image_folder: str, output_pdf: str, pagesize=A4):
    """
    基于reportlab生成适合打印成册的PDF文件
    :param image_folder: 存放图片的文件夹路径（必填）
    :param output_pdf: 输出PDF文件的完整路径（必填）
    :param pagesize: PDF页面尺寸，默认A4横向（297mm×210mm）
    """
    # --------------- 第一步：参数校验 ---------------
    # 检查图片文件夹是否存在
    bucket_page_size = 5
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

    # --------------- 第三步：分组处理图片（每24页为一组） ---------------
    # 每6张A4纸为一册，每张A4纸4页，共24页为一组
    GROUP_SIZE = bucket_page_size * 4  # 每组24页
    grouped_images = []
    
    # 将图片按GROUP_SIZE分组
    for i in range(0, len(image_files), GROUP_SIZE):
        group = image_files[i:i + GROUP_SIZE]
        # 如果最后一组不足24页，用None填充
        while len(group) < GROUP_SIZE:
            group.append(None)
        grouped_images.append(group)
    
    # --------------- 第四步：初始化PDF画布（横向A4） ---------------
    from reportlab.lib.pagesizes import landscape
    landscape_pagesize = landscape(pagesize)  # 横向A4: 297mm x 210mm
    c = canvas.Canvas(output_pdf, pagesize=landscape_pagesize)
    page_width, page_height = landscape_pagesize  # 获取页面尺寸（单位：点，1点=1/72英寸）
    
    # A5区域尺寸（每个A5区域是A4页面的一半）
    a5_width = page_width / 2
    a5_height = page_height

    # --------------- 第五步：处理每组图片并添加到PDF ---------------
    total_sheet_count = 0
    
    for group_index, group in enumerate(grouped_images):
        # 每组24页需要6张A4纸
        a4_sheets_needed = bucket_page_size
        # 获取A4纸的页面排列顺序
        page_sequence = util.genNumberSeqByA4Page(a4_sheets_needed)
        
        # 重新排列图片顺序以匹配页面序列
        rearranged_group = [None] * GROUP_SIZE
        for sheet_index, sheet_pages in enumerate(page_sequence):
            for pos_index, page_num in enumerate(sheet_pages):
                # 页面编号从1开始，转换为0基索引
                img_index = page_num - 1
                if img_index < len(group):
                    # 在rearranged_group中找到对应位置
                    a4_index = sheet_index
                    position_in_a4 = pos_index
                    # 计算在rearranged_group中的位置
                    rearranged_index = a4_index * 4 + position_in_a4
                    if rearranged_index < GROUP_SIZE:
                        rearranged_group[rearranged_index] = group[img_index]
        
        # 处理重新排列后的图片（每张PDF页面放2张图片）
        for sheet_index in range(a4_sheets_needed):
            # 每张A4纸需要生成2页PDF（每页2个A5区域）
            for page_in_sheet in range(2):  # 0=正面, 1=背面
                if total_sheet_count > 0:
                    c.showPage()
                
                total_sheet_count += 1
                
                # 获取当前PDF页面上的2张图片
                start_idx = sheet_index * 4 + page_in_sheet * 2
                img1 = rearranged_group[start_idx] if start_idx < len(rearranged_group) else None
                img2 = rearranged_group[start_idx + 1] if start_idx + 1 < len(rearranged_group) else None
                
                # 在A4页面上绘制2个A5区域（左右排列）
                if img1 and os.path.exists(img1):
                    draw_single_image_on_a5(
                        canvas_obj=c,
                        img_path=img1,
                        x_offset=0,  # 左侧A5区域
                        y_offset=0,
                        a5_width=a5_width,
                        a5_height=a5_height
                    )
                
                if img2 and os.path.exists(img2):
                    draw_single_image_on_a5(
                        canvas_obj=c,
                        img_path=img2,
                        x_offset=a5_width,  # 右侧A5区域
                        y_offset=0,
                        a5_width=a5_width,
                        a5_height=a5_height
                    )
                
                print(f"进度：第 {total_sheet_count} 页PDF → 已处理第 {group_index + 1} 组，A4纸 {sheet_index + 1}/6，页面 {page_in_sheet + 1}/2")

    # --------------- 第六步：保存PDF文件 ---------------
    c.save()
    print(f"\n✅ PDF生成完成！")
    print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
    print(f"📄 PDF页数：{total_sheet_count}")
    print(f"📘 打印说明：")
    print(f"   1. 横向打印A4纸张")
    print(f"   2. 每页PDF包含2张图片（左右排列）")
    print(f"   3. 每6张A4纸为一册，按顺序打印")
    print(f"   4. 打印完成后对折装订成A5册子")

def draw_single_image_on_a5(canvas_obj, img_path, x_offset, y_offset, a5_width, a5_height):
    """
    在指定的A5区域内绘制单张图片（铺满整个A5区域）
    """
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