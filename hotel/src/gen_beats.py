"""Write beats.txt: final-video time of each narration line and the shot on screen (for reviewers)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as TL
B = TL.build(); L = B['lines']; t_of = B['t_of']
out = ['# Beat sheet: final-video time of each narration line, and the shot on screen\n']
shots = []
for k, (first, bg, cam, chars, fx) in enumerate(TL.SHOTS):
    st = 0.0 if k == 0 else TL.shot_time(t_of, first) - 0.15
    shots.append((st, bg, [c[0] for c in chars], sorted(fx)))
si = 0
s = shots[0]; out.append(f"  [SHOT {s[0]:7.2f}s] bg={s[1]} chars={s[2]} fx={s[3]}")
for i, l in enumerate(L):
    t = t_of(i)
    while si + 1 < len(shots) and shots[si + 1][0] <= t + 0.01:
        si += 1; s = shots[si]; out.append(f"  [SHOT {s[0]:7.2f}s] bg={s[1]} chars={s[2]} fx={s[3]}")
    m, sec = divmod(t, 60)
    out.append(f"{t:7.2f}s ({int(m)}:{sec:05.2f}) line {i:3d}: {l['text']}")
out.append(f"\nEnd card from about {B['total'] - TL.END_CARD:.2f}s to {B['total']:.2f}s")
out.append('\nChapters (card appears 1.45 s before the first line): ' + '; '.join(f"{n} {t} @ {t_of(f) - 1.45:.2f}s" for f, n, t in TL.CHAPTERS))
out.append('Rule cards: ' + '; '.join(f"{lab} {tt} lines {a}-{b}: {ls}" for a, b, lab, tt, ls in TL.RULES))
out.append('Status bar changes: ' + '; '.join(f"line {a} -> {x}" for a, *x in TL.STATUS))
out.append('SFX cues: ' + '; '.join(f"{n} @ line {l}+{o}s ({t_of(l) + o:.1f}s)" for l, o, n, g, *_ in TL.SFX))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'beats.txt'), 'w').write('\n'.join(out) + '\n')
print('beats.txt', len(out), 'lines')
