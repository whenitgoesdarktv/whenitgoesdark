"""Approximate word timings for each narration chunk from its audio, without a transcription model.

Splits the audio at pauses, matches pause-separated stretches to the script's sentences in order,
then spreads each stretch's words over its duration by spoken length.
Usage: python3 -I align.py  (reads chunk_X.txt and voice_X.mp3, writes words.json and lines.json)
"""
import json, re, subprocess, sys, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 16000

def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

def speech_runs(x, frame=0.01, thresh_db=-38, min_gap=0.16, min_run=0.06):
    n = int(frame * SR)
    m = len(x) // n
    rms = np.sqrt(np.mean(x[:m * n].reshape(m, n) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    peak = np.percentile(db, 95)
    on = db > max(thresh_db, peak - 32)
    runs = []
    i = 0
    while i < m:
        if on[i]:
            j = i
            while j < m and on[j]:
                j += 1
            runs.append([i * frame, j * frame])
            i = j
        else:
            i += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < min_gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [r for r in merged if r[1] - r[0] >= min_run], len(x) / SR

def syll(w):
    w = re.sub(r'[^a-z0-9]', '', w.lower())
    if not w:
        return 1
    if w.isdigit():
        return 2 * len(w)
    v = re.findall(r'[aeiouy]+', w)
    s = len(v)
    if w.endswith('e') and s > 1 and not w.endswith('le'):
        s -= 1
    return max(1, s)

def sentences(text):
    # split into sentences / short phrases the narrator pauses on
    text = text.replace('\n', ' ')
    parts = re.split(r'(?<=[.!?])\s+(?=["A-Z0-9])', text)
    return [p.strip() for p in parts if p.strip()]

def weight(s):
    ws = s.split()
    return sum(syll(w) for w in ws) + 0.6 * sum(1 for w in ws if w[-1] in ',.?!"')

def align_chunk(text, audio):
    x = load(audio)
    runs, dur = speech_runs(x)
    sents = sentences(text)
    W = [weight(s) for s in sents]
    # Dynamic programming: assign consecutive speech runs to sentences so that each sentence's
    # spoken duration is proportional to its weight. Cost = squared log-ratio of duration vs expected.
    rate = sum(r[1] - r[0] for r in runs) / sum(W)
    S, R = len(sents), len(runs)
    INF = 1e18
    cost = np.full((S + 1, R + 1), INF)
    back = np.zeros((S + 1, R + 1), int)
    cost[0][0] = 0
    for i in range(1, S + 1):
        exp = W[i - 1] * rate
        for j in range(1, R + 1):
            best, bk = INF, 0
            for k in range(max(0, j - 12), j):  # sentence i covers runs k..j-1
                if cost[i - 1][k] >= INF:
                    continue
                d = runs[j - 1][1] - runs[k][0]
                c = cost[i - 1][k] + (np.log(max(d, 0.05) / exp)) ** 2
                if c < best:
                    best, bk = c, k
            cost[i][j], back[i][j] = best, bk
    # backtrack
    seg = []
    j = R
    for i in range(S, 0, -1):
        k = back[i][j]
        seg.append((runs[k][0], runs[j - 1][1], runs[k:j]))
        j = k
    seg.reverse()
    words, lines = [], []
    for s, (a, b, rr) in zip(sents, seg):
        ws = s.split()
        wts = [syll(w) + (0.5 if w[-1] in ',;' else 0) for w in ws]
        # spread words across the speech runs inside this sentence (skip internal pauses)
        spoken = sum(r[1] - r[0] for r in rr)
        acc = 0.0
        tot = sum(wts)
        def at(frac):
            t = frac * spoken
            for r in rr:
                L = r[1] - r[0]
                if t <= L:
                    return r[0] + t
                t -= L
            return rr[-1][1]
        for w, wt in zip(ws, wts):
            st = at(acc / tot)
            acc += wt
            en = at(acc / tot)
            words.append({'text': w, 'start': round(st, 3), 'end': round(en, 3)})
        lines.append({'text': s, 'start': round(a, 3), 'end': round(b, 3)})
    return words, lines, dur

if __name__ == '__main__':
    allw, alll, offset = [], [], 0.0
    gaps = {'A': 0.0, 'B': 0.9, 'C': 0.9, 'D': 0.9}  # silence inserted before each chunk in the master
    out = {}
    for k in 'ABCD':
        text = open(os.path.join(HERE, f'chunk_{k}.txt')).read()
        w, l, dur = align_chunk(text, os.path.join(HERE, f'voice_{k}.mp3'))
        offset += gaps[k]
        for x in w:
            x['start'] += offset; x['end'] += offset; x['chunk'] = k
        for x in l:
            x['start'] += offset; x['end'] += offset; x['chunk'] = k
        out[k] = {'offset': offset, 'dur': dur}
        allw += w; alll += l
        offset += dur
    json.dump(allw, open(os.path.join(HERE, 'words.json'), 'w'), indent=0)
    json.dump(alll, open(os.path.join(HERE, 'lines.json'), 'w'), indent=1)
    json.dump(out, open(os.path.join(HERE, 'chunks.json'), 'w'), indent=1)
    print('total narration', round(offset, 2), 's;', len(alll), 'lines;', len(allw), 'words')
