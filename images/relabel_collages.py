"""Russian labels on the collages of chapter 4 that have no source script (collage_mask.png, collage_sparsify.png):
the English labels drawn in the bottom left corner of every 1024x1024 cell are painted over with the black background
and the Russian ones are drawn with the same font (Noto Sans). The painted rectangles do not touch the models.
The original images are in the git history of the report (commit 428c0c0). Usage: python relabel_collages.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = Path.home() / 'repos/papers/Труды ИСП РАН 2026/NotoSans-Regular.ttf'
CELL, SEP = 1024, 10
# image: (x extent of the painted rectangle in the cell, [labels per column, lines bottom to top in the same row])
LABELS = {
    'collage_mask.png': (340, [['без маски', 'реконструкция'], ['с маской', 'реконструкция'], ['референс']]),
    'collage_sparsify.png': (1000, [['(разреживание между эпохами)', 'реконструкция'],
                                    ['(разреживание и в течение эпохи)', 'реконструкция'], ['референс']]),
}
Y0, LINE, SIZE = 893, 58, 44   # top of the painted area in the cell, line pitch, font size (px)


def main():
    font = ImageFont.truetype(str(FONT), SIZE)
    for name, (width, cols) in LABELS.items():
        im = Image.open(OUT / name).convert('RGB')
        dr = ImageDraw.Draw(im)
        rows = (im.height + SEP) // (CELL + SEP)
        for r in range(rows):
            y = r * (CELL + SEP)
            for c, lines in enumerate(cols):
                x = c * (CELL + SEP)
                dr.rectangle((x + 10, y + Y0, x + width, y + CELL - 1), fill='black')
                for k, text in enumerate(lines):
                    dr.text((x + 24, y + CELL - 24 - (k + 1) * LINE), text, font=font, fill='white')
        im.save(OUT / name)
        print('written', OUT / name)


if __name__ == '__main__':
    main()
