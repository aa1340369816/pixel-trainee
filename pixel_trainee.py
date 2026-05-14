import tkinter as tk
from tkinter import filedialog, messagebox
import random
from PIL import Image

# ---------- 64x64 模板（随机模式仍用 64x64，之后放大显示） ----------
def create_template():
    grid = [[0] * 64 for _ in range(64)]

    def rect(x1, y1, x2, y2, code):
        for y in range(max(0, y1), min(64, y2 + 1)):
            for x in range(max(0, x1), min(64, x2 + 1)):
                grid[y][x] = code

    def circle(cx, cy, r, code):
        for y in range(max(0, cy - r), min(64, cy + r + 1)):
            for x in range(max(0, cx - r), min(64, cx + r + 1)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2:
                    grid[y][x] = code

    circle(32, 18, 9, 1)
    rect(23, 10, 41, 19, 1)
    circle(32, 14, 10, 2)
    circle(32, 18, 8, 1)
    rect(28, 12, 36, 14, 2)
    rect(30, 10, 34, 13, 2)
    rect(22, 14, 24, 22, 2)
    rect(40, 14, 42, 22, 2)
    rect(28, 17, 30, 18, 0)
    rect(34, 17, 36, 18, 0)
    rect(26, 28, 38, 45, 3)
    for i in range(10):
        x = 26 - i; y = 30 + i
        if 0 <= x < 64 and 0 <= y < 64:
            grid[y][x] = 1
        if 0 <= x-1 < 64: grid[y][x-1] = 1
    for i in range(10):
        x = 38 + i; y = 30 + i
        if 0 <= x < 64 and 0 <= y < 64:
            grid[y][x] = 1
        if 0 <= x+1 < 64: grid[y][x+1] = 1
    rect(17, 38, 20, 42, 1)
    rect(44, 38, 47, 42, 1)
    rect(26, 46, 31, 57, 4)
    rect(34, 46, 39, 57, 4)
    rect(25, 58, 32, 60, 5)
    rect(33, 58, 40, 60, 5)
    rect(29, 35, 35, 40, 6)
    return grid

def random_skin():
    r,g,b = random.randint(230,255),random.randint(180,210),random.randint(140,180)
    return f'#{r:02x}{g:02x}{b:02x}'

def random_hair():
    return random.choice(['#1a1a1a','#3b2f2f','#6b4c3b','#c8a45c',
                          '#a0522d','#2b2b2b','#d4a373','#b5651d',
                          '#4a2e2b','#1e1e2f','#cc5500'])

def random_clothes():
    return f'#{random.randint(50,220):02x}{random.randint(50,220):02x}{random.randint(50,220):02x}'

def render_image_64(template):
    skin = random_skin()
    hair = random_hair()
    top = random_clothes()
    pants = random_clothes()
    shoes = random_clothes()
    badge_bg = f'#{random.randint(200,255):02x}{random.randint(200,255):02x}{random.randint(200,255):02x}'
    badge_fg = '#000000'

    colors = [['#ffffff']*64 for _ in range(64)]
    for y in range(64):
        for x in range(64):
            code = template[y][x]
            if code == 0: continue
            elif code == 1: colors[y][x] = skin
            elif code == 2: colors[y][x] = hair
            elif code == 3: colors[y][x] = top
            elif code == 4: colors[y][x] = pants
            elif code == 5: colors[y][x] = shoes
            elif code == 6: colors[y][x] = badge_bg

    for ex,ey in [(28,17),(35,17)]: colors[ey][ex] = '#000000'
    star = [(32,35),(31,36),(29,36),(31,37),(30,38),
            (32,38),(34,38),(33,37),(35,36),(33,36)]
    for sx,sy in star:
        if template[sy][sx] == 6: colors[sy][sx] = badge_fg
    return colors


# ---------- 图片转 128x128 像素数组（自动适应尺寸） ----------
def image_to_colors(image_path):
    img = Image.open(image_path).convert('RGB')
    orig_w, orig_h = img.size

    # 创建 128x128 白色背景
    background = Image.new('RGB', (128, 128), (255, 255, 255))

    # 等比缩放，刚好放进 128x128
    scale = min(128 / orig_w, 128 / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    # 用邻近插值保持像素感
    img_resized = img.resize((new_w, new_h), Image.NEAREST)

    # 居中粘贴
    offset_x = (128 - new_w) // 2
    offset_y = (128 - new_h) // 2
    background.paste(img_resized, (offset_x, offset_y))

    pixels = background.load()
    colors = [[''] * 128 for _ in range(128)]
    for y in range(128):
        for x in range(128):
            r, g, b = pixels[x, y]
            colors[y][x] = f'#{r:02x}{g:02x}{b:02x}'
    return colors


# ---------- 将 64x64 颜色数组放大到 128x128（每个像素变成 2x2） ----------
def upscale_to_128(colors_64):
    """输入 64x64 的十六进制颜色列表，返回 128x128"""
    big = [[''] * 128 for _ in range(128)]
    for y in range(64):
        for x in range(64):
            col = colors_64[y][x]
            # 填充到 2x2 块
            big[y*2][x*2] = col
            big[y*2][x*2+1] = col
            big[y*2+1][x*2] = col
            big[y*2+1][x*2+1] = col
    return big


# ---------- 主窗口 ----------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("像素练习生 - 128x128")
        self.pixel_size = 128          # 网格尺寸
        self.scale = 3                 # 每个格子的显示像素（3 倍，窗口为 384x384）
        canvas_size = self.pixel_size * self.scale

        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg='white')
        self.canvas.pack(pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.btn_random = tk.Button(btn_frame, text="随机生成练习生", command=self.randomize)
        self.btn_random.pack(side=tk.LEFT, padx=5)

        self.btn_load = tk.Button(btn_frame, text="选择图片生成像素", command=self.load_image)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        # 创建 128x128 个矩形
        self.rect_ids = [[None]*self.pixel_size for _ in range(self.pixel_size)]
        for y in range(self.pixel_size):
            for x in range(self.pixel_size):
                x1 = x * self.scale
                y1 = y * self.scale
                x2 = x1 + self.scale
                y2 = y1 + self.scale
                rid = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                   fill='white', outline='')
                self.rect_ids[y][x] = rid

        self.template = create_template()    # 64x64 模板
        self.randomize()

    def randomize(self):
        # 生成 64x64 随机练习生，然后放大到 128x128 显示
        colors_64 = render_image_64(self.template)
        colors_128 = upscale_to_128(colors_64)
        self.apply_colors(colors_128)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="选择一张图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if not file_path:
            return
        try:
            colors_128 = image_to_colors(file_path)   # 直接生成 128x128
            self.apply_colors(colors_128)
        except Exception as e:
            messagebox.showerror("错误", f"无法处理图片：{e}")

    def apply_colors(self, colors):
        """将 128x128 颜色数组绘制到画布上"""
        for y in range(self.pixel_size):
            for x in range(self.pixel_size):
                self.canvas.itemconfig(self.rect_ids[y][x], fill=colors[y][x])


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
