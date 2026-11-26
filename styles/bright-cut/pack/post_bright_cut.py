#!/usr/bin/env python3
"""Bright Snap Cut (`bright-cut`) ffmpeg post pass.

Takes a rendered 1080x1920 30 fps film plus an effects plan (JSON) and writes the finished
video. All sizes are in pixels at 1080 wide and scale to the input width automatically.
Numbers come from STYLE.md section 14 (measured on five cannonanimates reels).

    python3 post_bright_cut.py in.mp4 out.mp4 --plan fx.json            # run
    python3 post_bright_cut.py in.mp4 out.mp4 --plan fx.json --dry-run  # print the command only
    python3 post_bright_cut.py --example                                # print an example plan

Plan keys (all optional, frames are 0-based at 30 fps):
  "whip_in":     {"frames": 4, "radius": 60, "angle": 0}           T3, blur on f0-f3 (60 px then 25 px)
  "rgb_glitch":  [{"cut": 40, "pre": 7, "post": 2}]                 T7, channel split 6 -> 12 -> 24 px into the cut
  "white_flash": [{"frame": 120, "fade": 3}]                        T13, 1 f white then 3 f fade
  "shake":       [{"frames": [300, 306], "px": 8, "freq": 5}]       T6, 4-10 px at 4-6 Hz (adds a constant 2.2 % crop)
  "halo":        true                                               optional 2-4 px light rim (unsharp 5:5:0.8)
  "sfx":         [{"time": 2.82, "file": "whoosh.wav", "gain_db": -8}]   whooshes/impacts (20-24 a minute, 82-88 % on cuts)
  "loudnorm":    true                                               house -14 LUFS
  "ass":         "captions.ass"                                     burn captions last (see captions_bright_cut.json)
Never add: freeze frames, grain, vignette, letterbox, fades to black (none were found).
"""
import argparse
import json
import shlex
import subprocess
import sys

FPS = 30
EXAMPLE = {
    "whip_in": {"frames": 4, "radius": 60, "angle": 0},
    "rgb_glitch": [{"cut": 41, "pre": 7, "post": 2}],
    "white_flash": [{"frame": 845, "fade": 3}],
    "shake": [{"frames": [1302, 1308], "px": 8, "freq": 5}],
    "halo": False,
    "sfx": [{"time": -0.07, "file": "sfx/whoosh_short.wav", "gain_db": -8},
            {"time": 1.30, "file": "sfx/glitch.wav", "gain_db": -10}],
    "loudnorm": True,
}


def probe_size(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height", "-of", "csv=p=0:s=x", path],
                             capture_output=True, text=True, check=True).stdout.strip()
        w, h = out.split("x")
        return int(w), int(h)
    except Exception:
        return 1080, 1920


def has_audio(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                              "stream=index", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
        return bool(out.strip())
    except Exception:
        return True


def video_chain(plan, w, h):
    k = w / 1080.0
    f = []
    wi = plan.get("whip_in")
    if wi:
        n = int(wi.get("frames", 4))
        r = wi.get("radius", 60) * k
        a = wi.get("angle", 0)
        half = max(1, n // 2)
        f.append(f"dblur=angle={a}:radius={r:.1f}:enable='between(n,0,{half - 1})'")
        f.append(f"dblur=angle={a}:radius={r * 0.42:.1f}:enable='between(n,{half},{n - 1})'")
    for g in plan.get("rgb_glitch", []):
        c, pre, post = int(g["cut"]), int(g.get("pre", 7)), int(g.get("post", 2))
        a0 = c - pre
        third = max(1, pre // 3)
        steps = [(a0, a0 + third - 1, 6), (a0 + third, a0 + 2 * third - 1, 12), (a0 + 2 * third, c + post - 1, 24)]
        for s, e, px in steps:
            p = max(1, int(round(px * k)))
            f.append(f"rgbashift=rh=-{p}:bh={p}:gv={max(1, p // 4)}:edge=smear:enable='between(n,{s},{e})'")
    for fl in plan.get("white_flash", []):
        fr, fade = int(fl["frame"]), int(fl.get("fade", 3))
        st = fr / FPS
        d = (fade + 1) / FPS
        f.append(f"fade=t=in:st={st:.4f}:d={d:.4f}:color=white:enable='between(n,{fr},{fr + fade})'")
    shakes = plan.get("shake", [])
    if shakes:
        amp_max = max(s.get("px", 8) for s in shakes) * k * 1.5
        mx = int(round(amp_max))
        my = int(round(amp_max * h / w))
        xs, ys = [], []
        for i, s in enumerate(shakes):
            a, b = s["frames"]
            px = s.get("px", 8) * k
            fq = s.get("freq", 5)
            win = f"between(n,{a},{b})"
            xs.append(f"{px:.2f}*sin(2*PI*{fq}*t+{i})*{win}")
            ys.append(f"{px * 0.75:.2f}*sin(2*PI*{fq * 1.17:.2f}*t+{i + 1.3})*{win}")
        f.append(f"crop=w=iw-{2 * mx}:h=ih-{2 * my}:x='{mx}+{'+'.join(xs)}':y='{my}+{'+'.join(ys)}'")
        f.append(f"scale={w}:{h}:flags=lanczos")
    if plan.get("halo"):
        f.append("unsharp=5:5:0.8")
    if plan.get("ass"):
        # burn captions LAST so the whip blur, glitch and shake never touch them (frame 0 caption is sharp)
        f.append("ass=" + plan["ass"].replace(chr(92), "/").replace(":", chr(92) + ":"))
    f.append("format=yuv420p")
    return ",".join(f)


def build_cmd(inp, out, plan):
    w, h = probe_size(inp)
    vf = video_chain(plan, w, h)
    sfx = plan.get("sfx", [])
    cmd = ["ffmpeg", "-y", "-i", inp]
    for s in sfx:
        cmd += ["-i", s["file"]]
    fc = [f"[0:v]{vf}[v]"]
    amaps = []
    base_audio = has_audio(inp)
    if base_audio:
        amaps.append("[0:a]")
    for i, s in enumerate(sfx, start=1):
        ms = max(0, int(round(s["time"] * 1000)))
        fc.append(f"[{i}:a]adelay={ms}|{ms},volume={s.get('gain_db', -8)}dB[s{i}]")
        amaps.append(f"[s{i}]")
    if amaps:
        if len(amaps) > 1:
            mix = f"{''.join(amaps)}amix=inputs={len(amaps)}:normalize=0:duration=first"
        else:
            mix = f"{amaps[0]}anull"
        if plan.get("loudnorm", True):
            mix += ",loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000"
        fc.append(mix + "[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]"]
    if amaps:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", out]
    return cmd


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inp", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--plan", help="effects plan JSON")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--example", action="store_true")
    a = ap.parse_args()
    if a.example:
        print(json.dumps(EXAMPLE, indent=1))
        return
    if not (a.inp and a.out):
        ap.error("need input and output")
    plan = json.load(open(a.plan)) if a.plan else {}
    cmd = build_cmd(a.inp, a.out, plan)
    print(" ".join(shlex.quote(c) for c in cmd))
    if not a.dry_run:
        sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
