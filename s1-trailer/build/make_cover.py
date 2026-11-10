"""Cover image for the trailer Short (1080x1920, key content inside the 3:4 grid crop)."""
import sys, os
sys.path.insert(0, '/home/claude/wigd_build')
import numpy as np, cv2
from PIL import Image
import render_trailer as R

src, out = sys.argv[1], sys.argv[2]
rd = R.Reader(src)
f = rd.get(12.5)
a, b, p = R.SHOTS[4]
p = dict(p, ytop0=0, ytop1=0, h0=996, h1=996, cx=820)
fr = R.crop_frame(f, a, b, p, a)
cv = R.to_pil(fr)
l1 = R.text_img('WOULD YOU OPEN', R.font('Anton-Regular.ttf', 132), colors=[('OPEN', R.AMBER)])
l2 = R.text_img('THE DOOR?', R.font('Anton-Regular.ttf', 132))
R.paste_center(cv, l1, R.W / 2, 330)
R.paste_center(cv, l2, R.W / 2, 475)
tag = R.text_img('HURRICANE BLACKOUT', R.font('Oswald[wght].ttf', 58, 'Bold'), fill=(20, 20, 20), stroke=0, shadow=False)
panel = R.rounded_panel(tag.width + 10, 100, 14, R.AMBER + (255,))
panel.alpha_composite(tag, (5, (100 - tag.height) // 2 + 4))
R.paste_center(cv, panel, R.W / 2, 1600)
cv.convert('RGB').save(out, quality=92)
print('ok')
