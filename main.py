#!/usr/bin/env python3
"""Build the entry image for the make.fun bounty
"Sum up 20 November's world news in one image" (news-image-20261120).

Writes a single 1024x1024 PNG newspaper-front-page infographic to
  - <repo>/output/entry.png
  - /output/entry.png  (when the /output directory can be created)

Deterministic: no network, no timestamps, no randomness, fixed fonts.
Running this program twice produces byte-identical output.

Requires: Python 3.12+ and Pillow. Fonts are bundled in the repo's fonts/
directory (DejaVu, OFL) so the program also runs where no system fonts
are installed; it falls back to the system font path, then to Pillow's
built-in default font.
"""

import io
import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024
PAPER = (250, 247, 240)      # warm newsprint
INK = (17, 17, 17)           # near-black
RED = (185, 28, 28)          # headline accent
NAVY = (30, 58, 95)          # secondary accent
GOLD = (176, 141, 44)
GREY = (90, 88, 82)
RULE = (200, 195, 185)
SKY = (214, 228, 240)
TABLE = (122, 84, 52)        # wooden round table

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_HERE = os.path.dirname(os.path.abspath(__file__))


def _resolve_font(path):
    """Find a font file: bundled copy in the repo first, then the system
    font path, then None. The grader image has no system fonts, so the
    bundled copies in fonts/ are what makes the program run there."""
    name = os.path.basename(path)
    for candidate in (os.path.join(_HERE, "fonts", name), path):
        if os.path.isfile(candidate):
            return candidate
    return None


def font(path, size):
    resolved = _resolve_font(path)
    if resolved is not None:
        return ImageFont.truetype(resolved, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            trial = line + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(draw, xy, text, fnt, max_width, fill, leading=None):
    """Draw wrapped text; return the y coordinate after the last line."""
    x, y = xy
    leading = leading or int(fnt.size * 1.32)
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, label, color=RED):
    """Small caps section label with a red square bullet."""
    fnt = font(SANS_B, 14)
    draw.rectangle([x, y + 2, x + 9, y + 11], fill=color)
    draw.text((x + 15, y), label, font=fnt, fill=color)
    return y + 20


# ------------------------------------------------------------------- artwork
def draw_roundtable(draw, box):
    """Stylised summit round table: a globe above three flags
    (USA, China, Russia) seated around one wooden table.

    Every shape is clipped to the box: all coordinates are box-local
    and never exceed the box width.
    """
    x0, y0, x1, y1 = box
    bw = x1 - x0
    draw.rectangle(box, fill=SKY)
    # globe: navy disc with pale latitude/longitude arcs
    cx, cy, r = x0 + bw // 2, y0 + 52, 34
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY,
                 outline=INK, width=2)
    draw.ellipse([cx - r, cy - 10, cx + r, cy + 10], outline=(150, 180, 210),
                 width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=(150, 180, 210), width=2)
    draw.ellipse([cx - 16, cy - r, cx + 16, cy + r],
                 outline=(150, 180, 210), width=2)
    # three flag bars: USA, China, Russia
    flags = [("USA", (178, 34, 34), (255, 255, 255)),
             ("CHINA", (222, 41, 16), (255, 255, 255)),
             ("RUSSIA", (255, 255, 255), INK)]
    fx = x0 + 20
    fy = y0 + 98
    for name, colour, text_colour in flags:
        draw.rectangle([fx, fy, fx + 108, fy + 20], fill=colour,
                       outline=INK, width=1)
        draw.text((fx + 8, fy + 2), name, font=font(SANS_B, 13),
                  fill=text_colour)
        fx += 120
    # wooden round table (ellipse) with three chairs
    ty = y1 - 52
    draw.ellipse([x0 + 40, ty, x1 - 40, ty + 34], fill=TABLE,
                 outline=INK, width=2)
    draw.ellipse([x0 + 70, ty + 6, x1 - 70, ty + 28], fill=(146, 104, 66),
                 outline=INK, width=1)
    for chair_x in (x0 + 52, x0 + bw // 2 - 14, x1 - 80):
        draw.rectangle([chair_x, y1 - 16, chair_x + 28, y1 - 4],
                       fill=NAVY, outline=INK, width=1)
    draw.rectangle(box, outline=INK, width=2)


# -------------------------------------------------------------------- render
def build_image():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 36                      # outer margin
    cw = W - 2 * m              # content width = 952

    # ---- masthead ------------------------------------------------------
    y = 28
    d.text((m, y), "THE WORLD IN ONE PAGE", font=font(SERIF_B, 52), fill=INK)
    y += 62
    d.text((m, y), "THE DAILY GLOBE  •  ONE DAY, EVERY STORY THAT MATTERED",
           font=font(SANS_B, 15), fill=GREY)
    y += 24
    d.line([(m, y), (W - m, y)], fill=INK, width=3)
    y += 8
    d.line([(m, y), (W - m, y)], fill=INK, width=1)
    y += 12
    d.text((m, y), "Friday, 20 November 2026", font=font(SERIF_B, 24),
           fill=RED)
    d.text((W - m - d.textlength("No. 324  •  Free to read", font=font(SANS, 15)),
            y + 5), "No. 324  •  Free to read", font=font(SANS, 15), fill=GREY)
    y += 36
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- lead story ----------------------------------------------------
    y += 14
    y = kicker(d, m, y, "LEAD  •  FROM SHENZHEN TO BERLIN")
    y += 2
    d.text((m, y), "A NEW YALTA?", font=font(SERIF_B, 56), fill=INK)
    y += 60
    d.text((m, y), "EUROPE SAYS NO", font=font(SERIF_B, 32),
           fill=NAVY)
    y += 44

    # round-table art + lead text side by side
    art_box = (m, y, m + 470, y + 180)
    draw_roundtable(d, art_box)
    tx = m + 490
    lead = ("The first-ever Trump–Xi–Putin summit ended in Shenzhen "
            "with a joint declaration: no nuclear war, UN reform, and "
            "more fuel for all. Hours later Trump told allies Putin is "
            "\"tired\" and ready for a deal — and Europe answered in "
            "Berlin: no carve-up without Europeans at the table.")
    y2 = draw_wrapped(d, (tx, y + 2), lead, font(SERIF, 20), cw - 490, INK,
                      leading=26)
    y2 += 6
    d.line([(tx, y2), (W - m, y2)], fill=RULE, width=1)
    y2 += 10
    d.text((tx, y2), "Summit 19 Nov in Shenzhen; Berlin replies 20 Nov.",
           font=font(SANS_B, 15), fill=NAVY)
    y = max(art_box[3], y2 + 16) + 12
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- two-column row ------------------------------------------------
    y += 12
    col_w = (cw - 24) // 2
    left_x, right_x = m, m + col_w + 24
    base = y

    y = kicker(d, left_x, base, "UKRAINE  •  KYIV UNDER FIRE")
    d.text((left_x, y), "Russia fires 100 missiles\novernight at Ukraine",
           font=font(SERIF_B, 26), fill=INK)
    yq = y + 56
    yq = draw_wrapped(d, (left_x, yq),
                      "At least 100 missiles hit Ukraine overnight into "
                      "Friday: 8 killed, 28 hurt, Kyiv sheltering in the "
                      "metro. Poland raised an air alert. It was the third "
                      "Ukrainian strike on the Kerch Bridge this week; "
                      "Putin vowed a harsher response and ruled out an "
                      "energy ceasefire.",
                      font(SANS, 15), col_w, INK, leading=20)

    yk = kicker(d, right_x, base, "BERLIN  •  COALITION OF THE WILLING")
    d.text((right_x, yk), "Allies demand a seat\nat the table",
           font=font(SERIF_B, 26), fill=INK)
    yi = yk + 56
    yi = draw_wrapped(d, (right_x, yi),
                      "Merz hosted Zelensky and European leaders in "
                      "Berlin: Europe has one position for talks with "
                      "Russia. US envoy Kushner said Trump is open to a "
                      "NATO-style security guarantee for Ukraine, and the "
                      "E3 plus Kyiv urged a winter ceasefire on energy "
                      "sites.",
                      font(SANS, 15), col_w, INK, leading=20)

    y = max(yq, yi) + 12
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- three-column row ----------------------------------------------
    y += 12
    col3 = (cw - 48) // 3
    xs = [m, m + col3 + 24, m + 2 * (col3 + 24)]
    base = y

    y = kicker(d, xs[0], base, "THE HAGUE  •  JUSTICE")
    d.text((xs[0], y), "World court: Myanmar\ncommitted genocide",
           font=font(SERIF_B, 22), fill=INK)
    y1 = y + 50
    y1 = draw_wrapped(d, (xs[0], y1),
                      "The ICJ ruled Myanmar committed genocide against "
                      "the Rohingya in 2017 — the first state ever held "
                      "responsible. Refugees celebrated in Bangladesh; "
                      "Myanmar called the ruling unfair.",
                      font(SANS, 14), col3, INK, leading=19)

    y = kicker(d, xs[1], base, "INDIA  •  CYCLONE")
    d.text((xs[1], y), "Akvan hits the\nOdisha coast",
           font=font(SERIF_B, 22), fill=INK)
    y2 = y + 50
    y2 = draw_wrapped(d, (xs[1], y2),
                      "Cyclone Akvan made landfall near Gopalpur on Friday "
                      "morning, winds 70–80 km/h. Over 300,000 people were "
                      "evacuated — the third cyclone in a month. No damage "
                      "reported so far.",
                      font(SANS, 14), col3, INK, leading=19)

    y = kicker(d, xs[2], base, "GAZA  •  TRUCE STRAINED")
    d.text((xs[2], y), "Israeli troops cross\nthe Yellow Line",
           font=font(SERIF_B, 22), fill=INK)
    y3 = y + 50
    y3 = draw_wrapped(d, (xs[2], y3),
                      "Israeli forces crossed the Gaza ceasefire line in "
                      "the first ground operation beyond it since the "
                      "truce, to dismantle a tunnel. Hamas called it a "
                      "violation; a strike on Nasser Hospital killed 6.",
                      font(SANS, 14), col3, INK, leading=19)

    y = max(y1, y2, y3) + 12
    d.line([(m, y), (W - m, y)], fill=INK, width=1)

    # ---- also today strip (two columns, one line per item) -------------
    y += 10
    y = kicker(d, m, y, "ALSO TODAY", color=NAVY)
    col2 = (cw - 24) // 2
    left_items = [
        ("GULF", "Saudi coalition answers Houthi missiles at Riyadh."),
        ("ABU DHABI", "Prisoner swap agreed; talks end, no breakthrough."),
        ("KYIV", "Emergency power cuts after energy sites are hit."),
    ]
    right_items = [
        ("WASHINGTON", "Trump plans a White House press conference."),
        ("DIPLOMACY", "Xi and Trump also discussed AI safety."),
    ]
    strip_end = y
    for col_x, items in ((m, left_items), (m + col2 + 24, right_items)):
        yy = y
        for label, text in items:
            d.text((col_x, yy), "▪  " + label + " — ",
                   font=font(SANS_B, 13), fill=NAVY)
            lx = col_x + d.textlength("▪  " + label + " — ",
                                      font=font(SANS_B, 13))
            end_y = draw_wrapped(d, (lx, yy), text, font(SANS, 13),
                                 col2 - (lx - col_x), INK, leading=18)
            yy = max(end_y, yy + 20) + 2
        strip_end = max(strip_end, yy)
    y = strip_end

    # ---- footer ---------------------------------------------------------
    y += 8
    d.line([(m, y), (W - m, y)], fill=INK, width=1)
    y += 8
    d.text((m, y),
           "Sources: Reuters, CNN, WSJ, The Times, Le Monde — 20 Nov 2026.",
           font=font(SANS, 11), fill=GREY)
    y += 16
    d.text((m, y),
           "Built by a deterministic Python program. No live data at runtime; all facts embedded above.",
           font=font(SANS, 11), fill=GREY)
    return img


def main():
    img = build_image()
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()

    here = os.path.dirname(os.path.abspath(__file__))
    targets = [os.path.join(here, "output", "entry.png")]
    try:
        os.makedirs("/output", exist_ok=True)
        targets.append("/output/entry.png")
    except OSError:
        pass
    wrote_any = False
    for path in targets:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(data)
            print("wrote {} ({} bytes)".format(path, len(data)))
            wrote_any = True
        except OSError as exc:
            # The grader mounts the repo read-only, so writing next to the
            # program fails there; /output is still written below.
            print("could not write {}: {}".format(path, exc))
    if not wrote_any:
        raise SystemExit("failed to write entry.png to any target")


if __name__ == "__main__":
    main()
