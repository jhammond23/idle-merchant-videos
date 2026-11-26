#!/usr/bin/env python3
"""Torchlit Blocktale (gneef-style) - ffmpeg post pass.

Usage:
    python3 post_gneef.py post_plan.json            # prints and runs the ffmpeg command
    python3 post_gneef.py post_plan.json --dry-run  # prints only

The pass works on the 1080x1920 30 fps picture BEFORE captions are burned in (captions come last,
from captions_gneef.json, so they never shake or tint). Every effect takes frame ranges [f0, f1]
(0-based output frames, inclusive). Plan keys (all optional except input/output):

{
  "input": "shots.mp4", "output": "post.mp4", "voice": "voice.mp3", "bed": "bed.mp3",
  "bed_db": -10,                       # bed level vs voice (measured floor ~10 dB under the voice)
  "grade": "ember" | "moon" | "day" | "golden" | null,   # only if the render was NOT graded already
  "vignette": 0.25,                    # edge darkening (measured 15-28 %)
  "push":   [[f0, f1, pct_per_s], ...],    # #1/#3 push-in (+6.5) or pull-out (-6), one range per shot
  "snap":   [[f, frames, pct, f_end], ...],# #2 snap push, cubic ease-out (18 frames, 35 %), held to f_end
  "roll":   [[f0, f1, deg_per_s], ...],    # #5 roll drift (+-2 deg/s)
  "wobble": [[f0, f1, px_rms], ...],       # #4 handheld wobble (2 px calm, 8-12 px action)
  "sepia":  [[f0, f1], ...],               # #19 flashback grade
  "bw":     [[f0, f1], ...],               # #19 black-and-white flashback with scan lines
  "danger": [[f0, f1], ...],               # #20 red monochrome (older format; use sparingly)
  "whiteout": [f_cut, ...],                # #21 3-frame glow before a hard cut
  "preroll": true,                          # #22 frames 0-2 rolled 10 deg (3D version does the full 25)
  "sfx": [[file, frame, gain_db], ...]      # #27 effects on ACTIONS (not on cuts)
}

Prefer doing camera moves in Blender (style_gneef.py) for real parallax; the post versions exist for
fixes and for shots rendered locked-off. Pushes in post need overscan: the pass scales the frame up
by OVERSCAN first, so every push/wobble/roll stays inside the picture.
"""
import json
import shlex
import subprocess
import sys

FPS = 30
W, H = 1080, 1920
OVERSCAN = 1.30  # render or scale 30% larger so pushes, wobble and roll never reveal an edge


def _piecewise(ranges, body, default='0'):
    """Nested if(between(n,a,b), body(a,b,...), ...) expression over the output frame number n."""
    expr = default
    for r in reversed(ranges):
        expr = 'if(between({N},%d,%d),%s,%s)' % (r[0], r[1], body(*r), expr)
    return expr


def zoom_expr(plan):
    """Total zoom factor (1 = framing as rendered) per frame from push and snap ranges."""
    parts = []
    for f0, f1, pct in plan.get('push', []):
        k = 1 + pct / 100.0
        # scale grows by k per second inside the range and holds after it
        parts.append('if(between({N},%d,%d),pow(%.5f,({N}-%d)/%d),1)' % (f0, f1, k, f0, FPS))
    for item in plan.get('snap', []):
        f, frames, pct = (list(item) + [18, 35])[:3]
        f_end = item[3] if len(item) > 3 else f + frames + 30  # hold the punched framing to the shot end
        parts.append('if(between({N},%d,%d),1+%.4f*(1-pow(1-min(({N}-%d)/%d,1),3)),1)' % (f, f_end, pct / 100.0, f, frames))
    return '*'.join(parts) if parts else '1'


def build(plan):
    inp, out = plan['input'], plan['output']
    chain = []
    # 1. overscan so moves stay inside the frame
    sw, sh = int(W * OVERSCAN) // 2 * 2, int(H * OVERSCAN) // 2 * 2
    chain.append('scale=%d:%d:flags=bicubic' % (sw, sh))
    # 2. roll (drift + pre-roll snap), about the centre, before cropping
    rparts = []
    for f0, f1, dps in plan.get('roll', []):
        rparts.append('if(between(n,%d,%d),(n-%d)/%d*%.5f,0)' % (f0, f1, f0, FPS, dps * 3.14159265 / 180))
    if plan.get('preroll'):
        # 10 deg for frames 0-2: the most 30% overscan can hide. The measured 20-30 deg needs the
        # 3D version (style_gneef.preroll_snap) - post can only suggest it.
        rparts.append('if(lt(n,3),0.1745,0)')
    if rparts:
        chain.append("rotate=a='%s':ow=iw:oh=ih:c=black" % '+'.join(rparts))
    # 3. push / snap zoom + wobble via a per-frame crop of the overscanned frame, then scale to 1080
    z = zoom_expr(plan)
    wob = plan.get('wobble', [])
    def wob_body(axis):
        def b(f0, f1, px):
            amp = px * OVERSCAN / 1.414  # per-axis amplitude so the 2D rms ~= px
            if axis == 'x':
                return '%.3f*(0.78*sin(2*PI*4.3*{N}/%d)+0.62*sin(2*PI*7.7*{N}/%d+1))' % (amp, FPS, FPS)
            return '%.3f*(0.78*sin(2*PI*3.7*{N}/%d+2)+0.62*sin(2*PI*6.1*{N}/%d))' % (amp, FPS, FPS)
        return b
    wx = _piecewise(wob, wob_body('x')) if wob else '0'
    wy = _piecewise(wob, wob_body('y')) if wob else '0'
    # crop w/h are fixed per stream in ffmpeg, so zoom uses zoompan (d=1: 'in' = frame number)
    if z != '1':
        chain.append("zoompan=z='%.4f*(%s)':d=1:x='iw/2-(iw/zoom/2)+(%s)':y='ih/2-(ih/zoom/2)+(%s)':s=%dx%d:fps=%d"
                     % (OVERSCAN, z.format(N='in'), wx.format(N='in'), wy.format(N='in'), W, H, FPS))
    else:
        cw, chh = int(sw / OVERSCAN) // 2 * 2, int(sh / OVERSCAN) // 2 * 2
        chain.append("crop=%d:%d:x='(iw-%d)/2+(%s)':y='(ih-%d)/2+(%s)'" % (cw, chh, cw, wx.format(N='n'), chh, wy.format(N='n')))
        chain.append('scale=%d:%d' % (W, H))
    # 4. grade (only if the render was not graded in Blender)
    g = plan.get('grade')
    if g == 'ember':
        chain.append('eq=saturation=1.30:contrast=1.06,colorbalance=rh=0.06:bh=-0.10:rs=0.03:bs=-0.04')
    elif g == 'moon':
        chain.append('eq=saturation=1.30:contrast=1.06:brightness=-0.03,colorbalance=bs=0.06:rh=-0.06:bh=0.08')
    elif g == 'day':
        chain.append('eq=saturation=1.20')
    elif g == 'golden':
        chain.append('eq=saturation=1.25,colorbalance=rh=0.07:bh=-0.10')
    # 5. flashback / danger tints on ranges (timeline 'enable')
    for f0, f1 in plan.get('sepia', []):
        chain.append("colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:enable='between(n,%d,%d)'" % (f0, f1))
    for f0, f1 in plan.get('bw', []):
        chain.append("hue=s=0:enable='between(n,%d,%d)'" % (f0, f1))
        chain.append("drawgrid=w=iw:h=6:t=1:c=black@0.18:enable='between(n,%d,%d)'" % (f0, f1))
    for f0, f1 in plan.get('danger', []):
        chain.append("colorchannelmixer=1:0:0:0:.25:0:0:0:.25:0:0:0:enable='between(n,%d,%d)'" % (f0, f1))
    # 6. whiteout glow: 3 frames brightening + blur before each cut frame
    for f in plan.get('whiteout', []):
        chain.append("eq=brightness='if(between(n,%d,%d),0.08*(n-%d),0)':eval=frame" % (f - 3, f - 1, f - 4))
        chain.append("gblur=sigma=6:enable='between(n,%d,%d)'" % (f - 2, f - 1))
    # 7. vignette (measured edge/centre luma 0.72-0.85)
    v = plan.get('vignette', 0.25)
    if v:
        chain.append('vignette=angle=%.3f' % (0.35 + v * 1.6))
    chain.append('format=yuv420p')
    vf = ','.join(chain)
    cmd = ['ffmpeg', '-y', '-i', inp]
    amap = None
    audio_inputs = []
    if plan.get('voice'):
        cmd += ['-i', plan['voice']]; audio_inputs.append('voice')
    if plan.get('bed'):
        cmd += ['-stream_loop', '-1', '-i', plan['bed']]; audio_inputs.append('bed')
    for s in plan.get('sfx', []):
        cmd += ['-i', s[0]]; audio_inputs.append('sfx')
    fc = ['[0:v]%s[v]' % vf]
    if audio_inputs:
        labels = []
        idx = 1
        for kind in audio_inputs:
            if kind == 'voice':
                fc.append('[%d:a]anull[a%d]' % (idx, idx))
            elif kind == 'bed':
                fc.append('[%d:a]volume=%sdB[a%d]' % (idx, plan.get('bed_db', -10), idx))
            idx += 1
        idx = 1
        sfx_i = 0
        for kind in audio_inputs:
            if kind == 'sfx':
                f, gain = plan['sfx'][sfx_i][1], plan['sfx'][sfx_i][2] if len(plan['sfx'][sfx_i]) > 2 else 0
                ms = int(round(f / FPS * 1000))
                fc.append('[%d:a]adelay=%d|%d,volume=%sdB[a%d]' % (idx, ms, ms, gain, idx))
                sfx_i += 1
            labels.append('[a%d]' % idx)
            idx += 1
        fc.append('%samix=inputs=%d:duration=first:normalize=0[a]' % (''.join(labels), len(labels)))
        amap = '[a]'
    cmd += ['-filter_complex', ';'.join(fc), '-map', '[v]']
    if amap:
        cmd += ['-map', amap, '-c:a', 'aac', '-b:a', '192k']
    cmd += ['-r', str(FPS), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', out]
    return cmd


if __name__ == '__main__':
    plan = json.load(open(sys.argv[1]))
    cmd = build(plan)
    print(' '.join(shlex.quote(c) for c in cmd))
    if '--dry-run' not in sys.argv:
        sys.exit(subprocess.call(cmd))
