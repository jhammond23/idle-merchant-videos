# Sample characters for a character kit, built with OUR Cast v2 pipeline (new characters of our own).
# Usage: KIT=sunny|toybox SHOT=lineup|faces OUT=... RES=WxH SAMP=n python3 -I render_kit.py
import os, sys, math
src = open('/tmp/claude-0/cast2/cast_v2.py').read()
src = src[:src.index('# hair colours')]          # helpers + materials only, no Cast v2 lineup
src = src.replace("MYF = '/tmp/claude-0/cast2/faces/'", "MYF = '/tmp/claude-0/kits/faces/'")
exec(compile(src, 'cast_v2_prefix', 'exec'))
import bpy
from mathutils import Vector

KIT = os.environ.get('KIT', 'sunny'); SHOT = os.environ.get('SHOT', 'lineup')
OUT = os.environ.get('OUT', f'/tmp/claude-0/kits/out/{KIT}_{SHOT}.png')
RES = tuple(map(int, os.environ.get('RES', '1080x1000').split('x'))); SAMP = int(os.environ.get('SAMP', '24'))

def hexrgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def stripes(name, c1, c2, n=5, height=2.0, z0=0.0):
    """bold horizontal two-colour stripes in object space"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.5
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = n / height; nt.links.new(sep.outputs[2], mu.inputs[0])
    fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'; nt.links.new(mu.outputs[0], fr.inputs[0])
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.5; nt.links.new(fr.outputs[0], gt.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; nt.links.new(gt.outputs[0], mix.inputs['Factor'])
    mix.inputs['A'].default_value = (*srgb(*c1), 1); mix.inputs['B'].default_value = (*srgb(*c2), 1); nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    return m
def restyle(P, m, parts=('torso', 'A')):
    for o in [P['root']] + list(P['root'].children_recursive):
        if o.type == 'MESH' and (o.name.endswith('T') or 'A' in o.name[-2:]) and not o.name.endswith('k'):
            if o.data.materials and 's' in o.data.materials[0].name[-1:]:
                o.data.materials[0] = m

C = {}   # characters
BUSTS = None
if KIT == 'sunny':
    # Sunny Block Folk: classic heads, line faces in wide shots, neutral base + ONE bright accent garment each, noon light.
    skin = [hexrgb(x) for x in ['#F4D4B7', '#E2B282', '#B07A55', '#8A5A3C', '#5E3B2A', '#F5CD30', '#CD9E79']]
    tint_hair('hero_pixie', (227, 194, 122)); tint_hair('hero_swept_undercut', (227, 194, 122)); tint_hair('hero_low_bun', (105, 54, 16)); tint_hair('face_full_beard', (53, 45, 44))
    tint_hair('hero_slick_back', (19, 18, 27)); tint_hair('hero_side_wave', (179, 38, 30)); tint_hair('hero_medium_tousle', (53, 45, 44))
    if SHOT == 'lineup':
        F = 'sunny_line_'; FS = 1.3
        C['bell'] = person('bell', (224, 38, 42), (76, 88, 106), skin[0], F + 'happy', 'hero_pixie', head='classic', fs=FS, loc=(-6.6, -1.2, 0), s=0.88, rot=12, out=(6, 4), arms=(-18, 0))
        C['baker'] = person('baker', (226, 233, 233), (76, 88, 106), skin[2], F + 'neutral', 'hero_low_bun', head='classic', fs=FS, loc=(-3.3, 0.6, 0), s=1.0, rot=6)
        box('apron', (2.04, 0.12, 2.6), (0, -0.56, 2.9), fabric('apronm', (39, 196, 208)), parent=C['baker']['root'], bevel=0.03)
        C['smith'] = person('smith', (162, 171, 187), (52, 45, 44), skin[3], F + 'determined', None, 'face_full_beard', head='classic', fs=FS, loc=(0.4, 1.6, 0), s=1.0, tw=2.4, rot=-2, out=(8, 8))
        box('sapron', (2.44, 0.14, 3.0), (0, -0.57, 2.6), fabric('sapronm', (135, 65, 55), 1.5), parent=C['smith']['root'], bevel=0.03)
        C['capt'] = person('capt', (76, 88, 106), (19, 18, 27), skin[4], F + 'smug', 'hero_slick_back', head='classic', fs=FS, loc=(4.0, 0.8, 0), s=1.1, rot=-8)
        box('tabard', (1.3, 1.08, 2.3), (0, 0, 3.1), fabric('tabm', (212, 190, 67)), parent=C['capt']['root'], bevel=0.04)
        C['crowd'] = person('crowd', (13, 105, 172), (75, 151, 75), skin[5], F + 'shocked', None, head='classic', fs=FS, loc=(7.2, -0.8, 0), s=0.9, rot=-16, arms=(-30, -30))
        C['kid2'] = person('kid2', (118, 199, 132), (162, 171, 187), skin[6], F + 'scared', 'hero_side_wave', head='classic', fs=FS, loc=(-9.6, 0.4, 0), s=0.86, rot=18)
        cam = camera(lens=34); cam.location = (-1.2, -22.0, 3.9); look(cam, (-1.2, 0.5, 3.4))
    else:  # comic faces close-up row on one new character
        BUSTS = []
        for i, (e, x) in enumerate(zip(['shocked', 'angry', 'happy', 'scared'], [-12, -4, 4, 12])):
            C[e] = person('c' + e, (224, 38, 42), (76, 88, 106), skin[0], 'sunny_comic_' + e, 'hero_swept_undercut', head='classic', loc=(x, 0, 0), s=1.0, fs=1.3, rot=0); BUSTS.append((e, x))
        cam = camera(lens=50)
    # noon: pale sky, bright, low saturation
    sky(sun_el=62, sun_rot=160, strength=0.55)
    sun(el=62, rot=160, energy=5.0, color=(1, 0.97, 0.92))
    gm = noise_mat('cobble', srgb(170, 176, 186), srgb(140, 148, 162), scale=1.6, rough=0.85, bump=0.2, voronoi=True)
    wallc = (190, 200, 206); EXP = -4.5
elif KIT == 'ink':
    # Inkface Blockfolk: classic heads, flat ink faces, one signature colour for the lead, textured clothes, one motivated light.
    skin = [hexrgb(x) for x in ['#F6D2B0', '#F0BE8C', '#E3A06C', '#C98E5F', '#8D5A3B', '#5A3524', '#F5CD30']]
    tint_hair('hero_medium_tousle', (245, 110, 2)); tint_hair('hero_long_tie', (122, 74, 42)); tint_hair('hero_slick_back', (30, 26, 26))
    tint_hair('hero_side_braid', (232, 194, 90)); tint_hair('face_full_beard', (184, 180, 176)); tint_hair('hero_crop', (166, 58, 30))
    if SHOT == 'lineup':
        F = 'ink_'; FS = 1.1
        C['lead'] = person('lead', (40, 120, 200), (50, 46, 60), skin[1], F + 'smug', 'hero_medium_tousle', head='classic', fs=FS, loc=(-0.4, -1.2, 0), s=0.85, rot=6, out=(6, 4))
        box('vest', (2.06, 1.08, 1.6), (0, 0, 3.2), fabric('vestm', (90, 60, 40), 2.0), parent=C['lead']['root'], bevel=0.1)
        C['sis'] = person('sis', (200, 170, 120), (90, 70, 60), skin[3], F + 'scared', 'hero_side_braid', head='classic', fs=FS, loc=(-3.4, -0.6, 0), s=0.62, rot=14)
        C['inn'] = person('inn', (120, 40, 30), (60, 50, 44), skin[4], F + 'happy', 'hero_long_tie', head='classic', fs=FS, loc=(-6.6, 0.8, 0), s=1.0, rot=12)
        box('iapron', (2.04, 0.12, 2.6), (0, -0.56, 2.9), fabric('iapm', (200, 190, 170), 1.6), parent=C['inn']['root'], bevel=0.03)
        C['guard'] = person('guard', (70, 74, 60), (40, 40, 44), skin[5], F + 'angry', 'hero_slick_back', head='classic', fs=FS, loc=(3.4, 0.6, 0), s=1.05, tw=2.4, rot=-8)
        box('gplate', (2.5, 1.12, 1.4), (0, 0, 3.3), steel, parent=C['guard']['root'], bevel=0.12)
        C['old'] = person('old', (60, 50, 90), (40, 36, 50), skin[0], F + 'shocked', None, 'face_full_beard', head='classic', fs=FS, loc=(6.8, 1.2, 0), s=1.0, rot=-14, arms=(-30, 0))
        C['kid'] = person('kid', (230, 200, 60), (60, 70, 110), skin[2], F + 'terror', 'hero_crop', head='classic', fs=FS, loc=(-9.4, 0.2, 0), s=0.85, rot=18)
        cam = camera(lens=40); cam.location = (-1.2, -22.0, 3.9); look(cam, (-1.2, 0.5, 3.3))
    else:
        BUSTS = []
        for i, (e, x) in enumerate([(a, b) for a, b in zip(['terror', 'angry', 'crying', 'smug'], [-12, -4, 4, 12]) if a in os.environ.get('ONLY', a)]):
            P = person('c' + e, (40, 120, 200), (50, 46, 60), skin[1], 'ink_' + e, 'hero_medium_tousle', head='classic', loc=(x, 0, 0), s=1.0, fs=1.1)
            box('cv' + e, (2.06, 1.08, 1.6), (0, 0, 3.2), fabric('cvm' + e, (90, 60, 40), 2.0), parent=P['root'], bevel=0.1); BUSTS.append((e, x))
        cam = camera(lens=50)
    # torchlit: dim cool moonlight + one warm lantern; crushed blacks
    sky(sun_el=8, sun_rot=200, strength=0.05)
    sun(el=30, rot=210, energy=0.6, color=(0.62, 0.62, 0.95))
    if SHOT == 'lineup': point((2.0, -6.0, 6.5), (1.0, 0.62, 0.3), 9000, radius=0.6)
    if SHOT != 'lineup':
        for e, x in BUSTS: point((x + 2.6, -4.2, 6.6), (1.0, 0.62, 0.3), 150, radius=0.5)
    gm = noise_mat('cobble', srgb(90, 80, 74), srgb(60, 52, 48), scale=1.6, rough=0.85, bump=0.25, voronoi=True)
    wallc = (120, 100, 86); EXP = -1.35
elif KIT == 'sticker':
    # Sticker Saga Cast: classic heads, thin ink line faces + anime-lite faces, OVERSIZED hair, one dominant outfit colour, natural light with true blacks.
    skin = [hexrgb(x) for x in ['#F3D2B3', '#E2B48C', '#C8956A', '#9A6A48', '#6A4630', '#F5CD30']]
    tint_hair('hero_medium_tousle', (18, 16, 20)); tint_hair('hero_long_straight', (40, 28, 24)); tint_hair('hero_slick_back', (60, 40, 28))
    tint_hair('hero_twin_tails', (200, 150, 90)); tint_hair('hero_half_knot', (30, 26, 30)); tint_hair('hero_crop', (22, 20, 24))
    if SHOT == 'lineup':
        F = 'stk_'; FS = 1.08
        C['hero'] = person('hero', (24, 24, 28), (40, 44, 60), skin[1], F + 'determined', 'hero_medium_tousle', head='classic', fs=FS, loc=(-0.4, -1.0, 0), s=1.0, hair_s=1.25, rot=6)
        box('print', (1.2, 0.1, 1.0), (0, -0.52, 3.2), mat('printm', srgb(240, 240, 236), 0.6), parent=C['hero']['root'], bevel=0.02)
        C['girl'] = person('girl', (40, 60, 120), (150, 40, 50), skin[0], F + 'smug', 'hero_long_straight', head='classic', fs=FS, loc=(-3.8, 0.4, 0), s=1.0, hair_s=1.2, rot=10)
        box('bow', (0.6, 0.12, 0.3), (0, -0.55, 3.9), mat('bowm', srgb(200, 40, 50), 0.5), parent=C['girl']['root'], bevel=0.02)
        C['mum'] = person('mum', (70, 130, 80), (60, 56, 70), skin[2], F + 'happy', 'hero_twin_tails', head='classic', fs=FS, loc=(-7.2, 1.2, 0), s=1.0, rot=14)
        C['guard'] = person('guard', (120, 30, 36), (40, 40, 46), skin[3], F + 'shouting', 'hero_slick_back', head='classic', fs=FS, loc=(3.4, 0.6, 0), s=1.0, rot=-8, arms=(-30, 0))
        C['friend'] = person('friend', (230, 170, 40), (60, 70, 110), skin[4], F + 'alarmed', 'hero_crop', head='classic', fs=FS, loc=(6.8, 1.0, 0), s=0.9, hair_s=1.2, rot=-14)
        C['kid'] = person('kid', (120, 120, 130), (60, 60, 70), skin[5], F + 'nervous', None, head='classic', fs=FS, loc=(-10.2, 0.4, 0), s=0.85, rot=18)
        cam = camera(lens=40); cam.location = (-1.6, -22.0, 3.9); look(cam, (-1.6, 0.5, 3.4))
    else:
        BUSTS = []
        for i, (e, x) in enumerate([(a, b) for a, b in zip(['smug', 'alarmed', 'shouting', 'happy'], [-12, -4, 4, 12]) if a in os.environ.get('ONLY', a)]):
            P = person('c' + e, (24, 24, 28), (40, 44, 60), skin[1], 'stk_' + e, 'hero_crop', head='classic', loc=(x, 0, 0), s=1.0, fs=1.08, hair_s=1.04)
            box('cp' + e, (1.2, 0.1, 1.0), (0, -0.52, 3.2), mat('cpm' + e, srgb(240, 240, 236), 0.6), parent=P['root'], bevel=0.02); BUSTS.append((e, x))
        cam = camera(lens=50)
    sky(sun_el=40, sun_rot=140, strength=0.3)
    sun(el=40, rot=140, energy=3.6, color=(1, 0.95, 0.88))
    gm = noise_mat('floor', srgb(150, 140, 128), srgb(110, 100, 92), scale=1.4, rough=0.8, bump=0.15)
    if SHOT != 'lineup':
        for e, x in BUSTS: point((x - 1.0, -4.5, 5.4), (1.0, 0.97, 0.92), 120, radius=1.5)
    wallc = (196, 186, 170); EXP = -4.15
else:
    # Toybox Blockfolk: everyone the same height (s=1.0), classic head, thick ink line faces, hero in bold stripes.
    skin = [hexrgb(x) for x in ['#FDD296', '#F8B383', '#EAB494', '#E0A46C', '#C88A4C', '#8D6C4C', '#6B4A35', '#F5CD30']]
    tint_hair('hero_crop', (107, 66, 38)); tint_hair('hero_twin_tails', (242, 208, 74)); tint_hair('hero_long_straight', (237, 230, 208))
    tint_hair('hero_swept_undercut', (63, 163, 58)); tint_hair('hero_half_knot', (28, 26, 30)); tint_hair('face_braided_beard', (138, 143, 150))
    hs = 1.04
    if SHOT == 'lineup':
        F = 'toybox_'; FS = 1.1
        C['hero'] = person('hero', (207, 61, 19), (60, 52, 64), skin[1], F + 'grin', 'hero_crop', head='classic', fs=FS, loc=(-0.2, -1.0, 0), s=1.0, hs=hs, rot=4, out=(6, 6), arms=(-20, 0))
        restyle(C['hero'], stripes('herostripe', (207, 61, 19), (243, 230, 200), n=5, height=2.0))
        C['farm'] = person('farm', (240, 200, 90), (90, 70, 60), skin[3], F + 'innocent', 'hero_twin_tails', head='classic', fs=FS, loc=(-4.2, 0.6, 0), s=1.0, hs=hs, rot=10)
        C['knight'] = person('knight', (64, 92, 160), (40, 44, 58), skin[5], F + 'angry', 'hero_half_knot', head='classic', fs=FS, loc=(3.8, 0.4, 0), s=1.0, hs=hs, rot=-8)
        box('trim', (2.06, 1.06, 0.3), (0, 0, 2.1), mat('trimm', srgb(236, 180, 60), 0.4), parent=C['knight']['root'], bevel=0.03)
        C['gran'] = person('gran', (150, 70, 120), (90, 60, 90), skin[0], F + 'smug', 'hero_long_straight', head='classic', fs=FS, loc=(-7.8, 1.4, 0), s=1.0, hs=hs, rot=16)
        cone('gdress', 1.7, 1.05, 2.0, (0, 0, 1.0), fabric('gdressm', (150, 70, 120)), C['gran']['root'])
        C['elder'] = person('elder', (110, 130, 80), (70, 60, 50), skin[6], F + 'shocked', None, 'face_braided_beard', head='classic', fs=FS, loc=(7.6, 1.4, 0), s=1.0, hs=hs, rot=-16, arms=(-40, -40))
        C['tot'] = person('tot', (120, 200, 230), (120, 200, 230), skin[7], F + 'happy', None, head='classic', fs=FS, loc=(1.9, -2.4, 0), s=0.6, hs=hs, rot=-10)
        cam = camera(lens=40); cam.location = (-0.2, -22.0, 3.9); look(cam, (-0.2, 0.5, 3.3))
    else:
        BUSTS = []
        for i, (e, x) in enumerate([(a, b) for a, b in zip(['terrified', 'angry', 'crying', 'innocent'], [-12, -4, 4, 12]) if a in os.environ.get('ONLY', a)]):
            P = person('c' + e, (207, 61, 19), (60, 52, 64), skin[1], 'toybox_' + e, 'hero_crop', head='classic', loc=(x, 0, 0), s=1.0, hs=hs, fs=1.1)
            restyle(P, stripes('cs' + e, (207, 61, 19), (243, 230, 200), n=5, height=2.0)); BUSTS.append((e, x))
        cam = camera(lens=50)
    sky(sun_el=48, sun_rot=150, strength=0.45)
    sun(el=48, rot=150, energy=4.2, color=(1, 0.96, 0.9))
    gm = noise_mat('grass', srgb(150, 178, 110), srgb(120, 150, 90), scale=1.2, rough=0.9, bump=0.15)
    wallc = (214, 196, 168); EXP = -4.4

ground(200, gm)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 16, 4.0)); wall = bpy.context.active_object
wall.scale = (70, 8, 1); wall.rotation_euler = (math.radians(90), 0, 0)
wall.data.materials.append(noise_mat('wall', srgb(*wallc), srgb(*[int(v * 0.9) for v in wallc]), scale=0.6, rough=0.9, bump=0.12))
setup_render(RES[0], RES[1], SAMP)
vs_ = bpy.context.scene.view_settings; vs_.view_transform = 'Standard'
try: vs_.look = 'Medium High Contrast'
except Exception: pass
vs_.exposure = float(os.environ.get('EXP', EXP))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
if BUSTS:
    for e, x in BUSTS:
        cam.location = (x, -4.1, 4.8); look(cam, (x, 0, 4.45))
        bpy.context.scene.render.filepath = OUT.replace('.png', '_' + e + '.png'); bpy.ops.render.render(write_still=True)
        print('WROTE', bpy.context.scene.render.filepath)
else:
    bpy.context.scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
    print('WROTE', OUT)
