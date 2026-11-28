# CIELAB colour separation check for Cast v3 (phases 1+2) against Cast v2 (Claude, 11-27).  python3 -I colour_check.py -> scratch/colour_check.txt
# sRGB (D65) -> CIELAB, distance = CIE76 dE (straight Lab distance), same as the phase-1 check.
import math, sys
def lab(c):
    f = lambda u: ((u / 255 + 0.055) / 1.055) ** 2.4 if u / 255 > 0.04045 else u / 255 / 12.92
    r, g, b = (f(v) for v in c)
    X = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047; Y = 0.2126 * r + 0.7152 * g + 0.0722 * b; Z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    t = lambda v: v ** (1 / 3) if v > 0.008856 else 7.787 * v + 16 / 116
    return (116 * t(Y) - 16, 500 * (t(X) - t(Y)), 200 * (t(Y) - t(Z)))
def dE(a, b): return math.dist(lab(a), lab(b))
V2 = {'Hero kid shirt': (206, 76, 48), 'Hero kid trousers': (52, 58, 82), 'Newbie shirt': (13, 105, 172), 'Newbie trousers': (75, 151, 75), 'Big kid shirt': (178, 44, 40),
      'Big kid denim': (40, 70, 130), 'Rich kid purple': (104, 46, 150), 'Rich kid gold': (236, 180, 60), 'Rich kid cape': (70, 24, 90), 'Little sister pink': (232, 112, 170),
      'Bacon green': (60, 150, 80), 'Bacon trousers': (60, 70, 110), 'Girl hero red': (150, 40, 40), 'Knight steel': (90, 100, 120), 'Queen green': (40, 120, 80),
      'Wizard blue': (50, 70, 160), 'Villain robe': (40, 26, 50), 'Villain collar': (90, 20, 40), 'Guard grey': (140, 150, 160), 'Slender black': (24, 24, 30),
      'Slender teen teal hair': (40, 200, 190), 'Slender trousers': (236, 236, 240)}
P1 = {'Oathbound obsidian': (40, 44, 56), 'Oathbound ice glow': (140, 220, 255), 'First Rank gold': (255, 192, 70), 'First Rank white': (232, 228, 218),
      'True-Form coat (=Hero)': (206, 76, 48), 'True-Form power glow': (255, 196, 70), 'Rigger lime': (150, 232, 40), 'Rigger charcoal': (46, 48, 54),
      'Ember orange': (242, 110, 28), 'Jailer rust': (142, 72, 36), 'Jailer hood': (20, 18, 22), 'Squire teal': (18, 138, 142), 'Squire brass': (206, 150, 62),
      'Crowd ochre': (196, 150, 58), 'Crowd olive': (112, 120, 58), 'Crowd rust': (136, 84, 62), 'Crowd slate': (84, 96, 112)}
P2 = {'Herald scarlet': (214, 22, 30), 'Herald gold trim': (236, 182, 62),
      'Horde Slate stone': (96, 102, 112), 'Horde Ash stone': (66, 62, 62), 'Horde Ash cracks': (255, 80, 30), 'Horde Moss moss': (86, 120, 52), 'Horde Frost stone': (118, 146, 176),
      'Old Legend coat grey': (104, 106, 110), 'Old Legend cloak': (122, 48, 56),
      'Golden Sister rose': (138, 22, 64), 'Golden Sister laurel': (240, 186, 66), 'Golden Sister stripe (=Hero shirt)': (206, 76, 48),
      'Roll Merchant plum': (96, 36, 86), 'Roll Merchant chest glow (epic)': (190, 90, 255),
      'Master Smith apron': (82, 50, 32), 'Master Smith forge glow': (255, 126, 30), 'Master Smith headwrap': (196, 84, 34),
      'Stone Keeper robe': (226, 218, 198), 'Stone Keeper indigo': (46, 44, 116),
      'Rival Heir cobalt': (24, 54, 168), 'Rival Heir steel': (186, 192, 204),
      'Turned Friend violet-black': (46, 26, 62), 'Turned Friend magenta': (255, 50, 200),
      'Mirror Twin shirt (inverted)': (49, 179, 207), 'Mirror Twin trousers (inverted)': (203, 197, 173), 'Mirror Twin hair (inverted)': (181, 207, 223),
      'Jester mustard': (226, 178, 24), 'Jester black': (26, 24, 30)}
SIGNATURE = {'Herald scarlet', 'Horde Slate stone', 'Horde Ash cracks', 'Horde Moss moss', 'Horde Frost stone', 'Old Legend cloak', 'Golden Sister rose', 'Roll Merchant plum',
             'Master Smith forge glow', 'Stone Keeper indigo', 'Rival Heir cobalt', 'Turned Friend magenta', 'Mirror Twin shirt (inverted)', 'Jester mustard'}
def nearest(name, c, pool, k=2):
    return sorted(((round(dE(c, v)), n) for n, v in pool.items() if n != name and not (n.split(' ')[0] == name.split(' ')[0] and n.split(' ')[1] == name.split(' ')[1])), key=lambda x: x[0])[:k]
out = ['CIELAB (CIE76 dE) separation check, Cast v3 phases 1+2 vs Cast v2 anchors. dE < 10 = same colour family on screen, 10-20 = close, > 20 = clearly different.', '',
       'calibration vs the phase-1 file: First Rank gold vs Rich kid gold dE=%d (phase-1 file: 6), Squire teal vs Slender teen teal hair dE=%d (25), Rigger lime vs Bacon green dE=%d (56)' % (
           round(dE(P1['First Rank gold'], V2['Rich kid gold'])), round(dE(P1['Squire teal'], V2['Slender teen teal hair'])), round(dE(P1['Rigger lime'], V2['Bacon green']))), '']
for title, D in (('PHASE 1', P1), ('PHASE 2', P2)):
    out.append(title)
    for n, c in D.items():
        nv = nearest(n, c, V2); others = dict(P1); others.update(P2); nn = nearest(n, c, others, 1)
        flag = '  <- signature' if n in SIGNATURE else ''
        out.append('%-36s nearest v2: %s dE=%d; next %s %d | nearest v3: %s %d%s' % (n, nv[0][1], nv[0][0], nv[1][1], nv[1][0], nn[0][1], nn[0][0], flag))
    out.append('')
out.append('PHASE 2 SIGNATURES CLOSER THAN dE 15 TO ANY v2 ANCHOR OR OTHER v3 COLOUR:')
allc = dict(V2); allc.update(P1); allc.update(P2); any_ = False
for n in SIGNATURE:
    for m, v in allc.items():
        if m == n or m.split(' ')[:2] == n.split(' ')[:2]: continue
        d = dE(P2[n], v)
        if d < 15: out.append('  %-34s ~ %-34s dE=%.0f' % (n, m, d)); any_ = True
if not any_: out.append('  none')
open('/tmp/claude-0/cast3/scratch/colour_check.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
