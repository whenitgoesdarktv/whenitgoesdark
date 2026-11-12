"""Coded puppet layer for the flat character cutouts.

build_rig(c, name, box, scale, flip) -> rig for the cutout as it is pasted (hand-placed points from rigs.py)
pose(c, rig, t, phase, amp)          -> the cutout re-posed for time t: blinks, head tilts and nods on the neck
breath(layer, x, y, t, phase, scale, drift) -> a cold-air breath cloud leaving the mouth
"""
import math
import numpy as np
import cv2
from rigs import RIGS


def build_rig(c, name, box, flip):
    """box = (base_name, base_w, base_h, crop_x, crop_y) from load_char; c is the final pasted cutout."""
    base, bw, bh, ox, oy, crop_h = box
    spec = RIGS.get(base)
    if spec is None:
        return None
    h, w = c.shape[:2]
    s = h / float(crop_h)          # the cutout was cut from the base at (ox, oy), then scaled by s
    def P(fx, fy):
        x = (fx * bw - ox) * s; y = (fy * bh - oy) * s
        if flip:
            x = w - 1 - x
        return x, y
    rig = dict(eyes=[], head=None)
    for (x0, y0, x1, y1) in spec.get('eyes', []):
        ax, ay = P(x0, y0); bx, by = P(x1, y1)
        xa, xb = sorted((ax, bx)); ya, yb = sorted((ay, by))
        pw, ph = (xb - xa) * 0.12 + 1, (yb - ya) * 0.12 + 1
        xa, xb, ya, yb = int(xa - pw), int(math.ceil(xb + pw)), int(ya - ph), int(math.ceil(yb + ph))
        if xa < 0 or ya < 0 or xb >= w or yb >= h or xb - xa < 3 or yb - ya < 3:
            continue
        rig['eyes'].append(dict(x0=xa, y0=ya, x1=xb, y1=yb, skin=_skin(c, xa, ya, xb, yb)))
    rig['eyes'] = [e for e in rig['eyes'] if e['skin'] is not None]
    hx, hy, rx, ry = spec['head']
    cx, cy = P(hx, hy); rxp, ryp = rx * bw * s, ry * bh * s
    px, py = P(*spec['pivot'])
    if 0 <= px < w and 0 <= py < h and 0 <= cx < w and 0 <= cy < h and ryp > 12:
        # generous hard ellipse: the whole head and its outline move together, so no outline is left behind
        E = np.zeros((h, w), np.float32)
        cv2.ellipse(E, (int(cx), int(cy)), (int(rxp * 1.10), int(ryp * 1.08)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        for (x0, y0, x1, y1) in spec.get('excl', []):
            ax, ay = P(x0, y0); bx, by = P(x1, y1)
            cv2.rectangle(E, (int(min(ax, bx)), int(min(ay, by))), (int(max(ax, bx)), int(max(ay, by))), 0.0, -1)
        E = cv2.GaussianBlur(E, (0, 0), max(2.0, ryp * 0.045))   # soft edge where hair, collars or props cross it
        yy = np.arange(h, dtype=np.float32)[:, None]
        band0, band1 = py - ryp * 0.16, py + ryp * 0.03      # neck band: body stays, head fades in over it
        ramp = np.clip((band1 - yy) / (band1 - band0), 0, 1)
        m = E * ramp
        core = (E > 0.99) & (yy < band0)
        rig['head'] = dict(mask=m, core=core, px=px, py=py, ry=ryp, rx=rxp, cx=cx, cy=cy)
    if 'mouth' in spec:
        rig['mouth'] = P(*spec['mouth'])
        rig['face_dir'] = 1 if rig['mouth'][0] > cx + rxp * 0.08 else (-1 if rig['mouth'][0] < cx - rxp * 0.08 else 0)
    rig['amp'] = spec.get('amp', 1.5)
    if not rig['eyes'] and rig['head'] is None:
        return None
    return rig


def _skin(c, x0, y0, x1, y1):
    """Median colour of the face around an eye, for painting the closed lid."""
    h, w = c.shape[:2]
    ex, ey = (x1 - x0), (y1 - y0)
    X0, Y0, X1, Y1 = max(0, x0 - ex // 2), max(0, y0 - ey // 3), min(w, x1 + ex // 2), min(h, y1 + ey // 2)
    sub = c[Y0:Y1, X0:X1].astype(np.int32)
    m = np.ones(sub.shape[:2], bool)
    m[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = False
    lum = sub[..., :3].mean(-1)
    m &= (sub[..., 3] > 200) & (lum > 60)
    if m.sum() < 6:
        return None
    return tuple(int(v) for v in np.median(sub[..., :3][m], axis=0))


def blink_amount(t, phase):
    """1 = closed. A blink every 2.8-4.6 s lasting 4 frames, sometimes a double blink."""
    period = 2.8 + 1.8 * ((phase * 0.6180339) % 1)
    u = (t + phase * 3.1) % period
    if u < 0.13:
        return 1.0
    if 0.36 < u < 0.47 and ((phase * 7.13) % 1) > 0.6:
        return 1.0
    return 0.0


def close_eyes(c, rig):
    out = c.copy()
    for e in rig['eyes']:
        x0, y0, x1, y1 = e['x0'], e['y0'], e['x1'], e['y1']
        w, h = x1 - x0, y1 - y0
        m = np.zeros((h, w), np.uint8)
        cv2.ellipse(m, (w // 2, h // 2), (max(1, w // 2), max(1, h // 2)), 0, 0, 360, 255, -1, cv2.LINE_AA)
        a = (m.astype(np.float32) / 255)[..., None]
        sub = out[y0:y1, x0:x1].astype(np.float32)
        sub[..., :3] = sub[..., :3] * (1 - a) + np.array(e['skin'], np.float32) * a
        out[y0:y1, x0:x1] = sub.astype(np.uint8)
        th = max(2, int(round(min(w, h * 1.6) * 0.13)))
        cy = y0 + int(h * 0.55)
        cv2.ellipse(out, ((x0 + x1) // 2, cy - th), (max(2, int(w * 0.46)), max(2, int(h * 0.22))), 0, 15, 165, (24, 20, 22, 255), th, cv2.LINE_AA)
    return out


def head_angle(t, phase, amp):
    return amp * (0.62 * math.sin(2 * math.pi * 0.21 * t + phase) + 0.38 * math.sin(2 * math.pi * 0.37 * t + 2.3 * phase))


def pose(c, rig, t, phase, amp=None, angle=None, blink=True):
    if rig is None:
        return c
    src = c
    if blink and rig['eyes'] and blink_amount(t, phase) > 0.5:
        src = close_eyes(c, rig)
    hd = rig['head']
    a = rig['amp'] if amp is None else amp
    if hd is None or (a <= 0 and angle is None):
        return src
    ang = head_angle(t, phase, a) if angle is None else angle
    nod = 0.012 * hd['ry'] * math.sin(2 * math.pi * 0.29 * t + 1.7 * phase)
    m = hd['mask']
    head = src.copy()
    head[..., 3] = (head[..., 3].astype(np.float32) * m).astype(np.uint8)
    body = src.copy()
    body[..., 3][hd['core']] = 0
    M = cv2.getRotationMatrix2D((hd['px'], hd['py']), ang, 1.0)
    M[1, 2] += nod
    h, w = c.shape[:2]
    rot = cv2.warpAffine(head, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    ha = rot[..., 3:4].astype(np.float32) / 255
    ba = body[..., 3:4].astype(np.float32) / 255
    oa = ha + ba * (1 - ha)
    rgb = (rot[..., :3].astype(np.float32) * ha + body[..., :3].astype(np.float32) * ba * (1 - ha)) / np.maximum(oa, 1e-4)
    return np.dstack([rgb, oa * 255]).clip(0, 255).astype(np.uint8)


def breath(layer, mx, my, t, phase, scale, drift=1.0, period=3.4):
    """Cold-air breath on a low-res float layer: a soft cloud leaves the mouth on each exhale,
    pushes out in front of the face, grows, rises and fades."""
    u = ((t + phase * 1.9) % period) / period
    if u > 0.50:
        return
    k = u / 0.50
    for j in range(7):
        kk = k - j * 0.045
        if kk <= 0:
            continue
        x = mx + scale * (0.30 + 2.6 * kk) * drift + scale * 0.20 * math.sin(j * 2.1 + phase)
        y = my + scale * (0.10 - 1.10 * kk * kk) + scale * 0.10 * j
        r = scale * (0.16 + 0.80 * kk) * (1 - 0.07 * j)
        a = 0.85 * (1 - kk) ** 1.2 * min(1.0, kk / 0.05)
        cv2.circle(layer, (int(x), int(y)), max(1, int(r)), max(a, 0.0), -1, cv2.LINE_AA)
