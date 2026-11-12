# ---------------------------------------------------------------- coded animation for the slow spots (exec'd inside render_long)
def cam_at(shot, t):
    u = (t - shot['start']) / max(shot['end'] - shot['start'], 0.01); e = ease(u)
    z0, z1, cx0, cy0, cx1, cy1 = shot['cam']
    z = z0 + (z1 - z0) * e
    cx = min(max(cx0 + (cx1 - cx0) * e, 0.5 / z), 1 - 0.5 / z)
    cy = min(max(cy0 + (cy1 - cy0) * e, 0.5 / z), 1 - 0.5 / z)
    return z, cx, cy

def p2f(shot, t, px, py):
    z, cx, cy = cam_at(shot, t)
    return (0.5 + z * (px - cx)) * W, (0.5 + z * (py - cy)) * H, z

def word_t(line, word):
    for w in WORDS:
        if w['line'] == line and word.lower() in w['text'].lower():
            return w['start']
    return t_of(line)

def draw_arc(fr, cx, cy, r, frac, col, th):
    if frac <= 0: return
    cv2.ellipse(fr, (int(cx), int(cy)), (int(r), int(r)), -90, 0, 360 * min(frac, 1), col, th, cv2.LINE_AA)

def pill(txt, f, fg, bg, pad=26, h=None):
    tx = text_rgba(txt, f, fg, shadow=False)
    ph = h or tx.shape[0] + 4
    p = panel_rgba(tx.shape[1] + pad * 2 - 48, ph, ph // 2, bg)
    put(p, tx, p.shape[1] / 2, p.shape[0] / 2)
    return p

def battery_icon(fr, cx, cy, k_draw, k_x, scale=1.0):
    """Empty battery outline that draws itself, then a red X strikes it."""
    w, h = int(130 * scale), int(64 * scale)
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    pts = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)]
    total = 2 * (w + h); done = total * min(k_draw, 1)
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        seg = abs(bx - ax) + abs(by - ay)
        if done <= 0: break
        f = min(1, done / seg)
        cv2.line(fr, (ax, ay), (int(ax + (bx - ax) * f), int(ay + (by - ay) * f)), (245, 245, 245), max(3, int(6 * scale)), cv2.LINE_AA)
        done -= seg
    if k_draw >= 1:
        cv2.rectangle(fr, (x0 + w, int(cy - h * 0.22)), (x0 + w + int(12 * scale), int(cy + h * 0.22)), (245, 245, 245), -1)
        # a sliver of red charge blinking, then nothing
    if k_x > 0:
        for (ax, ay), (bx, by) in (((x0 - 14, y0 - 14), (x0 + w + 14, y0 + h + 14)), ((x0 + w + 14, y0 - 14), (x0 - 14, y0 + h + 14))):
            f = min(1, k_x * 2) if ax < bx else max(0, min(1, k_x * 2 - 1))
            if f > 0:
                cv2.line(fr, (ax, ay), (int(ax + (bx - ax) * f), int(ay + (by - ay) * f)), (60, 60, 235), max(5, int(10 * scale)), cv2.LINE_AA)

ALARM_C = (0.581, 0.283)   # bg10 alarm body centre (plate fractions)
ALARM_LED = (0.5815, 0.397)

def alarm_fx(fr, shot, t):
    """CO alarm beat: the headlamp finds it, its light is dead, it only runs on hotel power, no battery."""
    dt = t - shot['start']
    ax, ay, z = p2f(shot, t, *ALARM_C)
    # 1) the beam sweeps in from the left and settles on the alarm
    k = ease(dt / 1.4)
    bx = (0.18 + (ax / W - 0.18) * k) + 0.012 * math.sin(t * 2.3)
    by = (0.62 + (ay / H - 0.62) * k) + 0.010 * math.sin(t * 1.9)
    m = beam_mask(bx, by, True)
    fr = np.clip(fr.astype(np.float32) * (0.45 + 0.75 * m), 0, 255).astype(np.uint8)
    lx, ly, _ = p2f(shot, t, *ALARM_LED)
    r = 0.030 * W * z
    # 2) "Its light is off": a ring draws itself around the dead LED, with a tag
    t1 = t_of(148)
    if t >= t1 - 0.1:
        kk = ease((t - t1 + 0.1) / 0.5)
        draw_arc(fr, lx, ly, r, kk, (60, 60, 235), 6)
        if kk >= 1:
            put(fr, pill('LIGHT: OFF', F_OSW(40), WHITE, (200, 40, 40, 235)), lx + r + 150, ly, ease((t - t1 - 0.4) / 0.3))
    # 3) "It runs on the hotel's power": a cord runs from the alarm to the wall and the power cuts
    t2 = t_of(149)
    if t >= t2 - 0.1:
        kk = ease((t - t2 + 0.1) / 0.6)
        x_end = int(lx - (lx - 0.06 * W) * kk)
        cv2.line(fr, (int(ax - 0.10 * W * z), int(ay)), (x_end, int(ay)), (200, 205, 215), 5, cv2.LINE_AA)
        if kk >= 1:
            a = ease((t - t2 - 0.5) / 0.3)
            put(fr, pill('HOTEL POWER: OFF', F_OSW(40), WHITE, (30, 34, 44, 235)), 0.20 * W, ay - 70, a)
    # 4) "No battery backup": empty battery draws on, then a red X
    t3 = t_of(150)
    if t >= t3 - 0.1:
        kd = ease((t - t3 + 0.1) / 0.6); kx = ease((t - t3 - 0.55) / 0.45)
        battery_icon(fr, W / 2 - 390, H * 0.74, kd, kx, 0.9)
    return fr

_noise = None
def noise_field():
    global _noise
    if _noise is None:
        rng = np.random.default_rng(11)
        n = rng.random((135, 240)).astype(np.float32)
        a = cv2.GaussianBlur(n, (0, 0), 6)
        b = cv2.GaussianBlur(rng.random((135, 240)).astype(np.float32), (0, 0), 3)
        a = (a - a.mean()) / (a.std() + 1e-6); b = (b - b.mean()) / (b.std() + 1e-6)
        _noise = (a, b)
    return _noise

CO_SRC = (0.37, 0.446)   # bg05 generator top (plate fractions)
def co_plume(fr, shot, t):
    """Carbon monoxide as you'd never see it: a widening shimmer rising off the generator, no colour at all."""
    dt = t - shot['start']
    sx, sy, z = p2f(shot, t, *CO_SRC)
    a, b = noise_field()
    hh, ww = H // 8, W // 8
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    na = cv2.resize(np.roll(a, int(t * 9) % a.shape[0], axis=0), (ww, hh))
    nb = cv2.resize(np.roll(b, int(-t * 6) % b.shape[1], axis=1), (ww, hh))
    reach = (0.10 + 0.95 * ease(dt / 6.0)) * W / 8
    dxs = xx - sx / 8; dys = (yy - sy / 8) * 1.4 + 0.25 * np.abs(dxs)
    d = np.sqrt(dxs ** 2 + np.minimum(dys, 0) ** 2 * 0.6 + np.maximum(dys, 0) ** 2 * 3.0)
    m = np.clip(1 - d / max(reach, 1), 0, 1) ** 0.7
    amp = 11.0
    dx = amp * m * np.sin(yy / 2.3 - t * 3.1 + 1.6 * na)
    dy = amp * 0.7 * m * np.cos(xx / 2.9 + t * 2.4 + 1.6 * nb)
    gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
    mx = gx + cv2.resize(dx, (W, H)); my = gy + cv2.resize(dy, (W, H))
    fr = cv2.remap(fr, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # "no color" / "no smell" tags pop on the words
    for i, (word, label) in enumerate((('color', 'NO COLOR'), ('smell', 'NO SMELL'))):
        tw = word_t(125, word)
        if t >= tw - 0.05:
            k = ease((t - tw + 0.05) / 0.22)
            put(fr, pill(label, F_ANTON(64), WHITE, (20, 22, 30, 225)), W * (0.70 if i == 0 else 0.70), H * (0.30 if i == 0 else 0.45), k, )
    return fr

def stat_frame(t, t0):
    fr = np.full((H, W, 3), (18, 14, 12), np.uint8)
    dt = t - t0
    k = ease(min(1, dt / 2.2))
    n = int(round(k * 100))
    put(fr, text_rgba(f'{n}+' if n >= 100 else f'{n}', F_ANTON(200), RED, stroke=2), W / 2, 250, ease(dt / 0.3))
    # 100 people, filling in one by one
    cols, rows, cw, rh = 25, 4, 46, 74
    gx0, gy0 = W / 2 - cols * cw / 2 + cw / 2, 440
    for i in range(100):
        r_, c_ = divmod(i, cols)
        x, y = int(gx0 + c_ * cw), int(gy0 + r_ * rh)
        on = i < n
        pop = 1.0
        if on and i >= n - 4 and n < 100:
            pop = 1.25
        col = (72, 72, 232) if on else (58, 52, 50)
        s = 1.0 * pop
        cv2.circle(fr, (x, y - int(18 * s)), int(9 * s), col, -1, cv2.LINE_AA)
        cv2.ellipse(fr, (x, y + int(12 * s)), (int(14 * s), int(19 * s)), 0, 180, 360, col, -1, cv2.LINE_AA)
        cv2.rectangle(fr, (x - int(14 * s), y + int(12 * s)), (x + int(14 * s), y + int(16 * s)), col, -1)
    put(fr, text_rgba('people die every year in the US', F_OSW(54, 'SemiBold'), WHITE), W / 2, 790, ease((dt - 0.6) / 0.4))
    put(fr, text_rgba('from carbon monoxide from portable generators', F_OSW(44, 'Regular'), (215, 220, 230)), W / 2, 865, ease((dt - 0.9) / 0.4))
    return fr

_frost = None
def frost_tex():
    global _frost
    if _frost is None:
        rng = np.random.default_rng(5)
        n = rng.random((H // 2, W // 4)).astype(np.float32)
        n = cv2.GaussianBlur(n, (0, 0), 1.2)
        n = (n - n.min()) / (n.max() - n.min())
        _frost = cv2.resize(n, (W // 2, H), interpolation=cv2.INTER_LINEAR) ** 0.8
    return _frost

SPLIT_T0 = None
def split_frame(t, a_label='STAY INSIDE', b_label='GO OUT INTO THE STORM'):
    global SPLIT_T0
    if SPLIT_T0 is None:
        SPLIT_T0 = next((s['start'] for s in SHOTS if s['bg'] == 'SPLIT'), t)
    dt = max(0.0, t - SPLIT_T0)
    L = load_bg('bg05_lobby_fire'); R = load_bg('bg11_porch_blizzard')
    zk = 1 + 0.06 * ease(min(dt / 10.0, 1))   # slow push-in on both sides
    def side(img, x0f, x1f):
        x0, x1 = int(BGW * x0f), int(BGW * x1f)
        cx, cy = (x0 + x1) / 2, BGH / 2
        hw, hh = (x1 - x0) / 2 / zk, BGH / 2 / zk
        crop = img[int(cy - hh):int(cy + hh), int(cx - hw):int(cx + hw)]
        return cv2.resize(crop, (W // 2, H))
    l = side(L, 0.2, 0.7); r = side(R, 0.25, 0.75)
    fl = 1 + 0.05 * math.sin(t * 9.1) * math.sin(t * 5.3 + 1)
    l = (l.astype(np.float32) * np.array([0.85, 0.95, 1.1]) * fl).clip(0, 255).astype(np.uint8)
    # the side being described is lit, the other one waits in shadow
    t156, t157 = t_of(156), t_of(157)
    wl = 0.62 if t157 - 0.1 <= t < t157 + 4.2 else 1.0
    wr = 0.62 if t156 - 0.1 <= t < t157 - 0.1 else 1.0
    l = (l.astype(np.float32) * wl).astype(np.uint8); r = (r.astype(np.float32) * wr).astype(np.uint8)
    fr = np.hstack([l, r])
    fx_snow(fr[:, W // 2:], t, 120)
    # frost creeping in from the edges of the cold side: fine crystals, never over the middle
    kf = ease((t - t157) / 3.5)
    if kf > 0:
        tex = frost_tex()
        hw = W // 2
        xn = np.linspace(0, 1, hw)[None, :]; yn = np.linspace(0, 1, H)[:, None]
        edge = np.maximum(np.maximum(np.maximum(0, 0.22 - xn) / 0.22, np.maximum(0, xn - 0.80) / 0.20),
                          np.maximum(np.maximum(0, yn - 0.80) / 0.20, np.maximum(0, 0.10 - yn) / 0.10))
        reach = 0.35 + 0.65 * kf
        fm = np.clip((edge * reach * 1.3 - (1 - tex) * 0.55), 0, 1) * 0.6 * kf
        sub = fr[:, hw:].astype(np.float32)
        fr[:, hw:] = (sub * (1 - fm[..., None]) + fm[..., None] * np.array([250, 240, 228])).astype(np.uint8)
    cv2.line(fr, (W // 2, 0), (W // 2, H), (255, 255, 255), 4)
    put(fr, text_rgba(a_label, F_ANTON(70), AMBER, stroke=2), W * 0.25, 170)
    put(fr, text_rgba('Warm. The air is poison.', F_BAR(34), WHITE), W * 0.25, 250)
    put(fr, text_rgba(b_label, F_ANTON(70), (150, 210, 255), stroke=2), W * 0.75, 170)
    put(fr, text_rgba('Clean air. Nine degrees.', F_BAR(34), WHITE), W * 0.75, 250)
    # gauges: the poison climbs while she is talking about inside; the temperature drops for outside
    ga = ease((t - t_of(155) - 0.3) / 0.4)
    if ga > 0:
        gx, gy0, gy1, gw = int(W * 0.25), int(H * 0.36), int(H * 0.78), 56
        kc = 0.12 + 0.80 * ease((t - t156) / 3.4)
        ov = fr.copy()
        cv2.rectangle(ov, (gx - gw // 2, gy0), (gx + gw // 2, gy1), (26, 22, 20), -1)
        fill_top = int(gy1 - (gy1 - gy0) * kc)
        for y in range(fill_top, gy1, 4):
            f = (gy1 - y) / (gy1 - gy0)
            col = (60, int(200 - 150 * f), int(90 + 160 * f))   # green -> red (BGR)
            cv2.rectangle(ov, (gx - gw // 2 + 6, y), (gx + gw // 2 - 6, min(y + 4, gy1 - 6)), col, -1)
        cv2.rectangle(ov, (gx - gw // 2, gy0), (gx + gw // 2, gy1), (235, 235, 235), 4, cv2.LINE_AA)
        if kc > 0.6:
            p = 0.5 + 0.5 * math.sin(t * 7)
            cv2.rectangle(ov, (gx - gw // 2 - 8, gy0 - 8), (gx + gw // 2 + 8, gy1 + 8), (60, 60, 235), int(2 + 4 * p), cv2.LINE_AA)
        put(ov, text_rgba('CO', F_ANTON(54), WHITE), gx, gy0 - 44)
        # thermometer
        tx = int(W * 0.75)
        kt = ease((t - t157) / 2.6)
        temp = int(round(49 - 40 * kt))
        lvl = 0.62 - 0.47 * kt
        cv2.rectangle(ov, (tx - 22, gy0), (tx + 22, gy1 - 30), (26, 22, 20), -1)
        cv2.circle(ov, (tx, gy1), 46, (26, 22, 20), -1, cv2.LINE_AA)
        top = int(gy1 - 30 - (gy1 - 30 - gy0) * lvl)
        cv2.rectangle(ov, (tx - 12, top), (tx + 12, gy1 - 20), (240, 170, 90), -1)
        cv2.circle(ov, (tx, gy1), 36, (240, 170, 90), -1, cv2.LINE_AA)
        cv2.rectangle(ov, (tx - 22, gy0), (tx + 22, gy1 - 30), (235, 235, 235), 4, cv2.LINE_AA)
        cv2.circle(ov, (tx, gy1), 46, (235, 235, 235), 4, cv2.LINE_AA)
        put(ov, text_rgba(f'{temp}°F', F_ANTON(64), (150, 210, 255), stroke=2), tx + 120, top)
        fr[:] = (fr.astype(np.float32) * (1 - ga) + ov.astype(np.float32) * ga).astype(np.uint8)
    return fr
