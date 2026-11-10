"""Hotel trailer Short (1080x1920), cut from a clean (no overlay) render of the cold open.

Usage:
  python3 -I render_long.py clean 0 <T_END> out/clean_open.mp4      (once)
  python3 -I render_short.py out/clean_open.mp4 out/short_noaudio.mp4 [--preview T1,T2,...]
"""
import sys, os, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # wigd_build: Season 1 trailer helpers (fonts, text, panels, upscaler)
sys.path.insert(0, HERE)
import render_trailer as RT
import timeline as TL

W, H, FPS = 1080, 1920, 30
AMBER, WHITE, BGC = RT.AMBER, RT.WHITE, RT.BG
B = TL.build(); t_of = B['t_of']; LINES = B['lines']
OPEN_END = LINES[17]['end'] + 0.45          # cold open ends just after "...everyone in this hotel."
END_START = OPEN_END
END_END = END_START + 4.5
TOTAL = END_END
CAP_Y = 1380

# shot crops on the clean 1920x1080 source: (start, end, cx0, cx1, h0, h1)
def _shots():
    cuts = [0.0] + [t_of(f) - 0.15 for f, *_ in TL.SHOTS[1:] if t_of(f) - 0.15 < OPEN_END] + [OPEN_END]
    out = []
    for i in range(len(cuts) - 1):
        a, b = cuts[i], cuts[i + 1]
        if i == 0:
            out.append((a, b, 1560, 1330, 1080, 1000))   # follow the light to the open carrier
        else:
            out.append((a, b, 960, 960, 1080, 1010))     # slow push-in, centred
    return out
SHOTS = _shots()

def crop(src, t):
    for a, b, cx0, cx1, h0, h1 in SHOTS:
        if a <= t < b:
            break
    u = RT.ease((t - a) / max(b - a, 1e-6))
    h = h0 + (h1 - h0) * u; w = h * 9 / 16; cx = cx0 + (cx1 - cx0) * u
    x0 = min(max(cx - w / 2, 0), 1920 - w); y0 = (1080 - h) / 2
    xi, yi = int(x0), int(y0); wi, hi = int(math.ceil(w)) + 2, int(math.ceil(h)) + 2
    patch = src[yi:yi + hi, xi:xi + wi]
    up = RT.SR.upsample(patch)
    s = W / (w * 4)
    M = np.float32([[s, 0, -(x0 - xi) * 4 * s], [0, s, -(y0 - yi) * 4 * s]])
    return cv2.warpAffine(up, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)

# captions: short chunks (max ~16 characters) from the master word timings
import json
WORDS = [dict(w, text=w['text'].replace('"', '').upper()) for w in B['words'] if w['line'] <= 17]
STOP = set("A AN THE AND OR BUT OF TO IN ON AT BY FOR WITH FROM IS IT IT'S YOU YOUR HE SO THEN ONE THEM IS THAT".split())
CHUNKS = []
cur = []
for w in WORDS:
    if cur and (len(' '.join(x['text'] for x in cur + [w])) > 16 or w['line'] != cur[-1]['line'] or w['start'] - cur[-1]['end'] > 0.5):
        CHUNKS.append(cur); cur = []
    cur.append(w)
    if w['text'][-1:] in '.?!,' and len(' '.join(x['text'] for x in cur)) > 8:
        CHUNKS.append(cur); cur = []
if cur: CHUNKS.append(cur)
CAPS = []
for j, c in enumerate(CHUNKS):
    cands = [x['text'] for x in c if x['text'].strip('.,?!').upper() not in STOP]
    PRIORITY = ('KILL', 'EMPTY', 'SCRATCHING', 'HUM', 'HUM?', 'WALLS?', 'WALLS', 'STOPS', 'HEAD.', 'NOBODY', 'DARK')
    pri = [x for x in cands if x.strip('.,?!') in [p.strip('.,?!') for p in PRIORITY]]
    key = pri[0] if pri else (max(cands, key=len) if cands else c[-1]['text'])
    end = c[-1]['end'] + 0.35
    if j + 1 < len(CHUNKS): end = min(end, CHUNKS[j + 1][0]['start'])
    CAPS.append(dict(words=[(x['text'], x['start']) for x in c], key=key, start=c[0]['start'], end=min(end, OPEN_END)))

_cc = {}
def cap_img(ci, n):
    if (ci, n) in _cc: return _cc[(ci, n)]
    c = CAPS[ci]; f = RT.F_CAP
    words = [w for w, _ in c['words']]; sp = f.getlength(' ')
    widths = [f.getlength(w) for w in words]; total = sum(widths) + sp * (len(words) - 1)
    pad = 40
    img = Image.new('RGBA', (int(total) + pad * 2, 160), (0, 0, 0, 0)); sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img); ds = ImageDraw.Draw(sh); x = pad
    for i, w in enumerate(words):
        if i < n:
            col = AMBER if w == c['key'] else WHITE
            ds.text((x + 4, 36), w, font=f, fill=(0, 0, 0, 200), stroke_width=7, stroke_fill=(0, 0, 0, 200))
            d.text((x, 30), w, font=f, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
        x += widths[i] + sp
    out = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), img)
    _cc[(ci, n)] = (out, total); return _cc[(ci, n)]

def caption(cv, t):
    for ci, c in enumerate(CAPS):
        if c['start'] <= t < c['end']:
            n = max(1, sum(1 for _, s in c['words'] if s <= t + 0.02))
            img, _ = cap_img(ci, n); full = cap_img(ci, len(c['words']))[1]
            pop = 1.0 + 0.08 * (1 - RT.ease((t - c['start']) / 0.12))
            if full > 860: pop *= 860 / full
            RT.paste_center(cv, img, W / 2, CAP_Y, 1.0, pop)
            return

HOOK1 = RT.text_img("WHAT'S IN", RT.F_HOOK)
HOOK2 = RT.text_img('THE WALLS?', RT.F_HOOK, colors=[('WALLS?', AMBER)])
def hook(cv, t):
    if t >= 4.6: return
    a = 1 - RT.ease((t - 4.3) / 0.3)
    RT.paste_center(cv, HOOK1, W / 2, 300, a); RT.paste_center(cv, HOOK2, W / 2, 420, a)

def end_card(cv, t, lando):
    dt = t - END_START
    k = lambda d0, dur=0.3: RT.ease((dt - d0) / dur)
    l1 = RT.text_img('THE WALLS', RT.F_END_BIG, colors=[('WALLS', AMBER)])
    l2 = RT.text_img('OR THE HUM?', RT.F_END_BIG, colors=[('HUM?', AMBER)])
    RT.paste_center(cv, l1, W / 2, 330 + 20 * (1 - k(0)), k(0)); RT.paste_center(cv, l2, W / 2, 470 + 20 * (1 - k(0.05)), k(0.05))
    for i, lab in enumerate(['WALLS', 'HUM']):
        pill = RT.rounded_panel(300, 120, 60, (12, 16, 26, 230), outline=(255, 255, 255, 230), width=5)
        d = ImageDraw.Draw(pill); lw = RT.F_PILL.getlength(lab); d.text(((300 - lw) / 2, 14), lab, font=RT.F_PILL, fill=WHITE)
        RT.paste_center(cv, pill, W / 2 + (-170 if i == 0 else 170), 650, k(0.2 + 0.06 * i))
    RT.paste_center(cv, RT.text_img('Which one tries to kill everyone?', RT.F_END_SMALL, fill=(215, 220, 230), stroke=0), W / 2, 760, k(0.3))
    bt = RT.text_img('FULL VIDEO ON THE CHANNEL', RT.F_END_BOX, fill=(14, 14, 18), stroke=0, shadow=False)
    box = RT.rounded_panel(bt.width + 50, 132, 22, AMBER + (255,)); box.alpha_composite(bt, (25, (132 - bt.height) // 2 + 4))
    pulse = 1.0 + 0.025 * math.sin(max(dt - 0.8, 0) * 5.0)
    RT.paste_center(cv, box, W / 2, 935, k(0.45), (0.94 + 0.06 * k(0.45)) * pulse)
    RT.paste_center(cv, RT.text_img('Winter Storm: 12 Hours Trapped in a Hotel', RT.font('Barlow-SemiBold.ttf', 38), fill=(205, 210, 222), stroke=0), W / 2, 1040, k(0.55))
    lx, ly = 300, 1270
    RT.paste_center(cv, lando, lx, ly, k(0.75))
    t1 = RT.text_img('THE REAL LANDO', RT.F_LANDO, fill=AMBER, stroke=0)
    t2 = RT.text_img("Don't worry, he's OK.", RT.font('Barlow-SemiBold.ttf', 44), fill=WHITE, stroke=0)
    cv.alpha_composite(RT._fade(t1, k(0.85)), (lx + 150, ly - 95)); cv.alpha_composite(RT._fade(t2, k(0.9)), (lx + 150, ly - 15))

def render(src, out, preview=None):
    rd = RT.Reader(src)
    lando = RT.build_lando(RT.Reader('/home/claude/src_s1/s1_full.mp4'))
    eb = crop(rd.get(14.0), 14.0)                      # end-card background: the dark hallway, blurred
    eb = cv2.GaussianBlur(eb, (0, 0), 18); eb = (eb.astype(np.float32) * 0.42).astype(np.uint8)
    rd = RT.Reader(src)
    times = preview or [i / FPS for i in range(int(round(TOTAL * FPS)))]
    proc = None if preview else subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                                  '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for t in times:
        if t >= END_START:
            cv = RT.to_pil(eb.copy()); end_card(cv, t, lando)
            fr = (np.array(cv.convert('RGB')).astype(np.float32) * (0.15 + 0.85 * RT.ease((t - END_START) / 0.15))).astype(np.uint8)
        else:
            cv = RT.to_pil(crop(rd.get(t), t)); hook(cv, t); caption(cv, t)
            fr = np.array(cv.convert('RGB'))
            if END_START - 0.12 <= t:
                fr = (fr.astype(np.float32) * (0.25 + 0.75 * (END_START - t) / 0.12)).astype(np.uint8)
        if preview:
            cv2.imwrite(f'{out}_{t:06.2f}.jpg', cv2.cvtColor(fr, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        else:
            proc.stdin.write(fr.tobytes())
    if proc:
        proc.stdin.close(); proc.wait()

if __name__ == '__main__':
    pv = [float(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 and sys.argv[3] == '--preview' else None
    print('open ends', round(OPEN_END, 2), 'total', round(TOTAL, 2), 'shots', len(SHOTS), 'captions', len(CAPS))
    render(sys.argv[1], sys.argv[2], pv)
