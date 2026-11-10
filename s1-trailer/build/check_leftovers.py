"""For every trailer frame, check whether the crop window includes any of the source's burned-in caption pixels."""
import sys
sys.path.insert(0, '/home/claude/wigd_build')
import numpy as np, cv2
import render_trailer as R

src = sys.argv[1]
rd = R.Reader(src); rd_dark = R.Reader(src)
bad = []
for i in range(int(round(R.END_START * R.FPS))):
    t = i / R.FPS
    a, b, p = R.shot_for(t)
    if p.get('choice'):
        continue
    off = [s for s in R.SEGMENTS if s[0] <= t < s[1]][0][2]
    f = rd_dark.get(R.DARK_SRC + (t - a)) if p.get('dark') else rd.get(t + off)
    u = R.ease((t - a) / max(b - a, 1e-6))
    h = p['h0'] + (p['h1'] - p['h0']) * u; w = h * 9 / 16
    y0 = p['bottom'] - h if 'bottom' in p else p['ytop0'] + (p['ytop1'] - p['ytop0']) * u
    y1 = min(y0 + h, p.get('fill', 1080), p.get('bottom', 1080))
    x0 = p['cx'] - w / 2; x1 = x0 + w
    band = f[880:1000].astype(np.int16)
    bgr = band
    white = (bgr.min(axis=2) > 225)
    amber = (np.abs(bgr[..., 2] - 255) < 30) & (np.abs(bgr[..., 1] - 181) < 30) & (np.abs(bgr[..., 0] - 71) < 45)
    m = (white | amber)
    ys, xs = np.nonzero(m)
    ys = ys + 880
    inside = (xs >= x0) & (xs < x1) & (ys >= max(y0, 0)) & (ys < y1)
    n = int(inside.sum())
    if n > 25:
        bad.append((round(t, 2), n, int(xs[inside].min()), int(xs[inside].max()), int(ys[inside].min())))
print('frames checked', int(round(R.END_START * R.FPS)))
print('frames with possible caption pixels inside the crop:', len(bad))
for b in bad[:60]:
    print(b)
