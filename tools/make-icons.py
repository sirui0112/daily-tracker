#!/usr/bin/env python3
"""生成 PWA 图标，不依赖任何第三方库。

图案呼应应用首页的「药盒格子」：深松绿底色上四个圆角方格，
左上角那个是琥珀色，表示今天已经记过一格。

抗锯齿用圆角矩形的有符号距离场做 1 像素过渡，不做超采样，
所以 512×512 也就一两秒。

    python3 tools/make-icons.py
"""
import math, os, struct, zlib

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BG     = (0x14, 0x65, 0x5C)   # --accent 深松绿
TILE   = (0xEA, 0xF0, 0xEE)   # 偏绿的近白
FILLED = (0xED, 0xA1, 0x00)   # --c-yellow 琥珀，"已记过"的那一格


def rounded_rect_coverage(px, py, cx, cy, hw, hh, r):
    """圆角矩形的覆盖率 0..1，边缘一个像素内线性过渡。"""
    dx = abs(px - cx) - (hw - r)
    dy = abs(py - cy) - (hh - r)
    ox, oy = max(dx, 0.0), max(dy, 0.0)
    d = math.hypot(ox, oy) - r + min(max(dx, dy), 0.0)
    return min(max(0.5 - d, 0.0), 1.0)


def render(size):
    pad = 0.155 * size          # 四周留白，Android 遮罩裁切也不会切到格子
    gap = 0.052 * size
    area = size - 2 * pad
    cell = (area - gap) / 2.0   # 2×2，格子是正方形
    rad = 0.24 * cell

    tiles = []
    for row in range(2):
        for col in range(2):
            cx = pad + col * (cell + gap) + cell / 2.0
            cy = pad + row * (cell + gap) + cell / 2.0
            colour = FILLED if (row == 0 and col == 0) else TILE
            tiles.append((cx, cy, colour))

    hw = hh = cell / 2.0
    rows = []
    for y in range(size):
        py = y + 0.5
        row = bytearray()
        for x in range(size):
            px = x + 0.5
            r, g, b = BG
            for cx, cy, colour in tiles:
                a = rounded_rect_coverage(px, py, cx, cy, hw, hh, rad)
                if a > 0.0:
                    r = int(r + (colour[0] - r) * a)
                    g = int(g + (colour[1] - g) * a)
                    b = int(b + (colour[2] - b) * a)
            row += bytes((r, g, b))
        rows.append(row)
    return rows


def write_png(path, size, rows):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)   # 每行 filter 类型 0

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))  # 8-bit truecolour
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


for s in (180, 192, 512):
    out = os.path.join(HERE, "icon-%d.png" % s)
    n = write_png(out, s, render(s))
    print("icon-%d.png  %d 字节" % (s, n))
