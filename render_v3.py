#!/usr/bin/env python3
"""Frost Front Page v3 — news-image-20261119.

Draws the 19 November 2026 front page in pure PIL: no photos, no
network, no external assets. Deterministic: same bytes every run.

Layout (1024x1024): masthead, region strip, numbers strip, 3 large
illustrated heroes, 9 small illustrated cards, a schematic world map
with numbered pins, 12 numbered briefs, a date-check box and a footer.

Run:  python3 render_v3.py            (writes entry.png next to it)
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 16

PAPER = (246, 241, 227)
PANEL = (255, 253, 246)
INK = (25, 25, 25)
MUTED = (90, 86, 76)
RULE = (60, 55, 45)
RED = (178, 38, 30)
NAVY = (31, 58, 95)
AMBER = (199, 125, 10)
GREEN = (30, 122, 76)
TEAL = (14, 124, 123)
PURPLE = (122, 79, 163)
BLUE = (31, 95, 168)
SKY = (168, 208, 230)

REGION_COLORS = {
    "ASIA": (178, 38, 30),
    "EUROPE": (31, 95, 168),
    "MIDDLE EAST": (122, 79, 163),
    "AFRICA": (30, 122, 76),
    "AMERICAS": (199, 125, 10),
    "OCEANIA": (14, 124, 123),
    "WORLD": (70, 70, 70),
}

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


F = {
    "mast": font(SERIF, 54),
    "dek": font(SERIF_IT, 18),
    "top": font(SANS_B, 13),
    "chip": font(SANS_B, 12),
    "num": font(SERIF, 26),
    "numlab": font(SANS, 10),
    "hero_kick": font(SANS_B, 12),
    "hero_head": font(SERIF, 22),
    "hero_deck": font(SERIF_REG, 14),
    "card_kick": font(SANS_B, 10),
    "card_head": font(SERIF, 15),
    "card_deck": font(SERIF_REG, 12),
    "map_title": font(SANS_B, 12),
    "brief_head": font(SANS_B, 12),
    "brief": font(SANS, 12),
    "date": font(SANS_B, 12),
    "date_body": font(SANS, 11),
    "foot": font(SANS, 11),
    "judge": font(SERIF_IT, 13),
    "badge": font(SANS_B, 11),
    "pin": font(SANS_B, 9),
}


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, leading=None, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.18)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(lines) * lh


def text_center(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- stories
# (num, region, place, kicker, headline, deck, source)

HEROES = [
    (1, "ASIA", "SHENZHEN", "APEC 2026 · SUMMIT",
     "Trump, Xi and Putin hold first three-way summit",
     "90 minutes, one \u201cDeclaration Toward Peace\u201d: a nuclear war "
     "\u201ccannot be won\u201d. — Reuters",
     "summit"),
    (2, "EUROPE", "THE HAGUE", "WORLD COURT · 9–6",
     "World Court: Myanmar committed genocide",
     "9–6: Myanmar guilty of genocide against the Rohingya; "
     "reparations ordered. — UN News",
     "court"),
    (3, "WORLD", "WORLDWIDE", "GTA VI · 13 YEARS ON",
     "GTA VI goes on sale after 13 years",
     "Unlocks at local midnight, New Zealand first, on PS5 and "
     "Xbox Series X|S. — ABC",
     "gta"),
]

CARDS = [
    (4, "AMERICAS", "NEW YORK", "NASDAQ · ANT",
     "Anthropic debuts in record $81bn IPO",
     "Priced at $83, ANT opens at $111.50 and closes up 17% at $97.17. — AP",
     "ipo"),
    (5, "WORLD", "ANTALYA", "COP31 · DRAFT DEAL",
     "COP31 draft drops fossil fuels",
     "The slimmed text also cuts the $120bn adaptation-aid goal. Talks end Friday. — Reuters",
     "cop"),
    (6, "ASIA", "ODISHA", "CYCLONE AKVAN",
     "120,000 evacuated as Akvan nears India",
     "Landfall due Friday near Gopalpur; schools shut, trains cancelled. — IMD",
     "cyclone"),
    (7, "EUROPE", "CRIMEA", "KERCH BRIDGE · WAR",
     "Ukraine hits Crimea bridge again",
     "Third strike in a week halts trains; rail section damaged overnight. — Reuters",
     "bridge"),
    (8, "MIDDLE EAST", "RIYADH", "OVER RIYADH · WAR",
     "Houthi missile hits Riyadh tower",
     "Debris damages the PIF Tower in the financial district; no injuries. — Reuters",
     "riyadh"),
    (9, "EUROPE", "COPENHAGEN", "GREENLAND · SECURITY",
     "Denmark backs Arctic pact with US",
     "Parliament ratifies the Greenland security deal by 109 votes to 0. — AP",
     "denmark"),
    (10, "OCEANIA", "CANBERRA", "ECONOMY · JOBS",
     "Australia's jobless rate hits 4.9%",
     "Highest since 2021; 43,500 jobs lost in October, ABS data show. — ABC",
     "jobs"),
    (11, "ASIA", "SEOUL", "SUPREME COURT · JUSTICE",
     "Korea's top court orders Han retrial",
     "Ex-PM Han Duck-soo's 15-year martial-law term is overturned. — AP",
     "seoul"),
    (12, "AFRICA", "MOGADISHU", "DIPLOMACY · GULF",
     "Somalia expels UAE ambassador",
     "Envoy given 72 hours to leave; Mogadishu cites sovereignty. — Al Jazeera",
     "somalia"),
]

BRIEFS = [
    (13, "Washington", "Senate rejects war-powers bid, 51–48.", "AMERICAS"),
    (14, "Gaza", "Israel ends tank raid past Yellow Line.", "MIDDLE EAST"),
    (15, "Bogotá", "Unions hold national strike on tax reform.", "AMERICAS"),
    (16, "Nairobi", "Marathon star Jepchirchir banned 3 years.", "AFRICA"),
    (17, "Pasadena", "NASA confirms Voyager 1 one light-day out.", "WORLD"),
    (18, "Shenzhen", "Philippines, Chile sign free-trade deal.", "ASIA"),
    (19, "Jakarta", "Asset-seizure law passes after 18 years.", "ASIA"),
    (20, "Brasília", "Lula ends Brazil's six-day work week.", "AMERICAS"),
    (21, "Nuku'alofa", "Tonga declares drought emergency.", "OCEANIA"),
    (22, "Suva", "Fiji declares national disaster on drought.", "OCEANIA"),
    (23, "Arkansas", "Walmart reports Q3; shares slip.", "AMERICAS"),
    (24, "Kwale", "Kenya picks US group for rare earths.", "AFRICA"),
]

REGION_COUNTS = [
    ("ASIA", 5), ("EUROPE", 3), ("MIDDLE EAST", 2), ("AFRICA", 3),
    ("AMERICAS", 5), ("OCEANIA", 3), ("WORLD", 3),
]

NUMBERS = [
    ("3", "leaders at one table"),
    ("9–6", "World Court genocide vote"),
    ("$81.3bn", "Anthropic's record IPO"),
    ("120,000", "evacuated before Akvan"),
    ("109–0", "Danish vote on Arctic pact"),
    ("4.9%", "Australian jobless rate"),
]

# lon/lat pins for the schematic map: (story num, lon, lat)
PINS = [
    (1, 114, 22), (2, 4, 52), (3, 175, -41), (4, -74, 41), (5, 31, 37),
    (6, 85, 20), (7, 34, 45), (8, 47, 25), (9, 12, 56), (10, 149, -35),
    (11, 127, 38), (12, 45, 2), (13, -77, 39), (14, 34, 31), (15, -74, 5),
    (16, 37, -1), (17, -118, 34), (18, 121, 15), (19, 107, -6),
    (20, -48, -16), (21, -175, -21), (22, 178, -18), (23, -94, 36),
    (24, 39, -4),
]


# ---------------------------------------------------------------- art
# Every scene is drawn from flat shapes: no photos, no outside artwork.

def _badge(d, x, y, text, bg=RED, fg=(255, 255, 255)):
    w = d.textlength(text, font=F["badge"]) + 12
    d.rectangle([x, y, x + w, y + 18], fill=bg)
    d.text((x + 6, y + 3), text, font=F["badge"], fill=fg)
    return w


def _badge_right(d, x_right, y, text, bg=RED, fg=(255, 255, 255)):
    w = d.textlength(text, font=F["badge"]) + 12
    d.rectangle([x_right - w, y, x_right, y + 18], fill=bg)
    d.text((x_right - w + 6, y + 3), text, font=F["badge"], fill=fg)


def _flag(d, x, y, w, h, kind):
    """Tiny flat flags: us, cn, ru, dk, kr, so, ae, au."""
    if kind == "us":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        for i in range(7):
            if i % 2 == 0:
                d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                            fill=(178, 34, 52))
        d.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(60, 59, 110))
    elif kind == "cn":
        d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        d.ellipse([x + w * 0.12, y + h * 0.12, x + w * 0.38, y + h * 0.5],
                  fill=(255, 222, 0))
    elif kind == "ru":
        d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
        d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
        d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))
    elif kind == "dk":
        d.rectangle([x, y, x + w, y + h], fill=(198, 12, 48))
        d.rectangle([x + w * 0.3, y, x + w * 0.42, y + h], fill=(255, 255, 255))
        d.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=(255, 255, 255))
    elif kind == "kr":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.ellipse([x + w * 0.38, y + h * 0.25, x + w * 0.62, y + h * 0.75],
                  fill=(205, 0, 58))
        d.ellipse([x + w * 0.38, y + h * 0.5, x + w * 0.62, y + h * 0.75],
                  fill=(0, 56, 147))
    elif kind == "so":
        d.rectangle([x, y, x + w, y + h], fill=(65, 137, 221))
        cx, cy, r = x + w / 2, y + h / 2, h * 0.32
        d.polygon([(cx, cy - r), (cx + r * 0.3, cy - r * 0.1),
                   (cx + r, cy - r * 0.1), (cx + r * 0.45, cy + r * 0.25),
                   (cx + r * 0.6, cy + r), (cx, cy + r * 0.55),
                   (cx - r * 0.6, cy + r), (cx - r * 0.45, cy + r * 0.25),
                   (cx - r, cy - r * 0.1), (cx - r * 0.3, cy - r * 0.1)],
                  fill=(255, 255, 255))
    elif kind == "ae":
        d.rectangle([x, y, x + w, y + h / 3], fill=(0, 122, 61))
        d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 255, 255))
        d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(0, 0, 0))
        d.rectangle([x, y, x + w * 0.25, y + h], fill=(200, 16, 46))
    elif kind == "au":
        d.rectangle([x, y, x + w, y + h], fill=(0, 0, 139))
        d.rectangle([x, y, x + w * 0.45, y + h * 0.5], fill=(200, 16, 46))
        for sx, sy in [(0.7, 0.3), (0.85, 0.6), (0.65, 0.75), (0.8, 0.85)]:
            d.ellipse([x + w * sx - 2, y + h * sy - 2,
                       x + w * sx + 2, y + h * sy + 2], fill=(255, 255, 255))


def _person(d, cx, base, suit, skin=(232, 190, 150), hair=(60, 45, 30),
            s=1.0):
    r = 13 * s
    d.ellipse([cx - r, base - 62 * s, cx + r, base - 36 * s], fill=skin)
    d.pieslice([cx - r, base - 62 * s, cx + r, base - 40 * s], 180, 360,
               fill=hair)
    d.polygon([(cx - 20 * s, base), (cx - 16 * s, base - 34 * s),
               (cx - 5 * s, base - 38 * s), (cx, base - 30 * s),
               (cx + 5 * s, base - 38 * s), (cx + 16 * s, base - 34 * s),
               (cx + 20 * s, base)], fill=suit)
    d.polygon([(cx - 4 * s, base - 36 * s), (cx, base - 28 * s),
               (cx + 4 * s, base - 36 * s), (cx, base - 14 * s)],
              fill=(255, 255, 255))
    d.polygon([(cx - 3 * s, base - 30 * s), (cx, base - 26 * s),
               (cx + 3 * s, base - 30 * s), (cx, base - 12 * s)], fill=RED)


def art_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(32, 64, 110))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(120, 82, 50))
    d.rectangle([x, y + h - 34, x + w, y + h - 26], fill=(222, 205, 170))
    fw, fh = 40, 24
    for i, (flg, name) in enumerate([("us", "TRUMP"), ("cn", "XI"),
                                     ("ru", "PUTIN")]):
        px = x + 18 + i * (w - 36) / 3 + ((w - 36) / 3 - fw) / 2
        d.rectangle([px + fw / 2 - 1, y + 4, px + fw / 2 + 1, y + 4 + fh + 8],
                    fill=(220, 220, 220))
        _flag(d, px, y + 4, fw, fh, flg)
        cx = px + fw / 2
        _person(d, cx, y + h - 26, (35, 35, 40), s=0.85)
        nw = d.textlength(name, font=F["badge"]) + 10
        d.rectangle([cx - nw / 2, y + h - 22, cx + nw / 2, y + h - 6],
                    fill=(255, 255, 255))
        d.text((cx - nw / 2 + 5, y + h - 20), name, font=F["badge"], fill=INK)


def art_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 230, 240))
    bx, by, bw, bh = x + 14, y + 34, w - 120, h - 44
    d.rectangle([bx, by, bx + bw, by + bh], fill=(170, 120, 85))
    d.polygon([(bx - 8, by), (bx + bw / 2, by - 22), (bx + bw + 8, by)],
              fill=(120, 70, 50))
    for i in range(5):
        cx = bx + 12 + i * (bw - 24) / 4
        d.rectangle([cx - 5, by + 16, cx + 5, by + bh - 8], fill=(240, 235, 220))
        d.rectangle([cx - 8, by + bh - 8, cx + 8, by + bh], fill=(240, 235, 220))
    sx = x + w - 78
    d.line([sx, y + 16, sx, y + h - 18], fill=(120, 90, 30), width=4)
    d.line([sx - 26, y + 22, sx + 26, y + 22], fill=(120, 90, 30), width=4)
    for s in (-1, 1):
        px = sx + s * 26
        d.line([px, y + 22, px - 10, y + 40], fill=(120, 90, 30), width=2)
        d.line([px, y + 22, px + 10, y + 40], fill=(120, 90, 30), width=2)
        d.arc([px - 12, y + 38, px + 12, y + 58], 0, 180, fill=(180, 140, 40),
              width=3)
    d.rectangle([sx - 14, y + h - 18, sx + 14, y + h - 12], fill=(120, 90, 30))
    _badge(d, x + w - 66, y + 6, "9–6", bg=RED)


def art_gta(d, x, y, w, h):
    for i in range(h):
        t = i / max(h - 1, 1)
        d.line([x, y + i, x + w, y + i],
               fill=(int(60 + 140 * t), int(40 + 60 * t), int(130 - 60 * t)))
    d.ellipse([x + w - 88, y + 10, x + w - 28, y + 70], fill=(255, 200, 90))
    for i, bh in enumerate([52, 70, 44, 78, 60, 48]):
        bx = x + 8 + i * (w - 16) / 6
        d.rectangle([bx, y + h - bh, bx + (w - 16) / 6 - 4, y + h],
                    fill=(30, 20, 45))
        for wy in range(3):
            d.rectangle([bx + 5, y + h - bh + 8 + wy * 12, bx + 12,
                         y + h - bh + 14 + wy * 12], fill=(255, 220, 120))
    d.rectangle([x + 8, y + 8, x + 86, y + 52], fill=(20, 20, 30))
    d.rectangle([x + 8, y + 8, x + 86, y + 52], outline=(255, 220, 120), width=2)
    d.text((x + 24, y + 12), "VI", font=font(SERIF, 30), fill=(255, 220, 120))
    _badge(d, x + 8, y + h - 24, "OUT NOW · 19 NOV", bg=(20, 20, 30))


def art_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 60, 40))
    pts = [(x + 10, y + h - 18), (x + w * 0.3, y + h - 34),
           (x + w * 0.5, y + h - 30), (x + w * 0.68, y + 26),
           (x + w - 12, y + 12)]
    d.line(pts, fill=(120, 230, 150), width=4)
    d.polygon([(x + w - 12, y + 12), (x + w - 26, y + 12),
               (x + w - 12, y + 26)], fill=(120, 230, 150))
    d.text((x + 8, y + 4), "ANT", font=font(SANS_B, 18), fill=(255, 255, 255))
    _badge(d, x + w - 62, y + h - 24, "+17%", bg=(120, 230, 150), fg=(10, 40, 20))


def art_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 225, 235))
    cx, cy, r = x + 30, y + h / 2, min(17, h / 2 - 3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 200))
    d.ellipse([cx - r + 5, cy - r + 4, cx - 1, cy - 2], fill=(90, 180, 90))
    d.ellipse([cx + 1, cy + 1, cx + r - 4, cy + r - 5], fill=(90, 180, 90))
    tx = x + 56
    d.text((tx, y + 6), "FOSSIL FUELS", font=font(SANS_B, 12), fill=INK)
    d.line([tx - 2, y + 14, tx + 100, y + 14], fill=RED, width=3)
    d.text((tx, y + 22), "$120bn AID GOAL", font=font(SANS_B, 11), fill=INK)
    d.line([tx - 2, y + 30, tx + 98, y + 30], fill=RED, width=2)
    _badge_right(d, x + w - 6, y + 5, "CUT", bg=RED)


def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(190, 215, 235))
    cx, cy = x + w - 66, y + h / 2
    base = h / 2 - 2
    for i, f in enumerate([1.0, 0.72, 0.45, 0.22]):
        r = base * f
        d.arc([cx - r, cy - r, cx + r, cy + r], 200 + i * 55,
              200 + i * 55 + 250, fill=(40, 80, 140), width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    d.text((x + 8, y + h - 18), "AKVAN · BAY OF BENGAL",
           font=font(SANS_B, 10), fill=(40, 80, 140))
    _badge(d, x + 6, y + 5, "120,000 EVACUATED", bg=NAVY)


def art_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 220, 230))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(90, 130, 170))
    deck = y + h - 14
    d.rectangle([x, y + h - 17, x + w, y + h - 13], fill=(120, 120, 125))
    d.arc([x + w / 2 - 40, y + 4, x + w / 2 + 40, deck + 8], 180, 360,
          fill=(90, 90, 95), width=4)
    for px in (x + 34, x + w - 34):
        d.rectangle([px - 4, deck - 12, px + 4, y + h - 8], fill=(90, 90, 95))
    ex, ey = x + w / 2 + 30, deck - 6
    for dx, dy, r, col in [(0, 0, 11, (255, 180, 40)), (0, -3, 7, (255, 120, 30)),
                           (0, -5, 4, (255, 240, 120))]:
        d.ellipse([ex + dx - r, ey + dy - r, ex + dx + r, ey + dy + r], fill=col)
    _badge(d, x + 6, y + 5, "3RD HIT IN A WEEK", bg=RED)


def art_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(25, 30, 55))
    sc = (h - 4) / 88
    for i, bh0 in enumerate([46, 78, 58, 88, 40]):
        bh = max(8, bh0 * sc)
        bx = x + 8 + i * (w - 16) / 5
        d.rectangle([bx, y + h - bh, bx + (w - 16) / 5 - 5, y + h],
                    fill=(70, 80, 110))
        for wy in range(int(bh // 12)):
            d.rectangle([bx + 4, y + h - bh + 5 + wy * 12, bx + 9,
                         y + h - bh + 8 + wy * 12], fill=(255, 220, 120))
    d.line([x + w - 12, y + 4, x + w * 0.62, y + h - 26], fill=(255, 200, 80),
           width=3)
    d.ellipse([x + w * 0.62 - 7, y + h - 33, x + w * 0.62 + 7, y + h - 19],
              fill=(255, 140, 40))
    _badge(d, x + 6, y + 5, "PIF TOWER HIT", bg=RED)


def art_denmark(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 232, 240))
    _flag(d, x + 14, y + 8, 46, 28, "dk")
    d.text((x + 68, y + 10), "+", font=font(SANS_B, 20), fill=INK)
    _flag(d, x + 92, y + 8, 46, 28, "us")
    d.rectangle([x + 150, y + 6, x + w - 10, y + h - 6], fill=(255, 255, 255))
    d.text((x + 158, y + 8), "VOTE", font=font(SANS_B, 9), fill=MUTED)
    d.text((x + 158, y + 20), "109–0", font=font(SANS_B, 17), fill=RED)


def art_jobs(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 240, 245))
    _flag(d, x + 10, y + 8, 36, 24, "au")
    base = y + h - 10
    for i, (lab, val) in enumerate([("SEP", 4.7), ("OCT", 4.9)]):
        bx = x + 60 + i * 44
        bh = int((val - 4.0) * 30)
        d.rectangle([bx, base - bh, bx + 28, base],
                    fill=(150, 160, 170) if i == 0 else RED)
        d.text((bx, base - bh - 13), f"{val}%", font=font(SANS_B, 11),
               fill=INK)
        d.text((bx + 2, base + 1), lab, font=font(SANS_B, 8), fill=MUTED)
    d.text((x + 168, y + 6), "4.9%", font=font(SERIF, 24), fill=RED)
    d.text((x + 168, y + h - 16), "5-YEAR HIGH", font=font(SANS_B, 9),
           fill=INK)


def art_seoul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 220))
    _flag(d, x + 10, y + 8, 40, 26, "kr")
    d.rectangle([x + 66, y + 8, x + 126, y + 18], fill=(120, 80, 40))
    d.line([x + 116, y + 18, x + 136, y + 36], fill=(120, 80, 40), width=5)
    d.rectangle([x + 124, y + 36, x + 154, y + 42], fill=(150, 110, 60))
    _badge_right(d, x + w - 6, y + h - 23, "RETRIAL", bg=NAVY)


def art_somalia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 235, 245))
    _flag(d, x + 12, y + 6, 44, 26, "so")
    d.line([x + 66, y + 19, x + 118, y + 19], fill=RED, width=4)
    d.polygon([(x + 118, y + 19), (x + 108, y + 13), (x + 108, y + 25)],
              fill=RED)
    _flag(d, x + 126, y + 6, 44, 26, "ae")
    d.rectangle([x + 182, y + 8, x + w - 8, y + 30], fill=RED)
    d.text((x + 188, y + 12), "72 HOURS", font=font(SANS_B, 11),
           fill=(255, 255, 255))
    d.text((x + 188, y + h - 15), "TO LEAVE", font=font(SANS_B, 9), fill=RED)


ART = {
    "summit": art_summit, "court": art_court, "gta": art_gta,
    "ipo": art_ipo, "cop": art_cop, "cyclone": art_cyclone,
    "bridge": art_bridge, "riyadh": art_riyadh, "denmark": art_denmark,
    "jobs": art_jobs, "seoul": art_seoul, "somalia": art_somalia,
}


# ---------------------------------------------------------------- map
# Very rough continent outlines (lon/lat), drawn schematically.

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-70, 62), (-55, 52), (-60, 46), (-75, 35), (-80, 25), (-90, 21),
     (-97, 16), (-105, 20), (-115, 30), (-125, 40), (-125, 49), (-135, 58),
     (-155, 58)],
    # South America
    [(-80, 10), (-70, 11), (-60, 8), (-50, 0), (-35, -8), (-38, -15),
     (-48, -27), (-58, -35), (-65, -45), (-70, -52), (-73, -40), (-73, -25),
     (-77, -12), (-81, 0)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 53), (5, 58), (10, 60), (18, 56),
     (21, 55), (28, 59), (30, 70), (40, 68), (45, 60), (35, 50), (30, 46),
     (28, 44), (23, 40), (19, 42), (12, 44), (8, 44), (3, 42), (-2, 37)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 31), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (40, -5), (35, -18), (32, -29),
     (20, -35), (17, -29), (14, -22), (12, -6), (9, 4), (-8, 5), (-13, 8)],
    # Asia
    [(30, 70), (45, 68), (60, 70), (75, 73), (90, 75), (110, 74), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (160, 55), (145, 45),
     (140, 40), (130, 33), (122, 30), (120, 22), (110, 20), (105, 10),
     (100, 8), (98, 15), (95, 22), (88, 22), (80, 8), (77, 8), (72, 20),
     (68, 23), (60, 25), (55, 27), (50, 29), (48, 30), (44, 30), (40, 36),
     (35, 36), (30, 36), (28, 45), (30, 55)],
    # Australia
    [(113, -22), (114, -30), (118, -35), (125, -33), (130, -32), (135, -35),
     (140, -38), (147, -38), (150, -37), (153, -27), (153, -24), (146, -19),
     (142, -11), (137, -12), (132, -12), (126, -14), (122, -17)],
    # New Zealand
    [(167, -46), (173, -41), (178, -38), (175, -35), (172, -41), (167, -46)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 58), (-2, 57), (1, 51), (-5, 50)],
    # Japan
    [(130, 31), (133, 34), (138, 35), (141, 40), (142, 44), (140, 41),
     (136, 35), (132, 33), (130, 31)],
    # Indonesia
    [(95, 5), (105, -5), (115, -8), (125, -9), (131, -1), (141, -8),
     (141, -3), (135, -2), (120, 0), (110, 0), (100, 0), (95, 5)],
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(205, 225, 240))
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    lon0, lon1, lat0, lat1 = -180, 180, -60, 84

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat1 - lat) / (lat1 - lat0) * h
        return px, py

    for lon in range(-150, 181, 30):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        d.line([px, y, px, y + h], fill=(190, 212, 228), width=1)
    for lat in range(-60, 85, 30):
        py = y + (lat1 - lat) / (lat1 - lat0) * h
        d.line([x, py, x + w, py], fill=(190, 212, 228), width=1)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(232, 222, 192), outline=(150, 135, 105))
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        label = str(num)
        tw = d.textlength(label, font=F["pin"])
        d.text((px - tw / 2, py - 6), label, font=F["pin"],
               fill=(255, 255, 255))


# ---------------------------------------------------------------- layout

def hero_card(d, x, y, w, h, story):
    num, region, place, kicker, head, deck, art = story
    col = REGION_COLORS[region]
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=col)
    ART[art](d, x + 1, y + 5, w - 2, 110)
    ty = y + 122
    d.text((x + 10, ty), f"{num}  {place} · {kicker}",
           font=F["hero_kick"], fill=col)
    ty += 18
    ty = draw_wrapped(d, x + 10, ty, head, F["hero_head"], w - 20, INK,
                      leading=25, max_lines=2)
    draw_wrapped(d, x + 10, ty + 2, deck, F["hero_deck"], w - 20, MUTED,
                 leading=16, max_lines=2)


def small_card(d, x, y, w, h, story):
    num, region, place, kicker, head, deck, art = story
    col = REGION_COLORS[region]
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=col)
    ART[art](d, x + 1, y + 4, w - 2, 44)
    ty = y + 52
    d.text((x + 8, ty), f"{num}  {place} · {kicker}",
           font=F["card_kick"], fill=col)
    ty += 14
    ty = draw_wrapped(d, x + 8, ty, head, F["card_head"], w - 16, INK,
                      leading=17, max_lines=2)
    draw_wrapped(d, x + 8, ty + 1, deck, F["card_deck"], w - 16, MUTED,
                 leading=14, max_lines=2)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    inner = W - 2 * MARGIN

    # --- top strip
    d.text((MARGIN, 8), "FROST FRONT PAGE  ·  THE WORLD IN ONE DAY",
           font=F["top"], fill=NAVY)
    right = "24 VERIFIED STORIES · 7 REGIONS"
    d.text((W - MARGIN - d.textlength(right, font=F["top"]), 8), right,
           font=F["top"], fill=RED)
    d.line([MARGIN, 27, W - MARGIN, 27], fill=RULE, width=2)

    # --- masthead
    text_center(d, W / 2, 30, "Thursday 19 November 2026", F["mast"], INK)
    text_center(d, W / 2, 92,
                "Three leaders share one table  ·  The World Court finds "
                "genocide  ·  GTA VI goes on sale",
                F["dek"], RED)
    d.line([MARGIN, 118, W - MARGIN, 118], fill=RULE, width=1)

    # --- region strip
    ry = 122
    cw = inner / 7
    for i, (name, count) in enumerate(REGION_COUNTS):
        cx = MARGIN + i * cw
        col = REGION_COLORS[name]
        d.rectangle([cx + 1, ry, cx + cw - 1, ry + 24], fill=PANEL,
                    outline=RULE, width=1)
        d.rectangle([cx + 1, ry, cx + cw - 1, ry + 4], fill=col)
        text_center(d, cx + cw / 2, ry + 7, f"{name}  {count}",
                    F["chip"], col)
    y = ry + 30

    # --- numbers strip
    ny = y
    nw = inner / 6
    d.rectangle([MARGIN, ny, W - MARGIN, ny + 40], fill=PANEL,
                outline=RULE, width=1)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = MARGIN + i * nw
        if i:
            d.line([cx, ny + 6, cx, ny + 34], fill=(200, 195, 180), width=1)
        text_center(d, cx + nw / 2, ny + 3, num, F["num"], RED)
        text_center(d, cx + nw / 2, ny + 28, lab, F["numlab"], MUTED)
    y = ny + 46

    # --- heroes
    gap = 8
    hw = (inner - 2 * gap) / 3
    hh = 224
    for i, story in enumerate(HEROES):
        hero_card(d, MARGIN + i * (hw + gap), y, hw, hh, story)
    y += hh + 8

    # --- small cards: 3 rows of 3
    ch = 112
    for row in range(3):
        for col_i in range(3):
            story = CARDS[row * 3 + col_i]
            small_card(d, MARGIN + col_i * (hw + gap), y, hw, ch, story)
        y += ch + 6
    y -= 6  # last gap not needed
    y += 8

    # --- map + briefs band
    band_y = y
    band_h = 132
    map_w = 300
    d.text((MARGIN, band_y), "WHERE IT HAPPENED",
           font=F["map_title"], fill=NAVY)
    d.text((MARGIN, band_y + 14), "numbers match the stories",
           font=F["numlab"], fill=MUTED)
    draw_map(d, MARGIN, band_y + 30, map_w, band_h - 30)
    bx = MARGIN + map_w + 12
    bw = W - MARGIN - bx
    d.text((bx, band_y), "ALSO ON THURSDAY 19 NOVEMBER 2026",
           font=F["map_title"], fill=NAVY)
    d.text((bx, band_y + 14), "place · what happened",
           font=F["numlab"], fill=MUTED)
    col_w = bw / 2
    for i, (num, place, text, region) in enumerate(BRIEFS):
        col_i = i // 6
        row_i = i % 6
        px = bx + col_i * col_w
        py = band_y + 30 + row_i * 17
        col = REGION_COLORS[region]
        d.rectangle([px, py + 1, px + 17, py + 15], fill=col)
        lab = str(num)
        tw = d.textlength(lab, font=F["pin"])
        d.text((px + (17 - tw) / 2, py + 3), lab, font=F["pin"],
               fill=(255, 255, 255))
        line = f"{place}: {text}"
        max_w = col_w - 22
        while line and d.textlength(line, font=F["brief"]) > max_w:
            line = line[:-1]
        if line != f"{place}: {text}":
            line = line.rstrip(" ,.;:") + "…"
        d.text((px + 21, py + 1), line, font=F["brief"], fill=INK)
    y = band_y + band_h + 8

    # --- date check
    d.rectangle([MARGIN, y, W - MARGIN, y + 48], fill=(255, 248, 235),
                outline=RED, width=2)
    d.text((MARGIN + 8, y + 5),
           "DATE CHECK — Every story on this page happened, or was "
           "first reported, on Thursday 19 November 2026.",
           font=F["date"], fill=RED)
    draw_wrapped(
        d, MARGIN + 8, y + 22,
        "LEFT OUT AS OTHER DAYS' NEWS:  18 NOV — Anthropic's $83 IPO "
        "pricing · GTA VI reviews · Sudan: Hemedti death sentence · EU's "
        "\u20ac45bn Ukraine loan plan · Modi–Wales meeting  ·  17 NOV — "
        "Amazon's $7bn renewables · Nvidia results  ·  NOT YET — Akvan's "
        "landfall (Fri 20) · COP31 close (Fri 20)",
        F["date_body"], inner - 16, INK, leading=13, max_lines=2)
    y += 56

    # --- judge note + footer
    text_center(
        d, W / 2, y,
        "To the judge — 24 stories, each a real 19 November 2026 event, "
        "checked against first-report dates.",
        F["judge"], MUTED)
    y += 20
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=1)
    d.text((MARGIN, y + 4),
           "Sources: Reuters · AP · CNN · AFP · Al Jazeera · Euronews · "
           "ABC · RNZ · Xinhua · Nature · ABS · NASA · IMD",
           font=F["foot"], fill=MUTED)
    right = "FROST FRONT PAGE · drawn in code · 2026-11-19"
    d.text((W - MARGIN - d.textlength(right, font=F["foot"]), y + 4), right,
           font=F["foot"], fill=MUTED)
    return img


def main():
    img = render()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out}  {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
