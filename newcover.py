import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def merge_two_images_with_vertical_text(img1_path, img2_path, text_width_mm, text_content):
    """
    拼接两张图片，中间添加指定毫米宽度的白色背景+竖排黑色文字
    :param img1_path: 第一张图片路径
    :param img2_path: 第二张图片路径
    :param text_width_mm: 中间文字区域的宽度，单位mm
    :param text_content: 中间要显示的竖排文字内容
    """
    # -------------------------- 基础配置（固定） --------------------------
    DPI = 96  # 屏幕/打印通用DPI，96DPI是Windows/Linux默认，Mac为72，可根据需求微调
    MM_TO_INCH = 1 / 25.4  # 毫米转英寸的固定系数
    text_color = (0, 0, 0)  # 文字颜色：纯黑色
    bg_color = (255, 255, 255)  # 中间背景色：纯白色

    # -------------------------- 单位转换：毫米(mm) → 像素(pixel) --------------------------
    # 公式：像素数 = 毫米数 × DPI × (1/25.4)
    text_width_pixel = int(round(text_width_mm * DPI * MM_TO_INCH))
    if text_width_pixel < 20:  # 最小宽度限制，避免文字无法显示
        text_width_pixel = 20

    # -------------------------- 打开并统一两张图片的高度 --------------------------
    # 打开图片，确保为RGB模式（避免透明通道/灰度图异常）
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")
    # 取两张图片的最大高度作为拼接后统一高度，宽度不变，保证图片不变形
    target_height = max(img1.height, img2.height)
    # 等比例调整图片高度，宽度自适应
    img1 = img1.resize((int(img1.width * target_height / img1.height), target_height), Image.Resampling.LANCZOS)
    img2 = img2.resize((int(img2.width * target_height / img2.height), target_height), Image.Resampling.LANCZOS)

    # -------------------------- 创建中间的「白色背景+竖排文字」画布 --------------------------
    text_canvas = Image.new("RGB", (text_width_pixel, target_height), bg_color)
    draw = ImageDraw.Draw(text_canvas)

    # -------------------------- 自动适配文字大小 + 竖排文字绘制 --------------------------
    # 文字大小自适应：基于留白宽度动态调整字号，保证文字在宽度内显示完整
    font_size = int(text_width_pixel * 0.4)  # 字号为留白宽度的80%，核心适配逻辑
    # 加载字体（优先系统默认无衬线字体，跨平台兼容）
    try:
        # Windows系统
        font = ImageFont.truetype("./FZXSS-Lusitana-Hybrid.ttf", font_size, encoding="utf-8")
    except:
        try:
            # Mac系统
            font = ImageFont.truetype("./FZXSS-Lusitana-Hybrid.ttf", font_size)
        except:
            # Linux/无指定字体时，使用默认字体
            font = ImageFont.load_default(size=font_size)

    # 核心：竖排文字绘制（每个字单独换行，居中对齐）
    # 计算文字总高度，用于垂直居中
    total_text_height = sum([draw.textbbox((0, 0), char, font=font)[3] for char in text_content])
    # 计算文字绘制的起始Y坐标（垂直居中）
    start_y = (target_height - total_text_height) / 2
    x = text_width_pixel / 2  # 文字绘制的X坐标（水平居中）

    # 逐个字符绘制，实现竖排效果
    current_y = start_y
    for char in text_content:
        # 获取单个字符的宽高，精准居中
        char_bbox = draw.textbbox((0, 0), char, font=font)
        char_w, char_h = char_bbox[2] - char_bbox[0], char_bbox[3] - char_bbox[1]
        draw.text((x - char_w/2, current_y), char, fill=text_color, font=font)
        current_y += char_h + int(font_size * 0.2)  # 字符间留20%字号的间距，更美观

    # -------------------------- 拼接三张画布：img1 + 文字背景 + img2 --------------------------
    # 计算最终拼接图的总宽度
    final_width = img1.width + text_width_pixel + img2.width
    final_height = target_height
    # 创建最终画布
    final_img = Image.new("RGB", (final_width, final_height), bg_color)
    # 粘贴图片和文字背景
    final_img.paste(img1, (0, 0))
    final_img.paste(text_canvas, (img1.width, 0))
    final_img.paste(img2, (img1.width + text_width_pixel, 0))

    # -------------------------- 保存结果 --------------------------
    save_path = "merged_result.png"
    final_img.save(save_path, quality=95)
    print(f"✅ 拼接完成！结果已保存至: {save_path}")
    print(f"📌 相关参数：文字区域宽度={text_width_mm}mm({text_width_pixel}px)，文字内容={text_content}")

if __name__ == "__main__":
    # 校验命令行参数数量
    if len(sys.argv) != 5:
        print("❌ 参数错误！正确运行方式：")
        print("python img_merge_with_text.py <img1路径> <img2路径> <文字区域宽度mm> <竖排文字内容>")
        print("📌 示例：python img_merge_with_text.py a.jpg b.png 20 测试竖排文字")
        sys.exit(1)
    
    # 接收命令行传入的4个参数
    img1 = sys.argv[1]
    img2 = sys.argv[2]
    txt_width_mm = float(sys.argv[3])
    text = sys.argv[4]

    # 执行拼接
    merge_two_images_with_vertical_text(img1, img2, txt_width_mm, text)


