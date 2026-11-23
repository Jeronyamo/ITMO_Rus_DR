"""Collages of reconstruction examples for chapter 4 (collage1.png, collage2.png): reference, reconstruction after the
last epoch with the PSNR of this view, and the difference (blue: reconstruction brighter, red: darker, contrast x12).

Data: run of scripts/run_sparsedr_measurements.sh in LiteRT (~/repos/DRMeasureFinal: <scene>/ref/ref_<view>.png,
<scene>/res/ep7_res_<view>.png) and its log with the per-view PSNR of the final evaluation.
Usage: python make_collages.py [run_dir] [log]
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RUN = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / 'repos/DRMeasureFinal')
LOG = Path(sys.argv[2] if len(sys.argv) > 2 else
           Path.home() / 'repos/papers/Труды ИСП РАН 2026/sparsedr_out_2026-11-final.txt')
FONT = Path.home() / 'repos/papers/Труды ИСП РАН 2026/NotoSans-Regular.ttf'
OUT = Path(__file__).resolve().parent
# (model, view) per collage: the views of the previous version of the collages
COLLAGES = {'collage1.png': [('Armadillo', 1), ('Bunny', 10), ('Happy', 0), ('Nefertiti', 4)],
            'collage2.png': [('Demogorgon', 10), ('Doom', 0), ('Helicopter', 0), ('Pufferfish', 0)]}
CELL, SEP, K = 1024, 10, 12.0


def final_view_psnr(log):
    """{scene: [PSNR per training view]} of the last evaluation on the training views of every scene."""
    res, cur, cams = {}, None, []
    for line in log.read_text(errors='replace').splitlines():
        line = re.sub(r'\x1b\[[0-9;]*m', '', line)
        if line.startswith('Optimizing scene:'):
            cur = line.split()[-1]
        elif (m := re.match(r'Camera (\d+): PSNR = ([\d.]+)', line)):
            cams.append(float(m.group(2)))
        elif line.startswith('Average PSNR'):
            if 'res_novel' not in line:
                res[cur] = cams
            cams = []
    return res


def diff_image(ref, rec):
    d = rec.astype(float).mean(2) - ref.astype(float).mean(2)
    v = np.clip(K * np.abs(d), 0, 255)
    out = np.full(d.shape + (3,), 255.0)
    pos, neg = d > 0, d < 0
    out[pos, 0] -= v[pos]; out[pos, 1] -= v[pos]   # blue
    out[neg, 1] -= v[neg]; out[neg, 2] -= v[neg]   # red
    return out.astype(np.uint8)


def main():
    psnr = final_view_psnr(LOG)
    font = ImageFont.truetype(str(FONT), 72)
    for name, items in COLLAGES.items():
        canvas = Image.new('RGB', (3 * CELL + 2 * SEP, len(items) * CELL + (len(items) - 1) * SEP), 'white')
        for r, (model, view) in enumerate(items):
            scene = model + 'NewLong'
            run, ps = RUN, psnr
            ref = np.array(Image.open(run / scene / 'ref' / f'ref_{view}.png').convert('RGB').resize((CELL, CELL)))
            rec = np.array(Image.open(run / scene / 'res' / f'ep7_res_{view}.png').convert('RGB').resize((CELL, CELL)))
            y = r * (CELL + SEP)
            for c, img in enumerate((ref, rec, diff_image(ref, rec))):
                canvas.paste(Image.fromarray(img), (c * (CELL + SEP), y))
            dr = ImageDraw.Draw(canvas)
            kw = dict(font=font, fill='white', stroke_width=3, stroke_fill='black')
            dr.text((24, y + CELL - 100), 'референс', **kw)
            dr.text((CELL + SEP + 24, y + CELL - 190), 'реконструкция', **kw)
            dr.text((CELL + SEP + 24, y + CELL - 100), f'PSNR {ps[scene][view]:.1f} дБ'.replace('.', ','), **kw)
            print(name, model, view, ps[scene][view])
        canvas.save(OUT / name)


if __name__ == '__main__':
    main()
