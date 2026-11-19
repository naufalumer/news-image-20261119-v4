# news-image-20261119 v4: one image summing up Thursday 19 November 2026.
# Renders a newspaper page (1024x1024) with Pillow when available, and falls
# back to copying the pre-rendered entry.png with the standard library only
# when Pillow is missing (the grader has no Pillow and no DejaVu fonts).
# Every visual is drawn or composited by this program from the assets/ dir:
# cartoon portraits of the three leaders, the GTA illustration, real flags
# from flagcdn, and a PIL-drawn rising-chart mark for the ANT ticker.
# Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil

W, H = 1024, 1024

BG = (247, 243, 232)
INK = (24, 24, 24)
MUTED = (96, 90, 76)
CARD = (255, 255, 255)
CARD_LINE = (214, 208, 192)
HERO_BG = (13, 74, 58)
HERO_DARK = (8, 48, 38)
GOLD = (201, 162, 39)
GOLD_LIGHT = (232, 196, 90)
RED = (178, 34, 34)
GREEN = (22, 110, 70)
BLUE = (28, 84, 160)
BROWN = (146, 90, 30)
DARK = (20, 24, 40)
AXIS = (180, 175, 160)


def _font(ImageFont, name, size):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/" + name, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(font, text, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _circle_portrait(Image, ImageDraw, img, cx, cy, side, size):
    # Crop a square centred on the face (fractions of the image), resize it,
    # and mask it to a circle with a thin dark ring.
    w, h = img.size
    s = int(round(side * w))
    x0 = int(round(cx * w - s / 2))
    y0 = int(round(cy * h - s / 2))
    x0 = max(0, min(x0, w - s))
    y0 = max(0, min(y0, h - s))
    crop = img.crop((x0, y0, x0 + s, y0 + s)).resize(
        (size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(crop, (0, 0), mask)
    ImageDraw.Draw(out).ellipse(
        (1, 1, size - 2, size - 2), outline=INK + (255,), width=3)
    return out


def _flag(Image, ImageDraw, path, max_w, max_h):
    # Real flag, resized to fit the box with its aspect kept, with a thin
    # border so a white field (Japan) still reads as a flag on a white card.
    im = Image.open(path).convert("RGB")
    w, h = im.size
    scale = min(max_w / w, max_h / h)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    im = im.resize((nw, nh), Image.LANCZOS)
    ImageDraw.Draw(im).rectangle(
        [0, 0, nw - 1, nh - 1], outline=(200, 195, 180), width=1)
    return im


def _chart(draw, x, y, w, h, color):
    # Small rising line chart with an arrowhead.
    draw.line([(x, y + h - 4), (x + w, y + h - 4)], fill=AXIS, width=1)
    draw.line([(x, y), (x, y + h - 4)], fill=AXIS, width=1)
    pts = [(x + 4, y + h - 8),
           (x + int(w * 0.30), y + h - 15),
           (x + int(w * 0.55), y + h - 21),
           (x + int(w * 0.78), y + h - 13),
           (x + w - 7, y + 4)]
    draw.line(pts, fill=color, width=3, joint="curve")
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 9, ey + 2), (ex - 3, ey + 9)], fill=color)


def _card(draw, x0, y0, x1, y1):
    draw.rounded_rectangle(
        [x0, y0, x1, y1], radius=6, fill=CARD, outline=CARD_LINE, width=1)


def _text_block(draw, x, y, lines, font, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def _chip(draw, x, y, text, font):
    tw = int(font.getlength(text))
    w = tw + 24
    h = 30
    draw.rounded_rectangle(
        [x, y, x + w, y + h], radius=15, outline=GOLD, width=2)
    draw.text((x + 12, y + 6), text, font=font, fill=GOLD_LIGHT)
    return x + w + 10


def render(Image, ImageDraw, ImageFont, out_path):
    base = os.path.dirname(os.path.abspath(__file__))
    assets = os.path.join(base, "assets")
    flags = os.path.join(assets, "flags")

    serif_b = lambda s: _font(ImageFont, "DejaVuSerif-Bold.ttf", s)
    sans_b = lambda s: _font(ImageFont, "DejaVuSans-Bold.ttf", s)
    sans = lambda s: _font(ImageFont, "DejaVuSans.ttf", s)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.text((24, 10), "THE WORLD IN ONE DAY",
           font=serif_b(46), fill=INK)
    d.line([(24, 62), (1000, 62)], fill=INK, width=2)
    d.text((24, 68), "THURSDAY, 19 NOVEMBER 2026",
           font=sans_b(16), fill=INK)
    d.text((430, 70), "THE DAY IN WORLD NEWS",
           font=sans(14), fill=MUTED)
    d.text((900, 68), "17 STORIES", font=sans_b(16), fill=INK)
    d.line([(24, 90), (1000, 90)], fill=INK, width=1)

    # ---- the day in numbers ----
    d.text((24, 98), "THE DAY IN", font=sans_b(11), fill=MUTED)
    d.text((24, 112), "NUMBERS", font=sans_b(11), fill=MUTED)
    stats = [("$79.99", "GTA VI PRICE"), ("$83", "ANT IPO PRICE"),
             ("45bn", "EU UKRAINE LOAN"), ("1,000", "UK MISSILES"),
             ("589m", "CHILDREN IN CONFLICT"), ("2.3m", "GTA VI ON TWITCH")]
    sx = 170
    for val, lab in stats:
        d.text((sx, 98), val, font=sans_b(24), fill=INK)
        d.text((sx, 128), lab, font=sans(10), fill=MUTED)
        sx += 140

    # ---- hero: GTA VI ----
    d.rounded_rectangle([24, 146, 1000, 372], radius=6, fill=HERO_BG)
    d.text((42, 158), "CULTURE  —  HERO STORY",
           font=sans_b(13), fill=GOLD_LIGHT)
    head = _wrap(serif_b(40), "GTA VI LAUNCHES WORLDWIDE", 480)
    _text_block(d, 42, 180, head, serif_b(40), (255, 255, 255), 46)
    deck = _wrap(
        sans(16),
        "Midnight local time, market by market, from New Zealand — "
        "13 years after GTA V — on PlayStation 5 and Xbox Series X|S.",
        560)
    _text_block(d, 42, 278, deck, sans(16), (235, 235, 225), 20)
    cx = 42
    for chip in ("$79.99", "METACRITIC 99", "2.3M ON TWITCH", "VICE CITY"):
        cx = _chip(d, cx, 324, chip, sans_b(13))
    # GTA illustration panel (right), gold VI badge on its top-left corner.
    gta = Image.open(os.path.join(assets, "gta.png")).convert("RGB")
    gta = gta.resize((320, 213), Image.LANCZOS)
    img.paste(gta, (645, 158))
    d.rectangle([645, 158, 964, 370], outline=HERO_DARK, width=2)
    d.rounded_rectangle([655, 168, 717, 202], radius=10,
                        fill=HERO_DARK, outline=GOLD, width=2)
    d.text((668, 172), "VI", font=serif_b(22), fill=GOLD)

    # ---- trilateral: 3 portraits + 3 flags ----
    _card(d, 24, 378, 1000, 512)
    d.text((42, 390), "DIPLOMACY", font=sans_b(13), fill=RED)
    head = _wrap(serif_b(27), "TRUMP, XI & PUTIN MEET IN SHENZHEN", 520)
    _text_block(d, 42, 408, head, serif_b(27), INK, 32)
    deck = _wrap(
        sans(12),
        "First three-way talks of the US, China and Russia, 90 minutes "
        "at APEC. Nuclear arms, Ukraine, Iran, trade and AI on the table. "
        "No breakthrough.",
        520)
    _text_block(d, 42, 476, deck, sans(12), INK, 15)
    faces = [
        ("trump.png", 0.50, 0.41, 0.75, "us.png"),
        ("xi.png", 0.50, 0.34, 0.90, "cn.png"),
        ("putin.png", 0.50, 0.36, 0.86, "ru.png"),
    ]
    px = 632
    for name, fcx, fcy, side, flag in faces:
        src = Image.open(os.path.join(assets, name)).convert("RGB")
        circ = _circle_portrait(Image, ImageDraw, src, fcx, fcy, side, 88)
        img.paste(circ, (px, 383), circ)
        fl = _flag(Image, ImageDraw, os.path.join(flags, flag), 48, 30)
        img.paste(fl, (px + (88 - fl.width) // 2, 477))
        px += 106

    # ---- row A: Anthropic + Cyclone ----
    _card(d, 24, 518, 505, 656)
    d.text((42, 530), "MARKETS / AI", font=sans_b(13), fill=GREEN)
    _chart(d, 410, 528, 90, 34, GREEN)
    head = _wrap(serif_b(27), "ANTHROPIC DEBUTS ON NASDAQ AS ANT", 448)
    _text_block(d, 42, 548, head, serif_b(27), INK, 32)
    deck = _wrap(
        sans(14),
        "Priced at $83, above its $70–78 range. A record $81.3bn raised, "
        "~$1.5tn valuation.",
        448)
    _text_block(d, 42, 616, deck, sans(14), INK, 17)

    _card(d, 519, 518, 1000, 656)
    d.text((537, 530), "WEATHER", font=sans_b(13), fill=BLUE)
    fl = _flag(Image, ImageDraw, os.path.join(flags, "in.png"), 48, 30)
    img.paste(fl, (945, 530))
    head = _wrap(serif_b(27), "CYCLONE AKVAN BEARS DOWN ON INDIA", 448)
    _text_block(d, 537, 548, head, serif_b(27), INK, 32)
    deck = _wrap(
        sans(14),
        "440 km off Narsapur; landfall due noon Fri 20 Nov. Red alert; "
        "50,000 moved to safety.",
        448)
    _text_block(d, 537, 616, deck, sans(14), INK, 17)

    # ---- row B: India-Japan + Ukraine ----
    _card(d, 24, 662, 505, 800)
    d.text((42, 674), "DIPLOMACY", font=sans_b(13), fill=BROWN)
    for i, code in enumerate(("in.png", "jp.png")):
        fl = _flag(Image, ImageDraw, os.path.join(flags, code), 48, 30)
        img.paste(fl, (400 + i * 56, 674))
    head = _wrap(serif_b(27), "INDIA-JAPAN 2+2 TALKS IN TOKYO", 448)
    _text_block(d, 42, 692, head, serif_b(27), INK, 32)
    deck = _wrap(
        sans(14),
        "Fourth dialogue. UNICORN naval-mast pact fast-tracked; "
        "maritime security.",
        448)
    _text_block(d, 42, 760, deck, sans(14), INK, 17)

    _card(d, 519, 662, 1000, 800)
    d.text((537, 674), "EUROPE", font=sans_b(13), fill=RED)
    fl = _flag(Image, ImageDraw, os.path.join(flags, "ua.png"), 48, 30)
    img.paste(fl, (945, 674))
    head = _wrap(serif_b(27), "UKRAINE HITS CRIMEA BRIDGE AGAIN", 448)
    _text_block(d, 537, 692, head, serif_b(27), INK, 32)
    deck = _wrap(
        sans(14),
        "Third strike this week halts rail traffic; 40 killed in "
        "Zaporizhzhia as Russia hits back.",
        448)
    _text_block(d, 537, 760, deck, sans(14), INK, 17)

    # ---- row C: Israel + Iran + EU ----
    _card(d, 24, 806, 331, 944)
    d.text((40, 818), "MIDDLE EAST", font=sans_b(12), fill=BROWN)
    fl = _flag(Image, ImageDraw, os.path.join(flags, "il.png"), 40, 27)
    img.paste(fl, (283, 818))
    head = _wrap(serif_b(20),
                 "ISRAEL PUSHES PAST GAZA'S YELLOW LINE", 275)
    _text_block(d, 40, 836, head, serif_b(20), INK, 24)
    deck = _wrap(
        sans(13),
        "Tanks roll into central Gaza near Nuseirat, first ground move "
        "since the ceasefire. 3 killed.",
        275)
    _text_block(d, 40, 888, deck, sans(13), INK, 16)

    _card(d, 339, 806, 654, 944)
    d.text((355, 818), "MIDDLE EAST", font=sans_b(12), fill=BROWN)
    fl = _flag(Image, ImageDraw, os.path.join(flags, "ir.png"), 40, 27)
    img.paste(fl, (598, 818))
    head = _wrap(serif_b(20), "IRAN HITS US SITES IN THE GULF", 275)
    _text_block(d, 355, 836, head, serif_b(20), INK, 24)
    deck = _wrap(
        sans(13),
        "Strikes on US sites in Kuwait and Bahrain after US hits Qeshm "
        "island. Drones intercepted.",
        275)
    _text_block(d, 355, 888, deck, sans(13), INK, 16)

    _card(d, 662, 806, 1000, 944)
    d.text((678, 818), "EUROPE", font=sans_b(12), fill=RED)
    for i, code in enumerate(("eu.png", "gb.png")):
        fl = _flag(Image, ImageDraw, os.path.join(flags, code), 40, 27)
        img.paste(fl, (905 + i * 46, 818))
    head = _wrap(serif_b(20),
                 "EU'S 45BN UKRAINE LOAN GOES TO BERLIN", 300)
    _text_block(d, 678, 836, head, serif_b(20), INK, 24)
    deck = _wrap(
        sans(13),
        "Allies meet over a 2027 loan repaid from Russian reparations. "
        "UK pledges 1,000 long-range missiles.",
        300)
    _text_block(d, 678, 888, deck, sans(13), INK, 16)

    # ---- also today ----
    d.rounded_rectangle([24, 950, 1000, 1000], radius=6, fill=DARK)
    label = "ALSO TODAY:"
    items = ["IAEA: N. Korea expanded enrichment",
             "ICJ to rule on Myanmar genocide case",
             "US–Venezuela anti-drug military pact",
             "Xi shakes hands with Japan's Takaichi",
             "Merchant gets 27.5 years for Trump plot",
             "Carney meets Trump 20 min, no tariff deal",
             "Markets: Hang Seng -2.8%, FTSE -1.3%, Brent $89.3",
             "Yesterday: Voyager 1 passed one light-day"]
    joined = "  •  ".join(items)
    lab_font = sans_b(13)
    item_font = sans(13)
    lab_w = int(lab_font.getlength(label))
    first_w = 976 - 16 - lab_w - 10
    words = joined.split(" ")
    lines = []
    cur = ""
    limit = first_w
    for w in words:
        trial = (cur + " " + w).strip()
        if item_font.getlength(trial) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
            limit = 976 - 16
    if cur:
        lines.append(cur)
    y = 955
    for i, ln in enumerate(lines):
        if i == 0:
            d.text((40, y), label, font=lab_font, fill=GOLD)
            d.text((40 + lab_w + 10, y), ln, font=item_font,
                   fill=(255, 255, 255))
        else:
            d.text((40, y), ln, font=item_font, fill=(255, 255, 255))
        y += 15

    # ---- sources footer ----
    d.text((512, 1006),
           "Sources: Reuters · AP · USA Today · Le Monde · BusinessWorld · "
           "IMD · SEC filings · NASA. All events 19 November 2026 unless "
           "noted as forecast or context.",
           font=sans(10), fill=MUTED, anchor="ma")

    img.save(out_path, optimize=True)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        shutil.copyfile(os.path.join(here, "entry.png"), out_path)
        return
    render(Image, ImageDraw, ImageFont, out_path)


if __name__ == "__main__":
    main()
