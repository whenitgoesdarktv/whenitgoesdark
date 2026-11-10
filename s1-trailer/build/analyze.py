import cv2, numpy as np, sys
src, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
cap = cv2.VideoCapture(src); cap.set(cv2.CAP_PROP_POS_MSEC, t0*1000)
prev=None; i=0; fps=30
while True:
    ok, f = cap.read()
    if not ok: break
    t = t0 + i/fps; i+=1
    if t>t1: break
    g = cv2.cvtColor(cv2.resize(f,(480,270)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    if prev is not None:
        art = np.abs(g[:220]-prev[:220]).mean()
        band = np.abs(g[224:248, 100:380]-prev[224:248,100:380]).mean()
        if art>6 or band>4: print(f"{t:7.2f} art={art:5.1f} band={band:5.1f}")
    prev=g
