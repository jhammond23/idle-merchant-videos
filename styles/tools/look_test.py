# Same shot, five build styles: one town-square frame lit/graded with each style pack (our own scene and cast).
# STYLE=house|bright-cut|gneef-style|craftee-style|fourth-style OUT=... RES=540x960 SAMP=24
import os, sys, math, importlib
src = open('/tmp/claude-0/cast2/cast_v2.py').read()
src = src[:src.index('# hair colours')]
if os.environ.get('STYLE', 'house') != 'house': src = src.replace("MYF = '/tmp/claude-0/cast2/faces/'", "MYF = '/tmp/claude-0/kits/faces/'")
exec(compile(src, 'cast_v2_prefix', 'exec'))
import bpy
from mathutils import Vector
ST = os.environ.get('STYLE', 'house'); OUT = os.environ.get('OUT', f'/tmp/claude-0/kits/look/{ST}.png')
RES = tuple(map(int, os.environ.get('RES', '540x960').split('x'))); SAMP = int(os.environ.get('SAMP', '24'))
FACES = {'house': ('face_bright', 'face_bluebell_friendly', 'face_classic_grin', 0.86),
         'bright-cut': ('sunny_comic_shocked', 'sunny_line_scared', 'sunny_line_smug', 1.3),
         'gneef-style': ('ink_shocked', 'ink_scared', 'ink_smug', 1.1),
         'craftee-style': ('toybox_shocked', 'toybox_terrified', 'toybox_smug', 1.1),
         'fourth-style': ('stk_alarmed', 'stk_nervous', 'stk_smug', 1.08)}[ST]

# ---- the town square (same for every style) ----
def place(name, loc, rot=0, scale=1.0):
    try: return glb(name, loc=loc, rot=rot, scale=scale)
    except Exception as e: print('missing', name, e)
place('a1_cottage_timber', (-15, 30, 0), rot=12, scale=1.2)
place('a1_cottage_thatch', (14, 32, 0), rot=-15, scale=1.3)
place('a1_cottage_blue', (0, 44, 0), rot=0, scale=1.3)
place('a1_market_stall', (-10, 12, 0), rot=25, scale=1.0)
place('a1_town_lamp', (8.0, 8, 0), rot=0, scale=0.85)
place('a1_fountain', (6, 20, 0), rot=0, scale=1.0)
place('oak_b', (-26, 46, 0), rot=0, scale=1.3)
place('a1_barrel_stack', (-6.5, 3.5, 0), rot=20, scale=0.9)
ground(400, noise_mat('cobble', srgb(176, 166, 150), srgb(140, 130, 116), scale=1.6, rough=0.85, bump=0.25, voronoi=True))

# ---- the cast: hero kid (front), little sister, the king's guard ----
tint_hair('hero_crop', (60, 40, 30)); tint_hair('hero_twin_tails', (40, 26, 20)); tint_hair('hero_slick_back', (24, 18, 14))
hero = person('hero', (206, 76, 48), (52, 58, 82), (238, 196, 156), FACES[0], 'hero_crop', head='classic', fs=FACES[3], loc=(-0.6, -1.5, 0), s=0.85, rot=8, out=(10, 6))
sis = person('sis', (232, 112, 170), (232, 112, 170), (150, 104, 74), FACES[1], 'hero_twin_tails', head='classic', fs=FACES[3], loc=(-3.6, 0.6, 0), s=0.62, rot=18, arms=(-25, 0))
cone('skirt', 1.55, 1.05, 1.3, (0, 0, 1.55), fabric('skirtm', (220, 96, 156)), sis['root'])
guard = person('guard', (90, 100, 120), (50, 54, 66), (120, 84, 60), FACES[2], 'hero_slick_back', head='classic', fs=FACES[3], loc=(3.4, 2.4, 0), s=1.05, tw=2.4, rot=-18, arms=(0, -30))
box('gplate', (2.5, 1.12, 1.4), (0, 0, 3.3), steel, parent=guard['root'], bevel=0.12)
box('spear', (0.16, 0.16, 7.5), (0, -0.35, -0.5), wood, parent=guard['armR'])
cone('tip', 0.35, 0.0, 0.9, (0, -0.35, 3.7), steel, guard['armR'], verts=4)

cam = camera(lens=30); cam.location = (-0.4, -15.0, 4.2); look(cam, (0.2, 4.0, 4.4))
setup_render(RES[0], RES[1], SAMP)
sc = bpy.context.scene

def cycles(): sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMP
def packmod(dirname, mod):
    sys.path.insert(0, f'/home/claude/styles/{dirname}/pack'); return importlib.import_module(mod)

if ST == 'house':
    sky(sun_el=34, sun_rot=150, strength=0.35); sun(el=34, rot=150, energy=4.5)
    vs = sc.view_settings; vs.view_transform = 'Standard'
    try: vs.look = 'Medium High Contrast'
    except Exception: pass
    vs.exposure = -3.3
elif ST == 'bright-cut':
    m = packmod('bright-cut', 'style_bright_cut'); m.apply_look(sc, engine='CYCLES'); m.light_rig('noon', sc, cam=cam); cycles()
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.view_settings.exposure = float(os.environ.get('EXP', sc.view_settings.exposure))
elif ST == 'gneef-style':
    m = packmod('gneef-style', 'style_gneef'); m.apply_look(sc, mood=os.environ.get('MOOD', 'ember')); m.light_rig('ember_interior', target=(0, 0, 4.0), spread=10.0); cycles()
    sc.render.resolution_x, sc.render.resolution_y = RES
    if 'EXP' in os.environ: sc.view_settings.exposure = float(os.environ['EXP'])
else:
    did = False
    for dirname, mod in (('craftee-style', 'style_craftee_style'), ('fourth-style', 'style_fourth_style')):
        if ST != dirname: continue
        try:
            m = packmod(dirname, mod); m.apply_look(sc)
            if dirname == 'craftee-style': m.light_rig('day', cam=cam, scene=sc)
            else: m.light_rig('day', scene=sc, center=(0.0, 0.0, 4.0))
            did = True
        except Exception as e:
            print('pack failed, fallback look', e)
    if not did:
        sky(sun_el=48, sun_rot=150, strength=0.45); sun(el=48, rot=150, energy=4.2)
    cycles(); sc.render.resolution_x, sc.render.resolution_y = RES
    if 'EXP' in os.environ: sc.view_settings.exposure = float(os.environ['EXP'])
sc.render.resolution_percentage = 100
sc.render.use_motion_blur = False
sc.render.filepath = OUT; os.makedirs(os.path.dirname(OUT), exist_ok=True)
print('LOOK', sc.view_settings.view_transform, sc.view_settings.look, sc.view_settings.exposure, sc.render.engine)
bpy.ops.render.render(write_still=True); print('WROTE', OUT)
