#!/usr/bin/env python3
"""post_craftee-style.py: ffmpeg post-processing for Toybox Fable (style id `craftee-style`).

The style is built from hard cuts and an UNGRADED image, so post does very little on purpose: no grade, tint,
vignette, grain, chromatic aberration, shake or zoom punches (STYLE.md S3, S14 "Not used"). This script holds the
few post effects the teardown measured, plus QA checks. Frames are 0-based at 30 fps.

  pulse      T15 light pulse: +30 luma (eq brightness +0.12), 2 frames up, 4 frames down, at each frame given
  dropout    T25 music drop-out: the MUSIC stem to silence over the given frame ranges (30 ms ramps)
  sfx        T24 sound-synced cuts: a whoosh/pop placed 2 frames before chosen cuts (plan.json from cut_plan)
  captions   S11 burn caption cards (cards.json from caption_cards) with libass, per captions_craftee-style.json
  letterbox  T22 cinematic variant only: 3:4 picture, black bars 240 px top and bottom
  flash      T20 cinematic variant only: mirror frames then one white frame (3 frames) at each frame given
  drift2d    T4 2D fallback: a slow lateral drift (200 px/s) over a still or over-rendered plate
  shake      OFF-STYLE (only with Jake's yes): one impact, 8 px, 12 Hz, decaying to 0 in 8 frames
  check      QA: mean luma, saturation, luma SD, dark-frame share, vignette ratio vs the S3 targets
  loopcheck  QA: how close the last frame is to frame 0 (T19 loop ending)

Every command prints the ffmpeg command it runs; add --dry to only print it.
Examples:
  python3 post_craftee-style.py pulse in.mp4 out.mp4 --frames 1830,2410
  python3 post_craftee-style.py dropout music.wav music_drop.wav --ranges 915-945
  python3 post_craftee-style.py sfx in.mp4 out.mp4 --plan plan.json --whoosh whoosh.wav --boom boom.wav
  python3 post_craftee-style.py captions in.mp4 out.mp4 --cards cards.json --fmt short
  python3 post_craftee-style.py check out.mp4 --mode day
"""
import argparse
import json
import math
import os
import shlex
import subprocess
import sys

FPS = 30
W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, dry=False):
    print(' '.join(shlex.quote(c) for c in cmd))
    if dry:
        return 0
    return subprocess.run(cmd, check=True).returncode


def parse_frames(s):
    return [int(x) for x in s.split(',') if x.strip()] if s else []


def parse_ranges(s):
    out = []
    for part in (s or '').split(','):
        part = part.strip()
        if not part:
            continue
        a, b = part.split('-')
        out.append((int(a), int(b)))
    return out


# --------------------------------------------------------------------------------------------- effects
def cmd_pulse(a):
    """eq brightness is added to luma (0..1). 0.12 ~ +30 luma. Same curve as style_craftee_style.light_pulse()."""
    terms = []
    for f in parse_frames(a.frames):
        r, d = a.rise, a.decay
        terms.append("if(between(n,{f},{fr}),{L}*(n-{f})/{r},if(between(n,{fr},{fe}),{L}*pow(1-(n-{fr})/{d},2),0))".format(
            f=f, fr=f + r, fe=f + r + d, r=r, d=d, L=a.lift))
    expr = '+'.join(terms) or '0'
    vf = "eq=brightness='{}':eval=frame".format(expr)
    return run(['ffmpeg', '-y', '-i', a.inp, '-vf', vf, '-c:a', 'copy', a.out], a.dry)


def cmd_dropout(a):
    """Apply to the MUSIC stem before the final mix (the voice keeps going)."""
    rmp = 0.03
    parts = []
    for f0, f1 in parse_ranges(a.ranges):
        t0, t1 = f0 / FPS, (f1 + 1) / FPS
        parts.append("if(between(t,{a},{b}),0,if(between(t,{a0},{a}),({a}-t)/{r},if(between(t,{b},{b1}),(t-{b})/{r},1)))".format(
            a=round(t0, 4), b=round(t1, 4), a0=round(t0 - rmp, 4), b1=round(t1 + rmp, 4), r=rmp))
    expr = '*'.join(parts) or '1'
    af = "volume='{}':eval=frame".format(expr)
    return run(['ffmpeg', '-y', '-i', a.inp, '-af', af, a.out], a.dry)


def _load_plan(path):
    with open(path) as fh:
        d = json.load(fh)
    return d['shots'] if isinstance(d, dict) and 'shots' in d else d


def cmd_sfx(a):
    """Whoosh/pop 2 frames before a cut (measured: 41-73% of cuts land on a transient). Default: shot 1 (the whip-in,
    whoosh + optional low boom peaking on frames 4-6) and every 2nd cut after it (~50%). --shots picks them by hand."""
    shots = _load_plan(a.plan)
    if a.shots:
        pick = set(parse_frames(a.shots))
    else:
        pick = {1} | {s['shot'] for s in shots if s['shot'] > 1 and s['shot'] % 2 == 0}
    times = []
    for s in shots:
        if s['shot'] in pick:
            t = max(0.0, s['f0'] / FPS - 2 / FPS) if s['shot'] > 1 else 0.0
            times.append(t)
    n = len(times)
    if n == 0:
        print('no cuts picked')
        return 0
    inputs = ['-i', a.inp, '-i', a.whoosh]
    fc = ['[1:a]volume={}dB,asplit={}{}'.format(a.gain, n, ''.join('[w%d]' % i for i in range(n)))]
    mix = ['[0:a]']
    for i, t in enumerate(times):
        ms = int(round(t * 1000))
        fc.append('[w{i}]adelay={ms}|{ms}[d{i}]'.format(i=i, ms=ms))
        mix.append('[d%d]' % i)
    k = n + 1
    if a.boom:
        inputs += ['-i', a.boom]
        fc.append('[2:a]volume={}dB,adelay=100|100[boom]'.format(a.gain))   # peaks around frames 4-6
        mix.append('[boom]')
        k += 1
    fc.append('{}amix=inputs={}:normalize=0:duration=first[aout]'.format(''.join(mix), k))
    cmd = ['ffmpeg', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', a.out]
    return run(cmd, a.dry)


def cmd_letterbox(a):
    vf = 'drawbox=x=0:y=0:w=iw:h=240:color=black:t=fill,drawbox=x=0:y=ih-240:w=iw:h=240:color=black:t=fill'
    return run(['ffmpeg', '-y', '-i', a.inp, '-vf', vf, '-c:a', 'copy', a.out], a.dry)


def cmd_flash(a):
    """T20 (cinematic only): frames F and F+1 show a left-half mirror, frame F+2 is white, then the cut."""
    chains = []
    cur = '[0:v]'
    for i, f in enumerate(parse_frames(a.frames)):
        chains.append('{c}split[a{i}][b{i}];[b{i}]crop=iw/2:ih:0:0,split[l{i}][r{i}];[r{i}]hflip[rf{i}];'
                      '[l{i}][rf{i}]hstack[m{i}];[a{i}][m{i}]overlay=enable=\'between(n,{f},{f1})\','
                      'drawbox=x=0:y=0:w=iw:h=ih:color=white:t=fill:enable=\'eq(n,{f2})\'[v{i}]'.format(c=cur, i=i, f=f, f1=f + 1, f2=f + 2))
        cur = '[v%d]' % i
    if not chains:
        print('no frames given')
        return 0
    cmd = ['ffmpeg', '-y', '-i', a.inp, '-filter_complex', ';'.join(chains), '-map', cur, '-map', '0:a?', '-c:a', 'copy', a.out]
    return run(cmd, a.dry)


def cmd_drift2d(a):
    """Over-scale 1.3x, then move the crop window at px_per_s (measured drift 150-300 px/s; default 200)."""
    sgn = {'left': -1, 'right': 1}[a.direction]
    vf = ("scale={sw}:{sh},crop={W}:{H}:x='(iw-{W})/2+{s}*{v}*(t-{d}/2)':y='(ih-{H})/2',fps={fps}"
          .format(sw=int(W * 1.3), sh=int(H * 1.3), W=W, H=H, s=sgn, v=a.px_per_s, d=a.dur, fps=FPS))
    cmd = ['ffmpeg', '-y', '-loop', '1', '-t', str(a.dur), '-i', a.inp, '-vf', vf, '-pix_fmt', 'yuv420p', a.out]
    return run(cmd, a.dry)


def cmd_shake(a):
    """OFF-STYLE. Only with Jake's yes. 1.04x over-scale, damped 12 Hz offset of `px`, 8 frames."""
    f, px, hz, fr = a.frame, a.px, a.hz, a.frames
    env = "between(n,{f},{fe})*(1-(n-{f})/{fr})".format(f=f, fe=f + fr, fr=fr)
    vf = ("scale={sw}:{sh},crop={W}:{H}:x='(iw-{W})/2+{px}*{env}*cos(2*PI*{hz}*(n-{f})/{fps})'"
          ":y='(ih-{H})/2+{py}*{env}*sin(2*PI*{hz}*(n-{f})/{fps})'").format(
        sw=int(W * 1.04), sh=int(H * 1.04), W=W, H=H, px=px, py=px / 2, env=env, hz=hz, f=f, fps=FPS)
    return run(['ffmpeg', '-y', '-i', a.inp, '-vf', vf, '-c:a', 'copy', a.out], a.dry)


# --------------------------------------------------------------------------------------------- captions
def _ass_colour(hexs, alpha=0):
    h = hexs.lstrip('#')
    return '&H{:02X}{}{}{}'.format(alpha, h[4:6], h[2:4], h[0:2]).upper()


def _ass_time(frame):
    t = frame / FPS
    hh = int(t // 3600)
    mm = int(t % 3600 // 60)
    ss = t % 60
    return '{}:{:02d}:{:05.2f}'.format(hh, mm, ss)


def write_ass(cards, fmt, path, spec=None):
    spec = spec or json.load(open(os.path.join(HERE, 'captions_craftee-style.json')))
    F = spec['font']
    size = F['size_px'] if fmt != 'cinematic' else spec['formats']['cinematic']['size_px']          # em size
    ass_size = F.get('ass_fontsize', size) if fmt != 'cinematic' else spec['formats']['cinematic'].get('ass_fontsize', size)
    yoff = F.get('ass_y_offset_px', 0)
    outline = spec['outline']['width_px']
    shadow = spec['shadow']['offset_px'][1]
    sh_alpha = int(round((1 - spec['shadow']['opacity']) * 255))
    style = ('Style: TF,{font},{size},{white},&H000000FF,{oc},{bc},-1,0,0,0,100,100,0,0,1,{ol},{sh},5,0,0,0,1'
             .format(font=F['family'], size=ass_size, white=_ass_colour('#FFFFFF'), oc=_ass_colour(spec['outline']['colour']),
                     bc=_ass_colour('#000000', sh_alpha), ol=outline, sh=shadow))
    lines = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: %d' % W, 'PlayResY: %d' % H, 'WrapStyle: 2',
             'ScaledBorderAndShadow: yes', '', '[V4+ Styles]',
             'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, '
             'Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
             style, '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    pitch = F.get('line_pitch_px', size * F['line_height_em'])
    for i, c in enumerate(cards):
        f0 = int(round(c['start'] * FPS))
        f1 = max(f0 + 1, int(round(c['end'] * FPS)))
        key = _ass_colour(c.get('keyword_colour', '#2ECE30'))
        if fmt == 'short':
            cx, cy = spec['formats']['short']['position_px']['x'], spec['formats']['short']['position_px']['y']
            ys = [cy] if len(c['lines']) == 1 else [cy - pitch / 2, cy + pitch / 2]
        elif fmt == 'long':
            cx, cy = spec['formats']['long']['position_px']['x'], spec['formats']['long']['position_px']['y']
            ys = [cy + (k - (len(c['lines']) - 1) / 2) * pitch for k in range(len(c['lines']))]
        else:
            cx, cy = W // 2, int(H * spec['formats']['cinematic']['position_pct']['y'] / 100)
            ys = [cy]
        pop = fmt == 'long' and i % 3 == 2
        for ln, y in zip(c['lines'], ys):
            tags = '{\\an5\\pos(%d,%d)' % (cx, round(y + yoff))
            if ln['role'] == 'keyword':
                tags += '\\c%s&' % key
            if pop:
                tags += '\\fscx85\\fscy85\\t(0,100,\\fscx100\\fscy100)'
            tags += '}'
            txt = ln['text'].replace('{', '(').replace('}', ')')
            lines.append('Dialogue: 0,{},{},TF,,0,0,0,,{}{}'.format(_ass_time(f0), _ass_time(f1), tags, txt))
    with open(path, 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    return path


def cmd_captions(a):
    with open(a.cards) as fh:
        cards = json.load(fh)
    ass = a.ass or os.path.splitext(a.out)[0] + '.ass'
    write_ass(cards, a.fmt, ass)
    print('wrote', ass)
    fonts = a.fontsdir or next((d for d in ('/usr/share/fonts/truetype/google-fonts', os.path.join(HERE, 'fonts'))
                                if os.path.isdir(d)), '')
    vf = "subtitles=filename='{}'".format(ass.replace("'", r"\'")) + (":fontsdir='{}'".format(fonts) if fonts else '')
    return run(['ffmpeg', '-y', '-i', a.inp, '-vf', vf, '-c:a', 'copy', a.out], a.dry)


# --------------------------------------------------------------------------------------------- QA
TARGETS = {'day': {'luma': (106, 125), 'sat': (0.38, 0.46), 'luma_sd': (55, 65)},
           'night': {'luma': (30, 60)}, 'mixed': {'luma': (85, 125), 'sat': (0.36, 0.50)}}


def _frames(path, fps, w=72, h=128, limit=None):
    import numpy as np
    vf = ('fps={},'.format(fps) if fps else '') + 'scale={}:{}'.format(w, h)
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24']
    if limit:
        cmd += ['-frames:v', str(limit)]
    raw = subprocess.run(cmd + ['-'], check=True, stdout=subprocess.PIPE).stdout
    return np.frombuffer(raw, dtype='uint8').reshape(-1, h, w, 3).astype('float32')


def cmd_check(a):
    import numpy as np
    fr = _frames(a.inp, a.fps)
    if len(fr) == 0:            # a single still: no fps resampling
        fr = _frames(a.inp, None)
    Y = 0.299 * fr[..., 0] + 0.587 * fr[..., 1] + 0.114 * fr[..., 2]
    mx, mn = fr.max(-1), fr.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    per_luma = Y.mean(axis=(1, 2))
    ch, cw = int(128 * .15), int(72 * .15)
    corners = np.concatenate([Y[:, :ch, :cw], Y[:, :ch, -cw:], Y[:, -ch:, :cw], Y[:, -ch:, -cw:]], axis=1).mean()
    centre = Y[:, int(128 * .35):int(128 * .65), int(72 * .35):int(72 * .65)].mean()
    r = {'frames': int(len(fr)), 'luma': round(float(Y.mean()), 1), 'sat': round(float(sat.mean()), 3),
         'luma_sd': round(float(Y.std(axis=(1, 2)).mean()), 1), 'dark_frames_pct': round(float((per_luma < 70).mean() * 100), 1),
         'corner_ratio': round(float(corners / max(centre, 1e-6)), 2)}
    t = TARGETS[a.mode]
    r['pass'] = {k: t[k][0] <= r[k] <= t[k][1] for k in t}
    r['pass']['no_vignette'] = r['corner_ratio'] >= 0.95
    print(json.dumps(r, indent=1))
    return 0


def cmd_loopcheck(a):
    import numpy as np
    fr = _frames(a.inp, FPS, 108, 192)
    d = float(np.abs(fr[0] - fr[-1]).mean())
    print(json.dumps({'first_vs_last_mean_abs_diff': round(d, 2), 'loops': d < 6.0}))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest='cmd', required=True)

    def add(name, fn, io=True):
        q = sp.add_parser(name)
        if io:
            q.add_argument('inp')
            q.add_argument('out')
        q.add_argument('--dry', action='store_true')
        q.set_defaults(fn=fn)
        return q
    q = add('pulse', cmd_pulse)
    q.add_argument('--frames', required=True)
    q.add_argument('--lift', type=float, default=0.12)
    q.add_argument('--rise', type=int, default=2)
    q.add_argument('--decay', type=int, default=4)
    q = add('dropout', cmd_dropout)
    q.add_argument('--ranges', required=True)
    q = add('sfx', cmd_sfx)
    q.add_argument('--plan', required=True)
    q.add_argument('--whoosh', required=True)
    q.add_argument('--boom')
    q.add_argument('--shots')
    q.add_argument('--gain', type=float, default=-6.0)
    q = add('captions', cmd_captions)
    q.add_argument('--cards', required=True)
    q.add_argument('--fmt', default='short', choices=['short', 'long', 'cinematic'])
    q.add_argument('--ass')
    q.add_argument('--fontsdir')
    add('letterbox', cmd_letterbox)
    q = add('flash', cmd_flash)
    q.add_argument('--frames', required=True)
    q = add('drift2d', cmd_drift2d)
    q.add_argument('--dur', type=float, default=1.4)
    q.add_argument('--px-per-s', dest='px_per_s', type=float, default=200.0)
    q.add_argument('--direction', default='left', choices=['left', 'right'])
    q = add('shake', cmd_shake)
    q.add_argument('--frame', type=int, required=True)
    q.add_argument('--px', type=float, default=8.0)
    q.add_argument('--hz', type=float, default=12.0)
    q.add_argument('--frames', type=int, default=8)
    q = add('check', cmd_check, io=False)
    q.add_argument('inp')
    q.add_argument('--mode', default='day', choices=list(TARGETS))
    q.add_argument('--fps', type=float, default=2.0)
    q = add('loopcheck', cmd_loopcheck, io=False)
    q.add_argument('inp')
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
