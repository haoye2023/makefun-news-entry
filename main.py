#!/usr/bin/env python3
"""The World in a Day - Friday 20 November 2026.

Generates a 1024x1024 newspaper-front-page PNG summarising one day of
world news. Pure Python standard library, no network, deterministic:
two runs produce a byte-identical entry.png.

SPDX-License-Identifier: MIT
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (0xF7, 0xF2, 0xE4)
INK = (0x19, 0x19, 0x24)
RED = (0xB3, 0x35, 0x2B)
BLUE = (0x1D, 0x4E, 0x89)

MX = 30                 # page margin
CW = W - 2 * MX         # content width = 964

# ---------------------------------------------------------------- fonts
# 5x7 dot-matrix font: each glyph is 7 rows of 5 bits, bit 4 = leftmost.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11),
    "Y": (0x11, 0x0A, 0x04, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x10, 0x1E, 0x01, 0x01, 0x1E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0F, 0x00, 0x00, 0x00),
    "—": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "·": (0x00, 0x00, 0x00, 0x0C, 0x0C, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "+": (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
}

# 3x5 micro font (drawn at scale 2 in the ALSO list): 5 rows of 3 bits.
MICRO = {
    "A": (0x2, 0x5, 0x7, 0x5, 0x5), "B": (0x6, 0x5, 0x6, 0x5, 0x6),
    "C": (0x3, 0x4, 0x4, 0x4, 0x3), "D": (0x6, 0x5, 0x5, 0x5, 0x6),
    "E": (0x7, 0x4, 0x6, 0x4, 0x7), "F": (0x7, 0x4, 0x6, 0x4, 0x4),
    "G": (0x3, 0x4, 0x5, 0x5, 0x3), "H": (0x5, 0x5, 0x7, 0x5, 0x5),
    "I": (0x7, 0x2, 0x2, 0x2, 0x7), "J": (0x1, 0x1, 0x1, 0x5, 0x2),
    "K": (0x5, 0x5, 0x6, 0x5, 0x5), "L": (0x4, 0x4, 0x4, 0x4, 0x7),
    "M": (0x5, 0x7, 0x7, 0x5, 0x5), "N": (0x5, 0x7, 0x5, 0x5, 0x5),
    "O": (0x2, 0x5, 0x5, 0x5, 0x2), "P": (0x6, 0x5, 0x6, 0x4, 0x4),
    "Q": (0x2, 0x5, 0x5, 0x6, 0x3), "R": (0x6, 0x5, 0x6, 0x5, 0x5),
    "S": (0x3, 0x4, 0x2, 0x1, 0x6), "T": (0x7, 0x2, 0x2, 0x2, 0x2),
    "U": (0x5, 0x5, 0x5, 0x5, 0x7), "V": (0x5, 0x5, 0x5, 0x5, 0x2),
    "W": (0x5, 0x5, 0x7, 0x7, 0x5), "X": (0x5, 0x5, 0x2, 0x5, 0x5),
    "Y": (0x5, 0x5, 0x2, 0x2, 0x2), "Z": (0x7, 0x1, 0x2, 0x4, 0x7),
    "0": (0x7, 0x5, 0x5, 0x5, 0x7), "1": (0x2, 0x6, 0x2, 0x2, 0x7),
    "2": (0x6, 0x1, 0x2, 0x4, 0x7), "3": (0x6, 0x1, 0x2, 0x1, 0x6),
    "4": (0x5, 0x5, 0x7, 0x1, 0x1), "5": (0x7, 0x4, 0x6, 0x1, 0x6),
    "6": (0x3, 0x4, 0x6, 0x5, 0x2), "7": (0x7, 0x1, 0x2, 0x2, 0x2),
    "8": (0x2, 0x5, 0x2, 0x5, 0x2), "9": (0x2, 0x5, 0x3, 0x1, 0x6),
    " ": (0x0, 0x0, 0x0, 0x0, 0x0), ".": (0x0, 0x0, 0x0, 0x0, 0x2),
    ",": (0x0, 0x0, 0x0, 0x2, 0x4), "'": (0x2, 0x2, 0x4, 0x0, 0x0),
    "-": (0x0, 0x0, 0x7, 0x0, 0x0), "·": (0x0, 0x0, 0x2, 0x0, 0x0),
    "$": (0x2, 0x7, 0x6, 0x3, 0x7), "%": (0x5, 0x1, 0x2, 0x4, 0x5),
    "(": (0x1, 0x2, 0x2, 0x2, 0x1), ")": (0x4, 0x2, 0x2, 0x2, 0x4),
    "/": (0x1, 0x1, 0x2, 0x4, 0x4), "&": (0x2, 0x5, 0x2, 0x5, 0x3),
    "+": (0x0, 0x2, 0x7, 0x2, 0x0), ":": (0x0, 0x2, 0x0, 0x2, 0x0),
}

# ----------------------------------------------------------------- data
KICKER = "30 STORIES · 6 REGIONS · EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
TITLE = "THE WORLD IN A DAY"
SUBTITLE = "FRIDAY 20 NOVEMBER 2026 — One day of world news on a single page"

# (number, label, colour) - the six-cell figures strip
STRIP = [
    ("8+", "KILLED IN KYIV STRIKES", RED),
    ("62-33", "US SENATE VOTE", INK),
    ("$41.7BN", "BORDER CONTRACTS", INK),
    ("-4.5%", "NIKKEI & KOSPI", RED),
    ("16,000", "BANK CUSTOMERS LEAKED", INK),
    ("$2.3BN", "GTA 6 SALES", INK),
]

# (tag, headline, summary, source, illustration key)
LEADS = [
    ("KYIV, UKRAINE — WAR",
     "Russia launches major attack on Kyiv",
     "Overnight missile and drone strikes hit bridges and power "
     "infrastructure in the capital; Ukraine reportedly struck a "
     "chemical plant and Poland reported airspace incursions.",
     "(AP · Open Chronicle)", "kyiv"),
    ("SHENZHEN, CHINA — DIPLOMACY",
     "Trump, Xi and Putin issue joint peace declaration",
     "The first trilateral summit ends with a joint peace declaration, "
     "though the text makes no mention of Ukraine or Iran.",
     "(Open Chronicle · Saudi Gazette)", "shenzhen"),
    ("THE HAGUE — JUSTICE",
     "World Court: Myanmar responsible for genocide",
     "The ICJ finds Myanmar responsible for genocide against the "
     "Rohingya; refugees in Bangladesh welcome the verdict.",
     "(UN · Open Chronicle)", "hague"),
]

# (location, story with source in brackets) - twelve briefs, row-major
SHORTS = [
    ("BRUSSELS", "UK and EU sign three deals: food exports, linked "
     "carbon markets, a youth scheme. (One Turn)"),
    ("BERLIN", "Merz rejects a new Yalta: big powers cannot settle "
     "Europe's future without Europeans. (Open Chronicle)"),
    ("ANTALYA", "COP31 ends with no fossil-fuel deal; final texts drop "
     "the transition, Pacific states protest. (350.org · CAN)"),
    ("TOKYO", "AI sell-off sinks Asia markets: Nikkei and Kospi -4.5% "
     "despite Anthropic's IPO debut. (AP)"),
    ("WASHINGTON", "Senate passes energy-permitting bill over "
     "environmental objections. (All Voices News)"),
    ("WASHINGTON", "$41.7bn in ICE and CBP border and deportation "
     "contracts revealed. (All Voices News)"),
    ("PORT-AU-PRINCE", "34 suspected gang members killed, Haiti "
     "national police report. (Open Chronicle)"),
    ("HORMUZ", "US blockade standoff holds; India a top driver of "
     "energy growth amid the crisis. (IANS · IEA)"),
    ("HANOI", "Vietnam abolishes the death penalty for drug "
     "trafficking in new penal code. (Kilambi News)"),
    ("NEW YORK", "Hackers leak data of 16,000 Visa, Mastercard and "
     "JPMorgan customers. (Saudi Gazette)"),
    ("TALLINN", "Estonia to close its Russia border crossings from "
     "1 December after sabotage. (One Turn)"),
    ("DEEP SPACE", "Voyager 1, now one full light-day from Earth, "
     "sends back a signal. (Agencies)"),
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

DATE_CHECK = ("DATE CHECK — Every story on this page was first reported "
              "on Friday 20 November 2026. Thursday's and Saturday's "
              "news was left out on purpose.")
FOOTER = ("Sources named beside each story · One page, one day · "
          "Drawn entirely by program (Python standard library)")

# ------------------------------------------------------------- drawing
def new_buf():
    return bytearray(bytes(PAPER) * (W * H))


def rect(buf, x, y, w, h, color):
    """Filled rectangle, clipped to the canvas."""
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        off = (yy * W + x0) * 3
        buf[off:off + len(row)] = row


def outline(buf, x, y, w, h, color, t=2):
    rect(buf, x, y, w, t, color)
    rect(buf, x, y + h - t, w, t, color)
    rect(buf, x, y, t, h, color)
    rect(buf, x + w - t, y, t, h, color)


def line(buf, x0, y0, x1, y1, color, t=1):
    """Bresenham line with square thickness t."""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        rect(buf, x0 - t // 2, y0 - t // 2, t, t, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def circle(buf, cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(r * r - dy * dy))
        rect(buf, cx - dx, cy + dy, 2 * dx + 1, 1, color)


def triangle(buf, ax, ay, bx, by, cx, cy, color):
    """Filled triangle via barycentric test on its bounding box."""
    lo_x, hi_x = max(0, min(ax, bx, cx)), min(W - 1, max(ax, bx, cx))
    lo_y, hi_y = max(0, min(ay, by, cy)), min(H - 1, max(ay, by, cy))
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if den == 0:
        return
    for yy in range(lo_y, hi_y + 1):
        for xx in range(lo_x, hi_x + 1):
            w0 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / den
            w1 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / den
            if w0 >= 0 and w1 >= 0 and (1 - w0 - w1) >= 0:
                off = (yy * W + xx) * 3
                buf[off:off + 3] = bytes(color)


# ---------------------------------------------------------------- text
def _glyphs(font):
    return FONT if font == "std" else MICRO


def _metrics(font):
    return (5, 7, 6) if font == "std" else (3, 5, 4)


def text_w(s, scale, font="std", tracking=0):
    gw, _gh, adv = _metrics(font)
    s = s.upper()
    if not s:
        return 0
    return (len(s) - 1) * (adv * scale - tracking) + gw * scale


def draw_text(buf, s, x, y, scale, color, font="std", tracking=0):
    glyphs = _glyphs(font)
    gw, gh, adv = _metrics(font)
    cx = x
    for ch in s.upper():
        g = glyphs.get(ch, glyphs[" "])
        for r in range(gh):
            row = g[r]
            for c in range(gw):
                if (row >> (gw - 1 - c)) & 1:
                    rect(buf, cx + c * scale, y + r * scale, scale, scale,
                         color)
        cx += adv * scale - tracking
    return cx


def draw_centered(buf, s, cx, y, scale, color, font="std", tracking=0):
    w = text_w(s, scale, font, tracking)
    return draw_text(buf, s, cx - w // 2, y, scale, color, font, tracking)


def wrap(s, maxchars):
    """Greedy word wrap to lines of at most maxchars characters."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if len(trial) <= maxchars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(buf, s, x, y, scale, color, maxchars, lh, font="std"):
    for i, ln in enumerate(wrap(s, maxchars)):
        draw_text(buf, ln, x, y + i * lh, scale, color, font)
    return y + len(wrap(s, maxchars)) * lh


# ----------------------------------------------------------------- png
def write_png(buf, path):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
           chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
           chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# --------------------------------------------------------- illustrations
def ill_kyiv(buf, x, y, w, h):
    rect(buf, x, y, w, h, BLUE)
    for dx, dy in ((20, 14), (55, 26), (120, 10), (200, 18), (280, 12),
                   (90, 32), (250, 32), (160, 26), (36, 44), (292, 44)):
        rect(buf, x + dx, y + dy, 2, 2, PAPER)
    circle(buf, x + w - 34, y + 20, 7, PAPER)
    for cx, cy in ((x + 42, y + 22), (x + w - 112, y + 14)):
        for ang in range(0, 360, 45):
            ex = cx + int(10 * math.cos(math.radians(ang)))
            ey = cy + int(10 * math.sin(math.radians(ang)))
            line(buf, cx, cy, ex, ey, RED)
        rect(buf, cx - 1, cy - 1, 3, 3, RED)
    rect(buf, x + 8, y + 70, w - 16, 3, PAPER)                 # deck
    rect(buf, x + 64, y + 34, 5, 39, PAPER)                    # towers
    rect(buf, x + w - 69, y + 34, 5, 39, PAPER)
    line(buf, x + 66, y + 34, x + 10, y + 70, PAPER)           # cables
    line(buf, x + 66, y + 34, x + 155, y + 70, PAPER)
    line(buf, x + w - 67, y + 34, x + 155, y + 70, PAPER)
    line(buf, x + w - 67, y + 34, x + w - 10, y + 70, PAPER)
    rect(buf, x + 20, y + 86, 90, 2, PAPER)                    # river
    rect(buf, x + 150, y + 95, 120, 2, PAPER)
    rect(buf, x + 60, y + 102, 70, 2, PAPER)


def ill_shenzhen(buf, x, y, w, h):
    base = y + h - 8
    circle(buf, x + 26, y + 16, 9, BLUE)
    towers = ((8, 34, 52), (48, 26, 74), (80, 40, 40), (126, 30, 88),
              (162, 24, 58), (192, 36, 68), (234, 28, 46), (268, 34, 78))
    for dx, bw, bh in towers:
        rect(buf, x + dx, base - bh, bw, bh, INK)
    for dx, dy in ((134, 30), (144, 30), (134, 44), (144, 44),
                   (134, 58), (144, 58), (56, 44), (276, 40), (286, 40),
                   (276, 54), (200, 52), (210, 52), (16, 66), (26, 66)):
        rect(buf, x + dx, y + dy, 3, 3, PAPER)
    for dx, bw, bh in (towers[1], towers[3], towers[7]):
        px = x + dx + bw // 2
        rect(buf, px, base - bh - 12, 2, 12, INK)
        rect(buf, px + 2, base - bh - 12, 11, 6, RED)
    rect(buf, x, base, w, 2, INK)


def ill_hague(buf, x, y, w, h):
    cx = x + w // 2
    base = y + h - 10
    triangle(buf, cx - 84, y + 32, cx + 84, y + 32, cx, y + 8, INK)
    circle(buf, cx, y + 25, 4, PAPER)
    rect(buf, cx - 78, y + 34, 156, 7, INK)                    # entablature
    for i in range(5):                                         # columns
        rect(buf, cx - 64 + i * 32, y + 44, 9, base - 12 - (y + 44), INK)
    rect(buf, cx - 8, base - 30, 16, 18, BLUE)                 # door
    rect(buf, cx - 76, base - 12, 152, 4, INK)                 # steps
    rect(buf, cx - 84, base - 6, 168, 4, INK)


ILLUSTRATIONS = {"kyiv": ill_kyiv, "shenzhen": ill_shenzhen,
                 "hague": ill_hague}


# -------------------------------------------------------------- layout
def build():
    buf = new_buf()
    outline(buf, 12, 12, W - 24, H - 24, INK, 2)

    draw_centered(buf, KICKER, W // 2, 30, 2, INK)
    rect(buf, MX, 54, CW, 2, INK)
    draw_centered(buf, TITLE, W // 2, 66, 8, INK)
    draw_centered(buf, SUBTITLE, W // 2, 132, 2, INK)
    rect(buf, MX, 156, CW, 4, INK)
    rect(buf, MX, 163, CW, 1, INK)

    # figures strip: six cells with dividers
    cellw = CW // 6
    for i, (num, label, color) in enumerate(STRIP):
        cx = 32 + i * cellw + cellw // 2
        scale = 4 if len(num) <= 6 else 3
        draw_centered(buf, num, cx, 176 + (28 - 7 * scale) // 2, scale,
                      color)
        draw_centered(buf, label, cx, 212, 1, INK)
        if i:
            line(buf, 32 + i * cellw, 176, 32 + i * cellw, 222, INK)
    rect(buf, MX, 228, CW, 2, INK)

    # three lead stories
    colw, gap = 310, 16
    for i, (tag, head, summ, src, key) in enumerate(LEADS):
        x = MX + i * (colw + gap)
        ILLUSTRATIONS[key](buf, x, 244, colw, 118)
        outline(buf, x, 244, colw, 118, INK, 1)
        draw_text(buf, tag, x, 370, 2, RED, tracking=1)
        draw_wrapped(buf, head, x, 390, 2, INK, colw // 12, 18)
        draw_wrapped(buf, summ, x, 430, 1, INK, colw // 6, 10)
        draw_text(buf, src, x, 478, 1, BLUE)
        if i:
            line(buf, x - gap // 2, 244, x - gap // 2, 482, INK)
    rect(buf, MX, 494, CW, 2, INK)

    # twelve briefs, 4 columns x 3 rows
    scolw, sgap = 230, 14
    for idx, (loc, story) in enumerate(SHORTS):
        r, c = divmod(idx, 4)
        x = MX + c * (scolw + sgap)
        y = 510 + r * 58
        draw_text(buf, loc, x, y, 1, RED)
        draw_wrapped(buf, story, x, y + 11, 1, INK, scolw // 6, 9)
    rect(buf, MX, 682, CW, 1, INK)

    # also on friday: two micro-type columns
    draw_text(buf, "ALSO ON FRIDAY 20 NOVEMBER", MX, 696, 2, RED)
    rect(buf, MX, 718, CW, 2, INK)
    for j, item in enumerate(ALSO):
        col = 0 if j < 8 else 1
        x = MX if col == 0 else 512
        y = 734 + (j - 8 * col) * 17
        rect(buf, x, y + 3, 5, 5, RED)
        draw_text(buf, item, x + 12, y, 2, INK, font="micro")

    # date check in a red box
    outline(buf, MX, 878, CW, 56, RED, 2)
    draw_wrapped(buf, DATE_CHECK, MX + 16, 892, 2, INK, 76, 17)

    draw_centered(buf, FOOTER, W // 2, 952, 1, INK)
    return buf


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(build(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
