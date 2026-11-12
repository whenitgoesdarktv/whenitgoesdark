"""Thumbnails for the hotel episode (1280x720). Usage: python3 -I make_thumb.py"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
H = os.path.dirname(os.path.abspath(__file__))
FONTS = '/home/claude/wigd_build/fonts'
OUT = os.path.join(H, 'thumb'); os.makedirs(OUT, exist_ok=True)
W, HH = 1920, 1080

def bg(name, zoom=1.0, cx=.5, cy=.5, bright=1.0, tint=None):
    im = Image.open(os.path.join(H, 'art', name + '.png')).convert('RGB')
    w, h = im.size; cw, ch = w / zoom, h / zoom
    x0 = min(max(cx * w - cw / 2, 0), w - cw); y0 = min(max(cy * h - ch / 2, 0), h - ch)
    im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, HH), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(bright)
    if tint:
        a = np.asarray(im).astype(np.float32) * np.array(tint); im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    return im

def char(img, name, x, yb, h, flip=False, dark=1.0, keep=None):
    c = Image.open(os.path.join(H, 'chars', name + '.png')).convert('RGBA')
    c = c.crop(c.getbbox())
    if keep: c = c.crop((0, 0, c.width, int(c.height * keep)))
    s = h / c.height; c = c.resize((int(c.width * s), int(h)), Image.LANCZOS)
    if flip: c = c.transpose(Image.FLIP_LEFT_RIGHT)
    if dark != 1.0:
        r, g, b, a = c.split(); rgb = ImageEnhance.Brightness(Image.merge('RGB', (r, g, b))).enhance(dark); c = Image.merge('RGBA', (*rgb.split(), a))
    # rim glow so the character pops off a dark background
    a = c.split()[3].filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
    glow = Image.new('RGBA', c.size, (255, 200, 120, 0)); glow.putalpha(a.point(lambda v: int(v * 0.55)))
    img.paste(glow, (int(x - c.width / 2), int(yb - c.height)), glow)
    img.paste(c, (int(x - c.width / 2), int(yb - c.height)), c)

def vignette(img, k=0.75):
    yy, xx = np.mgrid[0:HH, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - HH / 2) / (HH / 2)) ** 2)
    v = np.clip(1 - k * np.clip(d - 0.35, 0, 1), 0, 1)[..., None]
    return Image.fromarray((np.asarray(img).astype(np.float32) * v).astype(np.uint8))

def glow_spot(img, x, y, r, color, strength=1.0):
    lay = Image.new('L', (W, HH), 0); ImageDraw.Draw(lay).ellipse((x - r, y - r, x + r, y + r), fill=255)
    lay = lay.filter(ImageFilter.GaussianBlur(r * 0.6))
    a = np.asarray(lay).astype(np.float32)[..., None] / 255 * strength
    out = np.asarray(img).astype(np.float32) + a * np.array(color)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def eyes(img, cx, cy, sep, size):
    for dx in (-sep, sep):
        img = glow_spot(img, cx + dx, cy, size * 2.2, (60, 255, 110), 0.9)
    d = ImageDraw.Draw(img)
    for dx in (-sep, sep):
        d.ellipse((cx + dx - size, cy - size * 0.62, cx + dx + size, cy + size * 0.62), fill=(150, 255, 150))
        d.ellipse((cx + dx - size * 0.16, cy - size * 0.55, cx + dx + size * 0.16, cy + size * 0.55), fill=(10, 30, 10))
    return img

def text(img, lines, x, y, size, colors, anchor='la', stroke=10, gap=0.95):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(os.path.join(FONTS, 'Anton-Regular.ttf'), size)
    for i, (t, col) in enumerate(zip(lines, colors)):
        yy = y + i * size * gap
        # hard drop shadow
        d.text((x + 8, yy + 10), t, font=f, fill=(0, 0, 0), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
        d.text((x, yy), t, font=f, fill=col, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))

def tag(img, t, x, y, size=58, fill=(205, 30, 30)):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(os.path.join(FONTS, 'Anton-Regular.ttf'), size)
    l, tp, r, b = d.textbbox((0, 0), t, font=f)
    pad = 18
    d.rounded_rectangle((x, y, x + r - l + pad * 2, y + b - tp + pad * 2), 12, fill=fill, outline=(0, 0, 0), width=5)
    d.text((x + pad - l, y + pad - tp), t, font=f, fill=(255, 255, 255))

WHITE, AMBER, RED = (255, 255, 255), (255, 181, 71), (255, 70, 60)

# A: the hallway, the vent, the eyes
im = bg('bg01_hallway_dark', 1.25, .5, .62, 1.15)
im = glow_spot(im, 1100, 920, 420, (120, 90, 40), 0.5)          # headlamp pool on the carpet
d = ImageDraw.Draw(im)                                           # floor vent grate
gx, gy, gw, gh = 900, 870, 440, 155
d.rounded_rectangle((gx, gy, gx + gw, gy + gh), 10, fill=(18, 18, 22), outline=(120, 120, 128), width=8)
for i in range(1, 9):
    xx = gx + i * gw / 9; d.line((xx, gy + 10, xx, gy + gh - 10), fill=(110, 110, 118), width=9)
im = eyes(im, 1120, 948, 80, 42)
char(im, 'hero_kneel_vent', 470, 1090, 860, flip=True, dark=1.05)
im = vignette(im, 0.6)
text(im, ["IT'S IN", "THE WALLS"], 1030, 40, 215, [WHITE, AMBER])
tag(im, 'NO POWER  2:47 AM', 1040, 560)
im.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, 'thumb_A_walls.jpg'), quality=92)

# B: the lobby, the generator, the sleepers
im = bg('bg05_lobby_fire', 1.35, .33, .5, 1.05)
im = Image.fromarray(np.asarray(im)); _a = np.asarray(im)[..., ::-1].copy()
import cv2, sys; sys.path.insert(0, H); import render_long as _R
im = Image.fromarray(_R.windows_off(_a, 1.0, exterior=False)[..., ::-1].copy())
im = glow_spot(im, 760, 560, 360, (0, 0, 140), 0.75)              # red menace around the generator
char(im, 'rosa_sleep_couch', 1330, 1085, 640, dark=0.95)
im = vignette(im, 0.55)
text(im, ["DON'T FALL", "ASLEEP"], 60, 40, 220, [WHITE, RED])
tag(im, 'NO POWER', 70, 530)
im.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, 'thumb_B_asleep.jpg'), quality=92)
print('ok')

# C: the hero's face, huge and scared; the generator glowing behind; Lando yowling in the corner
im = bg('bg05_lobby_fire', 2.1, .38, .45, 0.95)
im = glow_spot(im, 700, 560, 420, (0, 10, 150), 0.85)
char(im, 'hero_dizzy', 1330, 1500, 1500, dark=1.05)
char(im, 'lando_yowl', 330, 1080, 380, flip=True, dark=1.0)
im = vignette(im, 0.5)
text(im, ["POISON", "INSIDE"], 60, 40, 230, [WHITE, RED])
tag(im, '9°F OUTSIDE', 70, 520, fill=(30, 90, 200))
im.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, 'thumb_C_poison.jpg'), quality=92)
print('C ok')
