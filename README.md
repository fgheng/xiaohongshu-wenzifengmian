# 小红书文字封面生成器

本工具可以根据输入文字快速生成适合小红书封面的高质量图片，支持渐变背景、网格背景、文字高亮、Emoji 添加以及动态字体大小调整。适合制作社交媒体封面、笔记封面和海报。

![文字封面](outputs/generated_image.png)

---

## 功能特点

1. **自动适配字体大小**  
   根据图片尺寸和文字内容自动调整字体大小，保证文字完整显示。

2. **多种背景类型**  
   - 单色背景  
   - 渐变背景（水平或垂直渐变）  
   - 网格背景（类似笔记本风格）

3. **文字高亮**  
   可指定子文字进行高亮显示，支持半透明和圆角效果。

4. **文字样式**  
   - 支持加粗（通过描边模拟）  
   - 文本对齐：左对齐、居中、右对齐  
   - 自定义行间距

5. **Emoji 支持**  
   可在图片顶部或底部添加 Emoji，增强视觉效果。

6. **灵活的内边距设置**  
   支持统一 padding 或单独设置上下左右 padding。

7. **输出格式**  
   PNG 图片，支持透明度和高质量色彩。

---

## 安装依赖


1.  **克隆仓库**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **安装依赖**:
    ```bash
    pip install Pillow
    ```

3.  **准备字体**:
    -   下载一款你喜欢的中文字体（例如[思源黑体](https://github.com/adobe-fonts/source-han-sans/releases/download/2.004R/SourceHanSans.ttc.zip)）。
    -   在项目根目录下创建一个 `fonts` 文件夹，并将字体文件放入其中。
    -   你可以根据需要组织字体文件，例如 `fonts/thin/SmileySans-Oblique.otf`。

---

## 使用方法

```bash
python generate_image.py "你的文字内容" --output outputs/my_image.png
```

### 常用参数说明

| 参数                                                                          | 说明                      | 默认值                             |
| --------------------------------------------------------------------------- | ----------------------- | ------------------------------- |
| `text`                                                                      | 要绘制的文字                  | 必填                              |
| `--output`                                                                  | 输出图片路径                  | `outputs/generated_image.png`   |
| `--font`                                                                    | 字体文件路径 (.ttf/.otf/.ttc) | `fonts/ZCOOLKuaiLe-Regular.ttf` |
| `--width`                                                                   | 图片宽度                    | `1080`                          |
| `--height`                                                                  | 图片高度                    | `1920`                          |
| `--bg-color`                                                                | 背景颜色，可传1个或2个，支持渐变       | `white`                         |
| `--text-color`                                                              | 文字颜色                    | `#333333`                       |
| `--padding`                                                                 | 默认内边距                   | `100`                           |
| `--padding-top` / `--padding-bottom` / `--padding-left` / `--padding-right` | 单独设置边距                  | 同 `--padding`                   |
| `--line-spacing`                                                            | 行间距倍数                   | `1.1`                           |
| `--align`                                                                   | 文本对齐方式                  | `center`                        |
| `--max-font-size`                                                           | 最大字体大小                  | `500`                           |
| `--bold`                                                                    | 是否加粗                    | False                           |
| `--grid`                                                                    | 是否启用网格背景                | False                           |
| `--grid-color`                                                              | 网格线颜色                   | `#DDDDDD`                       |
| `--grid-spacing`                                                            | 网格间距                    | `50`                            |
| `--highlight`                                                               | 要高亮的文字                  | None                            |
| `--highlight-color`                                                         | 高亮颜色                    | `#FFEB3B`                       |
| `--emoji`                                                                   | 要添加的 Emoji              | None                            |
| `--emoji-position`                                                          | Emoji 位置                | `top`                           |

---

## 小红书封面示例

1. **单色背景封面**

```bash
python generate_image.py "今日分享" --bg-color "#FF6B6B" --text-color "#FFFFFF" --bold
```


效果示意：
![单色背景示例](./outputs/monochrome.png)

2. **渐变背景封面**

```bash
python generate_image.py "渐变封面" --bg-color "#FFB347" "#FFCC33" --text-color "#333333" --bold
```

效果示意：
![渐变背景示例](./gradient.png)

3. **网格笔记风格**

```bash
python generate_image.py "笔记风格封面" --grid --grid-color "#CCCCCC" --grid-spacing 40 --text-color "#333333"
```

效果示意：
![网格背景示例](./outputs/grid.png)

4. **文字高亮 + Emoji**

```bash
python generate_image.py "小红书封面" --highlight "封面" --highlight-color "#FFFF00" --emoji "🎉" --emoji-position top --bg-color "#FF6B6B" --text-color "#FFFFFF"
```

效果示意：
![高亮+Emoji示例](./outputs/highlight.png)

> 注：示意图为占位图，实际生成图片以本工具输出为准。

---

## 推荐配色方案

| 背景类型 | 配色示例                              | 文字颜色         |
| ---- | --------------------------------- | ------------ |
| 单色   | `#FF6B6B` / `#4ECDC4` / `#1A535C` | 白色 / 黑色      |
| 渐变   | `#FFB347` → `#FFCC33`             | 深灰 `#333333` |
| 渐变   | `#6A82FB` → `#FC5C7D`             | 白色 `#FFFFFF` |


---

## 注意事项

1. 文字过长时字体会自动缩小，但可能仍无法完全显示，请适当增加图片尺寸。
2. 高亮文字支持跨行，但需确保子文字在原文中存在。
3. Emoji 渲染依赖系统字体，部分系统可能显示为方块。
4. 输出目录默认 `outputs/`，生成 PNG 图片。


## 贡献

欢迎通过提交 Pull Request 来为此项目做出贡献。

## 许可证

本项目采用 [MIT](LICENSE) 许可证。
