from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import zipfile
import sys
import re

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


def epub_html_iter(epub_path):
    """
    按文档顺序返回 HTML 迭代器
    """
    book = epub.read_epub(epub_path)
    for item_id, _ in book.spine:
        item = book.get_item_with_id(item_id)
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content()
            soup = BeautifulSoup(content, "html.parser")
            yield soup.prettify()  # 返回格式化的 HTML 字符串


# 尝试导入 PyPDF2 用于合并 PDF
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("错误：需要安装 PyPDF2 或 pypdf 库来合并PDF文件")
        print("请运行: pip install PyPDF2 或 pip install pypdf")
        sys.exit(1)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import util

# ==================== 配置常量 ====================
# 页面配置
PAGE_LAYOUT = "A4_VERTICAL_4_A6"  # A4竖版，每页4个A6区域
A6_REGIONS_PER_PAGE = 4  # 每页4个A6区域（2x2布局）

# 注册字体
FONT_NAME = "FangSong"
FONT_PATH = os.path.dirname(os.path.abspath(__file__)) + "/fs.ttf"

# 检查字体文件是否存在
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    DEFAULT_FONT = FONT_NAME
else:
    print(f"⚠️ 字体文件 {FONT_PATH} 不存在，使用默认字体")
    DEFAULT_FONT = "Helvetica"
# A4页面尺寸（竖版）
PAGE_WIDTH, PAGE_HEIGHT = A4
# 每个A6区域尺寸
A6_WIDTH = PAGE_WIDTH / 2
A6_HEIGHT = PAGE_HEIGHT / 2
print("纸张高度:", PAGE_HEIGHT, "纸张宽度:", PAGE_WIDTH)
# 文本渲染配置
TEXT_FONT_SIZE = 12
TEXT_LINE_SPACE = 3
MARGIN = 10  # 区域内边距
render_order = [(0, 0), (1, 1), (1, 0), (0, 1), (0, 2), (1, 3), (1, 2), (0, 3)]
# 初始化两个PDF画布（A4竖版）
front_c = canvas.Canvas("front.pdf", pagesize=A4)
back_c = canvas.Canvas("back.pdf", pagesize=A4)

page_lr_margin = 14  # A4页面左右边距
page_center_margin = 8
a6_lr_margin = 4
a6_tb_margin = 2

# A6区域位置定义
page_positions = [
    [  # 第1页
        (0, A6_HEIGHT),  # 物理位置：左上 (索引0)
        (A6_WIDTH, A6_HEIGHT),  # 物理位置：右上 (索引1)
        (0, 0),  # 物理位置：左下 (索引2)
        (A6_WIDTH, 0)  # 物理位置：右下 (索引3)
    ],
    [  # 第2页
        (0, A6_HEIGHT),  # 物理位置：左上 (索引0)
        (A6_WIDTH, A6_HEIGHT),  # 物理位置：右上 (索引1)
        (0, 0),  # 物理位置：左下 (索引2)
        (A6_WIDTH, 0)  # 物理位置：右下 (索引3)
    ]
]


def draw_text_in_a6_region_with_cursor(
    a6_index,
    text,
    start_cursor,
    cursor_x,
    cursor_y,
    font_size=TEXT_FONT_SIZE,
    font_name=DEFAULT_FONT,
    align="left",
):
    """
    在指定的A6区域内绘制文本，使用游标模式
    :param a6_index: A6区域索引
    :param text: 完整文本内容
    :param start_cursor: 开始位置游标
    :param cursor_x: 当前绘制的x坐标
    :param cursor_y: 当前绘制的y坐标
    :param font_size: 字体大小
    :param font_name: 字体名称
    :param align: 对齐方式 ("left", "center", "right")
    :return: (finished, text_cursor, next_x, next_y) - 是否完成、文本游标位置、下次绘制的x和y坐标
    """
    # 获取当前要渲染的A6区域位置
    print(f"处理A6区域 {a6_index}")
    page_idx, pos_idx = render_order[a6_index % 8]

    # 选择当前应该渲染的画布（正面或背面）
    if page_idx == 0:  # 正面页
        canvas_obj = front_c
        print("  绘制正面页")
    else:  # 背面页
        canvas_obj = back_c
        print("  绘制背面页")

    # 获取当前A6区域的物理位置
    x_offset, y_offset = page_positions[page_idx][pos_idx]

    # 设置字体
    canvas_obj.setFont(font_name, font_size)
    # 文本边距
    margin = MARGIN
    available_width = A6_WIDTH - 2 * a6_lr_margin - page_lr_margin - page_center_margin
    available_height = A6_HEIGHT - 2 * a6_tb_margin

    # 绘制文本行的高度
    line_height = font_size + TEXT_LINE_SPACE
    current_cursor = start_cursor
    print(f"从位置 {start_cursor} 开始绘制")
    # 从指定的光标位置开始绘制
    text_y = cursor_y + y_offset if cursor_y is not None else y_offset + A6_HEIGHT - a6_tb_margin

    if a6_index % 2 == 0:
        text_x = cursor_x + x_offset if cursor_x is not None else x_offset + page_lr_margin + a6_lr_margin
    else:
        text_x = cursor_x + x_offset if cursor_x is not None else x_offset + page_center_margin + a6_lr_margin
    print(f"当前绘制位置：{text_x}, {text_y}")
    print(f"当前光标位置：{current_cursor}")
    print("  开始绘制文本:", text)
    print(f"a6_index: {a6_index}     available_width: {available_width}")
    # 逐行处理文本直到区域用完或文本处理完毕
    while current_cursor < len(text):
        # 检查当前行是否还有足够的垂直空间
        if (text_y - line_height) < (y_offset + a6_tb_margin):
            # 没有足够空间绘制下一行，返回未完成状态
            return False, current_cursor, text_x, text_y
        # 找到当前行的文本
        line_start = current_cursor
        line_end = line_start
        # 计算当前行的可用宽度
        current_line_available_width = available_width

        # 寻找合适的换行点
        while line_end < len(text):
            # 检查是否遇到换行符
            if text[line_end] == '\n':
                line_end += 1  # 包含换行符
                break
            # 检查当前行的宽度
            test_line = text[line_start:line_end + 1]
            line_width = canvas_obj.stringWidth(test_line, font_name,
                                                font_size)
            # 如果当前行宽度超过可用宽度，回退到上一个合适的断点
            if line_width > current_line_available_width:
                if line_end == line_start:
                    break
                else:
                    line_end -= 1
                    break
            else:
                line_end += 1

        # 获取当前行文本
        current_line = text[line_start:line_end].rstrip('\n')
        # 检查是否遇到段落分隔符
        if '\n' in current_line and current_line.endswith('\n'):
            # 如果当前行以换行符结尾，处理段落分隔
            paragraph_pos = current_line.rindex('\n')
            current_line = current_line[:paragraph_pos]
            # 修正游标位置
            actual_end = line_start + paragraph_pos + 1  # 加上换行符
        else:
            actual_end = line_end

        if current_line:
            text_width = canvas_obj.stringWidth(current_line, font_name,
                                                font_size)

            # 根据对齐方式计算x坐标
            if align == "center":
                line_x = x_offset + (available_width - text_width) / 2
            elif align == "right":
                line_x = x_offset + A6_WIDTH - text_width - margin
            else:  # left
                line_x = text_x

            canvas_obj.drawString(line_x, text_y - font_size, current_line)
            print(f"绘制行：{current_line}")

            canvas_obj.rect(x_offset,
                            y_offset,
                            A6_WIDTH,
                            A6_HEIGHT,
                            stroke=1,
                            fill=0)
        # 更新y坐标
        text_y -= line_height
        # 更新游标
        current_cursor = actual_end
        # 检查是否已经处理完整个文本
        if current_cursor >= len(text):
            return True, 0, None, text_y - y_offset
    # 如果循环结束但文本未处理完，说明A6区域已满
    return False, current_cursor, None, None


def draw_image_in_a6_region(a6_index, image_file):
    """
    绘制图片到A6区域
    :param a6_index: A6区域索引
    :param image_file: 图片文件路径或URL
    :return: None
    """
    import os
    from reportlab.lib.utils import ImageReader
    from PIL import Image as PILImage

    print(f"处理A6区域 {a6_index}，图片文件: {image_file}")
    page_idx, pos_idx = render_order[a6_index % 8]

    # 选择当前应该渲染的画布（正面或背面）
    if page_idx == 0:  # 正面页
        canvas_obj = front_c
        print("  绘制正面页")
    else:  # 背面页
        canvas_obj = back_c
        print("  绘制背面页")

    # 获取当前A6区域的物理位置
    x_offset, y_offset = page_positions[page_idx][pos_idx]

    # 图片边距
    img_margin = MARGIN

    # 计算A6区域可用空间
    available_width = A6_WIDTH - 2 * img_margin
    available_height = A6_HEIGHT - 2 * img_margin

    # 获取图片路径（相对于EPUB的images目录）
    epub_dir = os.path.dirname(sys.argv[1]) if len(sys.argv) > 1 else "."
    full_image_path = os.path.join(
        epub_dir, "images",
        image_file) if "images/" in image_file else os.path.join(
            epub_dir, image_file)

    # 如果图片文件不存在，尝试从EPUB内容中查找
    if not os.path.exists(full_image_path):
        # 尝试在当前工作目录下查找
        full_image_path = os.path.join(os.getcwd(), image_file)

    if not os.path.exists(full_image_path):
        # 如果仍然找不到，跳过绘制
        print(f"  警告：图片文件不存在: {full_image_path}")
        # 绘制一个占位符
        placeholder_text = "[图片: " + image_file + "]"
        canvas_obj.drawString(x_offset + img_margin, y_offset + A6_HEIGHT / 2,
                              placeholder_text)
        return

    try:
        # 使用PIL获取图片尺寸
        with PILImage.open(full_image_path) as img:
            img_width, img_height = img.size

        # 计算缩放比例以适应A6区域
        scale_w = available_width / img_width
        scale_h = available_height / img_height
        scale = min(scale_w, scale_h)  # 保持宽高比
        # 计算缩放后的尺寸
        scaled_w = img_width * scale
        scaled_h = img_height * scale
        # 计算居中位置
        centered_x = x_offset + img_margin + (available_width - scaled_w) / 2
        centered_y = y_offset + img_margin + (available_height - scaled_h) / 2
        # 绘制图片
        canvas_obj.drawImage(full_image_path,
                             x=centered_x,
                             y=centered_y,
                             width=scaled_w,
                             height=scaled_h,
                             preserveAspectRatio=True,
                             mask='auto')  # auto表示使用图片的透明度信息

        print(
            f"  成功绘制图片: {image_file} (原始尺寸: {img_width}x{img_height}, 绘制尺寸: {scaled_w}x{scaled_h})"
        )

    except Exception as e:
        print(f"  错误：无法绘制图片 {image_file}: {str(e)}")
        # 绘制一个占位符
        placeholder_text = "[图片: " + image_file + " - 加载失败]"
        canvas_obj.drawString(x_offset + img_margin, y_offset + A6_HEIGHT / 2,
                              placeholder_text)


def draw_html_in_a6_region(a6_index,
                           html_content,
                           cursor_x=None,
                           cursor_y=None,
                           font_size=TEXT_FONT_SIZE,
                           font_name=DEFAULT_FONT):
    """
    draw_html_in_a6_region 的 Docstring
    
    :param a6_index: A6区域索引
    :param html_content: HTML内容
    :param cursor_x: 当前绘制的x坐标
    :param cursor_y: 当前绘制的y坐标
    :param font_size: 字体大小
    :param font_name: 字体名称
    :return: (a6_index, next_x, next_y) - 返回A6索引和下次绘制的位置
    """
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    margin = MARGIN

    # 获取当前要渲染的A6区域位置

    # 使用深度优先遍历，按顺序提取所有元素
    def extract_elements_in_order(tag):
        """按文档顺序提取所有元素"""
        elements = []
        child_tags = [
            child for child in tag.children
            if hasattr(child, 'name') and child.name
        ]
        if child_tags:
            # 有子标签，递归处理每个子元素，保持文档顺序
            for child in tag.children:
                if hasattr(child, 'name') and child.name:  # 是标签
                    elements.extend(extract_elements_in_order(child))
                elif hasattr(child, 'strip') and child.strip():  # 是文本节点
                    elements.append(str(child).strip())
        else:
            elements.append(tag)
        return elements

    # 提取根元素下的所有子元素，保持文档顺序
    all_elements = []
    for child in soup.children:
        if hasattr(child, 'name') and child.name:  # 是标签
            all_elements.extend(extract_elements_in_order(child))
        elif hasattr(child, 'strip') and child.strip():  # 是文本节点
            all_elements.append(str(child).strip())
    # 处理提取出的元素，保持文档顺序
    for element in all_elements:
        print(element)
        if isinstance(element, str):
            pass
        elif element.name == "p":
            if len(element.text.strip()) <= 2:
                continue
            text_content = "    " + element.text.strip()
            is_complete = False
            text_cursor = 0
            print(f"准备处理处理ttt text_content {text_content}")
            print(f"页面:{a6_index} 绘制位置:{cursor_x}, {cursor_y}")
            while not is_complete:
                is_complete, text_cursor, cursor_x, cursor_y = draw_text_in_a6_region_with_cursor(
                    a6_index, text_content, text_cursor, cursor_x, cursor_y,
                    font_size, font_name)
                if not is_complete:
                    cursor_x = None
                    cursor_y = None
                    if a6_index % 8 == 7:
                        front_c.showPage()
                        back_c.showPage()
                    a6_index += 1
                else:
                    text_cursor = 0
                    pass
        elif element.name == "img" or element.name == "image":
            cover_filename = ""
            if element.has_attr("xlink:href"):
                cover_filename = element["xlink:href"]
                print(f"图片:{cover_filename}")
            else:
                cover_filename = element.get("src")
            
            if a6_index % 8 == 7:
                front_c.showPage()
                back_c.showPage()
            if a6_index >= 1 and cursor_y is not None:
                a6_index += 1
            cover_filename = "./tmpdir/" + cover_filename
            print(f"图片:{cover_filename}")
            draw_image_in_a6_region(a6_index, cover_filename)
            if a6_index % 8 == 7:
                front_c.showPage()
                back_c.showPage()
            a6_index += 1
            cursor_y = None
            text_cursor = 0
    return a6_index, cursor_x, cursor_y


def generate_custom_order_pdfs(epub_path, front_pdf, back_pdf):
    """
    从EPUB文件生成两个PDF（正面和背面），按照自定义顺序交替渲染内容
    :param epub_path: EPUB文件路径
    :param front_pdf: 正面PDF文件路径
    :param back_pdf: 背面PDF文件路径
    :param render_order: 渲染顺序列表，包含8个元素，每个元素是(页码, 位置索引)的元组
    """

    a6_index = 0
    cursor_x = None  # 初始化游标
    cursor_y = None  # 初始化游标
    # 遍历EPUB的HTML内容
    for html_content in epub_html_iter(epub_path):
        # 合并剩余内容和当前内容
        a6_index, cursor_x, cursor_y = draw_html_in_a6_region(
            a6_index=a6_index,
            html_content=html_content,
            cursor_x=cursor_x,
            cursor_y=cursor_y,
            font_name=DEFAULT_FONT)

    # 保存两个PDF
    front_c.showPage()
    back_c.showPage()
    front_c.save()
    back_c.save()
    print(f"✅ 正面PDF生成完成！路径：{os.path.abspath(front_pdf)}")
    print(f"✅ 背面PDF生成完成！路径：{os.path.abspath(back_pdf)}")
    print(f"📄 总共渲染了 {a6_index} 个A6区域")

    return front_pdf, back_pdf, a6_index


def merge_front_back_pdfs(front_pdf, back_pdf, output_pdf):
    """
    将正面PDF和背面PDF合并成一个PDF，按照一页front，一页back的顺序
    :param front_pdf: 正面PDF路径
    :param back_pdf: 背面PDF路径
    :param output_pdf: 输出合并后的PDF路径
    """
    # 读取两个PDF文件
    front_reader = PdfReader(front_pdf)
    back_reader = PdfReader(back_pdf)

    writer = PdfWriter()

    # 获取两个PDF的页数
    front_pages = len(front_reader.pages)
    back_pages = len(back_reader.pages)

    # 取较小的页数进行合并
    min_pages = min(front_pages, back_pages)

    print(f"开始合并PDF，正面{front_pages}页，背面{back_pages}页")

    # 按照一页front，一页back的顺序合并
    for i in range(min_pages):
        # 添加正面页
        writer.add_page(front_reader.pages[i])
        # 添加背面页
        writer.add_page(back_reader.pages[i])
        print(f"已添加第{i+1}对页面")

    # 如果正面或背面PDF页数更多，将剩余页面添加到合并后的PDF
    if front_pages > back_pages:
        for i in range(back_pages, front_pages):
            writer.add_page(front_reader.pages[i])
            print(f"已添加正面PDF的额外页面 {i+1}")
    elif back_pages > front_pages:
        for i in range(front_pages, back_pages):
            writer.add_page(back_reader.pages[i])
            print(f"已添加背面PDF的额外页面 {i+1}")

    # 保存合并后的PDF
    with open(output_pdf, 'wb') as out_file:
        writer.write(out_file)

    print(f"✅ PDF合并完成！路径：{os.path.abspath(output_pdf)}")
    print(f"📄 合并后的PDF共有 {len(writer.pages)} 页")


def main():
    if len(sys.argv) < 2:
        print("❌ 参数错误！正确用法：")
        print(f"python {os.path.basename(__file__)} <epub文件路径> [PDF路径]")
        print("示例：")
        print(f"python {os.path.basename(__file__)} ./book.epub ./output.pdf")
        sys.exit(1)

    # 获取命令行参数
    epub_path = sys.argv[1]
    front_pdf_file = "front.pdf"
    back_pdf_file = "back.pdf"

    # 检查输入文件是否存在
    if not os.path.exists(epub_path):
        print(f"❌ 输入文件不存在：{epub_path}")
        sys.exit(1)
    # 默认渲染顺序
    output_dir = "./tmpdir"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
        print(f"解压完成，文件已保存到: {output_dir}")

    # 检查是否提供了合并PDF路径
    merge_pdf_path = "all.pdf"
    if len(sys.argv) >= 3:
        merge_pdf_path = sys.argv[2]
    print(f"渲染顺序：{render_order}")

    _, _, total_a6_regions = generate_custom_order_pdfs(
        epub_path, front_pdf_file, back_pdf_file)

    # 如果提供了合并PDF路径，则合并PDF
    if merge_pdf_path:
        merge_front_back_pdfs(front_pdf_file, back_pdf_file, merge_pdf_path)


if __name__ == "__main__":
    main()
