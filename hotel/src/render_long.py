"""When It Goes Dark: long-video renderer (1920x1080, 30 fps) for the Snowed-In Hotel episode.

python3 -I render_long.py segments            -> renders out/seg_XXX.mp4 (60 s each) with done markers
python3 -I render_long.py preview T1,T2,...   -> writes preview/frame_T.jpg
python3 -I render_long.py concat              -> joins segments into out/video_noaudio.mp4
"""
import sys, os, re, math, json, subprocess, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timeline as TL

W, H, FPS = 1920, 1080, 30
FONTS = os.path.join(os.path.dirname(HERE), 'fonts')
ART = os.path.join(HERE, 'art'); CHARS = os.path.join(HERE, 'chars')
OUT = os.path.join(HERE, 'out'); PREV = os.path.join(HERE, 'preview')
AMBER = (255, 181, 71); WHITE = (255, 255, 255); RED = (232, 72, 72)
BGW, BGH = 2560, 1440   # working canvas for backgrounds (16:9)

_fonts = {}
def font(name, size, var=None):
    # cached so each (file, size, weight) is one object; text caches key on that identity
    k = (name, size, var)
    if k not in _fonts:
        f = ImageFont.truetype(os.path.join(FONTS, name), size)
        if var:
            f.set_variation_by_name(var)
        f._wigd_key = k
        _fonts[k] = f
    return _fonts[k]

F_CAP = font('Oswald[wght].ttf', 58, 'Bold')
F_ANTON = lambda s: font('Anton-Regular.ttf', s)
F_OSW = lambda s, v='Bold': font('Oswald[wght].ttf', s, v)
F_BAR = lambda s: font('Barlow-SemiBold.ttf', s)

B = TL.build()
LINES, WORDS, TOTAL = B['lines'], B['words'], B['total']
t_of = B['t_of']

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def line_at(t):
    for l in reversed(LINES):
        if l['start'] - 0.05 <= t:
            return l['i']
    return 0

# ------------------------------------------------------------------ shots with absolute times
SHOTS = []
for k, s in enumerate(TL.SHOTS):
    first, bg, cam, chars, fx = s
    st = 0.0 if k == 0 else TL.shot_time(t_of, first) - 0.15
    nxt = TL.SHOTS[k + 1][0] if k + 1 < len(TL.SHOTS) else None
    en = TOTAL if nxt is None else TL.shot_time(t_of, nxt) - 0.15
    SHOTS.append(dict(first=first, bg=bg, cam=cam, chars=chars, fx=fx, start=st, end=en))
# chapter title cards should sit in the pause before the chapter's first line
CH_TIMES = [(t_of(f) - 1.45, n, title) for f, n, title in TL.CHAPTERS]

def shot_at(t):
    for s in SHOTS:
        if s['start'] <= t < s['end']:
            return s
    return SHOTS[-1]

# ------------------------------------------------------------------ assets
_sr = None
def upscale(img_bgr, target_h):
    global _sr
    if img_bgr.shape[0] >= target_h * 0.9:
        return img_bgr
    if _sr is None:
        _sr = cv2.dnn_superres.DnnSuperResImpl_create()
        _sr.readModel(os.path.join(os.path.dirname(HERE), 'FSRCNN_x4.pb')); _sr.setModel('fsrcnn', 4)
    return _sr.upsample(img_bgr)

_bg_cache = {}
def load_bg(name):
    if name in _bg_cache:
        return _bg_cache[name]
    p = os.path.join(ART, name + '.png')
    if os.path.exists(p):
        im = cv2.imread(p, cv2.IMREAD_COLOR)
        ih, iw = im.shape[:2]
        # cover-crop to 16:9
        tw = int(ih * 16 / 9)
        if tw <= iw:
            x0 = (iw - tw) // 2; im = im[:, x0:x0 + tw]
        else:
            th = int(iw * 9 / 16); y0 = (ih - th) // 2; im = im[y0:y0 + th]
        # 1080 -> 1440 is a mild 1.33x step: Lanczos is clean enough and avoids the ~2 GB peak of a 4x super-resolution pass
        im = cv2.resize(im, (BGW, BGH), interpolation=cv2.INTER_AREA if im.shape[0] > BGH else cv2.INTER_LANCZOS4)
    else:
        # placeholder: dark gradient with label
        im = np.zeros((BGH, BGW, 3), np.uint8)
        g = np.linspace(40, 12, BGH).astype(np.uint8)[:, None]
        im[..., 0] = g + 20; im[..., 1] = g + 8; im[..., 2] = g
        cv2.putText(im, name, (80, 160), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (90, 90, 120), 4)
    _bg_cache[name] = im
    return im

import puppet as PUP
import zlib
PUPPETS = True
_char_cache = {}
_char_box = {}
def load_char(name):
    if name in _char_cache:
        return _char_cache[name]
    # crop ops after the file name: '@f' keeps the top f, '<f' keeps the left f, '>f' drops the left f
    m = re.match(r'^([A-Za-z0-9_]+)((?:[@<>][0-9.]+)*)$', name)
    base_name, ops = m.group(1), re.findall(r'([@<>])([0-9.]+)', m.group(2))
    p = os.path.join(CHARS, base_name + '.png')
    if os.path.exists(p):
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 4:   # trim to the drawing first so fractions refer to the character, not the canvas
            ys, xs = np.nonzero(im[..., 3] > 8)
            if len(ys):
                im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        bh_, bw_ = im.shape[:2]          # trimmed base drawing: the frame the hand-placed rigs are measured in
        ox, oy = 0, 0                    # where this crop starts inside it
        for op, v in ops:
            v = float(v)
            if op == '@': im = im[:int(v * im.shape[0])]
            elif op == '<': im = im[:, :int(v * im.shape[1])]
            elif op == '>':
                d = int(v * im.shape[1]); im = im[:, d:]; ox += d
        if im.shape[2] == 3:
            im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        ys, xs = np.nonzero(im[..., 3] > 8)
        if len(ys):
            im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            ox += xs.min(); oy += ys.min()
        _char_box[name] = (base_name, bw_, bh_, ox, oy, im.shape[0])
    else:
        im = None
    _char_cache[name] = im
    return im

def paste_rgba(dst, src, x, y):
    """alpha-blend BGRA src onto BGR dst with top-left (x, y)."""
    h, w = src.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x1 <= x0 or y1 <= y0:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = s[..., 3:4] / 255.0
    d = dst[y0:y1, x0:x1].astype(np.float32)
    if dst.shape[2] == 4:
        da = d[..., 3:4] / 255.0
        oa = a + da * (1 - a)
        rgb = (s[..., :3] * a + d[..., :3] * da * (1 - a)) / np.maximum(oa, 1e-6)
        dst[y0:y1, x0:x1] = np.concatenate([rgb, oa * 255], axis=2).clip(0, 255).astype(np.uint8)
    else:
        dst[y0:y1, x0:x1] = (s[..., :3] * a + d * (1 - a)).astype(np.uint8)

def warm_mask(img, thr=165, sep=60, grow=5):
    f = img.astype(np.float32); b, g, r = f[..., 0], f[..., 1], f[..., 2]
    m = ((r > thr) & (r - b > sep) & (g > 0.45 * r)).astype(np.float32)
    m = cv2.dilate(m, np.ones((grow, grow), np.uint8))
    return np.clip(cv2.GaussianBlur(m, (0, 0), 3)[..., None], 0, 1)

def windows_off(img, strength=1.0, exterior=True):
    """Lit windows / lamp glow go dark (power out): warm light becomes dim night blue.
    Exteriors: anything warm is a light source, so a low threshold catches the whole window glow."""
    m = (warm_mask(img, 95, 35, 9) if exterior else warm_mask(img)) * strength
    f = img.astype(np.float32)
    dark = f.mean(axis=2, keepdims=True) * 0.22 * np.array([1.35, 1.0, 0.75])
    return np.clip(f * (1 - m) + dark * m, 0, 255).astype(np.uint8)

FIRE_BOX = (0.0, 0.12, 0.34, 0.58)  # bg05 fireplace area (x0, y0, x1, y1) as fractions of the plate
def fire_to_coals(img):
    h, w = img.shape[:2]; x0, y0, x1, y1 = [int(v) for v in (FIRE_BOX[0] * w, FIRE_BOX[1] * h, FIRE_BOX[2] * w, FIRE_BOX[3] * h)]
    reg = img[y0:y1, x0:x1]
    f = reg.astype(np.float32); b, g, r = f[..., 0], f[..., 1], f[..., 2]
    m = ((r > 150) & (r - b > 70)).astype(np.float32)
    m = cv2.GaussianBlur(cv2.dilate(m, np.ones((9, 9), np.uint8)), (0, 0), 6)[..., None]
    coal = np.stack([b * 0.10, g * 0.14, r * 0.42], axis=2)
    out = img.copy(); out[y0:y1, x0:x1] = np.clip(f * (1 - m) + coal * m, 0, 255).astype(np.uint8)
    # the whole room loses most of its firelight
    return (out.astype(np.float32) * np.array([0.92, 0.82, 0.74])).astype(np.uint8)

GEN_BOX = (0.27, 0.30, 0.50, 0.56)  # search box for the red generator baked into bg05
def hide_generator(img):
    h, w = img.shape[:2]; x0, y0, x1, y1 = [int(v) for v in (GEN_BOX[0] * w, GEN_BOX[1] * h, GEN_BOX[2] * w, GEN_BOX[3] * h)]
    f = img[y0:y1, x0:x1].astype(np.int32); b, g, r = f[..., 0], f[..., 1], f[..., 2]
    red = ((r > 110) & (r > g * 1.7) & (r > b * 1.7)).astype(np.uint8)
    ys, xs = np.nonzero(red)
    if len(ys) < 50:
        return img
    m = np.zeros(img.shape[:2], np.uint8)
    py0, py1 = np.percentile(ys, 1), np.percentile(ys, 99.5); px0, px1 = np.percentile(xs, 1), np.percentile(xs, 99)
    pad = int(0.012 * w)
    cv2.rectangle(m, (int(x0 + px0) - pad, int(y0 + py0) - pad), (int(x0 + px1) + pad, int(y0 + py1) + pad), 255, -1)
    small = cv2.resize(img, (w // 2, h // 2)); ms = cv2.resize(m, (w // 2, h // 2), interpolation=cv2.INTER_NEAREST)
    filled = cv2.inpaint(small, ms, 9, cv2.INPAINT_TELEA)
    up = cv2.resize(filled, (w, h), interpolation=cv2.INTER_CUBIC)
    mm = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 6)[..., None]
    return (img.astype(np.float32) * (1 - mm) + up.astype(np.float32) * mm).astype(np.uint8)

_layer_cache = {}
def shot_layer(shot):
    key = id(shot)
    if key in _layer_cache:
        return _layer_cache[key]
    base = load_bg(shot['bg']).copy()
    fxs = shot['fx']
    if 'no_bg_gen' in fxs:
        base = hide_generator(base)
    if 'coals' in fxs:
        base = fire_to_coals(base)
    if 'windows_off' in fxs:
        base = windows_off(base)
    if 'door_dim' in fxs:   # porch after the fire burned down: the doorway glow is only embers
        base = windows_off(base, strength=0.7)
    if 'lights_off' in fxs:   # power is out: kill the lamp glow, push to a cold night look
        base = windows_off(base, strength=0.92, exterior=False)
        f = base.astype(np.float32)
        L = f.mean(axis=2, keepdims=True)
        f *= np.minimum(1.0, (60 + np.maximum(L - 60, 0) * 0.06) / np.maximum(L, 1))
        f = f * 0.62 * np.array([1.22, 0.98, 0.78])
        base = np.clip(f, 0, 255).astype(np.uint8)
    dark = 'dark' in shot['fx']
    prepped = []
    night_out = ('snow' in fxs or 'snow_heavy' in fxs) and not ('dawn' in fxs or 'warm' in fxs)
    for (name, xf, yb, hf, flip) in shot['chars']:
        c = load_char(name)
        if c is None:
            # placeholder silhouette
            hh = int(hf * BGH); ww = int(hh * 0.45)
            c = np.zeros((hh, ww, 4), np.uint8)
            cv2.ellipse(c, (ww // 2, hh // 2), (ww // 2 - 4, hh // 2 - 4), 0, 0, 360, (60, 60, 70, 230), -1)
            cv2.putText(c, name[:10], (4, hh // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200, 255), 2)
        else:
            th = int(hf * BGH)
            if c.shape[0] < th * 0.9:
                rgb = upscale(np.ascontiguousarray(c[..., :3]), th)
                a = cv2.resize(c[..., 3], (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_CUBIC)
                c = np.dstack([rgb, a])
            sc = th / c.shape[0]
            c = cv2.resize(c, (max(1, int(c.shape[1] * sc)), th), interpolation=cv2.INTER_AREA if sc < 1 else cv2.INTER_CUBIC)
        if flip:
            c = c[:, ::-1].copy()
        cc = c.astype(np.float32)
        if dark:  # sit the character into a night scene
            cc[..., :3] *= 0.78
            cc[..., 0] = cc[..., 0] * 1.06 + 6; cc[..., 2] *= 0.94
            cc = np.clip(cc, 0, 255)
        if 'char_dim' in fxs:   # extra-dark room: pull the cutout down to the plate's level
            cc[..., :3] *= np.array([0.80, 0.66, 0.58])
            cc = np.clip(cc, 0, 255)
        elif night_out:  # snowy night exterior: cool, slightly darker so cutouts don't read as stickers
            cc[..., :3] *= np.array([0.98, 0.88, 0.80]) * 0.9
            cc = np.clip(cc, 0, 255)
        if 'warm' in fxs or 'firelight' in fxs:   # firelit / lamplit rooms: warm the cutout to match
            cc[..., :3] *= np.array([0.85, 0.95, 1.12])
            cc = np.clip(cc, 0, 255)
        c = cc.astype(np.uint8)
        # contact shadow (skipped when the character's feet are off-frame or it sits behind furniture)
        if yb < 1.02 and '@' not in name:
            sh = np.zeros(base.shape[:2], np.float32)
            cv2.ellipse(sh, (int(xf * BGW), min(int(yb * BGH) - 6, BGH - 2)), (int(c.shape[1] * 0.42), int(c.shape[1] * 0.08)), 0, 0, 360, 1.0, -1)
            sh = cv2.GaussianBlur(sh, (0, 0), 14)[..., None]
            base = (base.astype(np.float32) * (1 - 0.7 * sh)).astype(np.uint8)
        nm = name.lower()
        wdir = 0
        for k, d in WALK_DIR.items():
            if nm.startswith(k) and 'no_travel' not in fxs:
                wdir = -d if flip else d
        kind = ('walk' if any(k in nm for k in ('walk', 'parade', 'drag', 'generator')) else
                'sleep' if any(k in nm for k in ('sleep', 'slumped', 'asleep', 'oxygen', 'bench', 'on_face')) else
                'sway' if any(k in nm for k in ('yowl', 'dizzy', 'confused', 'blanket')) else 'idle')
        rig = None
        if PUPPETS and kind != 'sleep' and 'no_rig' not in fxs:
            rig = PUP.build_rig(c, name, _char_box[name], flip) if name in _char_box else None
        prepped.append((c, xf * BGW, yb * BGH, kind, len(prepped) * 1.7 + 0.37 * (zlib.crc32(name.encode()) % 7), wdir, rig))
    _layer_cache.clear(); _layer_cache[key] = (base, prepped)   # keep only the current shot
    return _layer_cache[key]

WALK_DIR = {'hero_walk_headlamp': 1, 'lando_parade': 1, 'dale_generator': 1, 'hero_drag_dale': -1}   # unflipped facing

def breathe(c, amp):
    """Stretch only the upper 55% (chest and head); legs, seats and props stay put."""
    h, w = c.shape[:2]
    cut = int(h * 0.55)
    top = c[:cut]
    nt = max(1, int(round(cut * (1 + amp))))
    if nt == cut:
        return c
    return np.concatenate([cv2.resize(top, (w, nt), interpolation=cv2.INTER_LINEAR), c[cut:]], axis=0)

def shot_canvas(shot, t):
    """Background plate plus characters, posed for time t (breathing, walking across, rocking)."""
    base, prepped = shot_layer(shot)
    if not prepped:
        return base
    out = base.copy()
    u = (t - shot['start']) / max(shot['end'] - shot['start'], 0.01)
    fxs = shot['fx']
    night_out = ('snow' in fxs or 'snow_heavy' in fxs) and not ('dawn' in fxs or 'warm' in fxs)
    puffs = []
    for c, cx, by, kind, ph, wdir, rig in prepped:
        if rig is not None:
            if 'head_track' in fxs:   # following something with its eyes: a slow, wide head turn
                c = PUP.pose(c, rig, t, ph, angle=-2.0 + 5.0 * math.sin(2 * math.pi * 0.16 * (t - shot['start']) - 1.2))
            else:
                c = PUP.pose(c, rig, t, ph, amp=rig['amp'] * (0.75 if kind == 'walk' else 1.0))
        h, w = c.shape[:2]
        dx = dy = 0.0
        ang = 0.0
        if kind == 'walk':
            amp = 0.006 * math.sin(2 * math.pi * 0.3 * t + ph)
            dy = 0.0015 * BGH * math.sin(2 * math.pi * 1.0 * t + ph)
            dx = wdir * 0.04 * BGW * (u - 0.5)
        elif kind == 'sleep':
            amp = 0.008 * math.sin(2 * math.pi * 0.22 * t + ph)
        elif kind == 'sway':
            amp = 0.008 * math.sin(2 * math.pi * 0.35 * t + ph)
            ang = 1.0 * math.sin(2 * math.pi * 0.5 * t + ph)
        else:
            amp = 0.007 * math.sin(2 * math.pi * 0.3 * t + ph)
        cc = breathe(c, amp)
        nh = cc.shape[0]
        if ang:
            pad = int(0.08 * nh)
            big = cv2.copyMakeBorder(cc, pad, 0, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
            M = cv2.getRotationMatrix2D((big.shape[1] / 2, big.shape[0] - 1), ang, 1.0)   # pivot at the feet
            cc = cv2.warpAffine(big, M, (big.shape[1], big.shape[0]), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
            w2 = cc.shape[1]
            x0p, y0p = int(cx - w2 / 2 + dx), int(by - cc.shape[0] + dy)
            paste_rgba(out, cc, x0p, y0p)
            x0p += pad; y0p += pad
        else:
            x0p, y0p = int(cx - w / 2 + dx), int(by - nh + dy)
            paste_rgba(out, cc, x0p, y0p)
        if night_out and rig is not None and 'mouth' in rig and 'no_breath' not in fxs:
            mx, my = rig['mouth']
            fd = rig.get('face_dir', 0)
            drift = 1.0 * fd + (0.5 if fd >= 0 else -0.1)
            puffs.append((x0p + mx, y0p + my, ph, rig['head']['rx'] * 0.55 if rig['head'] else w * 0.08, drift))
    if puffs:   # breath clouds in the freezing air, on a quarter-size layer
        lay = np.zeros((BGH // 4, BGW // 4), np.float32)
        for mx, my, ph, sc, drift in puffs:
            PUP.breath(lay, mx / 4, my / 4, t, ph, sc / 4, drift)
        lay = cv2.GaussianBlur(lay, (0, 0), 2.2)
        lay = cv2.resize(np.minimum(lay * 1.1, 0.7), (BGW, BGH), interpolation=cv2.INTER_LINEAR)[..., None]
        out = np.clip(out.astype(np.float32) * (1 - lay) + lay * np.array([232, 228, 222]), 0, 255).astype(np.uint8)
    return out

# ------------------------------------------------------------------ text helpers (PIL -> BGRA numpy, cached)
_txt = {}
def text_rgba(txt, f, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), shadow=True, key=None):
    k = key or (txt, getattr(f, '_wigd_key', id(f)), fill, stroke, shadow)
    if k in _txt:
        return _txt[k]
    l, t, r, b = f.getbbox(txt, stroke_width=stroke)
    pad = 24
    im = Image.new('RGBA', (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 3, pad - t + 5), txt, font=f, fill=(0, 0, 0, 200), stroke_width=stroke + 1, stroke_fill=(0, 0, 0, 200))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(5)))
        d = ImageDraw.Draw(im)
    d.text((pad - l, pad - t), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)
    _txt[k] = arr
    return arr

def panel_rgba(w, h, r, fill, outline=None, width=0):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=fill, outline=outline, width=width)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)

def fade(arr, a):
    if a >= 0.999:
        return arr
    o = arr.copy(); o[..., 3] = (o[..., 3].astype(np.float32) * max(a, 0)).astype(np.uint8); return o

def put(dst, arr, cx, cy, a=1.0, anchor='c'):
    h, w = arr.shape[:2]
    if anchor == 'c':
        x, y = int(cx - w / 2), int(cy - h / 2)
    else:  # top-left
        x, y = int(cx), int(cy)
    paste_rgba(dst, fade(arr, a), x, y)

# ------------------------------------------------------------------ captions
STOP = set('a an the and or but of to in on at by for with from up is are was were be been it its it\'s you your you\'re he she they them his her him that this there these those so then than as into out over under all every one just not no do does did can can\'t'.split())

def build_captions():
    caps, cur = [], []
    def flush():
        if cur:
            caps.append(list(cur)); cur.clear()
    for w in WORDS:
        txt = w['text'].replace('"', '').replace('“', '').replace('”', '')
        ww = dict(w, text=txt.upper())
        if cur and (len(' '.join(x['text'] for x in cur)) + len(txt) > 30 or w['line'] != cur[-1]['line'] or w['start'] - cur[-1]['end'] > 0.6):
            flush()
        cur.append(ww)
        if txt[-1:] in '.?!,' and len(' '.join(x['text'] for x in cur)) > 14:
            flush()
    flush()
    out = []
    for i, c in enumerate(caps):
        cands = [x for x in c if x['text'].strip('.,?!:;').lower() not in STOP]
        key = max(cands, key=lambda x: len(x['text'])) if cands else c[-1]
        end = c[-1]['end'] + 0.35
        if i + 1 < len(caps):
            end = min(end, caps[i + 1][0]['start'])
        out.append({'words': c, 'key': key['text'], 'start': c[0]['start'], 'end': end})
    return out
CAPS = build_captions()

_capimg = {}
def caption_img(ci, n):
    k = (ci, n)
    if k in _capimg:
        return _capimg[k]
    c = CAPS[ci]
    words = [x['text'] for x in c['words']]
    sp = F_CAP.getlength(' ')
    widths = [F_CAP.getlength(w) for w in words]
    total = sum(widths) + sp * (len(words) - 1)
    pad = 30
    im = Image.new('RGBA', (int(total) + pad * 2, 120), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im); ds = ImageDraw.Draw(sh)
    x = pad
    for idx, w in enumerate(words):
        if idx < n:
            col = AMBER if w == c['key'] else WHITE
            ds.text((x + 3, 22 + 4), w, font=F_CAP, fill=(0, 0, 0, 210), stroke_width=6, stroke_fill=(0, 0, 0, 210))
            d.text((x, 22), w, font=F_CAP, fill=col, stroke_width=5, stroke_fill=(0, 0, 0))
        x += widths[idx] + sp
    im = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), im)
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGBA2BGRA)
    _capimg[k] = arr
    return arr

def draw_caption(fr, t):
    if shot_at(t)['bg'] == 'CHOICE':
        return
    for i, c in enumerate(CAPS):
        if c['start'] <= t < c['end']:
            n = max(1, sum(1 for x in c['words'] if x['start'] <= t + 0.03))
            put(fr, caption_img(i, n), W / 2, 960)
            return

# ------------------------------------------------------------------ overlays
def status_for(t):
    li = line_at(t)
    for a, b in TL.NO_STATUS:
        if a <= li < b:
            return None
    st = TL.STATUS[0]
    for s in TL.STATUS:
        if li >= s[0]:
            st = s
    return st

_status = {}
def draw_status(fr, t):
    st = status_for(t)
    if st is None:
        return
    if st not in _status:
        _, tm, pw, ph, tp = st
        items = [('TIME', tm, WHITE), ('POWER', pw, RED if pw == 'OFF' else (120, 220, 140)), ('PHONE', ph, AMBER), ('TEMP', tp, (140, 200, 255))]
        w = 0; parts = []
        for lab, val, col in items:
            a = text_rgba(lab, F_BAR(18), (200, 205, 215), shadow=False)
            b = text_rgba(val, F_OSW(34), col, shadow=False)
            parts.append((a, b)); w += max(a.shape[1], b.shape[1]) - 30
        pnl = panel_rgba(w + 40, 92, 14, (10, 13, 20, 200))
        x = 14
        for a, b in parts:
            paste_rgba(pnl, a, x - 14, -10)
            paste_rgba(pnl, b, x - 14, 14)
            x += max(a.shape[1], b.shape[1]) - 30
        _status[st] = pnl
    put(fr, _status[st], 40, 34, 1.0, 'tl')

def chapter_now(t):
    cur = None
    for (ct, n, title) in CH_TIMES:
        if t >= ct:
            cur = (ct, n, title)
    return cur

def draw_chapter(fr, t):
    ch = chapter_now(t)
    if ch is None:
        return
    ct, n, title = ch
    dt = t - ct
    # small label top-right always
    lab = text_rgba(f'CHAPTER {n}  ·  {title}', F_OSW(22, 'SemiBold'), (215, 220, 230), shadow=True)
    put(fr, lab, W - 40 - lab.shape[1], 30, 0.9, 'tl')
    # shorter card when the chapter opens on a full-screen card (split/choice/stat), so the two never overlap
    dur = 1.45 if shot_at(ct + 1.46)['bg'] in ('SPLIT', 'CHOICE', 'STAT') else 2.6
    if n == 1:
        dur = 0   # the title card right before already opens chapter 1
    if 0 <= dt < dur:
        a = ease(dt / 0.35) * (1 - ease((dt - (dur - 0.4)) / 0.4))
        fr[:] = (fr.astype(np.float32) * (1 - 0.45 * a)).astype(np.uint8)
        put(fr, text_rgba(f'CHAPTER {n}', F_OSW(36), AMBER), W / 2, H * 0.24 - 70, a)
        put(fr, text_rgba(title, F_ANTON(120), WHITE, stroke=2), W / 2, H * 0.24 + 30, a)

_rule = {}
def draw_rule(fr, t):
    li = line_at(t)
    for (a, b, lab, title, lines_) in TL.RULES:
        ta, tb = t_of(a) - 0.2, LINES[b]['end'] + 0.8
        if ta <= t < tb:
            if title not in _rule:
                L = text_rgba(lab, F_OSW(24), (20, 20, 20), shadow=False)
                T = text_rgba(title, F_ANTON(46), WHITE, shadow=False)
                Ls = [text_rgba(x, F_BAR(28), (220, 226, 236), shadow=False) for x in lines_]
                w = max([T.shape[1]] + [x.shape[1] for x in Ls]) + 20
                h = 70 + T.shape[0] - 30 + sum(x.shape[0] - 34 for x in Ls) + 30
                p = panel_rgba(w, h, 16, (10, 13, 20, 225), outline=(255, 181, 71, 255), width=3)
                tag = panel_rgba(L.shape[1] - 18, 36, 8, AMBER + (255,))
                paste_rgba(tag, L, -15, -14)
                paste_rgba(p, tag, 18, 16)
                paste_rgba(p, T, -6, 34)
                y = 34 + T.shape[0] - 36
                for x in Ls:
                    paste_rgba(p, x, -6, y); y += x.shape[0] - 34
                _rule[title] = p
            p = _rule[title]
            k = ease((t - ta) / 0.35) * (1 - ease((t - (tb - 0.4)) / 0.4))
            put(fr, p, 40 - (1 - k) * 60, 150, k, 'tl')
            return

TIMESTAMPS = {0: '2:47 AM', 19: '6:00 PM', 35: '7:00 PM', 39: '8:12 PM', 65: '10:00 PM', 91: '2:47 AM', 210: '5:50 AM'}
def draw_timestamp(fr, t):
    for li, txt in TIMESTAMPS.items():
        ta = t_of(li)
        if li == 0:
            ta = 0.3
        if ta <= t < ta + 2.4:
            a = ease((t - ta) / 0.3) * (1 - ease((t - ta - 1.9) / 0.5))
            put(fr, text_rgba(txt, F_ANTON(92), WHITE, stroke=2), W / 2, 300, a)

# ------------------------------------------------------------------ effects
rng = np.random.default_rng(3)
SNOW = rng.random((420, 4))  # x, y phase, speed, size

def fx_snow(fr, t, n=220, wind=0.25, bright=210):
    for i in range(n):
        x0, ph, sp, sz = SNOW[i]
        y = ((ph + t * (0.09 + 0.12 * sp)) % 1.0) * (H + 40) - 20
        x = ((x0 + t * wind * (0.04 + 0.05 * sp) + 0.01 * math.sin(t * 1.3 + i)) % 1.0) * W
        r = 1 + int(sz * 3)
        cv2.circle(fr, (int(x), int(y)), r, (bright, bright, bright), -1, cv2.LINE_AA)

def fx_dust(fr, t):
    for i in range(60):
        x0, ph, sp, sz = SNOW[i + 200]
        x = int(((x0 + 0.01 * math.sin(t * 0.4 + i)) % 1) * W); y = int(((ph - t * 0.01 * sp) % 1) * H)
        cv2.circle(fr, (x, y), 1 + int(sz * 1.5), (150, 160, 170), -1, cv2.LINE_AA)

_masks = {}
def beam_mask(cx, cy, strong):
    k = (round(cx, 2), round(cy, 2), strong)
    if k not in _masks:
        m = np.zeros((H // 4, W // 4), np.float32)
        cv2.ellipse(m, (int(cx * W / 4), int(cy * H / 4)), (int(W / 4 * 0.33), int(H / 4 * 0.42)), 0, 0, 360, 1.0, -1)
        m = cv2.GaussianBlur(m, (0, 0), 30)
        m = cv2.resize(m, (W, H))
        floor = 0.28 if strong else 0.55
        _masks.clear(); _masks[k] = (floor + (1 - floor) * m)[..., None]
    return _masks[k]

_vig = None
def vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2
        _vig = np.clip(1 - 0.55 * d, 0.35, 1)[..., None]
    return _vig

def haze(fr, t, amp):
    yy, xx = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    dx = amp * np.sin(yy / 23 + t * 2.1); dy = amp * 0.6 * np.cos(xx / 31 + t * 1.7)
    mx = cv2.resize(xx + dx, (W, H)); my = cv2.resize(yy + dy, (W, H))
    mx = mx * (W / (W - 4) if False else 1)
    return cv2.remap(fr, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def phone_overlay(fr, pct, calling, t, connected=False):
    pw, ph = 330, 620
    p = panel_rgba(pw, ph, 46, (14, 16, 22, 245), outline=(70, 74, 84, 255), width=6)
    put(p, text_rgba(pct, F_OSW(30), (255, 120, 100) if pct in ('9%', '6%', '3%', '12%') else WHITE, shadow=False), pw - 70, 40)
    nbars = 1 if (calling or pct in ('9%', '6%', '3%')) else 2
    for i in range(4):  # signal bars
        on = i < nbars
        cv2.rectangle(p, (40 + i * 16, 52 - i * 8), (50 + i * 16, 58), (235, 235, 235, 255) if on else (90, 90, 90, 255), -1)
    if calling:
        put(p, text_rgba('Connected' if connected else 'Calling', F_BAR(34), (120, 230, 140) if connected else (200, 205, 215), shadow=False), pw / 2, 230)
        put(p, text_rgba('911', F_ANTON(110), WHITE, shadow=False), pw / 2, 320)
        if connected:
            cv2.circle(p, (pw // 2, 500), 46, (60, 60, 220, 255), -1, cv2.LINE_AA)   # red end-call button
        elif (t * 1.2) % 1 < 0.6:
            cv2.circle(p, (pw // 2, 500), 46, (70, 200, 90, 255), -1, cv2.LINE_AA)
    else:
        put(p, text_rgba('1 bar' if nbars == 1 else 'Storm: weak signal', F_BAR(30), (200, 205, 215), shadow=False), pw / 2, 250)
        put(p, text_rgba(pct, F_ANTON(120), WHITE, shadow=False), pw / 2, 360)
    put(fr, p, W - 330, H / 2 - 20)

def choice_frame(t, t0):
    fr = cv2.GaussianBlur(split_frame(t), (0, 0), 14)
    fr = (fr.astype(np.float32) * 0.45).astype(np.uint8)
    dt = t - t0
    put(fr, text_rgba('WHAT WOULD YOU DO?', F_OSW(44), AMBER), W / 2, 250, ease(dt / 0.25))
    for i, (lab, sub) in enumerate([('STAY INSIDE', 'warm, poisoned air'), ('GO OUT', 'into a 9°F blizzard')]):
        k = ease((dt - 0.1 * i) / 0.3)
        p = panel_rgba(560, 220, 30, (12, 16, 26, 230), outline=(255, 255, 255, 235), width=5)
        put(p, text_rgba(lab, F_ANTON(82), WHITE, shadow=False), 280, 92)
        put(p, text_rgba(sub, F_BAR(32), (190, 196, 210), shadow=False), 280, 168)
        put(fr, p, W / 2 + (-320 if i == 0 else 320), 500 + 30 * (1 - k), k)
    frac = 1 - min(max(dt / 3.2, 0), 1)
    cv2.rectangle(fr, (W // 2 - 600, 700), (W // 2 + 600, 712), (60, 60, 60), -1)
    cv2.rectangle(fr, (W // 2 - 600, 700), (int(W // 2 - 600 + 1200 * frac), 712), (71, 181, 255), -1)
    return fr

exec(open(os.path.join(HERE, 'anim_extra.py')).read())

_lando_photo = None
def end_frame(t, t0):
    global _lando_photo
    fr = np.full((H, W, 3), (24, 16, 12), np.uint8)
    dt = t - t0
    if _lando_photo is None:
        src = cv2.imread(os.path.join(HERE, 'style_refs', 'real_lando.png')) if os.path.exists(os.path.join(HERE, 'style_refs', 'real_lando.png')) else None
        if src is None:
            cap = cv2.VideoCapture('/home/claude/src_s1/s1_full.mp4'); cap.set(cv2.CAP_PROP_POS_MSEC, 596000); ok, f = cap.read()
            src = f[90:990, 170:675]
        ph = cv2.resize(src, (380, int(380 * src.shape[0] / src.shape[1])))
        frame = panel_rgba(ph.shape[1] + 16, ph.shape[0] + 16, 26, AMBER + (255,))
        paste_rgba(frame, np.dstack([ph, np.full(ph.shape[:2], 255, np.uint8)]), 8, 8)
        _lando_photo = frame
    k = ease(dt / 0.5)
    put(fr, _lando_photo, 560, H / 2, k)
    put(fr, text_rgba('THE REAL LANDO', F_ANTON(96), AMBER), 1220, 380, k)
    put(fr, text_rgba("Don't worry, he's OK.", F_OSW(58, 'SemiBold'), WHITE), 1220, 490, ease((dt - 0.3) / 0.5))
    put(fr, text_rgba('Inside or out? Tell me in the comments.', F_BAR(38), (215, 220, 230)), 1220, 600, ease((dt - 0.6) / 0.5))
    put(fr, text_rgba('Next Monday: the lights go out somewhere new.', F_BAR(34), (190, 196, 210)), 1220, 680, ease((dt - 0.9) / 0.5))
    return fr

def title_card(fr, t, t0):
    dt = t - t0
    if dt < 0 or dt > 3.4:
        return
    a = ease(dt / 0.4) * (1 - ease((dt - 2.9) / 0.5))
    fr[:] = (fr.astype(np.float32) * (1 - 0.6 * a)).astype(np.uint8)
    put(fr, text_rgba('WHEN IT GOES DARK', F_ANTON(150), AMBER, stroke=2), W / 2, H / 2 - 40, a)
    put(fr, text_rgba('WINTER STORM.  12 HOURS.  NO POWER.', F_OSW(46), WHITE), W / 2, H / 2 + 90, a)

DOOR_BOX = (0.735, 0.13, 0.875, 0.70)   # bg05 open front door (plate fractions)
def door_rect(shot):
    z, cx, cy = shot['cam'][0], shot['cam'][2], shot['cam'][3]
    fx0 = 0.5 + z * (DOOR_BOX[0] - cx); fx1 = 0.5 + z * (DOOR_BOX[2] - cx)
    fy0 = 0.5 + z * (DOOR_BOX[1] - cy); fy1 = 0.5 + z * (DOOR_BOX[3] - cy)
    clip = lambda v, m: int(min(max(v, 0), 1) * m)
    return clip(fx0, W), clip(fy0, H), clip(fx1, W), clip(fy1, H)

COUNTER_Y = 0.418   # bg03 counter top, as a fraction of the plate
def candle_row(shot):
    z, cx, cy = shot['cam'][0], shot['cam'][2], shot['cam'][3]
    base_y = (COUNTER_Y - cy) * z + 0.5                      # counter line in frame coords
    xs = [(xp - cx) * z * (BGH / BGW) * (BGW / BGH) + 0.5 for xp in np.linspace(0.40, 0.84, 15)]
    return base_y, xs

def candles(fr, t, t0, shot, lit=True):
    base_y, xs = candle_row(shot)
    n = 15 if not lit else min(15, 1 + int((t - t0) * 4))
    rnd = random.Random(7)
    hs = [rnd.uniform(0.85, 1.15) for _ in range(15)]
    z = shot['cam'][0]
    if lit and n:
        # warm light spilling over the counter and whoever is lighting them
        g = np.zeros((H // 4, W // 4), np.float32)
        for i in range(n):
            cv2.circle(g, (int(xs[i] * W / 4), int(base_y * H / 4) - 10), int(26 * z), 1.0, -1)
        g = cv2.resize(cv2.GaussianBlur(g, (0, 0), 22 * z / 1.5), (W, H))[..., None]
        fr[:] = np.clip(fr.astype(np.float32) + np.minimum(g, 1.0) * np.array([40, 110, 210]) * 0.55, 0, 255).astype(np.uint8)
    for i in range(n):
        x = int(xs[i] * W); yb = int(base_y * H); ch = int(30 * z * hs[i]); cw = max(4, int(5 * z))
        if not (0 < x < W): continue
        cv2.ellipse(fr, (x, yb), (int(cw * 2.2), int(cw * 0.8)), 0, 0, 360, (40, 70, 110), -1, cv2.LINE_AA)   # brass holder
        cv2.rectangle(fr, (x - cw, yb - ch), (x + cw, yb - 2), (200, 214, 226) if lit else (150, 160, 170), -1)
        cv2.line(fr, (x, yb - ch), (x, yb - ch - int(5 * z)), (30, 30, 30), 2)
        if lit:
            fl = 1 + 0.15 * math.sin(t * 13 + i * 2)
            cv2.ellipse(fr, (x, yb - ch - int(9 * z)), (max(3, int(4 * z)), int(9 * z * fl)), 0, 0, 360, (120, 220, 255), -1, cv2.LINE_AA)

def eyes(fr, t, t0):
    dt = t - t0
    if dt < 0.4:
        return
    blink = ((t * 0.7) % 1) > 0.94
    a = ease((dt - 0.4) / 0.5)
    for dx in (-60, 60):
        cx, cy = W // 2 + dx, H // 2 + 20
        g = np.zeros((H, W), np.float32)
        cv2.ellipse(g, (cx, cy), (34, 6 if blink else 22), 0, 0, 360, 1.0, -1)
        g = cv2.GaussianBlur(g, (0, 0), 14) * 1.6 + g
        fr[:] = np.clip(fr.astype(np.float32) + a * np.minimum(g, 1.2)[..., None] * np.array([90, 255, 120]), 0, 255).astype(np.uint8)
        if not blink:
            cv2.ellipse(fr, (cx, cy), (5, 16), 0, 0, 360, (10, 30, 10), -1, cv2.LINE_AA)

def apply_fx(fr, shot, t):
    fx = shot['fx']; st = shot['start']; dt = t - st
    f = fr.astype(np.float32)
    if 'warm' in fx:
        f *= [0.95, 1.0, 1.06]
    if 'blackout_grade' in fx:
        f *= [0.82, 0.74, 0.66]
    if 'night' in fx:
        f *= [0.8, 0.72, 0.62]
    if 'cold' in fx:
        f = f * [1.12, 1.0, 0.86]
    if 'dawn' in fx or 'dawn_grade' in fx:
        f = f * [0.95, 1.0, 1.08] + 6
    if 'dash_glow' in fx:
        f = f * [0.9, 1.0, 1.1]
    if 'firelight' in fx or 'coals' in fx:
        fl = 1 + (0.035 if 'firelight' in fx else 0.015) * math.sin(t * 9.1) * math.sin(t * 5.3 + 1)
        f *= [fl, fl, fl * (0.85 if 'coals' in fx else 1.0)]
    if 'red_glow' in fx:
        p = 0.5 + 0.5 * math.sin(t * 3)
        f = f * [0.85, 0.85, 1.0 + 0.25 * p]
    if 'flicker_out' in fx:
        # flicker on "Once." (41) and "Twice." (42); dark on "Then the whole mountain goes dark." (43)
        for ft in (t_of(41), t_of(42)):
            if ft <= t < ft + 0.18:
                f *= 0.35
        if t >= t_of(43):
            f = windows_off(np.clip(f, 0, 255).astype(np.uint8), 1.0).astype(np.float32)
            f *= [0.55, 0.5, 0.45]
    if 'beam' in fx or 'beam_char' in fx:
        cx = 0.5 + 0.05 * math.sin(t * 0.7); cy = 0.55 + 0.03 * math.sin(t * 0.9)
        f *= beam_mask(cx, cy, 'beam' in fx)
    if 'dark' in fx:
        f *= vignette()
    if 'heartbeat' in fx:
        p = abs(math.sin(t * 3.4)) ** 6
        f = f * 0 + p * 60 * vignette()[..., 0:1] * np.array([0.3, 0.3, 1.0])
    fr = np.clip(f, 0, 255).astype(np.uint8)
    if 'heat_haze' in fx or 'heat_haze_strong' in fx or 'headache' in fx:
        fr = haze(fr, t, 6 if 'heat_haze_strong' in fx else 3)
    if 'dizzy' in fx or 'dizzy_soft' in fx:
        ang = (2.2 if 'dizzy' in fx else 1.0) * math.sin(t * 1.3)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1.04)
        fr = cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        if 'dizzy' in fx and (t * 0.8) % 1 < 0.25:
            fr = cv2.addWeighted(fr, 0.6, cv2.GaussianBlur(fr, (0, 0), 6), 0.4, 0)
    if 'headache' in fx:
        p = abs(math.sin(t * 2.2)) ** 4
        fr = cv2.addWeighted(fr, 1 - 0.3 * p, cv2.GaussianBlur(fr, (0, 0), 8), 0.3 * p, 0)
    if 'shake_soft' in fx or 'rumble' in fx or 'knock' in fx:
        a = 3 if 'shake_soft' in fx else 2
        if 'knock' in fx:
            a = 7 if (dt % 1.0) < 0.12 and dt < 1.2 else 0
        M = np.float32([[1, 0, a * math.sin(t * 37)], [0, 1, a * math.cos(t * 29)]])
        fr = cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if 'snow' in fx: fx_snow(fr, t, 160)
    if 'snow_heavy' in fx: fx_snow(fr, t, 380, wind=1.6, bright=225)
    if 'snow_light' in fx: fx_snow(fr, t, 90, bright=200)
    if 'door_snow' in fx or 'door_snow2' in fx:
        x0, y0, x1, y1 = door_rect(shot)
        if x1 - x0 > 20 and y1 - y0 > 20:
            sub = fr[y0:y1, x0:x1]
            fx_snow(sub, t, 160 if 'door_snow2' in fx else 70, wind=-1.0, bright=205)
    if 'dust' in fx: fx_dust(fr, t)
    if 'candles' in fx: candles(fr, t, t_of(57) + 0.3, shot)   # count keeps going across the candle shots
    if 'candles_out' in fx: candles(fr, t, -99, shot, lit=False)
    if 'eyes' in fx: eyes(fr, t, st)
    if 'figure' in fx:
        t0 = t_of(120)
        if t0 + 0.3 <= t < t_of(121) + 0.35 and not ((t * 9) % 1 < 0.25 and t > t_of(121)):
            cx, foot, hh = W // 2 + 30, int(H * 0.70), int(H * 0.34)
            col = (6, 6, 8)
            # rim light so it reads against the dark hall
            sil = np.zeros((H, W), np.uint8)
            pts = np.array([[cx - hh * 0.17, foot - hh * 0.78], [cx + hh * 0.17, foot - hh * 0.78], [cx + hh * 0.13, foot - hh * 0.42],
                            [cx + hh * 0.10, foot], [cx - hh * 0.10, foot], [cx - hh * 0.13, foot - hh * 0.42]], np.int32)
            cv2.fillPoly(sil, [pts], 255); cv2.circle(sil, (cx, int(foot - hh * 0.88)), int(hh * 0.10), 255, -1, cv2.LINE_AA)
            glow = cv2.GaussianBlur(cv2.dilate(sil, np.ones((9, 9), np.uint8)), (0, 0), 6).astype(np.float32)[..., None] / 255
            fr[:] = np.clip(fr.astype(np.float32) + glow * np.array([60, 70, 90]), 0, 255).astype(np.uint8)
            fr[sil > 0] = col
    if 'siren_lights' in fx:   # slow (0.5 Hz), soft red/blue drift at the frame edges, never a strobe
        p = 0.5 + 0.5 * math.sin(t * math.pi)
        col = np.array([60, 40, 230]) * p + np.array([230, 90, 40]) * (1 - p)
        edge = (1 - vignette()) * 1.1
        fr = np.clip(fr.astype(np.float32) + edge * col * 0.18, 0, 255).astype(np.uint8)
    if 'siren_soft' in fx:   # slow red wash from the ambulance lights
        p = 0.5 + 0.5 * math.sin(t * 2.6)
        edge = (1 - vignette()) * 1.2
        fr = np.clip(fr.astype(np.float32) + edge * np.array([20, 20, 120]) * p * 0.6, 0, 255).astype(np.uint8)
    if 'curtains_close' in fx:
        k = ease((dt - 0.3) / 1.0)
        for side in (0, 1):
            wpx = int(W * 0.5 * k)
            if wpx <= 0: continue
            panel = np.zeros((H, wpx, 3), np.uint8)
            xx = np.arange(wpx)
            fold = (0.75 + 0.25 * np.sin(xx / 22.0))[None, :, None]
            panel[:] = (np.array([70, 34, 18]) * fold).astype(np.uint8)   # heavy navy curtain (BGR)
            if side == 0: fr[:, :wpx] = panel
            else: fr[:, W - wpx:] = panel[:, ::-1]
    if 'eyes_now' in fx:
        eyes(fr, t + 1.0, st)
    if 'sign_nopets' in fx:
        put(fr, panel_rgba(420, 150, 12, (235, 225, 205, 255), outline=(60, 40, 25, 255), width=8), W / 2, H * 0.52)
        put(fr, text_rgba('NO PETS', F_ANTON(96), (150, 30, 30), shadow=False), W / 2, H * 0.52)
    if 'key_tag' in fx and dt > 1.2:
        k = ease((dt - 1.2) / 0.45)
        kx, ky = W * (0.50 - 0.08 * k), H * (0.50 + 0.10 * k)   # slides off the countertop toward you
        put(fr, panel_rgba(120, 72, 14, (200, 160, 70, 255), outline=(70, 45, 15, 255), width=5), kx, ky, min(1, k * 3))
        put(fr, text_rgba('22', F_ANTON(56), (40, 25, 10), shadow=False), kx, ky, min(1, k * 3))
    if 'phone64' in fx and t >= t_of(47) - 0.1:
        phone_overlay(fr, '64%', False, t)
    if 'phone_call' in fx:
        phone_overlay(fr, '9%', t >= t_of(175) - 0.1, t, connected=t >= t_of(178) - 0.05)
    if 'temp_readout' in fx:
        val = '58°F' if t < t_of(66) else '51°F'
        put(fr, text_rgba(val, F_ANTON(150), (150, 210, 255), stroke=2), W * 0.78, H * 0.35)
    if 'temp_9' in fx:
        put(fr, text_rgba('9°F', F_ANTON(170), (150, 210, 255), stroke=2), W * 0.78, H * 0.35)
    if 'alarm_anim' in fx:
        fr = alarm_fx(fr, shot, t)
    if 'co_plume' in fx:
        fr = co_plume(fr, shot, t)
    if 'no_battery' in fx and t >= t_of(150) - 0.1:
        k = ease((t - t_of(150) - 0.15) / 0.3) if 'alarm_anim' in fx else 1.0
        put(fr, panel_rgba(560, 90, 18, (200, 40, 40, 235)), W / 2, H * 0.74, k)
        put(fr, text_rgba('NO BATTERY BACKUP', F_ANTON(56), WHITE, shadow=False), W / 2, H * 0.74, k)
    if 'diagram_20ft' in fx and t_of(154) - 0.2 <= t < t_of(155) - 1.5:
        k = ease((t - t_of(154) + 0.2) / 0.4)
        y = int(H * 0.7)
        cv2.arrowedLine(fr, (int(W * 0.25), y), (int(W * 0.72), y), (71, 181, 255), 8, cv2.LINE_AA, tipLength=0.04)
        cv2.arrowedLine(fr, (int(W * 0.72), y), (int(W * 0.25), y), (71, 181, 255), 8, cv2.LINE_AA, tipLength=0.04)
        put(fr, text_rgba('20+ FEET', F_ANTON(80), AMBER, stroke=2), W * 0.485, y - 70, k)
    if 'smoke' in fx:   # soft wisps rising off the counter
        lay = np.zeros((H // 4, W // 4), np.float32)
        base_y, xs = candle_row(shot)
        for i in range(14):
            ph = (t * 0.35 + i / 14) % 1
            x = (W * xs[i] + 30 * math.sin(t * 1.3 + i * 1.7) * ph) / 4
            y = (H * base_y - 60 - 260 * ph) / 4
            cv2.circle(lay, (int(x), int(y)), int(4 + 10 * ph), 0.55 * (1 - ph), -1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 5)
        lay = cv2.resize(lay, (W, H))[..., None]
        fr = np.clip(fr.astype(np.float32) * (1 - lay * 0.85) + lay * 0.85 * np.array([175, 172, 168]), 0, 255).astype(np.uint8)
    if 'ominous' in fx:
        fr = (fr.astype(np.float32) * (0.92 + 0.08 * vignette())).astype(np.uint8)
    if 'dig' in fx:
        for i in range(30):
            ph = (t * 1.7 + i / 30) % 1
            x = int(W * 0.5 + (i - 15) * 18 * ph); y = int(H * 0.75 - 300 * ph * (1 - ph) * 2)
            cv2.circle(fr, (x, y), 4, (235, 235, 240), -1, cv2.LINE_AA)
    return fr

# ------------------------------------------------------------------ open shot (animated clip if present)
_open_cap = None
def open_frame(t):
    global _open_cap
    p = os.path.join(HERE, 'art', 'open_hallway.mp4')
    if os.path.exists(p):
        if _open_cap is None:
            _open_cap = cv2.VideoCapture(p)
        n = int(_open_cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = _open_cap.get(cv2.CAP_PROP_FPS) or 24
        fi = min(int(t * fps), n - 1)
        _open_cap.set(cv2.CAP_PROP_POS_FRAMES, fi); ok, f = _open_cap.read()
        if ok:
            f = cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC)
            extra = t - (n - 1) / fps
            if extra > 0:   # clip has ended: keep pushing in slowly on the empty carrier instead of freezing
                z = 1 + 0.035 * extra
                M = cv2.getRotationMatrix2D((W * 0.62, H * 0.6), 0, z)
                f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            return f
    return None

# ------------------------------------------------------------------ frame
def camera(layer, cam, u):
    z0, z1, cx0, cy0, cx1, cy1 = cam
    z = z0 + (z1 - z0) * u; cx = cx0 + (cx1 - cx0) * u; cy = cy0 + (cy1 - cy0) * u
    s = z * W / BGW
    # keep the view inside the canvas
    hw, hh = W / (2 * s), H / (2 * s)
    px = min(max(cx * BGW, hw), BGW - hw); py = min(max(cy * BGH, hh), BGH - hh)
    M = np.float32([[s, 0, W / 2 - s * px], [0, s, H / 2 - s * py]])
    return cv2.warpAffine(layer, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

CLEAN = False
# gamma lift for dark scenes: shadows come up a lot, highlights barely move
LIFT_LUT = np.clip(255 * (np.arange(256) / 255.0) ** 0.72 * 0.96 + 6, 0, 255).astype(np.uint8)
BRIGHT_LUT = np.clip(255 * (np.arange(256) / 255.0) ** 0.58 * 0.95 + 10, 0, 255).astype(np.uint8)   # cold-open walls readable on phones

def frame_at(t):
    shot = shot_at(t)
    u = (t - shot['start']) / max(shot['end'] - shot['start'], 0.01)
    bg = shot['bg']
    if bg == 'BLACK':
        fr = np.zeros((H, W, 3), np.uint8)
    elif bg == 'STAT':
        fr = stat_frame(t, shot['start'])
    elif bg == 'SPLIT':
        fr = split_frame(t)
    elif bg == 'CHOICE':
        fr = choice_frame(t, shot['start'])
    elif bg == 'END':
        fr = end_frame(t, shot['start'])
    elif bg == 'OPEN':
        fr = open_frame(t)
        if fr is None:
            shot2 = dict(shot, bg='bg01_hallway_dark')
            fr = camera(shot_canvas(shot2, t), shot['cam'], ease(u))
    else:
        fr = camera(shot_canvas(shot, t), shot['cam'], ease(u))
    if bg not in ('STAT', 'CHOICE', 'END', 'SPLIT'):
        fr = apply_fx(fr, shot, t)
        if 'dark' in shot['fx'] or bg == 'OPEN':
            fr = cv2.LUT(fr, BRIGHT_LUT if 'bright' in shot['fx'] else LIFT_LUT)
        if 'wallstrip' in shot['fx']:   # the wall he's listening to, right at his cupped hand
            x0 = int(W * 0.62)
            strip = cv2.resize(load_bg('bg07_room22')[int(BGH * 0.10):int(BGH * 0.40), int(BGW * 0.30):int(BGW * 0.42)], (W - x0, H))
            strip = cv2.LUT((strip.astype(np.float32) * 0.85).clip(0, 255).astype(np.uint8), LIFT_LUT).astype(np.float32)
            ramp = np.clip(np.arange(W - x0) / 70.0, 0, 1) * 0.30 + 0.70          # soft corner shade, no hard edge
            strip *= ramp[None, :, None]
            yy = (np.arange(H)[:, None] - H * 0.45) / (H * 0.35); xx = np.arange(W - x0)[None, :] / 220.0
            strip *= (1 + 0.45 * np.exp(-(yy ** 2 + xx ** 2)))[..., None]          # headlamp spill where his hand is
            fr[:, x0:] = (strip * np.array([1.08, 1.0, 0.9])).clip(0, 255).astype(np.uint8)
        if 'jamb' in shot['fx']:   # drawn after the lift so your dark room stays dark
            fx = shot['fx']
            x0 = int(W * 0.60)
            cv2.rectangle(fr, (x0, 0), (x0 + 60, H), (24, 30, 38), -1)          # door frame
            cv2.rectangle(fr, (x0, 0), (x0 + 5, H), (70, 84, 100), -1)           # lit edge from your headlamp
            g = np.linspace(16, 6, W - x0 - 60).astype(np.uint8)
            fr[:, x0 + 60:] = np.stack([g + 4, g + 2, g], axis=1)[None]           # your dark room, fading away

    # shot-start whoosh punch for montage cuts
    if 'whoosh' in shot['fx'] and t - shot['start'] < 0.25:
        k = 1 - (t - shot['start']) / 0.25
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + 0.08 * k)
        fr = cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if CLEAN:   # picture only, for re-framing into vertical Shorts
        return fr
    # title card after the cold open
    title_card(fr, t, LINES[17]['end'] + 0.25)
    if bg != 'END':
        draw_status(fr, t)
        draw_chapter(fr, t)
        draw_rule(fr, t)
        draw_timestamp(fr, t)
        draw_caption(fr, t)
    # fade from black at the very start, and between the last line and the end card
    if t < 0.4:
        fr = (fr.astype(np.float32) * (t / 0.4)).astype(np.uint8)
    return fr

def render_range(t0, t1, path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path],
                         stdin=subprocess.PIPE)
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    for n in range(n0, n1):
        p.stdin.write(frame_at(n / FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True); os.makedirs(PREV, exist_ok=True)
    mode = sys.argv[1]
    if mode == 'preview':
        for x in sys.argv[2].split(','):
            t = float(x)
            cv2.imwrite(os.path.join(PREV, f'f_{t:07.2f}.jpg'), frame_at(t), [cv2.IMWRITE_JPEG_QUALITY, 85])
    elif mode == 'segments':
        only = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else None
        nseg = int(math.ceil(TOTAL / 60))
        for i in range(nseg):
            if only is not None and i not in only:
                continue
            done = os.path.join(OUT, f'seg_{i:03d}.done')
            if os.path.exists(done) and only is None:
                continue
            path = os.path.join(OUT, f'seg_{i:03d}.mp4')
            render_range(i * 60, min((i + 1) * 60, TOTAL), path)
            open(done, 'w').write('ok')
            print('segment', i, 'done', flush=True)
    elif mode == 'concat':
        nseg = int(math.ceil(TOTAL / 60))
        lst = os.path.join(OUT, 'list.txt')
        open(lst, 'w').write(''.join(f"file 'seg_{i:03d}.mp4'\n" for i in range(nseg)))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(OUT, 'video_noaudio.mp4')], check=True)
        print('joined')
    elif mode == 'clean':   # clean picture for a time range: clean T0 T1 OUT.mp4
        CLEAN = True
        render_range(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
    elif mode == 'info':
        print('total', TOTAL, 'captions', len(CAPS), 'shots', len(SHOTS))
