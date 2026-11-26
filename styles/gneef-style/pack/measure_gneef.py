#!/usr/bin/env python3
"""Check a finished test or film against the Torchlit Blocktale numbers (no rendering: it only reads).

    python3 -I measure_gneef.py film.mp4 [--from 0 --to 15]

Decodes 10 frames/s at 54x96 with ffmpeg and prints, next to the style's targets:
brightness, saturation, shadow share, vignette (edge/centre), number of cuts and shot lengths,
and the share of shots with a push-in. These are the same measurements used on the source videos
(STYLE.md sections 3-5), so the numbers are directly comparable.
"""
import subprocess
import sys

import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

W, H, RATE = 54, 96, 10
TARGET = {
    'brightness': (60, 100), 'saturation': (0.60, 0.72), 'shadow_share': (0.30, 0.45),
    'edge_centre': (0.72, 0.85), 'avg_shot': (1.2, 1.6), 'avg_shot_first30': (0.9, 1.3),
    'push_share': (0.70, 1.0),
}


def frames(path, t0=None, t1=None):
    cmd = ['ffmpeg', '-v', 'error']
    if t0 is not None:
        cmd += ['-ss', str(t0)]
    cmd += ['-i', path]
    if t1 is not None:
        cmd += ['-t', str(t1 - (t0 or 0))]
    cmd += ['-vf', 'fps=%d,scale=%d:%d' % (RATE, W, H), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def main():
    path = sys.argv[1]
    a = sys.argv
    t0 = float(a[a.index('--from') + 1]) if '--from' in a else None
    t1 = float(a[a.index('--to') + 1]) if '--to' in a else None
    F = frames(path, t0, t1)
    rgb = F.astype(np.float32)
    gray = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    keep = np.r_[0:int(H * .55), int(H * .80):H]  # leave out the caption band
    res = {}
    res['brightness'] = float(gray.mean())
    res['saturation'] = float(sat[:, keep].mean())
    res['shadow_share'] = float((gray < 40).mean())
    centre = gray[:, H // 3:2 * H // 3, W // 3:2 * W // 3].mean()
    ring = np.concatenate([gray[:, :H // 8].ravel(), gray[:, -H // 8:].ravel(), gray[:, :, :W // 8].ravel(), gray[:, :, -W // 8:].ravel()]).mean()
    res['edge_centre'] = float(ring / max(centre, 1))
    # cuts: frame-difference peaks outside the caption band
    g = gray[:, keep]
    d = np.r_[0, np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))]
    cuts = []
    for i in range(1, len(d)):
        lo, hi = max(1, i - 3), min(len(d), i + 4)
        base = np.median(np.r_[d[lo:i], d[i + 1:hi]]) if hi - lo > 1 else 0
        if d[i] - base > 30 and d[i] > 1.8 * max(base, 1) and (not cuts or i - cuts[-1] > 1):
            cuts.append(i)
    starts = [0] + cuts
    ends = cuts + [len(F)]
    L = np.array([(b - a) / RATE for a, b in zip(starts, ends)])
    res['shots'] = len(L)
    res['avg_shot'] = float(L.mean())
    res['median_shot'] = float(np.median(L))
    first = [l for s, l in zip(starts, L) if s / RATE < 30]
    res['avg_shot_first30'] = float(np.mean(first)) if first else float('nan')
    # push-in share via dense-flow scale fit per shot
    pushes = 0
    n = 0
    if cv2 is not None:
        ys, xs = np.mgrid[0:H, 0:W]
        m = np.ones((H, W), bool); m[int(H * .55):int(H * .8)] = False
        X = (xs - W / 2)[m]; Y = (ys - H / 2)[m]; k = len(X)
        A = np.zeros((2 * k, 4)); A[:k, 0] = X; A[:k, 1] = -Y; A[:k, 2] = 1; A[k:, 0] = Y; A[k:, 1] = X; A[k:, 3] = 1
        P = np.linalg.pinv(A)
        for a_, b_ in zip(starts, ends):
            if b_ - a_ < 4:
                continue
            z = 1.0
            for i in range(a_ + 2, b_):
                fl = cv2.calcOpticalFlowFarneback(gray[i - 1].astype(np.uint8), gray[i].astype(np.uint8), None, 0.5, 2, 9, 3, 5, 1.1, 0)
                p = P @ np.r_[fl[..., 0][m], fl[..., 1][m]]
                z *= 1 + p[0]
            dur = (b_ - a_ - 2) / RATE
            rate = (z ** (1 / max(dur, 0.1)) - 1) * 100
            n += 1
            pushes += rate > 2
        res['push_share'] = pushes / n if n else float('nan')
    print('%-18s %10s   %s' % ('measure', 'value', 'target'))
    for k, v in res.items():
        t = TARGET.get(k)
        flag = '' if t is None else ('ok' if t[0] <= v <= t[1] else 'OFF')
        tt = '' if t is None else '%s-%s %s' % (t[0], t[1], flag)
        print('%-18s %10.3f   %s' % (k, v, tt))


if __name__ == '__main__':
    main()
