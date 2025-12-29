from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
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

# 文本渲染配置
TEXT_FONT_SIZE = 10
TEXT_LINE_SPACE = 3
MARGIN = 10  # 区域内边距
render_order = [(0, 0), (1, 1), (1, 0), (0, 1), (0, 2), (1, 3), (1, 2), (0, 3)]
# 初始化两个PDF画布（A4竖版）
front_c = canvas.Canvas("front.pdf", pagesize=A4)
back_c = canvas.Canvas("back.pdf", pagesize=A4)

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


def draw_html_in_a6_region(a6_index,
                           html_content,
                           cursor_x=None,
                           cursor_y=None,
                           font_size=TEXT_FONT_SIZE,
                           font_name=DEFAULT_FONT):
    """
    draw_html_in_a6_region 的 Docstring
    
    :param a6_index: 
    :param html_content: 说明
    :param cursor_x: 说明
    :param cursor_y: 说明
    :param font_size: 说明
    :param font_name: 说明
    """ 
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')

    print(soup)
    # 文本边距
    margin = MARGIN

    # 获取当前要渲染的A6区域位置
    page_idx, pos_idx = render_order[a6_index % 8]

    # 选择当前应该渲染的画布（正面或背面）
    if page_idx == 0:  # 正面页
        current_canvas = front_c
    else:  # 背面页
        current_canvas = back_c

    print(f"  渲染第 {a6_index+1} 个A6区域 (第{page_idx+1}页, 位置{pos_idx})")

    # 获取当前A6区域的物理位置
    x_offset, y_offset = page_positions[page_idx][pos_idx]

    # 设置起始绘制位置
    if cursor_x is None:
        cursor_x = x_offset + margin
    if cursor_y is None:
        cursor_y = y_offset - margin  # 从顶部开始

    # 绘制文本行的高度

    # 设置字体
    current_canvas.setFont(font_name, font_size)

    # 提取文本内容
    text_content = soup.get_text()
    lines = text_content.split('\n')

    remaining_content = ""
    has_more_content = False

    # for i, line in enumerate(lines):
    #     if not line.strip():
    #         continue

    #     # 普通文本处理
    #     words = line.split()
    #     current_line = ""

    #     for word in words:
    #         test_line = current_line + " " + word if current_line else word
    #         line_width = current_canvas.stringWidth(test_line, font_name,
    #                                             font_size)

    #         if line_width <= available_width:
    #             current_line = test_line
    #         else:
    #             # 当前行已满，绘制当前行
    #             required_height = font_size + TEXT_LINE_SPACE
    #             if (cursor_y - required_height) >= (y + margin):
    #                 current_canvas.drawString(cursor_x - margin,
    #                                         cursor_y - font_size,
    #                                         current_line)
    #                 cursor_y -= required_height
    #                 current_line = word
    #             else:
    #                 # 没有足够空间，保存剩余内容
    #                 remaining_words = [current_line] + [
    #                     word
    #                 ] + words[words.index(word) + 1:]
    #                 remaining_content += " ".join(
    #                     remaining_words) + "\n" + "\n".join(lines[i + 1:])
    #                 has_more_content = True
    #                 break

    #     # 绘制最后的行
    #     if current_line and not has_more_content:
    #         required_height = font_size + TEXT_LINE_SPACE
    #         if (cursor_y - required_height) >= (y + margin):
    #             current_canvas.drawString(cursor_x - margin,
    #                                     cursor_y - font_size, current_line)
    #             cursor_y -= required_height
    #         else:
    #             remaining_content += current_line + "\n" + "\n".join(
    #                 lines[i + 1:])
    #             has_more_content = True
    #             break

    # 返回下次绘制的位置
    next_x = cursor_x
    next_y = cursor_y
    return a6_index, next_x, next_y


def generate_custom_order_pdfs(epub_path, front_pdf, back_pdf):
    """
    从EPUB文件生成两个PDF（正面和背面），按照自定义顺序交替渲染内容
    :param epub_path: EPUB文件路径
    :param front_pdf: 正面PDF文件路径
    :param back_pdf: 背面PDF文件路径
    :param render_order: 渲染顺序列表，包含8个元素，每个元素是(页码, 位置索引)的元组
    """

    a6_index = 0
    cursor_x = 0  # 初始化游标
    cursor_y = A6_HEIGHT  # 初始化游标
    remaining_html = ""

    # 遍历EPUB的HTML内容
    for html_content in epub_html_iter(epub_path):
        print(f"处理HTML内容: {html_content[:100]}...")  # 只打印前100个字符

        # 合并剩余内容和当前内容
        current_content = remaining_html + html_content if remaining_html else html_content

        # 在A6区域内绘制HTML内容
        a6_index, cursor_x, cursor_y = draw_html_in_a6_region(
            a6_index == a6_index,
            html_content=current_content,
            cursor_x=cursor_x,
            cursor_y=cursor_y,
            font_name=DEFAULT_FONT)

    # 保存两个PDF
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

    # 检查是否提供了合并PDF路径
    merge_pdf_path = None
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
