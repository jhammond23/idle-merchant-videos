# stylecheck.py <mp4> : the same measurement used on the reference reels in the browser (11-24):
# sample 10 fps at 36x64, mean abs luma diff between samples; a cut = diff > 40 and > 1.8x the median of its 4 neighbours.
# Brightness = mean full-range luma of the RGB frames (0-255). Saturation = mean (max-min)/max.
import subprocess, sys, numpy as np
f = sys.argv[1]; W, H = 36, 64
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', 'fps=10,scale=%d:%d' % (W, H), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
y = 0.299 * fr[..., 0] + 0.587 * fr[..., 1] + 0.114 * fr[..., 2]
mx = fr.max(-1); mn = fr.min(-1); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
d = np.r_[0, np.abs(np.diff(y, axis=0)).mean(axis=(1, 2))]
cuts = []
for i in range(1, len(d)):
    nb = sorted([d[j] for j in (i - 2, i - 1, i + 1, i + 2) if 0 <= j < len(d)])
    med = (nb[1] + nb[2]) / 2 if len(nb) >= 3 else nb[0]
    if d[i] > 40 and d[i] > 1.8 * med: cuts.append(i / 10)
dur = len(d) / 10
print('duration %.1f s | shots %d | average shot %.2f s | brightness %.0f | saturation %.2f' % (dur, len(cuts) + 1, dur / (len(cuts) + 1), y.mean(), sat.mean()))
gaps = np.diff([0] + cuts + [dur]); print('longest shots:', ', '.join('%.1fs@%.1f' % (g, s) for g, s in sorted(zip(gaps, [0] + cuts), reverse=True)[:5]))
print('cuts:', ' '.join('%.1f' % c for c in cuts))
