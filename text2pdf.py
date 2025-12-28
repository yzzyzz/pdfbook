from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys
import re


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


def read_text_file(file_path):
    """
    读取txt文件内容
    :param file_path: txt文件路径
    :return: 文件内容字符串
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content



def draw_text_in_a6_region_with_cursor(canvas_obj,
                                       text,
                                       start_cursor,
                                       x,
                                       y,
                                       width,
                                       height,
                                       font_size=TEXT_FONT_SIZE,
                                       font_name=DEFAULT_FONT):
    """
    在指定的A6区域内绘制文本，使用游标模式
    :param canvas_obj: PDF画布对象
    :param text: 完整文本内容
    :param start_cursor: 开始位置游标
    :param x: 区域左下角x坐标
    :param y: 区域左下角y坐标
    :param width: 区域宽度
    :param height: 区域高度
    :param font_size: 字体大小
    :param font_name: 字体名称
    :return: (end_cursor, has_more_text) - 结束游标位置和是否还有更多文本
    """
    # 设置字体
    canvas_obj.setFont(font_name, font_size)

    # 文本边距
    margin = MARGIN
    available_width = width - 2 * margin
    available_height = height - 2 * margin

    # 绘制文本行
    text_y = y + height - margin  # 从顶部开始
    line_height = font_size + TEXT_LINE_SPACE

    current_cursor = start_cursor

    # 逐行处理文本直到区域用完或文本处理完毕
    while current_cursor < len(text) and (text_y - line_height) >= (y +
                                                                    margin):
        # 检查是否是新段落的开始
        # 检查是否是段落开头（在游标位置之前的前两个字符是'\n\n'，或游标在文本开头）
        is_paragraph_start = (
            current_cursor == 0 or  # 文本开头
            (current_cursor >= 2
             and text[current_cursor - 2:current_cursor] == '\n\n')  # 段落分隔后
        )

        # 找到当前行的文本
        line_start = current_cursor
        line_end = line_start

        # 确定当前行是否需要缩进，计算可用宽度
        if is_paragraph_start:
            indent_text = "    "  # 4个空格缩进
            current_line_available_width = available_width - canvas_obj.stringWidth(
                indent_text, font_name, font_size)
        else:
            current_line_available_width = available_width

        # 寻找合适的换行点
        while line_end < len(text):
            # 检查是否遇到换行符
            if text[line_end] == '\n':
                line_end += 1  # 包含换行符
                break

            # 检查当前行的宽度
            test_line = text[line_start:line_end + 1]
            # 检查是否新段落开始
            if '\n\n' in test_line and test_line.rindex(
                    '\n\n') == len(test_line) - 2:
                # 如果当前行包含段落结束符，截断到段落结束符
                line_end = line_start + test_line.rindex('\n\n')
                break

            line_width = canvas_obj.stringWidth(test_line, font_name,
                                                font_size)

            # 如果当前行宽度超过可用宽度，回退到上一个合适的断点
            if line_width > current_line_available_width:
                if line_end == line_start:
                    # 单个字符就超宽，强制换行
                    line_end += 1
                    break
                else:
                    # 找到上一个空格作为断点
                    space_pos = test_line.rfind(' ')
                    if space_pos > 0:
                        line_end = line_start + space_pos + 1
                    else:
                        # 没有空格，强制在当前字符处断开
                        line_end -= 1
                    break
            else:
                line_end += 1

        # 获取当前行文本
        current_line = text[line_start:line_end].rstrip('\n')

        # 检查是否遇到段落分隔符
        if '\n\n' in current_line:
            paragraph_end_pos = current_line.index('\n\n')
            current_line = current_line[:paragraph_end_pos]
            # 修正游标位置，确保下一次处理从新段落开始
            actual_end = line_start + paragraph_end_pos + 2  # 加上'\n\n'的长度
        else:
            actual_end = line_end

        # 绘制当前行
        if current_line:
            # 检查是否为章节标题（第x章 或 第x回 开头）
            chapter_pattern = r'^第[一二三四五六七八九十零\d]+[章节回篇卷].*'
            if re.match(chapter_pattern, current_line.strip()):
                # 设置章节标题字体大小
                title_font_size = 12
                canvas_obj.setFont(font_name, title_font_size)
                
                # 居中显示
                text_width = canvas_obj.stringWidth(current_line, font_name, title_font_size)
                center_x = x + (width - text_width) / 2
                text_y -= line_height
                canvas_obj.drawString(center_x, text_y - title_font_size, current_line)
                # 恢复默认字体大小
                canvas_obj.setFont(font_name, font_size)
            else:
                # 普通文本处理
                if is_paragraph_start:
                    # 第一行添加缩进
                    indented_line = "    " + current_line  # 4个空格缩进
                    canvas_obj.drawString(x + margin, text_y - font_size,
                                          indented_line)
                else:
                    # 非第一行不添加缩进
                    canvas_obj.drawString(x + margin, text_y - font_size,
                                          current_line)

        # 更新游标和Y坐标
        current_cursor = actual_end
        text_y -= line_height

        # 检查是否已经处理完整个文本
        if current_cursor >= len(text):
            break

    # 返回结束游标和是否还有更多文本
    has_more_text = current_cursor < len(text)
    return current_cursor, has_more_text

def generate_custom_order_pdfs(text_file_path, front_pdf, back_pdf,
                               render_order):
    """
    从txt文件生成两个PDF（正面和背面），按照自定义顺序交替渲染内容
    :param text_file_path: txt文件路径
    :param front_pdf: 正面PDF文件路径
    :param back_pdf: 背面PDF文件路径
    :param render_order: 渲染顺序列表，包含8个元素，每个元素是(页码, 位置索引)的元组
    """
    # 读取txt文件
    text_content = read_text_file(text_file_path)

    # 初始化两个PDF画布（A4竖版）
    front_c = canvas.Canvas(front_pdf, pagesize=A4)
    back_c = canvas.Canvas(back_pdf, pagesize=A4)

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

    cursor = 0  # 初始化游标
    has_more_text = True
    sheet_count = 0  # 双面打印对计数器
    a6_index = 0

    while has_more_text:
        print(f"正在处理第 {sheet_count + 1} 个双面打印对...")
        page_idx, pos_idx = render_order[a6_index % 8]
        # 选择当前应该渲染的画布（正面或背面）
        if page_idx == 0:  # 正面页
            current_canvas = front_c
        else:  # 背面页
            current_canvas = back_c

        print(f"  渲染第 {a6_index} 个A6区域 (第{page_idx+1}页, 位置{pos_idx})")

        # 获取当前A6区域的物理位置
        x_offset, y_offset = page_positions[page_idx][pos_idx]

        # 绘制A6区域边框（可选，便于查看布局）
        current_canvas.rect(x_offset,
                            y_offset,
                            A6_WIDTH,
                            A6_HEIGHT,
                            stroke=1,
                            fill=0)

        # 在A6区域内绘制文本，并更新游标
        cursor, has_more_text = draw_text_in_a6_region_with_cursor(
            canvas_obj=current_canvas,
            text=text_content,
            start_cursor=cursor,
            x=x_offset,
            y=y_offset,
            width=A6_WIDTH,
            height=A6_HEIGHT,
            font_name=DEFAULT_FONT)

        if a6_index % 8 == 7:
            front_c.showPage()
            back_c.showPage()
            sheet_count += 1

        a6_index += 1

    # 保存两个PDF
    front_c.save()
    back_c.save()

    print(f"✅ 正面PDF生成完成！路径：{os.path.abspath(front_pdf)}")
    print(f"✅ 背面PDF生成完成！路径：{os.path.abspath(back_pdf)}")
    print(f"📝 从位置 0 到位置 {cursor} 的文本已被处理")
    print(f"📝 原始文本长度: {len(text_content)}, 已处理长度: {cursor}")
    print(f"📄 每个PDF共生成了 {sheet_count} 页")
    
    return front_pdf, back_pdf, sheet_count


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
    if len(sys.argv) < 4:
        print("❌ 参数错误！正确用法：")
        print(
            f"python {os.path.basename(__file__)} <txt文件路径> <正面PDF路径> <背面PDF路径> [渲染顺序] [合并PDF路径]"
        )
        print("渲染顺序格式：用逗号分隔的'页码-位置'对，例如：0-0,0-1,1-0,1-1,0-2,0-3,1-2,1-3")
        print("页码从0开始（0=正面页，1=背面页），位置从0-3（左上=0，右上=1，左下=2，右下=3）")
        print("示例：")
        print(
            f"python {os.path.basename(__file__)} ./input.txt ./front.pdf ./back.pdf 0-3,0-0,1-0,1-1,0-2,0-1,1-2,1-3 ./all.pdf"
        )
        print("如不提供渲染顺序，则按默认顺序处理")
        print("如不提供合并PDF路径，则只生成正面和背面PDF")
        sys.exit(1)

    # 获取命令行参数
    input_txt_file = sys.argv[1]
    front_pdf_file = sys.argv[2]
    back_pdf_file = sys.argv[3]

    # 检查输入文件是否存在
    if not os.path.exists(input_txt_file):
        print(f"❌ 输入文件不存在：{input_txt_file}")
        sys.exit(1)
        # 按照可读顺序来搞定 0 1 2 3  4 5 6 7 ->
        # 执行默认顺序的PDF生成
    render_order = [(0, 0), (1, 1), (1, 0), (0, 1), (0, 2), (1, 3), (1, 2),
                    (0, 3)]
    
    # 检查是否提供了合并PDF路径
    merge_pdf_path = None
    if len(sys.argv) >= 5:
        merge_pdf_path = sys.argv[4]
    print(f"渲染顺序：{render_order}")
    
    _, _, sheet_count = generate_custom_order_pdfs(input_txt_file, front_pdf_file,
                                back_pdf_file, render_order)
    
    # 如果提供了合并PDF路径，则合并PDF
    if merge_pdf_path:
        merge_front_back_pdfs(front_pdf_file, back_pdf_file, merge_pdf_path)
    


if __name__ == "__main__":
    main()