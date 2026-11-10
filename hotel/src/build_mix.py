"""Mix the hotel episode: narration (with dramatic pauses), ambience beds, generator hum, SFX; duck under voice; -14 LUFS."""
import os, sys, json, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as TL

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
B = TL.build(); LINES = B['lines']; TOTAL = B['total']; t_of = B['t_of']
SRC = json.load(open(os.path.join(HERE, 'lines.json')))
CH = json.load(open(os.path.join(HERE, 'chunks.json')))

def load(path, stereo=True):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def db(x):
    return 10 ** (x / 20)

N = int(TOTAL * SR) + SR
voice = np.zeros((N, 2), np.float32)
# 1) concatenated narration on the align timeline
parts = []
for k in 'ABCD':
    gap = int(round((CH[k]['offset'] - (sum(CH[j]['dur'] for j in 'ABCD'[:'ABCD'.index(k)]))) * SR))
    parts.append(load(os.path.join(HERE, f'voice_{k}.mp3')))
narr_src = np.zeros((int((CH['D']['offset'] + CH['D']['dur']) * SR) + SR, 2), np.float32)
for k, p in zip('ABCD', parts):
    s = int(CH[k]['offset'] * SR); narr_src[s:s + len(p)] = p[:len(narr_src) - s]
# 2) cut between lines and place each piece at its shifted time
cuts = [0.0]
for i in range(len(SRC) - 1):
    cuts.append((SRC[i]['end'] + SRC[i + 1]['start']) / 2)
cuts.append(len(narr_src) / SR)
for i in range(len(SRC)):
    a, b = int(cuts[i] * SR), int(cuts[i + 1] * SR)
    seg = narr_src[a:b]
    dst = int((cuts[i] + B['shift'][i]) * SR)
    voice[dst:dst + len(seg)] += seg[:max(0, N - dst)]

# voice envelope for ducking
env = np.abs(voice).max(axis=1)
k = int(0.12 * SR)
env = np.convolve(env, np.ones(k) / k, mode='same')
duck = 1 - 0.72 * np.clip(env / 0.05, 0, 1)
dk = int(0.25 * SR)
duck = np.convolve(duck, np.ones(dk) / dk, mode='same')[:, None]

fx = np.zeros((N, 2), np.float32)
SFXD = os.path.join(HERE, 'sfx')
missing = set()
def sfx(name):
    p = os.path.join(SFXD, name + '.wav')
    if not os.path.exists(p):
        missing.add(name); return None
    return load(p)

def place(buf, x, t, gain_db, fade_in=0.02, fade_out=0.05):
    s = int(t * SR)
    if s >= N or x is None:
        return
    x = x[:N - s].copy() * db(gain_db)
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    if fi: x[:fi] *= np.linspace(0, 1, min(fi, len(x)))[:, None][:len(x[:fi])]
    if fo and len(x) > fo: x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    buf[s:s + len(x)] += x

def loop_to(x, n):
    if x is None:
        return None
    reps = int(np.ceil(n / len(x)))
    return np.tile(x, (reps, 1))[:n]

# beds
for a, b, name, g in TL.BEDS:
    t0 = 0.0 if a == 0 else t_of(a) - 0.3
    t1 = TOTAL if b >= len(LINES) else t_of(b) - 0.3
    x = loop_to(sfx(name), int((t1 - t0) * SR))
    place(fx, x, t0, g, 0.5, 0.6)
# generator hum: loud in the lobby, faint (low-passed) elsewhere
hum = sfx('sfx_generator_hum')
if hum is not None:
    from scipy.signal import butter, sosfilt
    _sos = butter(4, 180, 'low', fs=SR, output='sos')
    def lowpass(x, fc=180):
        return sosfilt(_sos, x, axis=0).astype(np.float32)
    for (a, b) in (TL.HUM_COLD_OPEN, TL.HUM):
        t0, t1 = t_of(a), t_of(b) + (0.4 if b == 162 else 0.0)
        x = loop_to(hum, int((t1 - t0) * SR))
        place(fx, lowpass(x), t0, -16, 1.5, 0.15)
    # extra presence in lobby shots
    # shot times computed the same way as render_long (start = first line - 0.15 s)
    for k, (first, bg, *_r) in enumerate(TL.SHOTS):
        if bg not in ('bg05_lobby_fire', 'bg06_balcony_view'):
            continue
        st = 0.0 if k == 0 else t_of(first) - 0.15
        en = TOTAL if k + 1 >= len(TL.SHOTS) else t_of(TL.SHOTS[k + 1][0]) - 0.15
        if t_of(TL.HUM[0]) <= st < t_of(TL.HUM[1]):
            x = loop_to(hum, int((en - st) * SR))
            place(fx, x, st, -20, 0.4, 0.4)
# one-shots
for line, off, name, g in TL.SFX:
    place(fx, sfx(name), t_of(line) + off, g)

mix = voice + fx * duck
# end card: let ambience fade out under the end card
mix = np.clip(mix, -1, 1)
tmp = os.path.join(HERE, 'out', 'mix_raw.wav'); os.makedirs(os.path.dirname(tmp), exist_ok=True)
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix[:int(TOTAL * SR)] * 32767).astype(np.int16).tobytes())
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
js = r.stderr[r.stderr.rfind('{'):]; st = json.loads(js[:js.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:"
      f"measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true,aresample=48000")
out = os.path.join(HERE, 'out', 'mix.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-c:a', 'pcm_s16le', out], check=True)
voice_only = os.path.join(HERE, 'out', 'voice_master.wav')
with wave.open(voice_only, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(voice[:int(TOTAL * SR)], -1, 1) * 32767).astype(np.int16).tobytes())
print('mix done', round(TOTAL, 1), 's; measured', st['input_i'], 'missing sfx:', sorted(missing))
