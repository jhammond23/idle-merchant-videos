#!/usr/bin/env python3
"""Lay a music-bank track under a finished film.

usage: python3 -I addbed.py FILM.mp4 VOICE.mp3 TRACK_ID OUT.mp4 [GAIN_DB]

- loops the bank track (crossfade XF s at each join) to the film's length, fades out the last 1.4 s
- ducks it under the narrator with a sidechain keyed on the voice-only track (the approved voice-final)
- mixes it under the film's own audio (voice + effects), loudnorm to -14 LUFS / -1.5 dBTP
- copies the video stream (no re-encode), so swipe-in, captions and watermark stay as finished
Default gain +8 dB on the bank's -26 LUFS masters puts the bed ~13 dB under speech (Bunny, 11-26).
"""
import json, os, subprocess, sys

BANK = os.path.dirname(os.path.abspath(__file__))
XF = 1.5


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())


def main():
    film, voice, tid, out = sys.argv[1:5]
    gain = float(sys.argv[5]) if len(sys.argv) > 5 else 8.0
    bank = json.load(open(os.path.join(BANK, 'bank.json')))
    t = next(x for x in bank['tracks'] if x['id'] == tid)
    track = os.path.join(BANK, 'tracks', t['file'])
    D, L = dur(film), dur(track)
    n = 1
    while n * L - (n - 1) * XF < D:
        n += 1
    ins = ['-i', film] + sum([['-i', track] for _ in range(n)], []) + ['-i', voice]
    chain = '[1:a]'
    fc = []
    for k in range(2, n + 1):
        lab = f'[j{k}]'
        fc.append(f'{chain}[{k}:a]acrossfade=d={XF}:c1=tri:c2=tri{lab}')
        chain = lab
    fade = max(0.0, D - 1.4)
    fc.append(f'{chain}atrim=0:{D:.3f},afade=t=out:st={fade:.3f}:d=1.4,volume={gain}dB,aresample=48000,aformat=channel_layouts=stereo[bed]')
    fc.append(f'[{n + 1}:a]aresample=48000,aformat=channel_layouts=stereo[key]')
    fc.append('[bed][key]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=350[bd]')
    fc.append('[0:a]aresample=48000,aformat=channel_layouts=stereo[fa]')
    fc.append('[fa][bd]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]')
    tmp = out[:-4] + '.part.mp4'
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[out]',
                           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', '-t', f'{D:.3f}', tmp])
    os.replace(tmp, out)
    print(out, os.path.getsize(out), f'{D:.2f}s', f'track={tid} loops={n} gain={gain}dB')


if __name__ == '__main__':
    main()
