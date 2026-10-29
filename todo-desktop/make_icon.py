"""生成应用图标 icon.ico（圆角渐变底 + 白色对勾）。"""

from PIL import Image, ImageDraw, ImageOps

SIZE = 256
S = SIZE * 4  # 超采样，缩小时边缘更平滑

# 圆角矩形遮罩
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.23), fill=255)

# 从上到下的渐变：#7c6cf5 -> #4f46e5
gradient = ImageOps.colorize(
    Image.linear_gradient("L").resize((S, S)),
    black=(124, 108, 245),
    white=(79, 70, 229),
).convert("RGB")

icon = Image.new("RGBA", (S, S), (0, 0, 0, 0))
icon.paste(gradient, (0, 0), mask)

# 白色对勾
draw = ImageDraw.Draw(icon)
width = int(S * 0.095)
points = [(S * 0.27, S * 0.53), (S * 0.44, S * 0.69), (S * 0.75, S * 0.35)]
draw.line(points, fill="white", width=width, joint="curve")
for x, y in (points[0], points[-1]):
    r = width / 2
    draw.ellipse((x - r, y - r, x + r, y + r), fill="white")

icon = icon.resize((SIZE, SIZE), Image.LANCZOS)
icon.save(
    "icon.ico",
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("icon.ico 已生成")
