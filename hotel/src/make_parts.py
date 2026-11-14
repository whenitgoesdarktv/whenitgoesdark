"""Cut the final hotel video into 4 vertical parts (720x1280, under 10 MB each) for TikTok, Instagram and Facebook.
Each part ends on a cliffhanger; header "PART n OF 4", a YouTube line, and a "PART n+1 IS ON MY PROFILE" tag at the end."""
import os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(HERE), 'fonts')
SRC = os.path.join(HERE, 'out', 'hotel_final.mp4')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out', 'parts')
os.makedirs(OUT, exist_ok=True)
W, H = 720, 1280
CUTS = [(0.0, 174.62), (174.62, 273.77), (273.77, 368.85), (368.85, 521.633)]
AMBER = (255, 181, 71)
TARGET_BYTES = 9.4e6

def font(name, size, var=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if var:
        try: f.set_variation_by_name(var)
        except Exception: pass
    return f

def ctext(d, y, txt, f, fill, stroke=0):
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

def background():
    im = cv2.imread(os.path.join(HERE, 'art', 'bg02_lodge_exterior_dusk.png'))
    h, w = im.shape[:2]
    s = max(W / w, H / h)
    im = cv2.resize(im, (int(w * s) + 1, int(h * s) + 1), interpolation=cv2.INTER_AREA)
    y0 = (im.shape[0] - H) // 2; x0 = (im.shape[1] - W) // 2
    im = im[y0:y0 + H, x0:x0 + W]
    im = cv2.GaussianBlur(im, (0, 0), 18).astype(np.float32) * 0.32
    yy = np.linspace(-1, 1, H)[:, None]
    im *= (1 - 0.35 * yy ** 2)[..., None]
    return cv2.cvtColor(im.clip(0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)

def overlays(n):
    base = Image.fromarray(background()).convert('RGBA')
    d = ImageDraw.Draw(base)
    ctext(d, 236, 'WINTER STORM: TRAPPED IN A HOTEL', font('Oswald[wght].ttf', 34, 'SemiBold'), (225, 230, 240))
    ctext(d, 282, f'PART {n} OF 4', font('Anton-Regular.ttf', 84), AMBER, stroke=2)
    ctext(d, 884, 'Full 9-min video on YouTube', font('Barlow-SemiBold.ttf', 30), (215, 220, 230))
    ctext(d, 922, 'When It Goes Dark', font('Barlow-Bold.ttf', 30), (255, 255, 255))
    base.convert('RGB').save(os.path.join(OUT, f'bg_{n}.png'))
    tag = Image.new('RGBA', (W, 140), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    txt = f'PART {n + 1} IS ON MY PROFILE' if n < 4 else 'FOLLOW FOR THE NEXT STORY'
    f = font('Anton-Regular.ttf', 50)
    tw = td.textlength(txt, font=f)
    td.rounded_rectangle(((W - tw) / 2 - 28, 18, (W + tw) / 2 + 28, 118), 24, fill=AMBER + (255,))
    td.text(((W - tw) / 2, 30), txt, font=f, fill=(14, 14, 18))
    tag.save(os.path.join(OUT, f'tag_{n}.png'))

def build(n, a, b):
    overlays(n)
    dur = b - a
    vbit = int((TARGET_BYTES * 8 / dur) * 0.97 - 64000)
    bg, tag = os.path.join(OUT, f'bg_{n}.png'), os.path.join(OUT, f'tag_{n}.png')
    out = os.path.join(OUT, f'hotel_part{n}.mp4')
    fc = (f"[0:v]scale={W}:-2,setsar=1[fg];[1:v][fg]overlay=0:(H-h)/2[v1];"
          f"[v1][2:v]overlay=0:990:enable='gte(t,{dur - 3.2:.2f})'[v]")
    af = f"afade=t=in:st=0:d=0.12,afade=t=out:st={dur - 0.25:.2f}:d=0.25"
    common = ['-ss', f'{a:.3f}', '-t', f'{dur:.3f}', '-i', SRC, '-loop', '1', '-i', bg, '-loop', '1', '-i', tag,
              '-filter_complex', fc, '-map', '[v]', '-map', '0:a', '-af', af, '-r', '30', '-t', f'{dur:.3f}',
              '-c:v', 'libx264', '-preset', 'slow', '-b:v', str(vbit), '-pix_fmt', 'yuv420p']
    plog = os.path.join(OUT, f'pass{n}')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + common + ['-pass', '1', '-passlogfile', plog, '-an', '-f', 'mp4', os.devnull], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + common + ['-pass', '2', '-passlogfile', plog, '-c:a', 'aac', '-b:a', '64k',
                                                            '-movflags', '+faststart', out], check=True)
    print(n, round(dur, 1), 's', os.path.getsize(out), 'bytes', vbit, 'bps', flush=True)

if __name__ == '__main__':
    for i, (a, b) in enumerate(CUTS, 1):
        build(i, a, b)
