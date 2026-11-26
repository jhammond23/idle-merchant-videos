#!/usr/bin/env python3
"""Measure a rendered film against the Bright Snap Cut targets (no rendering, just reading).

    python3 check_bright_cut.py film.mp4

Samples the video at 10 fps at 108x192 through ffmpeg and prints:
  mean luma      target 135-155 (measured 131-154 on daylight reels)
  HSV saturation target 0.30-0.42 (measured 0.29-0.41)
  vivid pixels   target <= ~10 % (measured 8 %)
  cuts / avg shot target avg 0.6-0.8 s, none over 2.6 s (measured 0.56-0.94, max 2.6)
  static shots   target <= 16 % of shots with near-zero motion (measured 10-16 %)
Same method as the analysis (histogram + frame-difference cut detection at 10 fps), so the
numbers are comparable with STYLE.md.
"""
import subprocess
import sys

import numpy as np


def frames(path, fps=10, w=108, h=192):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[: n * w * h * 3], np.uint8).reshape(n, h, w, 3)


def hsv_s(a):
    a = a.astype(np.float32)
    mx, mn = a.max(-1), a.min(-1)
    return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)


def main(path):
    F = frames(path)
    if len(F) < 2:
        print("too short")
        return
    L = (0.299 * F[..., 0] + 0.587 * F[..., 1] + 0.114 * F[..., 2]).astype(np.float32)
    S = hsv_s(F)
    V = F.max(-1) / 255.0
    vivid = ((S > 0.67) & (V > 0.59)).mean()
    # cuts
    def hist(f):
        q = (f // 64).astype(np.int32)
        idx = q[..., 0] * 16 + q[..., 1] * 4 + q[..., 2]
        return np.bincount(idx.ravel(), minlength=64) / idx.size
    H = np.array([hist(f) for f in F])
    hd = np.r_[0, np.abs(np.diff(H, axis=0)).sum(1)]
    gd = np.r_[0, np.abs(np.diff(L, axis=0)).mean((1, 2))]
    sc = np.maximum(hd / 0.45, gd / 38)
    cuts = [i for i in range(1, len(sc) - 1) if sc[i] >= 1 and sc[i] >= sc[i - 1] and sc[i] >= sc[i + 1]]
    pruned = []
    for c in cuts:
        if pruned and c - pruned[-1] < 3:
            continue
        pruned.append(c)
    b = [0] + pruned + [len(F)]
    lens = np.diff(b) / 10.0
    static = 0
    for a, e in zip(b[:-1], b[1:]):
        if e - a >= 3 and gd[a + 1:e].mean() < 2.0:
            static += 1
    dur = len(F) / 10.0
    def ok(v, lo, hi):
        return "OK " if lo <= v <= hi else "OFF"
    print(f"duration        {dur:.1f} s")
    print(f"mean luma       {L.mean():6.1f}   {ok(L.mean(), 135, 155)} target 135-155")
    print(f"HSV saturation  {S.mean():6.3f}   {ok(S.mean(), 0.30, 0.42)} target 0.30-0.42")
    print(f"vivid pixels    {vivid * 100:5.1f} %  {ok(vivid, 0, 0.10)} target <= 10 %")
    print(f"shots           {len(lens)}  avg {lens.mean():.2f} s  median {np.median(lens):.2f} s  max {lens.max():.1f} s"
          f"   {ok(lens.mean(), 0.55, 0.85)} target avg 0.6-0.8, {ok(lens.max(), 0, 2.6)} max <= 2.6")
    print(f"static shots    {static / max(1, len(lens)) * 100:5.1f} %  {ok(static / max(1, len(lens)), 0, 0.16)} target <= 16 %")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
