from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import util


# ==================== 配置常量 ====================
# 页面配置
PAGE_LAYOUT = "A4_VERTICAL_4_A6"  # A4竖版，每页4个A6区域
A6_REGIONS_PER_PAGE = 4  # 每页4个A6区域（2x2布局）

# 注册字体
FONT_NAME = "FangSong"
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fs.ttf")

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


def draw_text_in_a6_region_with_cursor(canvas_obj, text, start_cursor, x, y, width, height, font_size=TEXT_FONT_SIZE, font_name=DEFAULT_FONT):
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
    while current_cursor < len(text) and (text_y - line_height) >= (y + margin):
        # 检查是否是新段落的开始
        # 检查是否是段落开头（在游标位置之前的前两个字符是'\n\n'，或游标在文本开头）
        is_paragraph_start = (
            current_cursor == 0 or  # 文本开头
            (current_cursor >= 2 and text[current_cursor-2:current_cursor] == '\n\n')  # 段落分隔后
        )
        
        # 找到当前行的文本
        line_start = current_cursor
        line_end = line_start
        
        # 确定当前行是否需要缩进，计算可用宽度
        if is_paragraph_start:
            indent_text = "    "  # 4个空格缩进
            current_line_available_width = available_width - canvas_obj.stringWidth(indent_text, font_name, font_size)
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
            if '\n\n' in test_line and test_line.rindex('\n\n') == len(test_line) - 2:
                # 如果当前行包含段落结束符，截断到段落结束符
                line_end = line_start + test_line.rindex('\n\n')
                break
            
            line_width = canvas_obj.stringWidth(test_line, font_name, font_size)
            
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
            if is_paragraph_start:
                # 第一行添加缩进
                indented_line = "    " + current_line  # 4个空格缩进
                canvas_obj.drawString(x + margin, text_y - font_size, indented_line)
            else:
                # 非第一行不添加缩进
                canvas_obj.drawString(x + margin, text_y - font_size, current_line)
        
        # 更新游标和Y坐标
        current_cursor = actual_end
        text_y -= line_height
        
        # 检查是否已经处理完整个文本
        if current_cursor >= len(text):
            break
    
    # 返回结束游标和是否还有更多文本
    has_more_text = current_cursor < len(text)
    return current_cursor, has_more_text


def generate_pdf_from_text(text_file_path, output_pdf):
    """
    从txt文件生成PDF，每页4个A6区域，使用游标模式
    :param text_file_path: txt文件路径
    :param output_pdf: 输出PDF文件路径
    """
    # 读取txt文件
    text_content = read_text_file(text_file_path)
    
    # 初始化PDF画布（A4竖版）
    c = canvas.Canvas(output_pdf, pagesize=A4)
    
    # A6区域位置定义（2x2网格）
    a6_positions = [
        (0, A6_HEIGHT),  # 左上
        (A6_WIDTH, A6_HEIGHT),  # 右上
        (0, 0),  # 左下
        (A6_WIDTH, 0)  # 右下
    ]
    
    cursor = 0  # 初始化游标
    page_num = 1
    has_more_text = True
    
    while has_more_text:
        print(f"正在处理第 {page_num} 页...")
        
        # 每页最多4个A6区域
        for pos_idx in range(A6_REGIONS_PER_PAGE):
            if not has_more_text:
                break
                
            # 获取当前A6区域的位置
            x_offset, y_offset = a6_positions[pos_idx]
            
            # 绘制A6区域边框（可选，便于查看布局）
            c.rect(x_offset, y_offset, A6_WIDTH, A6_HEIGHT, stroke=1, fill=0)
            
            # 在A6区域内绘制文本，并更新游标
            cursor, has_more_text = draw_text_in_a6_region_with_cursor(
                canvas_obj=c,
                text=text_content,
                start_cursor=cursor,
                x=x_offset,
                y=y_offset,
                width=A6_WIDTH,
                height=A6_HEIGHT,
                font_name=DEFAULT_FONT
            )
            
        # 显示页面并准备下一页
        c.showPage()
        page_num += 1
        
        # 如果文本已处理完但当前页还有空余区域，跳出循环
        if not has_more_text:
            break
    
    # 保存PDF
    c.save()
    
    print(f"✅ PDF生成完成！")
    print(f"📁 输出路径：{os.path.abspath(output_pdf)}")
    print(f"📄 共生成了 {page_num-1} 页PDF")
    print(f"📝 从位置 0 到位置 {cursor} 的文本已被处理")


def main():
    if len(sys.argv) != 3:
        print("❌ 参数错误！正确用法：")
        print(f"python {os.path.basename(__file__)} <txt文件路径> <输出PDF文件路径>")
        print("示例：")
        print(f"python {os.path.basename(__file__)} ./input.txt ./output.pdf")
        sys.exit(1)

    # 获取命令行参数
    input_txt_file = sys.argv[1]
    output_pdf_file = sys.argv[2]

    # 检查输入文件是否存在
    if not os.path.exists(input_txt_file):
        print(f"❌ 输入文件不存在：{input_txt_file}")
        sys.exit(1)

    # 执行PDF生成
    try:
        generate_pdf_from_text(input_txt_file, output_pdf_file)
    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()