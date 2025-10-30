from PIL import Image, ImageDraw, ImageFont
import os
import argparse
import re

def create_gradient_background(image_size, color1, color2, direction='vertical'):
    """Creates a gradient background with RGBA support."""
    width, height = image_size
    
    # 将颜色转换为RGBA格式，支持透明度
    def ensure_rgba(color):
        if isinstance(color, str) and color.startswith('#') and len(color) == 7:
            # 如果是十六进制颜色，转换为RGBA，添加透明度
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return (r, g, b, 180)  # 设置透明度为180（淡淡的颜色）
        elif isinstance(color, tuple) and len(color) == 3:
            # 如果是RGB元组，转换为RGBA
            return color + (180,)  # 添加透明度
        elif isinstance(color, tuple) and len(color) == 4:
            # 已经是RGBA格式
            return color
        else:
            # 其他情况，返回淡淡的默认颜色
            return (255, 255, 255, 180)
    
    color1_rgba = ensure_rgba(color1)
    color2_rgba = ensure_rgba(color2)
    
    if direction == 'vertical':
        base = Image.new('RGBA', (width, height), color1_rgba)
        top = Image.new('RGBA', (width, height), color2_rgba)
        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base
    else:  # horizontal
        base = Image.new('RGBA', (width, height), color1_rgba)
        top = Image.new('RGBA', (width, height), color2_rgba)
        mask = Image.new('L', (width, height))
        mask_data = []
        for y in range(height):
            for x in range(width):
                mask_data.append(int(255 * (x / width)))
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base

def create_grid_background(image_size, bg_color='white', grid_color='#DDDDDD', grid_spacing=50):
    """Creates a grid background similar to notes app."""
    width, height = image_size
    
    # 创建背景
    if isinstance(bg_color, (list, tuple)) and len(bg_color) == 2:
        image = create_gradient_background(image_size, bg_color[0], bg_color[1])
    else:
        color = bg_color[0] if isinstance(bg_color, (list, tuple)) else bg_color
        # 创建RGBA模式的图像以支持透明度
        image = Image.new('RGBA', image_size, color=color)
    
    draw = ImageDraw.Draw(image)
    
    # 绘制水平线
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
    
    # 绘制垂直线
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    
    return image

def create_image_with_text(text, width, height, font_path, text_color, bg_color, padding=100, 
                      padding_top=None, padding_bottom=None, padding_left=None, padding_right=None,
                      line_spacing=1.1, align='center', max_font_size=500, bold=False, 
                      grid=False, grid_color="#DDDDDD", grid_spacing=50, 
                      highlight_text=None, highlight_color="#FFEB3B",
                      emoji=None, emoji_position="top"):
    """
    Create an image with text.
    
    Args:
        text (str): Text to draw on the image.
        width (int): Width of the image.
        height (int): Height of the image.
        font_path (str): Path to the .otf or .ttc font file.
        text_color (str): Color of the text.
        bg_color (list): Background color(s). One for solid, two for gradient.
        padding (int): Default padding for all sides.
        padding_top (int): Top padding (overrides padding).
        padding_bottom (int): Bottom padding (overrides padding).
        padding_left (int): Left padding (overrides padding).
        padding_right (int): Right padding (overrides padding).
        line_spacing (float): Line spacing multiplier.
        align (str): Text alignment ('left', 'center', 'right').
        max_font_size (int): Maximum font size to try.
        bold (bool): Whether to make text bold.
        grid (bool): Whether to add grid background like notes app.
        grid_color (str): Color of grid lines.
        grid_spacing (int): Spacing between grid lines.
        highlight_text (str): Text to highlight (substring of main text).
        highlight_color (str): Color for highlighted text.
        emoji (str): Emoji to add to the image.
        emoji_position (str): Position of the emoji ('top' or 'bottom').
    
    Returns:
        PIL.Image.Image: The generated image.
    """
    # 处理转义字符
    text = text.replace('\\n', '\n')
    
    # 处理padding
    padding_top = padding_top if padding_top is not None else padding
    padding_bottom = padding_bottom if padding_bottom is not None else padding
    padding_left = padding_left if padding_left is not None else padding
    padding_right = padding_right if padding_right is not None else padding
    
    # 创建图像尺寸
    image_size = (width, height)
    
    # 1. Create background
    if grid:
        image = create_grid_background(image_size, bg_color, grid_color, grid_spacing)
    elif isinstance(bg_color, (list, tuple)) and len(bg_color) == 2:
        image = create_gradient_background(image_size, bg_color[0], bg_color[1])
    else:
        color = bg_color[0] if isinstance(bg_color, (list, tuple)) else bg_color
        # 使用RGBA模式以支持半透明高亮
        image = Image.new('RGBA', image_size, color=color)
    
    draw = ImageDraw.Draw(image)

    # 2. Find the best font size
    font_size = max_font_size
    font = None
    lines = []

    while font_size > 20:
        if font_path:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                print(f"无法加载字体: {font_path}。将使用默认字体。")
                font = ImageFont.load_default()
                break
        else:
            print("警告：动态字体大小需要指定字体文件路径（font_path）。")
            font = ImageFont.load_default()
            break

        # 基于字符的换行，保留原始字符顺序并记录每行的全局索引范围
        lines = []
        line_ranges = []  # 每行在原始文本中的(start, end) 索引，end为不包含
        available_w = image_size[0] - padding_left - padding_right
        current_line = ""
        current_start = 0
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == '\n':
                # 结束当前行（不包含换行符）
                lines.append(current_line)
                line_ranges.append((current_start, i))
                current_line = ""
                current_start = i + 1
                i += 1
                continue
            test = current_line + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= available_w:
                current_line = test
                i += 1
            else:
                # 当前字符导致溢出，先提交上一行
                if current_line:
                    lines.append(current_line)
                    line_ranges.append((current_start, i))
                    current_line = ""
                    current_start = i
                else:
                    # 单字符超宽，强行作为一行
                    lines.append(ch)
                    line_ranges.append((i, i+1))
                    current_line = ""
                    current_start = i + 1
                    i += 1
        if current_line:
            lines.append(current_line)
            line_ranges.append((current_start, len(text)))

        # 检查是否在垂直方向内
        _, top, _, bottom = font.getbbox("安gjp")
        line_height_val = (bottom - top) * line_spacing
        total_text_height = len(lines) * line_height_val
        if total_text_height <= image_size[1] - padding_top - padding_bottom:
            break
        font_size -= 10

    # 3. Draw the text
    if not lines:
        print("没有内容可以绘制。")
        return image

    _, top, _, bottom = font.getbbox("安gjp")
    line_height_val = (bottom - top) * line_spacing
    total_text_height = (len(lines) -1) * line_height_val
    
    # 计算文本起始y坐标，考虑上下padding
    y = padding_top + (image_size[1] - padding_top - padding_bottom - total_text_height) / 2

    # 添加emoji字体加载器（优先使用系统Apple Color Emoji字体）
    def _load_emoji_font(size):
        candidates = [
            "/System/Library/Fonts/Apple Color Emoji.ttc",
            "/Library/Fonts/Apple Color Emoji.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    # 添加emoji（如果有）
    if emoji:
        emoji_font_size = int(max_font_size * 0.8)  # emoji大小为最大字体大小的80%
        emoji_font = _load_emoji_font(emoji_font_size)
        emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
        emoji_width = emoji_bbox[2] - emoji_bbox[0]
        emoji_height = emoji_bbox[3] - emoji_bbox[1]
        
        if emoji_position == 'top':
            # 在文本上方居中放置emoji
            emoji_x = (image_size[0] - emoji_width) / 2
            emoji_y = padding_top / 2 - emoji_height / 2
            draw.text((emoji_x, emoji_y), emoji, font=emoji_font, fill=text_color)
        elif emoji_position == 'bottom':
            # 在文本下方居中放置emoji
            emoji_x = (image_size[0] - emoji_width) / 2
            emoji_y = image_size[1] - padding_bottom / 2 - emoji_height / 2
            draw.text((emoji_x, emoji_y), emoji, font=emoji_font, fill=text_color)

    # 查找所有需要高亮的区间（支持跨行）
    highlight_spans = []
    if highlight_text:
        for m in re.finditer(re.escape(highlight_text), text):
            highlight_spans.append((m.start(), m.end()))

    for idx, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        
        if align == 'center':
            x = (image_size[0] - line_width) / 2
        elif align == 'right':
            x = image_size[0] - line_width - padding_right
        else:
            x = padding_left
        
        # 在该行内绘制所有与高亮区间相交的片段
        if highlight_color and highlight_spans:
            line_start, line_end = line_ranges[idx]
            corner_radius = 10
            # 计算本行的字符宽度前缀以定位
            def _text_width(s):
                return draw.textbbox((0, 0), s, font=font)[2] if s else 0
            for hs, he in highlight_spans:
                seg_start = max(hs, line_start)
                seg_end = min(he, line_end)
                if seg_end > seg_start:
                    # 该高亮片段在本行内的子串
                    pre_count = seg_start - line_start
                    seg_count = seg_end - seg_start
                    pre_text = line[:pre_count]
                    seg_text = line[pre_count:pre_count + seg_count]
                    pre_width = _text_width(pre_text)
                    seg_width = _text_width(seg_text)

                    highlight_x = x + pre_width
                    highlight_y = y - top
                    highlight_height = bottom - top

                    # 半透明颜色处理
                    if isinstance(highlight_color, str) and highlight_color.startswith('#'):
                        r = int(highlight_color[1:3], 16)
                        g = int(highlight_color[3:5], 16)
                        b = int(highlight_color[5:7], 16)
                        highlight_color_rgba = (r, g, b, 100)
                    elif isinstance(highlight_color, tuple) and len(highlight_color) in (3,4):
                        if len(highlight_color) == 3:
                            highlight_color_rgba = (*highlight_color, 100)
                        else:
                            highlight_color_rgba = highlight_color
                    else:
                        highlight_color_rgba = (255, 235, 59, 100)

                    draw.rounded_rectangle(
                        [(highlight_x - 5, highlight_y - 5),
                         (highlight_x + seg_width + 5, highlight_y + highlight_height + 5)],
                        fill=highlight_color_rgba,
                        radius=corner_radius
                    )
        
        # 如果需要加粗，使用描边技术模拟加粗效果
        if bold:
            # 通过多次绘制文本并轻微偏移来创建加粗效果
            offset = max(1, int(font_size * 0.008))  # 进一步减小偏移量，从0.015改为0.008
            for dx in range(-offset, offset + 1, offset):
                for dy in range(-offset, offset + 1, offset):
                    if dx != 0 or dy != 0:  # 跳过中心点，稍后绘制
                        draw.text((x + dx, y - top + dy), line, font=font, fill=text_color)
            
        # 绘制主要文本
        draw.text((x, y - top), line, font=font, fill=text_color)
        y += line_height_val

    return image

def main():
    parser = argparse.ArgumentParser(description="Generate an image with text.")
    parser.add_argument("text", type=str, help="Text to draw on the image.")
    parser.add_argument("--output", type=str, default="outputs/generated_image.png", help="Path to save the output image.")
    parser.add_argument("--font", type=str, default="fonts/ZCOOLKuaiLe-Regular.ttf", help="Path to the .otf or .ttc font file.")
    parser.add_argument("--width", type=int, default=1080, help="Width of the image.")
    parser.add_argument("--height", type=int, default=1920, help="Height of the image.")
    parser.add_argument("--bg-color", type=str, nargs='+', default=['white'], help="Background color(s). One for solid, two for gradient.")
    parser.add_argument("--text-color", type=str, default='#333333', help="Color of the text.")
    parser.add_argument("--padding", type=int, default=100, help="Default padding for all sides.")
    parser.add_argument("--padding-top", type=int, help="Top padding (overrides --padding).")
    parser.add_argument("--padding-bottom", type=int, help="Bottom padding (overrides --padding).")
    parser.add_argument("--padding-left", type=int, help="Left padding (overrides --padding).")
    parser.add_argument("--padding-right", type=int, help="Right padding (overrides --padding).")
    parser.add_argument("--line-spacing", type=float, default=1.1, help="Line spacing multiplier.")
    parser.add_argument("--align", type=str, default='center', choices=['left', 'center', 'right'], help="Text alignment.")
    parser.add_argument("--max-font-size", type=int, default=500, help="Maximum font size to try.")
    parser.add_argument("--bold", action="store_true", help="Make text bold.")
    parser.add_argument("--grid", action="store_true", help="Add grid background like notes app.")
    parser.add_argument("--grid-color", type=str, default="#DDDDDD", help="Color of grid lines.")
    parser.add_argument("--grid-spacing", type=int, default=50, help="Spacing between grid lines.")
    parser.add_argument("--highlight", type=str, help="Text to highlight (substring of main text).")
    parser.add_argument("--highlight-color", type=str, default="#FFEB3B", help="Color for highlighted text.")
    parser.add_argument("--emoji", type=str, help="Emoji to add to the image.")
    parser.add_argument("--emoji-position", type=str, default="top", choices=["top", "bottom"], help="Position of the emoji.")

    args = parser.parse_args()

    # Validate font file existence
    if not os.path.exists(args.font):
        print(f"错误：字体文件未找到 at '{args.font}'")
        print("请下载一款中文字体 (例如'思源黑体') 并将其放置在 'fonts' 文件夹中。")
        print("您可以从这里下载: https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSans.ttc.zip")
        return

    # Create and save the image
    image = create_image_with_text(
        text=args.text,
        width=args.width,
        height=args.height,
        font_path=args.font,
        text_color=args.text_color,
        bg_color=args.bg_color if len(args.bg_color) > 1 else args.bg_color[0],
        padding=args.padding,
        padding_top=args.padding_top,
        padding_bottom=args.padding_bottom,
        padding_left=args.padding_left,
        padding_right=args.padding_right,
        line_spacing=args.line_spacing,
        align=args.align,
        max_font_size=args.max_font_size,
        bold=args.bold,
        grid=args.grid,
        grid_color=args.grid_color,
        grid_spacing=args.grid_spacing,
        highlight_text=args.highlight,
        highlight_color=args.highlight_color,
        emoji=args.emoji,
        emoji_position=args.emoji_position
    )

    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image.save(args.output)
    print(f"图片已保存到: {args.output}")


if __name__ == '__main__':
    main()
