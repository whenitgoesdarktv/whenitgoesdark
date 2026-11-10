"""Audio for the hotel trailer Short: master mix 0..OPEN_END, then an impact and a low blizzard bed under the end card."""
import os, sys, subprocess, json, numpy as np, wave
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import timeline as TL
SR = 48000
B = TL.build(); OPEN_END = B['lines'][17]['end'] + 0.45; TOTAL = OPEN_END + 4.5
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
mix = load(os.path.join(HERE, 'out', 'mix.wav'))
N = int(TOTAL * SR); out = np.zeros((N, 2), np.float32)
a = int(OPEN_END * SR); seg = mix[:a].copy(); f = int(0.25 * SR); seg[-f:] *= np.linspace(1, 0, f)[:, None]; out[:a] = seg
hit = load(os.path.join(HERE, 'sfx', 'sfx_whoosh_hit.wav')) * 10 ** (-9 / 20)
s0 = a - int(0.35 * SR); n = min(len(hit), N - s0); out[s0:s0 + n] += hit[:n]
bed = load(os.path.join(HERE, 'sfx', 'amb_blizzard_outside.wav'))[:N - a] * 10 ** (-20 / 20)
fi = int(0.6 * SR); bed[:fi] *= np.linspace(0, 1, fi)[:, None]; fo = int(1.0 * SR); bed[-fo:] *= np.linspace(1, 0, fo)[:, None]
out[a:a + len(bed)] += bed
tmp = os.path.join(HERE, 'out', 'short_raw.wav')
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
js = r.stderr[r.stderr.rfind('{'):]; st = json.loads(js[:js.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:"
      f"measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true,aresample=48000")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-c:a', 'pcm_s16le', os.path.join(HERE, 'out', 'short_audio.wav')], check=True)
print('short audio', round(TOTAL, 2), 's')
