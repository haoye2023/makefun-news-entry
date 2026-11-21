#!/usr/bin/env python3
"""Generate /output/entry.png: the world news of Friday 20 November 2026 in one image.

Pure standard library (zlib + struct). No network, no randomness, no clock:
two runs in the same environment produce byte-identical output.
"""
import os
import struct
import zlib

W = H = 1024

# ---------- 5x7 bitmap font ('#' = on) ----------
FONT = {
"A": [".###.","#...#","#...#","#####","#...#","#...#","#...#"],
"B": ["####.","#...#","#...#","####.","#...#","#...#","####."],
"C": [".####","#....","#....","#....","#....","#....",".####"],
"D": ["###..","#..#.","#...#","#...#","#...#","#..#.","###.."],
"E": ["#####","#....","#....","####.","#....","#....","#####"],
"F": ["#####","#....","#....","####.","#....","#....","#...."],
"G": [".####","#....","#....","#.###","#...#","#...#",".###."],
"H": ["#...#","#...#","#...#","#####","#...#","#...#","#...#"],
"I": ["#####","..#..","..#..","..#..","..#..","..#..","#####"],
"J": ["..###","...#.","...#.","...#.","...#.","#..#.",".#.#."],
"K": ["#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"],
"L": ["#....","#....","#....","#....","#....","#....","#####"],
"M": ["#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"],
"N": ["#...#","#...#","##..#","#.#.#","#..##","#...#","#...#"],
"O": [".###.","#...#","#...#","#...#","#...#","#...#",".###."],
"P": ["####.","#...#","#...#","####.","#....","#....","#...."],
"Q": [".###.","#...#","#...#","#...#","#.#.#","#..#.",".##.#"],
"R": ["####.","#...#","#...#","####.","#.#..","#..#.","#...#"],
"S": [".####","#....","#....",".###.","....#","....#","####."],
"T": ["#####","..#..","..#..","..#..","..#..","..#..","..#.."],
"U": ["#...#","#...#","#...#","#...#","#...#","#...#",".###."],
"V": ["#...#","#...#","#...#","#...#","#...#",".#.#.","..#.."],
"W": ["#...#","#...#","#...#","#.#.#","#.#.#","##.##","#...#"],
"X": ["#...#",".#.#.","..#..","..#..","..#..",".#.#.","#...#"],
"Y": ["#...#","#...#",".#.#.","..#..","..#..","..#..","..#.."],
"Z": ["#####","....#","...#.","..#..",".#...","#....","#####"],
"0": [".###.","#..##","#.#.#","##..#","#...#","#...#",".###."],
"1": ["..#..",".##..","..#..","..#..","..#..","..#..",".###."],
"2": [".###.","#...#","....#","..##.",".#...","#....","#####"],
"3": ["####.","....#","....#",".###.","....#","....#","####."],
"4": ["...#.","..##.",".#.#.","#..#.","#####","...#.","...#."],
"5": ["#####","#....","####.","....#","....#","#...#",".###."],
"6": [".###.","#....","#....","####.","#...#","#...#",".###."],
"7": ["#####","....#","...#.","..#..","..#..","..#..","..#.."],
"8": [".###.","#...#","#...#",".###.","#...#","#...#",".###."],
"9": [".###.","#...#","#...#",".####","....#","....#",".###."],
" ": [".....",".....",".....",".....",".....",".....","....."],
".": [".....",".....",".....",".....",".....",".##..",".##.."],
",": [".....",".....",".....",".....",".##..",".##..",".#..."],
"'": ["..#..","..#..",".#...",".....",".....",".....","....."],
"-": [".....",".....",".....","#####",".....",".....","....."],
":": [".....",".##..",".##..",".....",".##..",".##..","....."],
"$": ["..#..",".####","#.#..",".###.","..#.#","####.","..#.."],
"/": ["....#","....#","...#.","..#..",".#...","#....","#...."],
"(": ["...##","..#..",".#...",".#...",".#...","..#..","...##"],
")": ["##...","..#..","...#.","...#.","...#.","..#..","##..."],
"+": [".....","..#..","..#..","#####","..#..","..#..","....."],
"!": ["..#..","..#..","..#..","..#..","..#..",".....","..#.."],
"?": [".###.","#...#","....#","..##.","..#..",".....","..#.."],
}

# ---------- framebuffer ----------
FB = bytearray(W * H * 3)

def px(x, y, rgb):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        FB[i] = rgb[0]; FB[i + 1] = rgb[1]; FB[i + 2] = rgb[2]

def rect(x, y, w, h, rgb):
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        for xx in range(w):
            i = base + xx * 3
            FB[i] = rgb[0]; FB[i + 1] = rgb[1]; FB[i + 2] = rgb[2]

def outline(x, y, w, h, rgb, t=2):
    rect(x, y, w, t, rgb); rect(x, y + h - t, w, t, rgb)
    rect(x, y, t, h, rgb); rect(x + w - t, y, t, h, rgb)

def circle(cx, cy, r, rgb, fill=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if fill and d2 <= r * r:
                px(xx, yy, rgb)
            elif not fill and r * r - 2 * r <= d2 <= r * r:
                px(xx, yy, rgb)

def line(x0, y0, x1, y1, rgb, t=3):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        rect(x - t // 2, y - t // 2, t, t, rgb)

def tri(cx, cy, r, rgb):
    for row in range(r):
        wdt = (row * 2) + 1
        rect(cx - row, cy - r // 2 + row, wdt, 1, rgb)

def text_w(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(x, y, s, scale, rgb):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for ry, row in enumerate(g):
            for rx, c in enumerate(row):
                if c == "#":
                    rect(cx + rx * scale, y + ry * scale, scale, scale, rgb)
        cx += 6 * scale
    return cx

def wrap(s, scale, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if text_w(t, scale) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines

def draw_wrapped(x, y, s, scale, rgb, maxw, lh):
    for ln in wrap(s, scale, maxw):
        draw_text(x, y, ln, scale, rgb)
        y += lh
    return y

# ---------- PNG writer (filter 0 rows) ----------
def write_png(path):
    raw = bytearray()
    row = W * 3
    for y in range(H):
        raw.append(0)
        raw += FB[y * row:(y + 1) * row]
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------- palette ----------
BG     = (10, 17, 40)
PANEL  = (17, 28, 58)
BORDER = (42, 59, 110)
INK    = (242, 240, 230)
MUTED  = (159, 178, 216)
GOLD   = (232, 179, 75)
RED    = (228, 87, 46)
TEAL   = (62, 193, 184)
SKY    = (96, 165, 250)
GREEN  = (74, 190, 110)
VIOLET = (167, 139, 250)

# ---------- icons (drawn in a 72x72 box at x,y) ----------
def icon_table(x, y, c):
    for dx in (-20, 0, 20):
        circle(x + 36 + dx, y + 22, 10, c, fill=False)
    line(x + 6, y + 52, x + 66, y + 52, c, 4)

def icon_missile(x, y, c):
    line(x + 14, y + 58, x + 52, y + 20, c, 5)
    tri(x + 58, y + 14, 10, c)
    for dx, dy in ((6, 62), (16, 66), (26, 60)):
        circle(x + dx, y + dy, 3, c)

def icon_scales(x, y, c):
    line(x + 36, y + 8, x + 36, y + 58, c, 4)
    line(x + 12, y + 16, x + 60, y + 16, c, 4)
    line(x + 12, y + 16, x + 5, y + 36, c, 3); line(x + 12, y + 16, x + 19, y + 36, c, 3)
    line(x + 5, y + 36, x + 19, y + 36, c, 3)
    line(x + 60, y + 16, x + 53, y + 36, c, 3); line(x + 60, y + 16, x + 67, y + 36, c, 3)
    line(x + 53, y + 36, x + 67, y + 36, c, 3)
    rect(x + 24, y + 62, 24, 4, c)

def icon_waves(x, y, c):
    for r in range(3):
        yy = y + 18 + r * 18
        for xx in range(0, 72, 12):
            circle(x + xx + (6 if r % 2 else 0), yy, 4, c, fill=False)
    circle(x + 56, y + 10, 6, GOLD)

def icon_cloud(x, y, c):
    circle(x + 26, y + 34, 13, c, fill=False)
    circle(x + 44, y + 28, 16, c, fill=False)
    rect(x + 14, y + 40, 46, 4, c)
    line(x + 24, y + 54, x + 18, y + 66, RED, 4)
    line(x + 40, y + 54, x + 34, y + 66, RED, 4)
    line(x + 54, y + 54, x + 48, y + 66, RED, 4)

def icon_dish(x, y, c):
    for yy in range(28):
        wdt = 44 - yy
        rect(x + 8 + yy // 2, y + 8 + yy, wdt, 2, c)
    line(x + 30, y + 34, x + 52, y + 12, c, 3)
    circle(x + 54, y + 10, 4, c)
    line(x + 30, y + 36, x + 22, y + 62, c, 4)
    line(x + 30, y + 36, x + 40, y + 62, c, 4)
    for r in (10, 18):
        for a in range(0, 180, 12):
            import math
            xx = int(54 + r * math.cos(math.radians(a + 200)))
            yy = int(10 + r * math.sin(math.radians(a + 200)))
            px(x + xx, y + yy, c)

# ---------- page ----------
STORIES = [
    ("THREE LEADERS, ONE TABLE",
     "XI, TRUMP AND PUTIN MEET IN SHENZHEN AND ISSUE A JOINT PEACE DECLARATION",
     GOLD, icon_table),
    ("KYIV UNDER FIRE",
     "RUSSIAN MISSILES STRIKE BRIDGES, EMBASSIES AND A CATHEDRAL IN THE CAPITAL",
     RED, icon_missile),
    ("JUSTICE IN THE HAGUE",
     "THE WORLD COURT FINDS MYANMAR COMMITTED GENOCIDE AGAINST THE ROHINGYA",
     SKY, icon_scales),
    ("STANDOFF AT HORMUZ",
     "US NAVAL BLOCKADE HOLDS WHILE IRAN THREATENS GULF OIL AND TANKERS",
     TEAL, icon_waves),
    ("CLIMATE DEADLOCK",
     "COP31 TALKS IN ANTALYA STALL AS FOSSIL FUELS ARE CUT FROM THE DRAFT DEAL",
     GREEN, icon_cloud),
    ("A CALL FROM DEEP SPACE",
     "VOYAGER 1 PHONES HOME FROM ONE LIGHT-DAY AWAY, THE FARTHEST VOICE EVER",
     VIOLET, icon_dish),
]

def build():
    rect(0, 0, W, H, BG)
    # deterministic starfield (fixed-seed LCG)
    s = 123456789
    for _ in range(260):
        s = (1103515245 * s + 12345) % (2 ** 31)
        x = s % W
        s = (1103515245 * s + 12345) % (2 ** 31)
        y = s % 210
        px(x, y, (70, 90, 150))
    # header
    draw_text(48, 36, "WORLD NEWS - ONE IMAGE", 2, GOLD)
    t = "THE WORLD IN A DAY"
    draw_text((W - text_w(t, 7)) // 2, 66, t, 7, INK)
    d = "FRIDAY 20 NOVEMBER 2026"
    draw_text((W - text_w(d, 3)) // 2, 152, d, 3, TEAL)
    rect(48, 196, W - 96, 3, GOLD)
    # tiles: 2 cols x 3 rows
    tw, th, gap, x0, y0 = 452, 218, 24, 48, 222
    for i, (head, sub, color, icon) in enumerate(STORIES):
        tx = x0 + (i % 2) * (tw + gap)
        ty = y0 + (i // 2) * (th + gap)
        rect(tx, ty, tw, th, PANEL)
        outline(tx, ty, tw, th, BORDER, 2)
        rect(tx, ty, 6, th, color)
        icon(tx + 22, ty + 24, color)
        draw_wrapped(tx + 112, ty + 26, head, 3, INK, tw - 132, 26)
        draw_wrapped(tx + 112, ty + 92, sub, 2, MUTED, tw - 132, 19)
    # footer
    rect(48, 928, W - 96, 3, GOLD)
    f1 = "ALSO TODAY: VAN GOGH SELLS FOR A RECORD $190M - GTA 6 TOPS $2.3B IN SALES -"
    f2 = "EU AND UK LEADERS MEET IN BRUSSELS - DENMARK APPROVES GREENLAND SECURITY DEAL"
    draw_text((W - text_w(f1, 2)) // 2, 946, f1, 2, MUTED)
    draw_text((W - text_w(f2, 2)) // 2, 976, f2, 2, MUTED)

def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    n = write_png(path)
    print(f"wrote {path} ({n} bytes)")

if __name__ == "__main__":
    main()
