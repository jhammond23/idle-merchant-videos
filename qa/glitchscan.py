#!/usr/bin/env python3
"""Full-length glitch scan: python3 glitchscan.py video.mp4
Reports: strobe/alternating frames, single-frame pops, frozen stretches, black/white flashes, hard jumps (cuts)."""
import sys, subprocess, numpy as np
p = sys.argv[1]
b = subprocess.run(['ffmpeg','-v','error','-i',p,'-vf','scale=90:160,format=gray','-f','rawvideo','-'],capture_output=True).stdout
a = np.frombuffer(b,np.uint8).reshape(-1,160,90).astype(float)
n = len(a); fps = 30.0
def runs(idx, gap=2, minlen=1):
    out=[]; s=None; p=None
    for i in idx:
        if s is None or i>p+gap:
            if s is not None and p-s+1>=minlen: out.append((round(s/fps,2), round(p/fps,2), p-s+1))
            s=i
        p=i
    if s is not None and p-s+1>=minlen: out.append((round(s/fps,2), round(p/fps,2), p-s+1))
    return out
d = np.abs(np.diff(a,axis=0)).mean((1,2))
alt=[]; pop=[]
for i in range(1,n-1):
    dp=d[i-1]; dn=d[i]; ds=np.abs(a[i+1]-a[i-1]).mean()
    if dp>3 and dn>3 and ds<0.5*min(dp,dn):
        alt.append(i)
mean = a.mean((1,2))
flash=[i for i in range(n) if mean[i]<8 or mean[i]>247]
frozen=[i for i in range(len(d)) if d[i]<0.05]
cuts=[i for i in range(len(d)) if d[i]>25]
print('frames', n, 'duration', round(n/fps,2))
print('STROBE/POP stretches (start s, end s, frames):', runs(alt))
print('black/white flash frames:', runs(flash))
print('frozen stretches >=5 frames:', runs(frozen, gap=1, minlen=5))
print('hard cuts at s:', [round((i+1)/fps,2) for i in cuts])
