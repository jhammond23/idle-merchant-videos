# Cast round 2 (Claude, 11-25): 13 reusable characters. Locked R6 code + library heads/faces/hair; accessories as geometry.
import sys, os, math
sys.path.insert(0, '/tmp/claude-0/cast2/src')
import lib
from lib import *
import bpy
from mathutils import Vector, Matrix

MYF = '/tmp/claude-0/cast2/faces/'
_orig_fp = lib.face_path
lib.face_path = lambda face: MYF + face + '.png' if os.path.exists(MYF + face + '.png') else _orig_fp(face)
OUT = os.environ.get('OUT', '/tmp/claude-0/cast2/out/cast_v2.png')
RES = tuple(map(int, os.environ.get('RES', '2400x1350').split('x')))
SAMP = int(os.environ.get('SAMP', '20'))
reset()

CH = '/mnt/user-data/uploads/library/cast/classic-roblox-head/v001/Classic Roblox head.blend'
with bpy.data.libraries.load(CH) as (src, dst):
    dst.meshes = ['Classic Roblox head geometry']
CMESH = dst.meshes[0]
vs = [v.co.copy() for v in CMESH.vertices]
mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
k = 1.3 / max((mx - mn).x, (mx - mn).y); CMESH.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-(mn + mx) / 2))
for p in CMESH.polygons: p.use_smooth = True

def head_mat2(name, skin, face, fs=0.86, voff=0.0):
    """like lib.head_mat, but the face decal can be enlarged (fs<1) so features read at full-body size"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.5
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY_ADD'; mu.inputs[1].default_value = 1 / (1.2 * fs); mu.inputs[2].default_value = 0.5; nt.links.new(sep.outputs[0], mu.inputs[0])
    mv = nt.nodes.new('ShaderNodeMath'); mv.operation = 'MULTIPLY_ADD'; mv.inputs[1].default_value = 1 / (1.2 * fs); mv.inputs[2].default_value = 0.5 + voff; nt.links.new(sep.outputs[2], mv.inputs[0])
    cmb = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(mu.outputs[0], cmb.inputs[0]); nt.links.new(mv.outputs[0], cmb.inputs[1])
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.extension = 'CLIP'
    tex.image = bpy.data.images.get(face + '.png') or bpy.data.images.load(lib.face_path(face)); nt.links.new(cmb.outputs[0], tex.inputs[0])
    front = nt.nodes.new('ShaderNodeMath'); front.operation = 'LESS_THAN'; front.inputs[1].default_value = -0.1; nt.links.new(sep.outputs[1], front.inputs[0])
    am = nt.nodes.new('ShaderNodeMath'); am.operation = 'MULTIPLY'; nt.links.new(tex.outputs['Alpha'], am.inputs[0]); nt.links.new(front.outputs[0], am.inputs[1])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; nt.links.new(am.outputs[0], mix.inputs['Factor'])
    mix.inputs['A'].default_value = (*skin, 1); nt.links.new(tex.outputs['Color'], mix.inputs['B']); nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    return m

def fabric(name, rgb, sc=1.0):
    c = srgb(*rgb); c2 = tuple(v * 0.9 for v in c)
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 6 * sc; nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (*c2, 1); r.color_ramp.elements[1].color = (*c, 1)
    r.color_ramp.elements[0].position = 0.35; r.color_ramp.elements[1].position = 0.65
    nt.links.new(n.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    w = nt.nodes.new('ShaderNodeTexWave'); w.inputs['Scale'].default_value = 60 * sc; nt.links.new(tc.outputs['Object'], w.inputs['Vector'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.18; nt.links.new(w.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = 0.85
    return m

def tint_hair(key, rgb):
    m = mat('hair_' + key, srgb(*rgb), 0.55)
    for o in hair_col(key).all_objects:
        if o.type == 'MESH': o.data.materials.clear(); o.data.materials.append(m)

def person(name, shirt, pants, skin, face, hair=None, beard=None, head='refl', loc=(0, 0, 0), s=1.0, fs=0.86,
           tw=2.0, td=1.0, th=2.0, lh=2.0, lw=1.0, aw=1.0, al=2.0, hs=1.0, rot=0, arms=(0, 0), out=(0, 0), hair_s=0.9):
    root = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(root)
    root.location = loc; root.scale = (s,) * 3; root.rotation_euler = (0, 0, math.radians(rot))
    sk = srgb(*skin); ms = fabric(name + 's', shirt); mp = fabric(name + 'p', pants, 1.3); mk = mat(name + 'k', sk, 0.5)
    P = {'root': root}
    P['torso'] = box(name + 'T', (tw, td, th), (0, 0, lh + th / 2), ms, parent=root, bevel=0.08)
    hz = lh + th + 0.6 * hs; P['hz'] = hz; P['top'] = lh + th
    if head == 'classic':
        h = bpy.data.objects.new(name + 'H', CMESH.copy()); bpy.context.scene.collection.objects.link(h); h.data.materials.clear()
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=0.6, depth=1.2, location=(0, 0, 0))
        h = bpy.context.active_object; h.name = name + 'H'
        bv = h.modifiers.new('bv', 'BEVEL'); bv.width = 0.22; bv.segments = 5; bv.limit_method = 'ANGLE'; bpy.ops.object.shade_smooth()
    h.parent = root; h.location = (0, 0, hz); h.scale = (hs,) * 3
    h.data.materials.append(head_mat2(name + 'face', sk, face, fs)); P['head'] = h
    for i, (side, sg) in enumerate((('L', -1), ('R', 1))):
        piv = bpy.data.objects.new(name + 'arm' + side, None); bpy.context.scene.collection.objects.link(piv)
        piv.parent = root; piv.location = (sg * (tw / 2 + aw / 2), 0, lh + th - 0.2)
        piv.rotation_euler = (math.radians(arms[i]), math.radians(-sg * out[i]), 0)
        box(name + 'A' + side, (aw, td, al), (0, 0, -al / 2 + 0.2), ms, parent=piv, bevel=0.06)
        box(name + 'Hd' + side, (aw * 0.98, td * 0.98, 0.5), (0, 0, -al + 0.42), mk, parent=piv, bevel=0.06)
        P['arm' + side] = piv
        lp = bpy.data.objects.new(name + 'leg' + side, None); bpy.context.scene.collection.objects.link(lp)
        lp.parent = root; lp.location = (sg * tw / 4, 0, lh)
        box(name + 'L' + side, (lw, td, lh), (0, 0, -lh / 2), mp, parent=lp, bevel=0.06)
        P['leg' + side] = lp
    for key, sc in ((hair, hair_s), (beard, 0.9)):
        if not key: continue
        inst = bpy.data.objects.new(name + '_' + key, None); inst.instance_type = 'COLLECTION'; inst.instance_collection = hair_col(key)
        bpy.context.scene.collection.objects.link(inst); inst.parent = root; inst.location = (0, 0, hz); inst.scale = (sc * hs,) * 3
    return P

def cone(name, r1, r2, d, loc, m, parent, verts=32):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=d, location=loc)
    o = bpy.context.active_object; o.name = name; o.parent = parent; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def torus(name, R, r, loc, m, parent):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; o.parent = parent; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def ball(name, r, loc, m, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc)
    o = bpy.context.active_object; o.name = name; o.parent = parent; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

steel = mat('steel', srgb(176, 184, 196), 0.35, metal=0.9)
iron = mat('iron', srgb(120, 126, 136), 0.55, metal=0.6)
gold = mat('gold', srgb(236, 180, 60), 0.25, metal=1.0)
wood = mat('wood', srgb(120, 82, 50), 0.7)
leather = fabric('leather', (110, 70, 40), 2.0)
black = mat('blackm', srgb(20, 20, 24), 0.3)
glowp = mat('glowp', srgb(170, 80, 255), 0.2, emit=(0.7, 0.3, 1.0), estr=6)

# hair colours (one key per character)
for k_, c_ in (('hero_medium_tousle', (30, 22, 18)), ('hero_swept_undercut', (236, 200, 110)), ('hero_twin_tails', (40, 26, 20)),
               ('hero_slick_back', (24, 18, 14)), ('face_braided_beard', (24, 18, 14)), ('hero_low_bun', (60, 36, 24)),
               ('hero_long_straight', (236, 236, 240)), ('face_full_beard', (236, 236, 240)), ('hero_half_knot', (16, 14, 20)),
               ('hero_side_wave', (110, 64, 34)), ('hero_pixie', (40, 200, 190)), ('hero_long_tie', (196, 70, 36))):
    tint_hair(k_, c_)

# ---------------- FRONT ROW: kids ----------------
FX = [-10.5, -7.0, -3.5, 0.0, 3.5, 7.0, 10.5]; FY = -2.0
hero = person('hero', (206, 76, 48), (52, 58, 82), (238, 196, 156), 'face_bright', 'hero_crop', loc=(FX[3], FY, 0), s=0.8, rot=10, out=(6, 4))
box('hbelt', (2.06, 1.06, 0.25), (0, 0, 2.15), leather, parent=hero['root'], bevel=0.03)
box('hstrap', (0.28, 1.08, 2.6), (0, 0, 3.0), leather, rot=(0, math.radians(40), 0), parent=hero['root'])
noob = person('noob', (13, 105, 172), (75, 151, 75), (245, 205, 48), 'face_classic_smile', head='classic', loc=(FX[1], FY, 0), s=0.85, arms=(-14, 0), out=(0, 8))
big = person('big', (178, 44, 40), (70, 52, 40), (120, 84, 60), 'face_rowan_curious', 'hero_medium_tousle', loc=(FX[4], FY, 0), s=0.95,
             tw=2.6, td=1.5, th=2.3, lh=1.8, lw=1.25, aw=1.05, al=2.1, hs=1.08, rot=-6, out=(8, 8))
for sg in (-1, 1): box('bstrap%d' % sg, (0.3, 1.56, 2.3), (sg * 0.7, 0, 1.8 + 1.15), mat('denim', srgb(40, 70, 130), 0.8), parent=big['root'])
rich = person('rich', (104, 46, 150), (40, 34, 60), (240, 204, 178), 'face_finn_determined', 'hero_swept_undercut', loc=(FX[6], FY, 0), s=1.0,
              tw=1.6, td=0.9, th=2.4, lh=2.7, lw=0.8, aw=0.75, al=2.5, hs=0.92, rot=-12, out=(4, 4))
box('rbelt', (1.65, 0.95, 0.22), (0, 0, 2.95), gold, parent=rich['root'], bevel=0.03)
box('rcollar', (1.0, 0.95, 0.18), (0, 0, 5.0), gold, parent=rich['root'], bevel=0.03)
box('rcape', (1.7, 0.12, 4.6), (0, 0.55, 2.85), fabric('rcapem', (70, 24, 90)), parent=rich['root'], bevel=0.04)
sis = person('sis', (232, 112, 170), (232, 112, 170), (150, 104, 74), 'face_bluebell_friendly', 'hero_twin_tails', loc=(FX[2], FY, 0), s=0.62, rot=6, arms=(-20, 0), fs=0.82)
cone('skirt', 1.55, 1.05, 1.3, (0, 0, 1.55), fabric('skirtm', (220, 96, 156)), sis['root'])
ball('flower', 0.28, (0.55, -0.3, sis['hz'] + 0.55), mat('flw', srgb(255, 230, 90), 0.5), sis['root'])
bacon = person('bacon', (60, 150, 80), (60, 70, 110), (214, 160, 122), 'face_classic_smirk', 'hero_side_wave', head='classic', loc=(FX[5], FY, 0), s=0.85, rot=-4, arms=(0, -10))
box('bpack', (1.6, 0.8, 1.8), (0, 0.85, 3.0), leather, parent=bacon['root'], bevel=0.15)
girl = person('girl', (150, 40, 40), (70, 50, 40), (246, 214, 190), 'face_clover_friendly', 'hero_long_tie', loc=(FX[0], FY, 0), s=0.85, rot=-10, out=(0, 10))
box('gvest', (2.1, 1.1, 1.7), (0, 0, 3.05), leather, parent=girl['root'], bevel=0.12)
box('gsword', (0.25, 0.15, 3.6), (0.4, 0.7, 3.4), steel, rot=(0, math.radians(-30), 0), parent=girl['root'], bevel=0.03)

# ---------------- BACK ROW: adults ----------------
BX = [-8.75, -5.25, -1.75, 1.75, 5.25, 8.75]; BY = 4.2; BZ = 1.3
kn = person('knight', (90, 100, 120), (50, 54, 66), (92, 62, 44), 'face_fierce', 'hero_slick_back', 'face_braided_beard', loc=(BX[0], BY, BZ), s=1.05,
            tw=2.5, td=1.25, th=2.2, lh=2.0, lw=1.1, aw=1.15, al=2.1, rot=8)
box('kplate', (2.62, 1.38, 1.6), (0, 0, 3.35), steel, parent=kn['root'], bevel=0.14)
for sg in (-1, 1): box('kpad%d' % sg, (1.3, 1.45, 0.5), (sg * 1.75, 0, 4.15), steel, parent=kn['root'], bevel=0.18)
queen = person('queen', (40, 120, 80), (40, 120, 80), (120, 80, 56), 'face_sweet', 'hero_low_bun', loc=(BX[1], BY, BZ), s=1.0, tw=1.8, td=0.95, th=2.2, lh=2.2, aw=0.85, rot=4)
cone('gown', 1.9, 1.0, 2.4, (0, 0, 1.25), fabric('gownm', (30, 100, 66)), queen['root'])
torus('circlet', 0.62, 0.08, (0, 0, queen['hz'] + 0.5), gold, queen['root'])
wiz = person('wizard', (50, 70, 160), (50, 70, 160), (232, 196, 170), 'face_calm', 'hero_long_straight', 'face_full_beard', loc=(BX[2], BY, BZ), s=1.0, tw=1.9, rot=-4, arms=(-25, 0))
cone('robe', 1.7, 1.05, 2.2, (0, 0, 1.15), fabric('robem', (40, 58, 140)), wiz['root'])
cone('hat', 0.9, 0.05, 2.0, (0, 0, wiz['hz'] + 1.75), fabric('hatm', (40, 58, 140)), wiz['root'])
torus('brim', 0.95, 0.12, (0, 0, wiz['hz'] + 0.8), fabric('brimm', (40, 58, 140)), wiz['root'])
box('staff', (0.2, 0.2, 7.0), (0, -0.4, -0.8), wood, parent=wiz['armL'])
ball('orb', 0.35, (0, -0.4, 2.8), mat('orbm', srgb(120, 200, 255), 0.1, emit=(0.4, 0.8, 1.0), estr=5), wiz['armL'])
vil = person('villain', (40, 26, 50), (30, 20, 36), (226, 214, 206), 'face_nico_angry', 'hero_half_knot', loc=(BX[3], BY, BZ), s=1.05,
             tw=1.7, td=0.9, th=2.6, lh=2.6, lw=0.85, aw=0.8, al=2.6, hs=0.95, rot=-8)
cone('vrobe', 1.6, 0.95, 2.6, (0, 0, 1.3), fabric('vrobem', (36, 22, 46)), vil['root'])
box('vcollar', (1.9, 0.2, 1.3), (0, 0.55, vil['top'] + 0.5), fabric('vcolm', (90, 20, 40)), parent=vil['root'], bevel=0.05)
box('vstaff', (0.18, 0.18, 7.4), (0, -0.4, -0.8), black, parent=vil['armR'])
ball('vorb', 0.38, (0, -0.4, 3.0), glowp, vil['armR'])
guard = person('guard', (140, 150, 160), (60, 60, 70), (245, 205, 48), 'face_classic_grin', head='classic', loc=(BX[4], BY, BZ), s=1.0, arms=(0, -30))
cone('pot', 0.74, 0.66, 0.5, (0, 0, guard['hz'] + 0.72), iron, guard['root'])
torus('potrim', 0.8, 0.06, (0, 0, guard['hz'] + 0.5), iron, guard['root'])
box('spear', (0.16, 0.16, 7.5), (0, -0.35, -0.5), wood, parent=guard['armR'])
cone('tip', 0.35, 0.0, 0.9, (0, -0.35, 3.7), steel, guard['armR'], verts=4)
slim = person('slender', (24, 24, 30), (236, 236, 240), (196, 140, 104), 'face_town_curious', 'hero_pixie', loc=(BX[5], BY, BZ), s=1.0,
              tw=1.45, td=0.8, th=2.5, lh=3.1, lw=0.7, aw=0.62, al=2.7, hs=0.78, rot=-14, out=(6, 0), fs=0.8)
box('shades', (0.95, 0.12, 0.2), (0, -0.52, slim['hz'] + 0.12), black, parent=slim['root'], bevel=0.04)
box('hood', (1.2, 0.5, 0.9), (0, 0.55, slim['top'] + 0.1), fabric('hoodm', (24, 24, 30)), parent=slim['root'], bevel=0.15)

# ---------------- set ----------------
step = box('step', (26, 4.4, BZ), (0, BY, BZ / 2), noise_mat('stepm', srgb(170, 160, 146), srgb(140, 130, 118), scale=1.2, rough=0.9, bump=0.2, voronoi=True), bevel=0.1)
ground(200, noise_mat('cobble', srgb(186, 170, 150), srgb(150, 136, 120), scale=1.6, rough=0.85, bump=0.25, voronoi=True))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 16, 9)); wall = bpy.context.active_object
wall.scale = (70, 18, 1); wall.rotation_euler = (math.radians(90), 0, 0)
wall.data.materials.append(noise_mat('wall', srgb(222, 200, 168), srgb(196, 170, 136), scale=0.6, rough=0.9, bump=0.15))
for x in range(-28, 29, 7):
    box('ban%d' % x, (2.2, 0.1, 5.0), (x, 15.8, 11.5), mat('ban%d' % x, srgb(*((176, 40, 46) if (x // 7) % 2 else (40, 70, 150))), 0.8))
sky(sun_el=34, sun_rot=150, strength=0.35)
sun(el=34, rot=150, energy=4.5)
cam = camera(lens=50); cam.location = (0, -40, 11.0); look(cam, (0, 1.5, 4.6))
setup_render(RES[0], RES[1], SAMP)
vs_ = bpy.context.scene.view_settings; vs_.view_transform = 'Standard'
try: vs_.look = 'Medium High Contrast'
except Exception: pass
vs_.exposure = float(os.environ.get('EXP', '-2.7'))
if os.environ.get('SAVE'):
    # one collection per character (root + all descendants) so builders can Append > Collection
    names = ['girl','noob','sis','hero','big','bacon','rich','knight','queen','wizard','villain','guard','slender']
    nice = {'girl':'Girl hero','noob':'Newbie','sis':'Little sister','hero':'Hero kid','big':'Big kid','bacon':'Bacon kid','rich':'Rich kid',
            'knight':'Knight','queen':'Queen','wizard':'Wizard','villain':'Villain','guard':'Goofy guard','slender':'Slender teen'}
    for n in names:
        root = bpy.data.objects[n]
        col = bpy.data.collections.new('Cast v2 | ' + nice[n]); bpy.context.scene.collection.children.link(col)
        for o in [root] + list(root.children_recursive):
            for c in list(o.users_collection): c.objects.unlink(o)
            col.objects.link(o)
        root.location = (root.location.x, root.location.y, 0)  # stand on the ground when appended
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVE'], compress=True)
    print('saved', os.environ['SAVE'])
else:
    bpy.context.scene.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
    print('wrote', OUT)
