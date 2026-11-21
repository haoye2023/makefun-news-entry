#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The World in a Day - Friday 20 November 2026.

Generates a 1024x1024 newspaper-front-page style PNG summarising the
world news of Friday 20 November 2026. Pure Python standard library.
Deterministic: two runs produce byte-identical output.
"""
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 228)
INK = (25, 25, 36)
DARK = (52, 52, 64)
RED = (179, 53, 43)
BLUE = (29, 78, 137)
GRAY = (107, 107, 107)
LGRAY = (178, 172, 152)
TINT = (238, 231, 205)
NIGHT = (34, 44, 66)
NIGHT2 = (18, 24, 40)
GOLD = (216, 164, 65)

BUF = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill_rect(x, y, t, h, c)


def draw_line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for ox in range(t):
            for oy in range(t):
                px(x0 + ox, y0 + oy, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += BUF[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- fonts
# 5x7 dot-matrix font. Each glyph: 7 strings of 5 chars.
FONT5 = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".###.", "#....", "#....", "#....", ".###."),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": (".....", "...#.", ".....", "..##.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".##..", ".##..", ".....", ".....", ".....", ".##..", ".##.."),
    ";": (".##..", ".##..", ".....", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##...", "##..#", "...#.", "..#..", ".#...", "#..##", "...##"),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
}

# 3x5 micro font (uppercase, digits, basic punctuation).
FONT3 = {
    "A": (".#.", "#.#", "###", "#.#", "#.#"),
    "B": ("##.", "#.#", "##.", "#.#", "##."),
    "C": (".##", "#..", "#..", "#..", ".##"),
    "D": ("##.", "#.#", "#.#", "#.#", "##."),
    "E": ("###", "#..", "##.", "#..", "###"),
    "F": ("###", "#..", "##.", "#..", "#.."),
    "G": (".##", "#..", "#.#", "#.#", ".##"),
    "H": ("#.#", "#.#", "###", "#.#", "#.#"),
    "I": ("###", ".#.", ".#.", ".#.", "###"),
    "J": ("..#", "..#", "..#", "#.#", ".#."),
    "K": ("#.#", "#.#", "##.", "#.#", "#.#"),
    "L": ("#..", "#..", "#..", "#..", "###"),
    "M": ("#.#", "###", "#.#", "#.#", "#.#"),
    "N": ("#.#", "###", "###", "#.#", "#.#"),
    "O": (".#.", "#.#", "#.#", "#.#", ".#."),
    "P": ("##.", "#.#", "##.", "#..", "#.."),
    "Q": (".#.", "#.#", "#.#", "##.", ".##"),
    "R": ("##.", "#.#", "##.", "#.#", "#.#"),
    "S": (".##", "#..", ".#.", "..#", "##."),
    "T": ("###", ".#.", ".#.", ".#.", ".#."),
    "U": ("#.#", "#.#", "#.#", "#.#", "###"),
    "V": ("#.#", "#.#", "#.#", "#.#", ".#."),
    "W": ("#.#", "#.#", "###", "###", "#.#"),
    "X": ("#.#", "#.#", ".#.", "#.#", "#.#"),
    "Y": ("#.#", "#.#", ".#.", ".#.", ".#."),
    "Z": ("###", "..#", ".#.", "#..", "###"),
    "0": ("###", "#.#", "#.#", "#.#", "###"),
    "1": (".#.", "##.", ".#.", ".#.", "###"),
    "2": ("##.", "..#", ".#.", "#..", "###"),
    "3": ("##.", "..#", ".#.", "..#", "##."),
    "4": ("#.#", "#.#", "###", "..#", "..#"),
    "5": ("###", "#..", "##.", "..#", "##."),
    "6": (".##", "#..", "##.", "#.#", ".#."),
    "7": ("###", "..#", ".#.", ".#.", ".#."),
    "8": (".#.", "#.#", ".#.", "#.#", ".#."),
    "9": (".#.", "#.#", ".##", "..#", "##."),
    " ": ("...", "...", "...", "...", "..."),
    ".": ("...", "...", "...", "...", ".#."),
    ",": ("...", "...", "...", ".#.", "#.."),
    ":": ("...", ".#.", "...", ".#.", "..."),
    "-": ("...", "...", "###", "...", "..."),
    "$": (".#.", "###", "##.", "###", ".#."),
    "%": ("#.#", "..#", ".#.", "#..", "#.#"),
    "&": (".#.", "#.#", ".#.", "#.#", ".##"),
    "+": ("...", ".#.", "###", ".#.", "..."),
    "/": ("..#", "..#", ".#.", "#..", "#.."),
    "(": ("..#", ".#.", ".#.", ".#.", "..#"),
    ")": ("#..", ".#.", ".#.", ".#.", "#.."),
    "'": (".#.", ".#.", "...", "...", "..."),
    "!": (".#.", ".#.", ".#.", "...", ".#."),
    "?": ("##.", "..#", ".#.", "...", ".#."),
}

NORMALIZE = {
    "\u2014": "-", "\u2013": "-", "\u2019": "'", "\u2018": "'",
    "\u201c": '"', "\u201d": '"', "\u00b7": "\x01",
}
MID = "\x01"  # middot placeholder, drawn as a small dot


def norm(s):
    for k, v in NORMALIZE.items():
        s = s.replace(k, v)
    return s

# ------------------------------------------------------------ text draw
def glyph_size(font):
    if font is FONT5:
        return 5, 7
    return 3, 5


def draw_char(x, y, ch, scale, color, font, bold):
    gw, gh = glyph_size(font)
    if ch == MID:
        r = max(1, scale)
        fill_rect(x + gw * scale // 2 - r // 2, y + gh * scale // 2 - r // 2,
                  r, r, color)
        return
    g = font.get(ch)
    if g is None:
        g = font.get("?")
    offs = (0, max(1, scale // 2)) if bold else (0,)
    for off in offs:
        for row in range(gh):
            line = g[row]
            for col in range(gw):
                if line[col] == "#":
                    fill_rect(x + off + col * scale, y + row * scale,
                              scale, scale, color)


def text_w(s, scale, font):
    gw, _ = glyph_size(font)
    return len(s) * (gw + 1) * scale - (scale if s else 0)


def draw_text(x, y, s, scale, color, font=FONT5, bold=False):
    s = norm(s)
    gw, _ = glyph_size(font)
    adv = (gw + 1) * scale
    cx = x
    for ch in s:
        draw_char(cx, y, ch, scale, color, font, bold)
        cx += adv
    return cx


def draw_centered(y, s, scale, color, font=FONT5, bold=False, cx=W // 2):
    w = text_w(norm(s), scale, font)
    draw_text(cx - w // 2, y, s, scale, color, font, bold)


def wrap(s, maxw, scale, font=FONT5):
    """Greedy word wrap; returns list of lines fitting maxw pixels."""
    s = norm(s)
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, maxw, scale, color, font=FONT5, bold=False,
                 line_h=None, max_lines=None):
    _, gh = glyph_size(font)
    if line_h is None:
        line_h = gh * scale + 2 * scale
    lines = wrap(s, maxw, scale, font)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * line_h, ln, scale, color, font, bold)
    return len(lines)

# ---------------------------------------------------------- illustrations
def ill_kyiv(x, y, w, h):
    """Night skyline, missile trails, one explosion star."""
    fill_rect(x, y, w, h, NIGHT)
    fill_circle(x + w - 42, y + 22, 10, PAPER)
    fill_circle(x + w - 36, y + 19, 9, NIGHT)
    for sx, sy in ((30, 18), (86, 10), (150, 24), (210, 12), (262, 20)):
        px(x + sx, y + sy, PAPER)
        px(x + sx + 1, y + sy, PAPER)
    base = y + h
    for bx, bw, bh in ((6, 44, 34), (58, 34, 48), (100, 52, 28),
                       (160, 38, 54), (206, 48, 32), (262, 40, 44)):
        fill_rect(x + bx, base - bh, bw, bh, NIGHT2)
        for wy in range(base - bh + 6, base - 6, 9):
            for wx in range(x + bx + 5, x + bx + bw - 5, 10):
                px(wx, wy, GOLD)
                px(wx + 1, wy, GOLD)
    # bridge silhouette right side
    hline(x + 196, base - 20, 112, NIGHT2, 4)
    draw_line(x + 210, base - 20, x + 236, base - 44, NIGHT2, 3)
    draw_line(x + 236, base - 44, x + 262, base - 20, NIGHT2, 3)
    # missile trails
    draw_line(x + 18, y + 8, x + 118, y + 52, RED, 2)
    draw_line(x + 52, y + 4, x + 138, y + 44, RED, 2)
    fill_circle(x + 122, y + 54, 3, RED)
    # explosion star over a rooftop
    ex, ey = x + 226, base - 62
    for dx, dy in ((0, -11), (0, 11), (-11, 0), (11, 0), (-8, -8),
                   (8, -8), (-8, 8), (8, 8)):
        draw_line(ex, ey, ex + dx, ey + dy, GOLD, 2)
    fill_circle(ex, ey, 3, RED)


def ill_flags(x, y, w, h):
    """Three flags on poles above a simple skyline."""
    fill_rect(x, y, w, h, TINT)
    base = y + h
    for bx, bw, bh in ((10, 52, 22), (84, 40, 16), (196, 46, 20),
                       (258, 44, 15)):
        fill_rect(x + bx, base - bh, bw, bh, LGRAY)
    hline(x, base - 1, w, INK, 2)
    poles = (52, 157, 262)
    for pxx in poles:
        vline(x + pxx, y + 12, h - 26, INK, 2)
    fw, fh = 62, 36
    # China: red field, gold dots
    fx, fy = x + poles[0] + 2, y + 12
    fill_rect(fx, fy, fw, fh, RED)
    for dx, dy in ((7, 6), (16, 3), (18, 10), (16, 17), (12, 12)):
        fill_rect(fx + dx, fy + dy, 3, 3, GOLD)
    # USA: stripes + blue canton
    fx, fy = x + poles[1] + 2, y + 12
    fill_rect(fx, fy, fw, fh, PAPER)
    for i in range(0, fh, 8):
        fill_rect(fx, fy + i, fw, 4, RED)
    fill_rect(fx, fy, 28, 18, BLUE)
    for ry in range(3, 16, 5):
        for rx in range(3, 25, 6):
            px(fx + rx, fy + ry, PAPER)
    # Russia: white / blue / red bands
    fx, fy = x + poles[2] + 2, y + 12
    fill_rect(fx, fy, fw, fh // 3, PAPER)
    fill_rect(fx, fy + fh // 3, fw, fh // 3, BLUE)
    fill_rect(fx, fy + 2 * fh // 3, fw, fh - 2 * fh // 3, RED)
    for fx0 in (x + poles[0] + 2, x + poles[1] + 2, x + poles[2] + 2):
        draw_line(fx0, y + 12, fx0 + fw, y + 12, INK, 1)
        draw_line(fx0, y + 12 + fh, fx0 + fw, y + 12 + fh, INK, 1)


def ill_scales(x, y, w, h):
    """Courthouse columns and the scales of justice."""
    fill_rect(x, y, w, h, TINT)
    base = y + h
    cx = x + w // 2
    # pediment + columns
    draw_line(x + 40, y + 30, cx, y + 8, INK, 2)
    draw_line(cx, y + 8, x + w - 40, y + 30, INK, 2)
    hline(x + 36, y + 32, w - 72, INK, 2)
    for cxx in (52, 96, 216, 260):
        vline(x + cxx, y + 36, h - 52, LGRAY, 5)
    hline(x + 30, base - 14, w - 60, INK, 2)
    # scales
    top = y + 40
    vline(cx, top, 52, INK, 3)
    hline(cx - 58, top, 116, INK, 3)
    fill_circle(cx, top - 4, 4, INK)
    for side in (-58, 58):
        px0 = cx + side
        draw_line(px0, top + 3, px0 - 16, top + 34, INK, 1)
        draw_line(px0, top + 3, px0 + 16, top + 34, INK, 1)
        draw_line(px0 - 19, top + 36, px0 + 19, top + 36, INK, 2)
        draw_line(px0 - 19, top + 36, px0 - 10, top + 43, INK, 2)
        draw_line(px0 + 19, top + 36, px0 + 10, top + 43, INK, 2)
        hline(px0 - 10, top + 43, 20, INK, 2)
    hline(cx - 20, top + 52, 40, INK, 3)
    hline(cx - 28, top + 57, 56, INK, 3)

# --------------------------------------------------------------- content
NUMBERS = [
    ("8+", "KILLED IN KYIV STRIKES"),
    ("62\u201333", "US SENATE VOTE"),
    ("$41.7BN", "BORDER CONTRACTS"),
    ("-4.5%", "NIKKEI & KOSPI"),
    ("16,000", "BANK CUSTOMERS LEAKED"),
    ("$2.3BN", "GTA 6 SALES"),
]

LEADS = [
    ("KYIV, UKRAINE \u2014 WAR",
     "Russia launches major attack on Kyiv",
     "Overnight missile and drone strikes hit bridges and power "
     "infrastructure in the capital; Ukraine reportedly struck a "
     "chemical plant and Poland reported airspace incursions.",
     "(AP \u00b7 Open Chronicle)", ill_kyiv),
    ("SHENZHEN, CHINA \u2014 DIPLOMACY",
     "Trump, Xi and Putin issue joint peace declaration",
     "The first trilateral summit ends with a joint peace declaration, "
     "though the text makes no mention of Ukraine or Iran.",
     "(Open Chronicle \u00b7 Saudi Gazette)", ill_flags),
    ("THE HAGUE \u2014 JUSTICE",
     "World Court: Myanmar responsible for genocide",
     "The ICJ finds Myanmar responsible for genocide against the "
     "Rohingya; refugees in Bangladesh welcome the verdict.",
     "(UN \u00b7 Open Chronicle)", ill_scales),
]

GRID = [
    ("BRUSSELS",
     "UK and EU sign three deals: food exports, linked carbon markets, "
     "a youth scheme.", "(One Turn)"),
    ("BERLIN",
     "Merz rejects a new Yalta: big powers cannot settle Europe's "
     "future without Europeans.", "(Open Chronicle)"),
    ("ANTALYA",
     "COP31 ends with no fossil-fuel deal; final texts drop the "
     "transition, Pacific states protest.", "(350.org \u00b7 CAN)"),
    ("TOKYO",
     "AI sell-off sinks Asia markets: Nikkei and Kospi -4.5% despite "
     "Anthropic's IPO debut.", "(AP)"),
    ("WASHINGTON",
     "Senate passes energy-permitting bill over environmental "
     "objections.", "(All Voices News)"),
    ("WASHINGTON",
     "$41.7bn in ICE and CBP border and deportation contracts "
     "revealed.", "(All Voices News)"),
    ("PORT-AU-PRINCE",
     "34 suspected gang members killed, Haiti national police report.",
     "(Open Chronicle)"),
    ("HORMUZ",
     "US blockade standoff holds; India a top driver of energy growth "
     "amid the crisis.", "(IANS \u00b7 IEA)"),
    ("HANOI",
     "Vietnam abolishes the death penalty for drug trafficking in new "
     "penal code.", "(Kilambi News)"),
    ("NEW YORK",
     "Hackers leak data of 16,000 Visa, Mastercard and JPMorgan "
     "customers.", "(Saudi Gazette)"),
    ("TALLINN",
     "Estonia to close its Russia border crossings from 1 December "
     "after sabotage.", "(One Turn)"),
    ("DEEP SPACE",
     "Voyager 1, now one full light-day from Earth, sends back a "
     "signal.", "(Agencies)"),
]

ALSO = [
    "Denmark approves Greenland-US security deal",
    "Russia invites Europeans to Moscow talks",
    "Mongolia's president resigns",
    "Japan PM gets cool welcome in China",
    "GTA 6 sales top $2.3bn",
    "Van Gogh sells for record $190.4m",
    "California subpoenas Nvidia",
    "Modi opens SCO dialogue forum in Delhi",
    "Saudi Arabia signs workers' rights framework",
    "Houthis urge Saudi port evacuation",
    "Trump threatens tax on AI data centres abroad",
    "Japan inflation 2.2% fuels hike bets",
    "APEC ministers issue joint statement",
    "Mosque set on fire in Israel",
    "Trump sacks cyber director after outages",
]

MX = 26          # left margin
CW = 972         # content width


def layout():
    fill_rect(0, 0, W, H, PAPER)
    # ---- masthead
    hline(MX, 30, CW, INK, 3)
    hline(MX, 35, CW, INK, 1)
    draw_centered(46, "30 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE "
                      "DATED FRIDAY 20 NOVEMBER 2026", 2, INK)
    draw_centered(70, "THE WORLD IN A DAY", 7, INK, bold=True)
    draw_centered(128, "FRIDAY 20 NOVEMBER 2026 \u2014 One day of world "
                       "news on a single page", 2, DARK)
    hline(MX, 152, CW, INK, 2)
    hline(MX, 156, CW, INK, 1)
    # ---- number strip
    cell_w, gap = 155, 8
    for i, (val, lab) in enumerate(NUMBERS):
        cx0 = MX + i * (cell_w + gap)
        if i:
            vline(cx0 - gap // 2, 168, 48, LGRAY, 1)
        vw = text_w(norm(val), 3, FONT5)
        draw_text(cx0 + (cell_w - vw) // 2, 172, val, 3, INK, bold=True)
        lines = wrap(lab, cell_w - 6, 1)
        for j, ln in enumerate(lines[:2]):
            lw = text_w(ln, 1, FONT5)
            draw_text(cx0 + (cell_w - lw) // 2, 200 + j * 9, ln, 1, DARK)
    hline(MX, 226, CW, INK, 2)
    # ---- lead stories
    col_w = 314
    xs = (MX, MX + 329, MX + 658)
    for (loc, head, body, src, ill), x0 in zip(LEADS, xs):
        ill(x0, 242, col_w, 132)
        hline(x0, 242, col_w, INK, 1)
        hline(x0, 373, col_w, INK, 1)
        vline(x0, 242, 132, INK, 1)
        vline(x0 + col_w - 1, 242, 132, INK, 1)
        draw_text(x0, 384, loc, 1, RED, bold=True)
        draw_wrapped(x0, 398, head, col_w, 2, INK, bold=True,
                     line_h=18, max_lines=2)
        draw_wrapped(x0, 440, body, col_w, 1, DARK,
                     line_h=11, max_lines=5)
        draw_text(x0, 502, src, 1, GRAY)
    hline(MX, 516, CW, INK, 1)
    # ---- grid of twelve shorts
    gcol_w, gxs = 234, (MX, MX + 246, MX + 492, MX + 738)
    gy0, pitch = 530, 64
    for idx, (loc, text, src) in enumerate(GRID):
        r, c = divmod(idx, 4)
        x0 = gxs[c]
        y0 = gy0 + r * pitch
        draw_text(x0, y0, loc, 1, RED, bold=True)
        draw_wrapped(x0, y0 + 12, text, gcol_w, 1, INK,
                     line_h=11, max_lines=3)
        draw_text(x0, y0 + 50, src, 1, GRAY)
    for r in (1, 2):
        hline(MX, gy0 + r * pitch - 6, CW, LGRAY, 1)
    for c in (1, 2, 3):
        vline(gxs[c] - 6, gy0, pitch * 3 - 12, LGRAY, 1)
    hline(MX, 724, CW, INK, 1)
    # ---- also on friday
    hline(MX, 738, CW, RED, 2)
    draw_text(MX, 746, "ALSO ON FRIDAY 20 NOVEMBER", 2, INK, bold=True)
    cols = ((MX, ALSO[:8]), (MX + 496, ALSO[8:]))
    for x0, items in cols:
        for j, item in enumerate(items):
            s = norm("\u00b7 " + item).upper()
            draw_text(x0, 770 + j * 17, s, 2, DARK, font=FONT3)
    # ---- date check box
    by = 914
    hline(MX, by, CW, RED, 2)
    hline(MX, by + 28, CW, RED, 2)
    vline(MX, by, 30, RED, 2)
    vline(MX + CW - 2, by, 30, RED, 2)
    draw_centered(by + 10,
                  "DATE CHECK \u2014 Every story on this page was first "
                  "reported on Friday 20 November 2026. Thursday's and "
                  "Saturday's news was left out on purpose.",
                  1, RED, bold=True)
    # ---- footer
    draw_centered(958, "Sources named beside each story \u00b7 One page, "
                       "one day \u00b7 Drawn entirely by program "
                       "(Python standard library)", 1, GRAY)
    hline(MX, 976, CW, INK, 3)
    hline(MX, 981, CW, INK, 1)


def main():
    layout()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = write_png(path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
