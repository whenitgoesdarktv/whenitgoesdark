"""When It Goes Dark: Season 1 trailer Short (9:16) cut from the full story.

Usage: python3 -I render_trailer.py <source.mp4> <out_video_noaudio.mp4> <variant: yt|social> [--preview T1,T2,...]
"""
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'fonts')
W, H, FPS = 1080, 1920, 30
AMBER = (255, 181, 71)
WHITE = (255, 255, 255)
BG = (10, 12, 18)
VALID_Y = 893          # source rows below this hold the old burned-in captions
CAP_Y = 1380           # caption centre line in the output

def font(name, size, var=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if var:
        f.set_variation_by_name(var)
    return f

F_CAP = font('Oswald[wght].ttf', 86, 'Bold')
F_HOOK = font('Anton-Regular.ttf', 104)
F_TAG = font('Oswald[wght].ttf', 54, 'Bold')
F_BTN = font('Anton-Regular.ttf', 120)
F_SUB = font('Barlow-SemiBold.ttf', 40)
F_Q = font('Oswald[wght].ttf', 50, 'Bold')
F_END_BIG = font('Anton-Regular.ttf', 132)
F_END_BOX = font('Anton-Regular.ttf', 66)
F_END_SMALL = font('Barlow-SemiBold.ttf', 40)
F_LANDO = font('Anton-Regular.ttf', 58)
F_PILL = font('Anton-Regular.ttf', 64)

# ---------------------------------------------------------------- timeline
# (out_start, out_end, src_offset): src_time = out_time + src_offset
SEGMENTS = [
    (0.00, 20.45, 0.0),       # cold open
    (20.45, 23.80, 12.50),    # M1: every light in the city goes out at once (src 32.95-36.30)
    (23.80, 28.60, 185.70),   # M2: every phone screams, tornado warning (src 209.50-214.30)
    (28.60, 32.40, 276.20),   # M3: someone is watching you (src 304.80-308.60)
]
END_START, END_END = 32.40, 36.40
TOTAL = END_END
CHOICE_START, CHOICE_END = 18.03, 20.45
TIMER_END = 20.22
LIGHTS_OUT = 35.76 - 12.50    # out time of "once."
DARK_SRC = 38.30              # clean dark-city frames start here in the source

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

# Shots: (out_start, out_end, dict(cx, h0, h1, ytop0/ytop1 or bottom, fill_below))
# rect width = h*9/16. Either 'bottom' (rect bottom row, kept fixed) or 'ytop'.
SHOTS = [
    (0.00, 4.50,  dict(cx=1170, h0=893, h1=840, bottom=VALID_Y)),            # cellar doors
    (4.50, 7.20,  dict(cx=1640, h0=996, h1=960, ytop0=380, ytop1=400, fill=1080)),  # neighbor's face
    (7.20, 9.47,  dict(cx=1300, h0=893, h1=760, bottom=VALID_Y)),            # doors, "let me in"
    (9.47, 11.97, dict(cx=1210, h0=893, h1=850, bottom=VALID_Y)),            # hands on the handle
    (11.97, 14.43, dict(cx=790, h0=996, h1=960, ytop0=160, ytop1=170, fill=VALID_Y)),  # Lando shaking
    (14.43, 18.03, dict(cx=940, h0=893, h1=820, bottom=VALID_Y)),           # tornado
    (18.03, 20.45, dict(cx=1640, h0=996, h1=996, ytop0=380, ytop1=380, fill=1080, choice=True)),
    (20.45, LIGHTS_OUT, dict(cx=975, h0=893, h1=800, bottom=VALID_Y)),       # lit city
    (LIGHTS_OUT, 23.80, dict(cx=945, h0=760, h1=720, bottom=VALID_Y, dark=True)),  # dark city
    (23.80, 28.60, dict(cx=1517, h0=798, h1=730, ytop0=95, ytop1=110)),      # phone alert
    (28.60, 32.40, dict(cx=958, h0=893, h1=800, bottom=VALID_Y)),            # farmhouse window
]

# ---------------------------------------------------------------- captions
import json
WORDS = [x for x in json.load(open(os.path.join(HERE, 'words_full.json')))['words'] if x['type'] == 'word']

def words_in(a, b):
    return [x for x in WORDS if a - 0.01 <= x['start'] <= b]

def clean(t):
    return t.replace('"', '').replace('“', '').replace('”', '').upper()

# chunks per segment: list of (n_words, key_word)
CHUNK_PLAN = [
    (0.0, 20.30, [(2, 'KNOCKS'), (4, 'CELLAR'), (4, 'VOICE'), (4, 'HEAD'), (1, 'PLEASE'), (3, 'IN'),
                  (2, 'NEIGHBOR'), (3, 'HANDS'), (3, 'HANDLE'), (4, 'SHAKING'), (3, 'CARRIER'),
                  (2, 'SOMEWHERE'), (4, 'DARK'), (2, 'STORM'), (2, 'FINISHED'), (3, 'ABOUT'),
                  (2, 'SECONDS'), (2, 'DECIDE')], 0.0),
    (32.95, 36.10, [(2, 'THEN'), (2, 'LIGHT'), (3, 'CITY'), (2, 'OUT'), (2, 'ONCE')], 12.50),
    (209.50, 214.10, [(3, 'PHONE'), (3, 'CAR'), (3, 'SCREAMS'), (2, 'WARNING')], 185.70),
    (304.80, 308.40, [(2, 'SOMEONE'), (2, 'WATCHING'), (3, 'THEY'), (2, 'NOT'), (2, 'DOOR')], 276.20),
]

CHUNKS = []   # dict(words=[(text,start_out)], key, start, end)
for a, b, plan, off in CHUNK_PLAN:
    ws = words_in(a, b)
    assert sum(n for n, _ in plan) == len(ws), (a, len(ws), sum(n for n, _ in plan), [w['text'] for w in ws])
    i = 0
    for n, key in plan:
        part = ws[i:i + n]; i += n
        CHUNKS.append(dict(words=[(clean(w['text']), w['start'] - off) for w in part], key=key,
                           start=part[0]['start'] - off, last_end=part[-1]['end'] - off))
for j, c in enumerate(CHUNKS):
    nxt = CHUNKS[j + 1]['start'] if j + 1 < len(CHUNKS) else 1e9
    c['end'] = min(nxt, c['last_end'] + 0.45)
# never let a caption cross a segment boundary
bounds = [s[1] for s in SEGMENTS]
for c in CHUNKS:
    for bd in bounds:
        if c['start'] < bd < c['end']:
            c['end'] = bd

_cap_cache = {}
def caption_img(ci, n):
    k = (ci, n)
    if k in _cap_cache:
        return _cap_cache[k]
    c = CHUNKS[ci]
    words = [w for w, _ in c['words']]
    sp = F_CAP.getlength(' ')
    widths = [F_CAP.getlength(w) for w in words]
    total = sum(widths) + sp * (len(words) - 1)
    pad = 40
    img = Image.new('RGBA', (int(total) + pad * 2, 160), (0, 0, 0, 0))
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img); ds = ImageDraw.Draw(shadow)
    x = pad
    for idx, w in enumerate(words):
        if idx < n:
            col = AMBER if w.strip('.,?!:').replace("'", "") == c['key'].replace("'", "") else WHITE
            ds.text((x + 4, 30 + 6), w, font=F_CAP, fill=(0, 0, 0, 200), stroke_width=7, stroke_fill=(0, 0, 0, 200))
            d.text((x, 30), w, font=F_CAP, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
        x += widths[idx] + sp
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    out = Image.alpha_composite(shadow, img)
    _cap_cache[k] = (out, total)
    return _cap_cache[k]

def caption_at(t):
    for ci, c in enumerate(CHUNKS):
        if c['start'] <= t < c['end']:
            n = sum(1 for _, s in c['words'] if s <= t + 0.02)
            n = max(n, 1)
            img, total = caption_img(ci, n)
            pop = 1.0 + 0.08 * (1 - ease((t - c['start']) / 0.12))
            return img, total, pop
    return None

# ---------------------------------------------------------------- drawing helpers
def text_img(txt, f, fill=WHITE, stroke=6, shadow=True, colors=None):
    """colors: optional list of (substring, colour) applied word-wise."""
    words = txt.split(' ')
    sp = f.getlength(' ')
    widths = [f.getlength(w) for w in words]
    total = sum(widths) + sp * (len(words) - 1)
    asc, desc = f.getmetrics()
    pad = 30
    img = Image.new('RGBA', (int(total) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img); ds = ImageDraw.Draw(sh)
    x = pad
    for w, wd in zip(words, widths):
        col = fill
        if colors:
            for sub, cc in colors:
                if sub in w:
                    col = cc
        if shadow:
            ds.text((x + 4, pad + 6), w, font=f, fill=(0, 0, 0, 210), stroke_width=stroke + 1, stroke_fill=(0, 0, 0, 210))
        d.text((x, pad), w, font=f, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += wd + sp
    if shadow:
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        img = Image.alpha_composite(sh, img)
    return img

def paste_center(canvas, img, cx, cy, alpha=1.0, scale=1.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
    if alpha < 1.0:
        a = img.getchannel('A').point(lambda v: int(v * alpha))
        img = img.copy(); img.putalpha(a)
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

def rounded_panel(w, h, r, fill, outline=None, width=0):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=fill, outline=outline, width=width)
    return im

# ---------------------------------------------------------------- source frames
SR = cv2.dnn_superres.DnnSuperResImpl_create()
SR.readModel(os.path.join(HERE, 'FSRCNN_x4.pb'))
SR.setModel('fsrcnn', 4)

class Reader:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path); self.pos = None; self.last = None
    def get(self, t):
        fi = int(round(t * FPS))
        if self.pos is None or fi < self.pos or fi > self.pos + 45:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, fi); self.pos = fi
            ok, self.last = self.cap.read(); self.pos = fi + 1
            return self.last
        while self.pos <= fi:
            ok, f = self.cap.read()
            if not ok:
                break
            self.last = f; self.pos += 1
        return self.last

def shot_for(t):
    for a, b, p in SHOTS:
        if a <= t < b:
            return a, b, p
    return SHOTS[-1]

def crop_frame(src, a, b, p, t):
    u = ease((t - a) / max(b - a, 1e-6))
    h = p['h0'] + (p['h1'] - p['h0']) * u
    w = h * 9 / 16
    if 'bottom' in p:
        y0 = p['bottom'] - h
    else:
        y0 = p['ytop0'] + (p['ytop1'] - p['ytop0']) * u
    x0 = p['cx'] - w / 2
    img = src.copy()
    fill = p.get('fill')
    if fill is not None and fill <= img.shape[0]:
        # fade the last 70 valid rows to the background colour, blank everything below
        g = 70
        ramp = np.linspace(1, 0, g, dtype=np.float32)[:, None, None]
        bgc = np.array(BG[::-1], np.float32)
        seg = img[fill - g:fill].astype(np.float32)
        img[fill - g:fill] = (seg * ramp + bgc * (1 - ramp)).astype(np.uint8)
        img[fill:] = bgc.astype(np.uint8)
    # pad so rectangles that run past the frame edge pick up the background colour
    pad = 400
    big = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=BG[::-1])
    xi, yi = int(math.floor(x0)) + pad, int(math.floor(y0)) + pad
    wi, hi = int(math.ceil(w)) + 2, int(math.ceil(h)) + 2
    patch = big[yi:yi + hi, xi:xi + wi]
    up = SR.upsample(patch)  # x4
    s = 4.0
    fx, fy = (x0 + pad - xi) * s, (y0 + pad - yi) * s
    scale = W / (w * s)
    M = np.array([[scale, 0, -fx * scale], [0, scale, -fy * scale]], np.float32)
    out = cv2.warpAffine(up, M, (W, H), flags=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=BG[::-1])
    return out

def to_pil(bgr):
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).convert('RGBA')

# ---------------------------------------------------------------- overlays
HOOK = text_img('WOULD YOU OPEN', F_HOOK, colors=[('OPEN', AMBER)])
HOOK2 = text_img('THE DOOR?', F_HOOK)
TAG = None

def draw_hook(cv, t):
    if t >= 4.45:
        return
    a = ease(t / 0.25) * (1 - ease((t - 4.2) / 0.25))
    s = 1.0 + 0.05 * (1 - ease(t / 0.3))
    paste_center(cv, HOOK, W / 2, 300, a, s)
    paste_center(cv, HOOK2, W / 2, 420, a, s)

def draw_tag(cv, t, start, txt):
    dt = t - start
    if dt < 0 or dt > 1.9:
        return
    a = ease(dt / 0.15) * (1 - ease((dt - 1.65) / 0.25))
    timg = text_img(txt, F_TAG, fill=(20, 20, 20), stroke=0, shadow=False)
    bw, bh = timg.width + 10, 96
    panel = rounded_panel(bw, bh, 14, AMBER + (255,))
    panel.alpha_composite(timg, (5, (bh - timg.height) // 2 + 4))
    paste_center(cv, panel, W / 2, 330, a)

def draw_choice(cv, t, timer=True, buttons_y=(790, 1060)):
    dt = t - CHOICE_START
    q = text_img('WHAT WOULD YOU DO?', F_Q, fill=AMBER, stroke=4)
    paste_center(cv, q, W / 2, 610, ease(dt / 0.2))
    for i, (lab, sub) in enumerate([('OPEN', 'let him in'), ('WAIT', 'keep the doors shut')]):
        k = ease((dt - 0.08 * i) / 0.22)
        panel = rounded_panel(720, 240, 28, (12, 16, 26, 225), outline=(255, 255, 255, 235), width=5)
        d = ImageDraw.Draw(panel)
        lw = F_BTN.getlength(lab)
        d.text(((720 - lw) / 2, 18), lab, font=F_BTN, fill=WHITE)
        sw = F_SUB.getlength(sub)
        d.text(((720 - sw) / 2, 182), sub, font=F_SUB, fill=(190, 196, 210))
        paste_center(cv, panel, W / 2, buttons_y[i] + 30 * (1 - k), k, 0.92 + 0.08 * k)
    if timer:
        frac = 1 - min(max((t - CHOICE_START) / (TIMER_END - CHOICE_START), 0), 1)
        bar = Image.new('RGBA', (720, 16), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bar)
        bd.rounded_rectangle([0, 0, 719, 15], 8, fill=(255, 255, 255, 60))
        if frac > 0:
            bd.rounded_rectangle([0, 0, max(16, int(719 * frac)), 15], 8, fill=AMBER + (255,))
        paste_center(cv, bar, W / 2, 1235, ease(dt / 0.2))

# ---------------------------------------------------------------- end card
def build_end_bg(reader):
    f = reader.get(1.25)
    a, b, p = SHOTS[0]
    bg = crop_frame(f, a, b, dict(p, h1=p['h0']), a)
    bg = cv2.GaussianBlur(bg, (0, 0), 18)
    bg = (bg.astype(np.float32) * 0.42).astype(np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.55 * (((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H * 0.45) / (H * 0.65)) ** 2)
    bg = (bg.astype(np.float32) * np.clip(vig, 0.25, 1)[..., None]).astype(np.uint8)
    return bg

def build_lando(reader):
    f = reader.get(596.0)
    ph = f[150:650, 170:675]
    ph = cv2.resize(ph, (300, 297), interpolation=cv2.INTER_AREA)
    im = Image.fromarray(cv2.cvtColor(ph, cv2.COLOR_BGR2RGB)).convert('RGBA')
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 26, fill=255)
    im.putalpha(mask)
    frame = rounded_panel(im.width + 12, im.height + 12, 32, AMBER + (255,))
    frame.alpha_composite(im, (6, 6))
    return frame

def draw_end(cv, t, variant, lando):
    dt = t - END_START
    def k(d0, dur=0.3):
        return ease((dt - d0) / dur)
    l1 = text_img('WOULD YOU OPEN', F_END_BIG, colors=[('OPEN', AMBER)])
    l2 = text_img('THE DOOR?', F_END_BIG)
    paste_center(cv, l1, W / 2, 330 + 20 * (1 - k(0)), k(0))
    paste_center(cv, l2, W / 2, 470 + 20 * (1 - k(0.05)), k(0.05))
    # one-word answer pills
    for i, lab in enumerate(['OPEN', 'WAIT']):
        pill = rounded_panel(300, 120, 60, (12, 16, 26, 230), outline=(255, 255, 255, 230), width=5)
        d = ImageDraw.Draw(pill)
        lw = F_PILL.getlength(lab)
        d.text(((300 - lw) / 2, 14), lab, font=F_PILL, fill=WHITE)
        paste_center(cv, pill, W / 2 + (-170 if i == 0 else 170), 650, k(0.2 + 0.06 * i))
    c1 = text_img('Comment one word', F_END_SMALL, fill=(215, 220, 230), stroke=0)
    paste_center(cv, c1, W / 2, 760, k(0.3))
    # full video box
    box_txt = 'FULL VIDEO ON THE CHANNEL' if variant == 'yt' else 'FULL 10-MIN VIDEO ON YOUTUBE'
    bt = text_img(box_txt, F_END_BOX, fill=(14, 14, 18), stroke=0, shadow=False)
    box = rounded_panel(bt.width + 50, 132, 22, AMBER + (255,))
    box.alpha_composite(bt, (25, (132 - bt.height) // 2 + 4))
    pulse = 1.0 + 0.025 * math.sin(max(dt - 0.8, 0) * 5.0)
    paste_center(cv, box, W / 2, 935, k(0.45), (0.94 + 0.06 * k(0.45)) * pulse)
    s2 = text_img('Hurricane Blackout Survival: 30 Hours', font('Barlow-SemiBold.ttf', 38), fill=(205, 210, 222), stroke=0)
    paste_center(cv, s2, W / 2, 1040, k(0.55))
    if variant != 'yt':
        s3 = text_img('@WhenItGoesDarkTV', font('Barlow-SemiBold.ttf', 38), fill=AMBER, stroke=0)
        paste_center(cv, s3, W / 2, 1092, k(0.6))
    # real Lando
    lx, ly = 300, 1270 if variant == 'yt' else 1310
    paste_center(cv, lando, lx, ly, k(0.75))
    t1 = text_img('THE REAL LANDO', F_LANDO, fill=AMBER, stroke=0)
    t2 = text_img("Don't worry, he's OK.", font('Barlow-SemiBold.ttf', 44), fill=WHITE, stroke=0)
    cv.alpha_composite(_fade(t1, k(0.85)), (lx + 150, ly - 95))
    cv.alpha_composite(_fade(t2, k(0.9)), (lx + 150, ly - 15))

def _fade(img, a):
    if a >= 1:
        return img
    im = img.copy(); im.putalpha(img.getchannel('A').point(lambda v: int(v * a))); return im

# ---------------------------------------------------------------- main
def render(src_path, out_path, variant, preview=None):
    rd = Reader(src_path)
    rd_dark = Reader(src_path)
    end_bg = build_end_bg(Reader(src_path))
    lando = build_lando(Reader(src_path))
    choice_bg = None
    times = preview if preview else [i / FPS for i in range(int(round(TOTAL * FPS)))]
    proc = None
    if not preview:
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                                 '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15',
                                 '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_path], stdin=subprocess.PIPE)
    for n, t in enumerate(times):
        if t >= END_START:
            base = end_bg.copy()
            cv = to_pil(base)
            draw_end(cv, t, variant, lando)
            fade_in = ease((t - END_START) / 0.15)
            arr = np.array(cv.convert('RGB')).astype(np.float32) * (0.15 + 0.85 * fade_in)
            frame = arr.astype(np.uint8)
        else:
            a, b, p = shot_for(t)
            seg_off = [s for s in SEGMENTS if s[0] <= t < s[1]][0][2]
            if p.get('choice'):
                if choice_bg is None:
                    f = rd.get(6.0)
                    bg = crop_frame(f, *SHOTS[1][:2], SHOTS[1][2], 6.0)
                    bg = cv2.GaussianBlur(bg, (0, 0), 14)
                    choice_bg = (bg.astype(np.float32) * 0.45).astype(np.uint8)
                src_frame = choice_bg.copy()
            elif p.get('dark'):
                f = rd_dark.get(DARK_SRC + (t - a))
                src_frame = crop_frame(f, a, b, p, t)
            else:
                f = rd.get(t + seg_off)
                src_frame = crop_frame(f, a, b, p, t)
            cv = to_pil(src_frame)
            draw_hook(cv, t)
            draw_tag(cv, t, 20.45, '20 HOURS EARLIER')
            if p.get('choice'):
                draw_choice(cv, t)
            cap = caption_at(t)
            if cap:
                img, total, pop = cap
                paste_center(cv, img, W / 2, CAP_Y, 1.0, pop)
            frame = np.array(cv.convert('RGB'))
            # flashes: segment cuts into the montage, and the lights going out
            flash = 0.0
            for ft, strength in [(20.45, 0.55), (23.80, 0.45), (28.60, 0.45)]:
                if 0 <= t - ft < 0.1:
                    flash = max(flash, strength * (1 - (t - ft) / 0.1))
            if 0 <= t - LIGHTS_OUT < 0.13:
                flash = max(flash, 0.8 * (1 - (t - LIGHTS_OUT) / 0.13))
            if flash > 0:
                frame = (frame.astype(np.float32) * (1 - flash) + 255 * flash).astype(np.uint8)
            # fade the very last frames of the montage to black before the end card
            if END_START - 0.12 <= t < END_START:
                k = (END_START - t) / 0.12
                frame = (frame.astype(np.float32) * (0.25 + 0.75 * k)).astype(np.uint8)
        if preview:
            cv2.imwrite(f'{out_path}_{t:06.2f}.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        else:
            proc.stdin.write(frame.tobytes())
            if n % 150 == 0:
                print(f'{t:.1f}s', flush=True)
    if proc:
        proc.stdin.close(); proc.wait()

if __name__ == '__main__':
    src, out, variant = sys.argv[1], sys.argv[2], sys.argv[3]
    prev = None
    if len(sys.argv) > 4 and sys.argv[4] == '--preview':
        prev = [float(x) for x in sys.argv[5].split(',')]
    if len(sys.argv) > 4 and sys.argv[4] == '--endcard-only':
        # render only the end card (END_START..END_END) as its own clip
        TOTAL_SAVE = TOTAL
        times = [END_START + i / FPS for i in range(int(round((END_END - END_START) * FPS)))]
        lando = build_lando(Reader(src)); end_bg = build_end_bg(Reader(src))
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                                 '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15',
                                 '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for t in times:
            cv = to_pil(end_bg.copy()); draw_end(cv, t, variant, lando)
            fade_in = ease((t - END_START) / 0.15)
            arr = (np.array(cv.convert('RGB')).astype(np.float32) * (0.15 + 0.85 * fade_in)).astype(np.uint8)
            proc.stdin.write(arr.tobytes())
        proc.stdin.close(); proc.wait()
        sys.exit(0)
    render(src, out, variant, prev)
