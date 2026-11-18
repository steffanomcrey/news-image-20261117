#!/usr/bin/env python3
"""Draw the news-image-20261117 front page. Build-time only.
Usage: python3 generate.py --variant A|B|C --out /tmp/cand_A.png
Variants: A = front page + map, B = front page + big lead illustration,
C = magazine cover, single scene + headline strip.
All facts come from FIELD.md (verified news of Tue 17 Nov 2026). No network.
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
F_REG = FONT_DIR + "DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, fnt, max_w):
    """Shorten text with an ellipsis so it fits max_w pixels."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    ell = "..."
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if draw.textlength(text[:mid] + ell, font=fnt) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:max(lo, 1)] + ell


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# (number, tag, headline, body, lon, lat) — facts per FIELD.md only.
STORIES = [
    (1, "EUROPE", "KERCH BRIDGE HIT",
     "Ukraine: a section collapsed into the sea; Russia hit Kyiv bridges",
     36.5, 45.3),
    (2, "MIDDLE EAST", "HORMUZ TANKERS MINED",
     "Two tankers hit mines and caught fire near the Strait",
     56.5, 26.5),
    (3, "MIDDLE EAST", "DRONES AT BAHRAIN BASE",
     "Iran fired drones at a US radar; Bahrain intercepted them",
     50.5, 26.2),
    (4, "US", "THIRD US CARRIER ARRIVES",
     "USS Theodore Roosevelt enters the Middle East",
     62.0, 15.0),
    (5, "US / IRAN", "DIRTY-BOMB CLAIM DENIED",
     "US officials say Iran plans an attack; Iran denies it",
     -76.0, 39.5),
    (6, "ASIA", "XI, TRUMP, PUTIN TO MEET",
     "Leaders meet Thu 19 Nov in Shenzhen, on APEC sidelines",
     114.0, 22.5),
    (7, "MIDDLE EAST", "GAZA CEASEFIRE AT RISK",
     "Board of Peace gives a bleak first report to the UN",
     34.5, 31.5),
    (8, "MIDDLE EAST", "GAZA WINTER WARNING",
     "1.4m face acute hunger; a baby died of hypothermia",
     35.8, 30.6),
    (9, "EUROPE", "DEUTSCHE BANK LEAK",
     "15m files leaked; shares fall 4.7%",
     8.7, 50.1),
    (10, "TECH", "US AI CHIP CURBS",
     "New rules limit remote access to advanced AI chips",
     -77.0, 38.9),
    (11, "US", "PENTAGON AUDIT FAILS",
     "9th year in a row; $4.8tn in assets unverified",
     -77.5, 38.5),
    (12, "EUROPE", "RWANDA RETURNS HUB",
     "Five European states agree a joint facility in Rwanda",
     29.9, -1.9),
    (13, "BUSINESS", "ANTHROPIC IPO AT ~$1TN",
     "Shares priced $70-78 for its Nasdaq debut",
     -122.4, 37.8),
    (14, "SCIENCE", "EUCLID MAPS 900M GALAXIES",
     "First major data release; a record-setting quasar",
     2.35, 48.85),
]

ALSO = ("ALSO — TUESDAY 17 NOVEMBER 2026: England 3-2 Spain  |  Earthshot in Mumbai; "
        "ocean 10% protected  |  Leonids peak  |  US measles worst since 1991  |  "
        "Japan jets scrambled  |  Xi-Carney tariff cuts  |  UN autonomous-weapons talks")

LAND = {
    "NA": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60), (-55, 47),
           (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
           (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    "SA": [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28), (-58, -35),
           (-65, -40), (-70, -52), (-73, -40), (-72, -20), (-80, -5), (-80, 5)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59), (18, 56),
           (21, 55), (24, 58), (28, 60), (30, 62), (30, 70), (20, 70), (12, 71), (5, 60),
           (5, 58), (-5, 50), (-10, 44)],
    "AF": [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 11), (48, 0),
           (40, -10), (35, -18), (32, -26), (26, -34), (18, -35), (15, -27), (12, -18),
           (9, -1), (9, 4), (-8, 4), (-15, 11), (-17, 15)],
    "AS": [(30, 70), (40, 68), (60, 69), (70, 72), (90, 75), (110, 76), (130, 72), (160, 70),
           (178, 66), (170, 60), (162, 56), (158, 52), (142, 50), (140, 40), (130, 33),
           (127, 35), (122, 30), (120, 22), (110, 20), (105, 10), (100, 8), (98, 15),
           (95, 16), (90, 22), (85, 20), (80, 13), (77, 8), (73, 20), (68, 25), (62, 25),
           (58, 26), (55, 26), (50, 29), (48, 30), (44, 29), (40, 31), (36, 36), (33, 36),
           (30, 36)],
    "OC": [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35), (140, -38),
           (146, -39), (150, -37), (153, -32), (153, -27), (146, -19), (142, -15), (142, -11),
           (136, -12), (132, -12), (126, -14), (122, -17), (118, -20)],
    "UK": [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    "JP": [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44)],
    "ID": [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
           (130, -3), (135, -4), (141, -8), (141, -2), (131, 1), (120, 1), (110, 2)],
}


def draw_bridge(d, x0, y0, x1, y1):
    """Broken Kerch Bridge over water, inside box (x0,y0,x1,y1)."""
    w, h = x1 - x0, y1 - y0
    horizon = y0 + int(h * 0.52)
    for i in range(horizon - y0):
        t = i / max(1, horizon - y0)
        d.rectangle([x0, y0 + i, x1, y0 + i],
                    fill=(int(250 - 60 * t), int(214 - 40 * t), int(150 - 20 * t)))
    d.rectangle([x0, horizon, x1, y1], fill=(38, 84, 124))
    for i in range(0, w, 26):
        d.line([x0 + i, horizon + 6, x0 + i + 14, horizon + 6], fill=(90, 140, 180), width=2)
    d.ellipse([x0 + int(w * 0.78), y0 + 8, x0 + int(w * 0.78) + 34, y0 + 42],
              fill=(255, 236, 170))
    deck_y = y0 + int(h * 0.46)
    # left deck span
    d.polygon([(x0 + 6, deck_y), (x0 + int(w * 0.44), deck_y),
               (x0 + int(w * 0.44), deck_y + 10), (x0 + 6, deck_y + 10)], fill=(60, 60, 66))
    # collapsed middle span, tilted into the water
    d.polygon([(x0 + int(w * 0.46), deck_y + 4), (x0 + int(w * 0.58), deck_y + 26),
               (x0 + int(w * 0.60), deck_y + 34), (x0 + int(w * 0.47), deck_y + 14)],
              fill=(80, 80, 88))
    # right deck span
    d.polygon([(x0 + int(w * 0.62), deck_y), (x1 - 6, deck_y),
               (x1 - 6, deck_y + 10), (x0 + int(w * 0.62), deck_y + 10)], fill=(60, 60, 66))
    # pillars
    for px in (0.10, 0.30, 0.72, 0.90):
        px0 = x0 + int(w * px)
        d.rectangle([px0, deck_y + 10, px0 + 8, horizon + 34], fill=(70, 70, 76))
    # fallen pillar + debris in the water at the gap
    d.polygon([(x0 + int(w * 0.50), horizon + 8), (x0 + int(w * 0.56), horizon + 30),
               (x0 + int(w * 0.58), horizon + 30), (x0 + int(w * 0.52), horizon + 8)],
              fill=(90, 90, 96))
    d.ellipse([x0 + int(w * 0.47), horizon + 26, x0 + int(w * 0.60), horizon + 38],
              outline=(220, 230, 240), width=2)
    # smoke from the break
    for cx, cy, r in ((0.50, 0.30, 13), (0.53, 0.22, 17), (0.56, 0.15, 12)):
        d.ellipse([x0 + int(w * cx) - r, y0 + int(h * cy) - r,
                   x0 + int(w * cx) + r, y0 + int(h * cy) + r], fill=(110, 110, 112))
    # blast star at the gap
    gx, gy = x0 + int(w * 0.52), deck_y + 2
    for ang in range(0, 360, 45):
        import math
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.line([gx, gy, gx + int(dx * 22), gy + int(dy * 22)], fill=(255, 200, 60), width=3)
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(30, 30, 30), width=2)


def draw_map(d, x0, y0, x1, y1):
    """Simplified world map with numbered pins 1-14."""
    d.rectangle([x0, y0, x1, y1], fill=(207, 227, 238))
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(30, 30, 30), width=2)

    def px(lon, lat):
        return (x0 + (lon + 180) / 360 * (x1 - x0),
                y0 + (90 - lat) / 180 * (y1 - y0))

    for poly in LAND.values():
        d.polygon([px(lon, lat) for lon, lat in poly], fill=(216, 210, 196),
                  outline=(150, 142, 128))
    labels = [("NORTH AMERICA", -112, 60), ("SOUTH AMERICA", -60, -16),
              ("EUROPE", 28, 62), ("AFRICA", 18, 4), ("ASIA", 95, 52),
              ("AUSTRALIA", 134, -26)]
    lf = font(F_BOLD, 13)
    for name, lon, lat in labels:
        lx, ly = px(lon, lat)
        d.text((lx, ly), name, font=lf, fill=(90, 88, 80), anchor="mm")
    # pins that would overlap a neighbour are drawn offset, with a leader
    # line back to their true spot
    PIN_OFF = {3: (-10, -7), 4: (12, -9), 5: (-12, 6), 8: (10, -8),
               11: (10, -7), 14: (-12, 6)}
    for num, _tag, _h, _b, lon, lat in STORIES:
        tx, ty = px(lon, lat)
        dlon, dlat = PIN_OFF.get(num, (0, 0))
        cx, cy = px(lon + dlon, lat + dlat)
        if (dlon, dlat) != (0, 0):
            d.line([tx, ty, cx, cy], fill=(120, 120, 120), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(178, 34, 34))
        r = 11
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 34, 34),
                  outline=(255, 255, 255), width=2)
        nf = font(F_BOLD, 12)
        d.text((cx, cy - 1), str(num), font=nf, fill=(255, 255, 255), anchor="mm")


def masthead(d, y=14):
    d.text((W // 2, y + 28), "THE WORLD IN ONE DAY", font=font(F_BOLD, 60),
           fill=(10, 10, 10), anchor="mm")
    d.text((W // 2, y + 72), "ONE DAY, ONE PAGE  —  TUESDAY 17 NOVEMBER 2026",
           font=font(F_BOLD, 21), fill=(120, 20, 20), anchor="mm")
    d.line([16, y + 92, W - 16, y + 92], fill=(10, 10, 10), width=3)
    return y + 100


def story_cards(d, x0, y0, cols, rows, cw, ch):
    hf, bf, tf = font(F_BOLD, 26), font(F_REG, 15), font(F_BOLD, 13)
    for i, (num, tag, head, body, _lon, _lat) in enumerate(STORIES):
        cx = x0 + (i % cols) * cw
        cy = y0 + (i // cols) * ch
        d.rectangle([cx + 2, cy + 2, cx + cw - 4, cy + ch - 4], outline=(160, 160, 160))
        d.rectangle([cx + 6, cy + 5, cx + 30, cy + 29], fill=(178, 34, 34))
        d.text((cx + 18, cy + 17), str(num), font=font(F_BOLD, 15),
               fill=(255, 255, 255), anchor="mm")
        d.text((cx + 36, cy + 6), tag, font=tf, fill=(120, 20, 20))
        d.text((cx + 36, cy + 26), fit(d, head, hf, cw - 44), font=hf, fill=(10, 10, 10))
        d.text((cx + 6, cy + ch - 18), fit(d, body, bf, cw - 14), font=bf, fill=(40, 40, 40))


def footer(d, y):
    d.line([16, y, W - 16, y], fill=(10, 10, 10), width=2)
    lines = wrap(d, ALSO, font(F_REG, 15), W - 32)
    yy = y + 7
    for ln in lines[:2]:
        d.text((16, yy), ln, font=font(F_REG, 15), fill=(30, 30, 30))
        yy += 19


def variant_a():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    y = masthead(d)
    # lead: text left, bridge art right
    d.text((16, y + 6), "TUESDAY 17 NOVEMBER 2026 — LEAD STORY",
           font=font(F_BOLD, 17), fill=(120, 20, 20))
    head = ["UKRAINE CRIPPLES", "THE KERCH BRIDGE"]
    yy = y + 34
    for ln in head:
        d.text((16, yy), ln, font=font(F_BOLD, 36), fill=(10, 10, 10))
        yy += 42
    body = ("Ukraine severely damaged the Crimean (Kerch) Bridge: a section "
            "collapsed into the water. Zelenskyy called it an “unprecedented "
            "operation” weeks in the making.")
    yy += 4
    for ln in wrap(d, body, font(F_REG, 18), 470)[:3]:
        d.text((16, yy), ln, font=font(F_REG, 18), fill=(30, 30, 30))
        yy += 23
    draw_bridge(d, 512, y + 6, W - 16, y + 180)
    d.text((512, y + 186), "The Kerch Bridge, after the strike: a span down in the strait.",
           font=font(F_REG, 14), fill=(90, 90, 90))
    my = y + 200
    d.text((16, my - 4), "THE DAY ON THE MAP — PIN NUMBERS MATCH THE STORIES BELOW",
           font=font(F_BOLD, 16), fill=(10, 10, 10))
    draw_map(d, 16, my + 20, W - 16, my + 160)
    sy = my + 174
    story_cards(d, 16, sy, 2, 7, 496, 70)
    footer(d, sy + 7 * 70 + 4)
    return img


def variant_b():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    y = masthead(d)
    d.text((16, y + 4), "TUESDAY 17 NOVEMBER 2026 — LEAD STORY",
           font=font(F_BOLD, 17), fill=(120, 20, 20))
    d.text((16, y + 30), "UKRAINE CRIPPLES THE KERCH BRIDGE",
           font=font(F_BOLD, 34), fill=(10, 10, 10))
    draw_bridge(d, 16, y + 70, W - 16, y + 280)
    d.text((16, y + 286), "A section of the Crimean (Kerch) Bridge collapsed into the water; "
           "Russia hit Kyiv’s Dnipro bridges overnight.",
           font=font(F_REG, 16), fill=(30, 30, 30))
    d.text((16, y + 308), "Zelenskyy called the strike an “unprecedented operation” weeks in the making.",
           font=font(F_REG, 16), fill=(30, 30, 30))
    sy = y + 336
    story_cards(d, 16, sy, 2, 7, 496, 72)
    footer(d, sy + 7 * 72 + 6)
    return img


def variant_c():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    y = masthead(d)
    d.text((16, y + 2), "TUESDAY 17 NOVEMBER 2026 — THE DAY IN ONE PICTURE",
           font=font(F_BOLD, 17), fill=(120, 20, 20))
    # one big scene: bridge across the whole width, skyline strip below it
    draw_bridge(d, 16, y + 28, W - 16, y + 330)
    d.rectangle([16, y + 330, W - 16, y + 392], fill=(24, 24, 30))
    sky = ["KYIV", "HORMUZ", "SHENZHEN", "GAZA", "MANILA", "MUMBAI"]
    xf = font(F_BOLD, 20)
    xx = 30
    for s in sky:
        d.text((xx, y + 361), s, font=xf, fill=(220, 220, 220))
        xx += d.textlength(s, font=xf) + 34
    d.text((16, y + 408), "UKRAINE CRIPPLES THE KERCH BRIDGE",
           font=font(F_BOLD, 38), fill=(10, 10, 10))
    d.text((16, y + 456), "A section collapsed into the sea; Russia hit Kyiv’s bridges overnight.",
           font=font(F_REG, 19), fill=(30, 30, 30))
    # headline strip: six biggest stories, large type
    strip = [
        ("2", "HORMUZ TANKERS MINED — two tankers hit mines, caught fire"),
        ("5", "DIRTY-BOMB CLAIM DENIED — US officials say Iran plans attack"),
        ("6", "XI, TRUMP, PUTIN MEET THU 19 NOV IN SHENZHEN"),
        ("9", "DEUTSCHE BANK LEAK — 15m files; shares fall 4.7%"),
        ("11", "PENTAGON AUDIT FAILS — 9th year; $4.8tn unverified"),
        ("14", "EUCLID MAPS 900M GALAXIES"),
    ]
    yy = y + 500
    for num, txt in strip:
        d.rectangle([16, yy, 44, yy + 28], fill=(178, 34, 34))
        d.text((30, yy + 14), num, font=font(F_BOLD, 15), fill=(255, 255, 255), anchor="mm")
        d.text((54, yy + 14), fit(d, txt, font(F_BOLD, 26), W - 70),
               font=font(F_BOLD, 26), fill=(10, 10, 10))
        yy += 40
    d.text((16, yy + 6), "Plus: Gaza ceasefire at risk  •  Anthropic IPO at ~$1tn  •  England 3-2 Spain",
           font=font(F_REG, 18), fill=(30, 30, 30))
    footer(d, yy + 44)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["A", "B", "C"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    img = {"A": variant_a, "B": variant_b, "C": variant_c}[args.variant]()
    img.save(args.out, "PNG", optimize=True)
    print(args.out, img.size)


if __name__ == "__main__":
    main()
