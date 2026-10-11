# -*- coding: utf-8 -*-
"""生成应用图标 app.ico（用于 exe 打包与页面展示）。"""
import os
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
SIZE = 256


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def make_icon():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 圆角矩形底 + 竖向渐变
    c_top, c_bottom = (37, 99, 235), (14, 165, 233)
    for y in range(SIZE):
        d.line([(0, y), (SIZE, y)], fill=lerp(c_top, c_bottom, y / SIZE) + (255,))
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=54, fill=255)
    img.putalpha(mask)

    # 图表折线（白色）
    pts = [(42, 178), (86, 140), (128, 158), (172, 96), (214, 118)]
    d.line(pts, fill=(255, 255, 255, 235), width=15, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9], fill=(255, 255, 255, 255))

    # 底部柱状（半透明白）
    for i, h in enumerate([34, 52, 44, 62]):
        x = 58 + i * 38
        d.rounded_rectangle([x, 214 - h, x + 22, 214], radius=7,
                            fill=(255, 255, 255, 150))

    os.makedirs(BASE, exist_ok=True)
    ico = os.path.join(BASE, "app.ico")
    img.save(ico, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    img.save(os.path.join(BASE, "static", "favicon.png"))
    print("saved:", ico)


if __name__ == "__main__":
    make_icon()
