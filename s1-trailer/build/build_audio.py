"""Assemble the trailer audio: source cuts + synthesized low hits + end-card storm bed, then -14 LUFS."""
import sys, subprocess, json, numpy as np, wave, os

SRC, OUT = sys.argv[1], sys.argv[2]
SR = 48000
CUTS = [(0.00, 20.45), (32.95, 36.30), (209.50, 214.30), (304.80, 308.60)]
END_LEN = 4.0

def load(a, b):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a}', '-t', f'{b - a}', '-i', SRC, '-vn', '-ac', '2',
                          '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(round((b - a) * SR))
    if len(x) < n:
        x = np.vstack([x, np.zeros((n - len(x), 2), np.float32)])
    return x[:n]

def fade(x, fin=0.015, fout=0.015):
    a, b = int(fin * SR), int(fout * SR)
    if a: x[:a] *= np.linspace(0, 1, a)[:, None]
    if b: x[-b:] *= np.linspace(1, 0, b)[:, None]
    return x

rng = np.random.default_rng(7)

def boom(length=1.4, f0=95, f1=38, gain=0.5):
    n = int(length * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 4)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 3.2) * np.minimum(t / 0.004, 1)
    s = np.sin(ph) * env
    nz = rng.standard_normal(n) * np.exp(-t * 30)
    # crude low-pass for the transient
    k = 60; nz = np.convolve(nz, np.ones(k) / k, mode='same')
    s = (s + nz * 0.8) * gain
    return np.stack([s, s], 1).astype(np.float32)

def storm_bed(length):
    n = int(length * SR)
    w = rng.standard_normal(n)
    brown = np.cumsum(w); brown -= np.convolve(brown, np.ones(4800) / 4800, mode='same')  # remove drift
    brown /= np.abs(brown).max() + 1e-9
    t = np.arange(n) / SR
    gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.35 * t + 1.0) * np.sin(2 * np.pi * 0.13 * t)
    rain = rng.standard_normal(n); rain = rain - np.convolve(rain, np.ones(8) / 8, mode='same')
    s = brown * gust * 0.22 + rain * 0.015
    l = s; r = np.roll(s, 240)
    return np.stack([l, r], 1).astype(np.float32)

parts = [fade(load(a, b), 0.0 if i == 0 else 0.012, 0.02) for i, (a, b) in enumerate(CUTS)]
end = storm_bed(END_LEN)
end[:int(0.25 * SR)] *= np.linspace(0, 1, int(0.25 * SR))[:, None]
end[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))[:, None]
parts.append(end)
mix = np.vstack(parts)

# low hits on the montage cuts and the end card
t_out = 0.0; marks = []
for a, b in CUTS:
    t_out += b - a; marks.append(t_out)
for i, m in enumerate(marks):
    bm = boom(gain=0.55 if i < len(marks) - 1 else 0.75)
    s = int(m * SR); e = min(len(mix), s + len(bm))
    mix[s:e] += bm[:e - s]

mix = np.clip(mix, -1, 1)
tmp = OUT + '.raw.wav'
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

# two-pass loudnorm to -14 LUFS, true peak -1.5
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True)
js = r.stderr[r.stderr.rfind('{'):]
st = json.loads(js[:js.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
      f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af + ',aresample=48000', '-c:a', 'pcm_s16le', OUT], check=True)
os.remove(tmp)
print('duration', len(mix) / SR, 'measured', st['input_i'], st['input_tp'])
