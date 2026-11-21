#!/usr/bin/env python3
"""Render the front page for the make.fun bounty
"Sum up 20 November's world news in one image" (news-image-20261120).

The program draws a single 1024x1024 newspaper front page with Pillow
and saves it as a PNG. It touches no network, reads no clock and uses
no randomness, so running it twice yields byte-identical output.

Usage:
    python3 main.py

Outputs:
    output/entry.png        (next to this file)
    /output/entry.png       (when that directory can be created)

The DejaVu fonts are bundled in fonts/ beside this file, which is what
lets the program run on machines with no system fonts installed. When
a bundled copy is absent, the system copy is tried, and finally
Pillow's built-in default font.
"""

import io
import os

from PIL import Image, ImageDraw, ImageFont


# ------------------------------------------------------------------ colours
PALETTE = {
    "paper": (250, 247, 240),    # warm newsprint
    "ink": (17, 17, 17),         # near-black text
    "red": (185, 28, 28),        # lead accent
    "navy": (30, 58, 95),        # secondary accent
    "grey": (90, 88, 82),        # datelines and captions
    "rule": (200, 195, 185),     # hairline separators
    "sky": (214, 228, 240),      # artwork backdrop
    "wood": (122, 84, 52),       # round table
    "wood_light": (146, 104, 66),
    "arc": (150, 180, 210),      # globe arcs
}

FONT_FILES = {
    "serif": "DejaVuSerif.ttf",
    "serif_bold": "DejaVuSerif-Bold.ttf",
    "sans": "DejaVuSans.ttf",
    "sans_bold": "DejaVuSans-Bold.ttf",
}

SYSTEM_FONT_DIR = "/usr/share/fonts/truetype/dejavu"

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 36


class FontBank:
    """Resolve and cache the DejaVu faces the page is drawn with."""

    def __init__(self, base_dir):
        self._base = base_dir
        self._loaded = {}

    def _locate(self, face):
        filename = FONT_FILES[face]
        bundled = os.path.join(self._base, "fonts", filename)
        if os.path.isfile(bundled):
            return bundled
        system = os.path.join(SYSTEM_FONT_DIR, filename)
        if os.path.isfile(system):
            return system
        return None

    def face(self, name, size):
        key = (name, size)
        if key not in self._loaded:
            path = self._locate(name)
            if path is not None:
                self._loaded[key] = ImageFont.truetype(path, size)
            else:
                try:
                    self._loaded[key] = ImageFont.load_default(size=size)
                except TypeError:
                    self._loaded[key] = ImageFont.load_default()
        return self._loaded[key]


def fit_lines(canvas, text, face, width):
    """Greedily wrap `text` to `width`, measuring with `face`.

    Paragraphs are split on newlines first; inside a paragraph words
    are packed into the longest lines that still fit.
    """
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for following in words[1:]:
            joined = current + " " + following
            if canvas.textlength(joined, font=face) <= width:
                current = joined
            else:
                lines.append(current)
                current = following
        lines.append(current)
    return lines


def draw_paragraph(canvas, x, y, text, face, width, colour, leading=None):
    """Draw `text` wrapped to `width` starting at (x, y).

    Returns the y coordinate just below the final line.
    """
    step = leading if leading is not None else int(face.size * 1.32)
    for row in fit_lines(canvas, text, face, width):
        canvas.text((x, y), row, font=face, fill=colour)
        y += step
    return y

# ------------------------------------------------------------------ content
LEAD_BODY = (
    "The first-ever Trump–Xi–Putin summit ended in Shenzhen "
    "with a joint declaration: no nuclear war, UN reform, "
    "and more fuel for all. Hours later Trump told allies "
    "Putin is \"tired\" and ready for a deal — and Europe "
    "answered in Berlin: no carve-up without Europeans at "
    "the table."
)

FRONT_STORIES = [
    {
        "kicker": "UKRAINE  •  KYIV UNDER FIRE",
        "headline": "Russia fires 100 missiles\novernight at Ukraine",
        "body": (
            "At least 100 missiles hit Ukraine overnight into "
            "Friday: 8 killed, 28 hurt, Kyiv sheltering in "
            "the metro. Poland raised an air alert. It was "
            "the third Ukrainian strike on the Kerch Bridge "
            "this week; Putin vowed a harsher response and "
            "ruled out an energy ceasefire."
        ),
    },
    {
        "kicker": "BERLIN  •  COALITION OF THE WILLING",
        "headline": "Allies demand a seat\nat the table",
        "body": (
            "Merz hosted Zelensky and European leaders in "
            "Berlin: Europe has one position for talks with "
            "Russia. US envoy Kushner said Trump is open to "
            "a NATO-style security guarantee for Ukraine, and "
            "the E3 plus Kyiv urged a winter ceasefire on "
            "energy sites."
        ),
    },
]

MID_STORIES = [
    {
        "kicker": "THE HAGUE  •  JUSTICE",
        "headline": "World court: Myanmar\ncommitted genocide",
        "body": (
            "The ICJ ruled Myanmar committed genocide against "
            "the Rohingya in 2017 — the first state ever held "
            "responsible. Refugees celebrated in Bangladesh; "
            "Myanmar called the ruling unfair."
        ),
    },
    {
        "kicker": "INDIA  •  CYCLONE",
        "headline": "Akvan hits the\nOdisha coast",
        "body": (
            "Cyclone Akvan made landfall near Gopalpur on "
            "Friday morning, winds 70–80 km/h. Over 300,000 "
            "people were evacuated — the third cyclone in a "
            "month. No damage reported so far."
        ),
    },
    {
        "kicker": "GAZA  •  TRUCE STRAINED",
        "headline": "Israeli troops cross\nthe Yellow Line",
        "body": (
            "Israeli forces crossed the Gaza ceasefire line "
            "in the first ground operation beyond it since "
            "the truce, to dismantle a tunnel. Hamas called "
            "it a violation; a strike on Nasser Hospital "
            "killed 6."
        ),
    },
]

ALSO_LEFT = [
    ("GULF", "Saudi coalition answers Houthi missiles at Riyadh."),
    ("ABU DHABI", "Prisoner swap agreed; talks end, no breakthrough."),
    ("KYIV", "Emergency power cuts after energy sites are hit."),
]

ALSO_RIGHT = [
    ("WASHINGTON", "Trump plans a White House press conference."),
    ("DIPLOMACY", "Xi and Trump also discussed AI safety."),
]


# --------------------------------------------------------------------- page
class FrontPage:
    """The front page itself: a canvas plus a cursor that walks down it."""

    def __init__(self):
        self.width = PAGE_W
        self.height = PAGE_H
        self.margin = MARGIN
        self.right = self.width - self.margin
        self.span = self.width - 2 * self.margin
        self.sheet = Image.new("RGB", (self.width, self.height),
                               PALETTE["paper"])
        self.cv = ImageDraw.Draw(self.sheet)
        self.fonts = FontBank(os.path.dirname(os.path.abspath(__file__)))
        self.y = 0

    def rule(self, y, weight=1, colour=None):
        """A horizontal rule across the content width at height `y`."""
        self.cv.line([(self.margin, y), (self.right, y)],
                     fill=colour or PALETTE["ink"], width=weight)

    def section_label(self, x, y, text, colour=None):
        """Kicker label: a coloured square bullet plus small-caps text.

        Returns the y coordinate just below the label.
        """
        colour = colour or PALETTE["red"]
        face = self.fonts.face("sans_bold", 14)
        self.cv.rectangle([x, y + 2, x + 9, y + 11], fill=colour)
        self.cv.text((x + 15, y), text, font=face, fill=colour)
        return y + 20

    def masthead(self):
        self.y = 28
        self.cv.text((self.margin, self.y), "THE WORLD IN ONE PAGE",
                     font=self.fonts.face("serif_bold", 52),
                     fill=PALETTE["ink"])
        self.y += 62
        self.cv.text((self.margin, self.y),
                     "THE DAILY GLOBE  •  ONE DAY, EVERY STORY THAT MATTERED",
                     font=self.fonts.face("sans_bold", 15),
                     fill=PALETTE["grey"])
        self.y += 24
        self.rule(self.y, 3)
        self.y += 8
        self.rule(self.y, 1)
        self.y += 12
        self.cv.text((self.margin, self.y), "Friday, 20 November 2026",
                     font=self.fonts.face("serif_bold", 24),
                     fill=PALETTE["red"])
        issue = "No. 324  •  Free to read"
        issue_face = self.fonts.face("sans", 15)
        issue_width = self.cv.textlength(issue, font=issue_face)
        self.cv.text((self.right - issue_width, self.y + 5), issue,
                     font=issue_face, fill=PALETTE["grey"])
        self.y += 36
        self.rule(self.y, 1)

    def lead_story(self):
        self.y += 14
        self.y = self.section_label(
            self.margin, self.y, "LEAD  •  FROM SHENZHEN TO BERLIN")
        self.y += 2
        self.cv.text((self.margin, self.y), "A NEW YALTA?",
                     font=self.fonts.face("serif_bold", 56),
                     fill=PALETTE["ink"])
        self.y += 60
        self.cv.text((self.margin, self.y), "EUROPE SAYS NO",
                     font=self.fonts.face("serif_bold", 32),
                     fill=PALETTE["navy"])
        self.y += 44
        art = (self.margin, self.y, self.margin + 470, self.y + 180)
        self.summit_art(art)
        text_x = self.margin + 490
        end = draw_paragraph(self.cv, text_x, self.y + 2, LEAD_BODY,
                             self.fonts.face("serif", 20),
                             self.span - 490, PALETTE["ink"], leading=26)
        end += 6
        self.cv.line([(text_x, end), (self.right, end)],
                     fill=PALETTE["rule"], width=1)
        end += 10
        self.cv.text((text_x, end),
                     "Summit 19 Nov in Shenzhen; Berlin replies 20 Nov.",
                     font=self.fonts.face("sans_bold", 15),
                     fill=PALETTE["navy"])
        self.y = max(art[3], end + 16) + 12
        self.rule(self.y, 1)

    def summit_art(self, box):
        """Stylised summit scene: a globe, three flags, one round table."""
        x0, y0, x1, y1 = box
        width = x1 - x0
        cv = self.cv
        cv.rectangle(box, fill=PALETTE["sky"])
        cx = x0 + width // 2
        cy = y0 + 52
        r = 34
        cv.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=PALETTE["navy"], outline=PALETTE["ink"], width=2)
        cv.ellipse([cx - r, cy - 10, cx + r, cy + 10],
                   outline=PALETTE["arc"], width=2)
        cv.line([cx, cy - r, cx, cy + r], fill=PALETTE["arc"], width=2)
        cv.ellipse([cx - 16, cy - r, cx + 16, cy + r],
                   outline=PALETTE["arc"], width=2)
        flags = [
            ("USA", (178, 34, 34), (255, 255, 255)),
            ("CHINA", (222, 41, 16), (255, 255, 255)),
            ("RUSSIA", (255, 255, 255), PALETTE["ink"]),
        ]
        fx = x0 + 20
        fy = y0 + 98
        for name, paint, letter in flags:
            cv.rectangle([fx, fy, fx + 108, fy + 20], fill=paint,
                         outline=PALETTE["ink"], width=1)
            cv.text((fx + 8, fy + 2), name,
                    font=self.fonts.face("sans_bold", 13), fill=letter)
            fx += 120
        top = y1 - 52
        cv.ellipse([x0 + 40, top, x1 - 40, top + 34],
                   fill=PALETTE["wood"], outline=PALETTE["ink"], width=2)
        cv.ellipse([x0 + 70, top + 6, x1 - 70, top + 28],
                   fill=PALETTE["wood_light"], outline=PALETTE["ink"],
                   width=1)
        for seat in (x0 + 52, x0 + width // 2 - 14, x1 - 80):
            cv.rectangle([seat, y1 - 16, seat + 28, y1 - 4],
                         fill=PALETTE["navy"], outline=PALETTE["ink"],
                         width=1)
        cv.rectangle(box, outline=PALETTE["ink"], width=2)

    def story_column(self, x, y, width, story, headline_size,
                     body_size, body_leading, body_gap):
        """One kicker + headline + body column; returns the y below it."""
        head_y = self.section_label(x, y, story["kicker"])
        self.cv.text((x, head_y), story["headline"],
                     font=self.fonts.face("serif_bold", headline_size),
                     fill=PALETTE["ink"])
        return draw_paragraph(self.cv, x, head_y + body_gap, story["body"],
                              self.fonts.face("sans", body_size), width,
                              PALETTE["ink"], leading=body_leading)

    def two_column_row(self):
        self.y += 12
        col_w = (self.span - 24) // 2
        base = self.y
        left_end = self.story_column(self.margin, base, col_w,
                                     FRONT_STORIES[0], 26, 15, 20, 56)
        right_end = self.story_column(self.margin + col_w + 24, base, col_w,
                                      FRONT_STORIES[1], 26, 15, 20, 56)
        self.y = max(left_end, right_end) + 12
        self.rule(self.y, 1)

    def three_column_row(self):
        self.y += 12
        col_w = (self.span - 48) // 3
        base = self.y
        ends = []
        for i, story in enumerate(MID_STORIES):
            x = self.margin + i * (col_w + 24)
            ends.append(self.story_column(x, base, col_w, story,
                                          22, 14, 19, 50))
        self.y = max(ends) + 12
        self.rule(self.y, 1)

    def also_today(self):
        self.y += 10
        self.y = self.section_label(self.margin, self.y, "ALSO TODAY",
                                    colour=PALETTE["navy"])
        col_w = (self.span - 24) // 2
        strip_bottom = self.y
        for col_x, entries in ((self.margin, ALSO_LEFT),
                               (self.margin + col_w + 24, ALSO_RIGHT)):
            yy = self.y
            for tag, text in entries:
                prefix = "▪  " + tag + " — "
                tag_face = self.fonts.face("sans_bold", 13)
                self.cv.text((col_x, yy), prefix, font=tag_face,
                             fill=PALETTE["navy"])
                text_x = col_x + self.cv.textlength(prefix, font=tag_face)
                end = draw_paragraph(self.cv, text_x, yy, text,
                                     self.fonts.face("sans", 13),
                                     col_w - (text_x - col_x),
                                     PALETTE["ink"], leading=18)
                yy = max(end, yy + 20) + 2
            strip_bottom = max(strip_bottom, yy)
        self.y = strip_bottom

    def footer(self):
        self.y += 8
        self.rule(self.y, 1)
        self.y += 8
        self.cv.text((self.margin, self.y),
                     "Sources: Reuters, CNN, WSJ, The Times, Le Monde — 20 Nov 2026.",
                     font=self.fonts.face("sans", 11), fill=PALETTE["grey"])
        self.y += 16
        self.cv.text((self.margin, self.y),
                     "Built by a deterministic Python program. No live data at runtime; all facts embedded above.",
                     font=self.fonts.face("sans", 11), fill=PALETTE["grey"])

    def render(self):
        self.masthead()
        self.lead_story()
        self.two_column_row()
        self.three_column_row()
        self.also_today()
        self.footer()
        return self.sheet


# --------------------------------------------------------------------- main
def build_image():
    """Compose the front page and return the finished image."""
    return FrontPage().render()


def write_png(data):
    """Write the PNG bytes beside this file and to /output if possible."""
    here = os.path.dirname(os.path.abspath(__file__))
    targets = [os.path.join(here, "output", "entry.png")]
    try:
        os.makedirs("/output", exist_ok=True)
        targets.append("/output/entry.png")
    except OSError:
        pass
    saved = False
    for target in targets:
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as handle:
                handle.write(data)
            print("wrote {} ({} bytes)".format(target, len(data)))
            saved = True
        except OSError as err:
            # The grader mounts the repo read-only, so the first target
            # fails there; /output is still written.
            print("could not write {}: {}".format(target, err))
    return saved


def main():
    sheet = build_image()
    buffer = io.BytesIO()
    sheet.save(buffer, format="PNG", optimize=True)
    if not write_png(buffer.getvalue()):
        raise SystemExit("failed to write entry.png to any target")


if __name__ == "__main__":
    main()
