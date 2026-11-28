# Cast v3 (Claude, 11-27): new characters for "In this town" on a data-driven R15-style kit (v3kit.py).
# Phase 1 = report rows 1-8: The Oathbound, The Crowd Six, First Rank, True-Form Lead, The Rigger, Ember (2 stages), The Jailer, The Squire.
# Usage:  SAVE=/tmp/claude-0/cast3/cast-v3.blend python3 -I cast_v3.py      (ONLY=key,key to build a subset)
# Every character is one collection "Cast v3 | <Name>": a rig "<Name> | rig" (R15 bone names, rigid bone-parented parts),
# 15 *_Geo body parts + clothing / armour / props, Roblox-style *_Att sockets, named poses, and a decal-face head driven by
# the rig's integer properties face / mouth / blink and float glow.
import sys, os, math, random, json
sys.path.insert(0, '/tmp/claude-0/cast3')
import bpy, bmesh
from mathutils import Vector, Matrix, Quaternion
import v3kit as K
from v3kit import (loft, lathe, ellipsoid, cube_bm, torus_bm, tube_bm, xform, text_bm, grid_sheet, cloth, leather, metal, plain, glow,
                   skin_mat, hair_mat, body_params, build_body, make_head, add_hair, base_pose_dirs, store_poses, Char, rgba, srgb, _m, _attr, _mixc, drive)

ONLY = [x for x in os.environ.get('ONLY', '').split(',') if x]
random.seed(7)
# Phase 2: BASE=/tmp/claude-0/cast3/cast-v3.blend ONLY=herald  -> opens the existing library, removes any old copy of the
# characters in ONLY, builds them, and places them after the others (phase 1 characters are left untouched).
BASE = os.environ.get('BASE')
if BASE:
    bpy.ops.wm.open_mainfile(filepath=BASE)
    bpy.context.preferences.filepaths.save_version = 0
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.engine = 'CYCLES'

def R(deg): return math.radians(deg)
def rotz(a): return Matrix.Rotation(R(a), 4, 'Z')
def rotx(a): return Matrix.Rotation(R(a), 4, 'X')
def roty(a): return Matrix.Rotation(R(a), 4, 'Y')
def T(x, y, z): return Matrix.Translation((x, y, z))

def wood(name, rgb):
    if 'CV3 ' + name in K._MATS: return K._MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, 0.12)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'RINGS'; wv.inputs['Scale'].default_value = 7; wv.inputs['Distortion'].default_value = 7; wv.inputs['Detail'].default_value = 3
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = rgba(tuple(int(c * 0.7) for c in rgb)); cr.color_ramp.elements[1].color = rgba(rgb)
    nt.links.new(wv.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.7
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.2; nt.links.new(wv.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    K._MATS['CV3 ' + name] = m; return m

def soft_glow(name, rgb, strength=6.0, edge=0.6):
    """emissive with soft transparent edges (flames, aura)"""
    if 'CV3 ' + name in K._MATS: return K._MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = rgba(rgb); e.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = edge
    mx = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(lw.outputs['Facing'], mx.inputs[0]); nt.links.new(e.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface']); K._MATS['CV3 ' + name] = m; return m

# ----------------------------------------------------------------------------- shared accessory builders
def dome(r, h, n=36, open_bottom=True):
    prof = [(0, h)] + [(r * math.sin(R(a)), h * math.cos(R(a))) for a in range(15, 91, 15)]
    if not open_bottom: prof.append((0, 0))
    return lathe(prof, n)

def pauldron(C, side, s, x, z, r, layers=3, mat=None, rim=None, bone=None, tilt=18, flare=1.0, lift=0.0):
    """stacked shoulder plates (dome + lames), tilted outward"""
    obs = []
    for i in range(layers):
        rr = r * (1.0 + 0.12 * i) * (flare if i else 1.0); hh = r * (0.62 - 0.12 * i)
        bm = dome(rr, hh); xform(bm, Matrix.Scale(1.0, 4))
        bmesh.ops.scale(bm, vec=(1.0, 0.9, 1.0), verts=bm.verts)
        xform(bm, T(x + s * r * 0.18 * i, 0, z - r * 0.32 * i + lift) @ Matrix.Rotation(R(-s * (tilt + 8 * i)), 4, 'Y'))
        o = C.obj('%sPauldron_%d' % (side, i), bm, mat, bone or side + 'UpperArm', origin=(x, 0, z), solid=0.05)
        obs.append(o)
    if rim:
        bm = torus_bm(r * 1.0, 0.035, 32, 8); bmesh.ops.scale(bm, vec=(1, 0.9, 1), verts=bm.verts)
        xform(bm, T(x, 0, z + lift) @ Matrix.Rotation(R(-s * tilt), 4, 'Y'))
        obs.append(C.obj('%sPauldron_rim' % side, bm, rim, bone or side + 'UpperArm', origin=(x, 0, z)))
    return obs

def cape(C, label, x_half_top, x_half_bot, z_top, z_bot, y0, mat, torn=0.0, flare_back=0.4, cols=14, rows=12, bone='UpperTorso', curve=0.35, solid=0.04, sway=0.0):
    rows_pts = []
    for r in range(rows + 1):
        t = r / rows; z = z_top + (z_bot - z_top) * t
        hw = x_half_top + (x_half_bot - x_half_top) * t
        row = []
        for c in range(cols + 1):
            u = c / cols * 2 - 1
            x = u * hw + sway * t * t
            y = y0 + curve * (1 - u * u) * (0.6 + 0.6 * t) + flare_back * t * t
            zz = z
            if r == rows and torn > 0:
                zz = z + torn * (0.25 + 0.75 * random.random()) * (1 if c % 2 else 0.25)
            row.append((x, y, zz))
        rows_pts.append(row)
    bm = grid_sheet(rows_pts)
    return C.obj(label, bm, mat, bone, origin=(0, y0, z_top), solid=solid)

def sword(C, label, length, width, guard, grip, blade_mat, guard_mat, grip_mat, M, bone, origin, rune=None, pommel_mat=None):
    """sword built along +Z (tip up at +length) then placed by matrix M"""
    parts = []
    bm = loft([(0, width, width * 0.16, 6), (length * 0.82, width * 0.92, width * 0.15, 6), (length, 0.02, 0.02, 2)], round_ends=0.0)
    parts.append((bm, blade_mat, 'blade'))
    if rune:
        bm = loft([(length * 0.06, width * 0.16, width * 0.2, 4), (length * 0.72, width * 0.12, width * 0.2, 4)]); parts.append((bm, rune, 'fuller'))
    bm = loft([(-0.06, guard, width * 0.34, 6), (0.06, guard, width * 0.34, 6)], round_ends=0.03); parts.append((bm, guard_mat, 'guard'))
    bm = loft([(-grip, width * 0.32, width * 0.32, 4), (-0.05, width * 0.3, width * 0.3, 4)]); parts.append((bm, grip_mat, 'grip'))
    bm = ellipsoid(width * 0.34, width * 0.34, width * 0.34, 16, 8); xform(bm, T(0, 0, -grip - width * 0.18)); parts.append((bm, pommel_mat or guard_mat, 'pommel'))
    obs = []
    for bm, m, lab in parts:
        xform(bm, M); obs.append(C.obj(label + '_' + lab, bm, m, bone, origin=origin))
    return obs

def chain_path(C, label, pts, mat, bone, origin, R_=0.11, r_=0.034, step=0.16):
    """iron chain: alternating torus links along a polyline"""
    P = [Vector(p) for p in pts]; L = sum((b - a).length for a, b in zip(P[:-1], P[1:]))
    n = int(L / step); bm_all = bmesh.new(); me_tmp = bpy.data.meshes.new('tmp')
    for i in range(n):
        d = i * step; acc = 0
        for a, b in zip(P[:-1], P[1:]):
            seg = (b - a).length
            if acc + seg >= d:
                t = (d - acc) / seg; p = a + (b - a) * t; dirv = (b - a).normalized(); break
            acc += seg
        bm = torus_bm(R_, r_, 14, 6); bmesh.ops.scale(bm, vec=(1.0, 1.5, 1.0), verts=bm.verts)   # oval link, long axis = local Y
        q = Vector((0, 1, 0)).rotation_difference(dirv)
        rot = q.to_matrix().to_4x4() @ Matrix.Rotation(R(90 * (i % 2)), 4, 'Y')
        xform(bm, Matrix.Translation(p) @ rot)
        bm.to_mesh(me_tmp); bm_all.from_mesh(me_tmp); bm.free()
    bpy.data.meshes.remove(me_tmp)
    return C.obj(label, bm_all, mat, bone, origin=origin)

def belt(C, P, z, mat, buckle=None, h=0.2, extra=0.06, bone='LowerTorso', label='Belt'):
    w = P['hw'] + extra * 2; d = P['td'] * 0.96 + extra * 2
    bm = loft([(z - h / 2, w, d, P['p']), (z + h / 2, w, d, P['p'])], round_ends=0.02)
    o = C.obj(label, bm, mat, bone, origin=(0, 0, z))
    if buckle:
        bm = loft([(z - h * 0.7, h * 1.5, 0.06, 8, 0, -d / 2 - 0.02), (z + h * 0.7, h * 1.5, 0.06, 8, 0, -d / 2 - 0.02)], round_ends=0.02)
        C.obj(label + '_buckle', bm, buckle, bone, origin=(0, 0, z))
    return o

def shell(C, label, part_secs, mat, bone, origin, round_ends=0.05, n=32, cap=(True, True)):
    return C.obj(label, loft(part_secs, n=n, cap=cap, round_ends=round_ends), mat, bone, origin=origin)

def finish(C, default_pose, extra_poses=None, overrides=None, record=None):
    names = ['idle', 'point', 'laugh', 'shocked', 'fists_up', 'arms_crossed']
    poses = {}
    for n in names:
        D = base_pose_dirs(C, n)
        if overrides and n in overrides: D.update(overrides[n])
        poses[n] = D
    for n, D in (extra_poses or {}).items():
        base = base_pose_dirs(C, 'idle'); base.update(D); poses[n] = base
    store_poses(C, poses, default_pose)
    rig = C.rig
    if record:
        for k, v in record.items(): rig[k] = v if not isinstance(v, (list, dict)) else json.dumps(v)
    rig['height_BU'] = round(C.height, 3); rig['height_x_hero'] = round(C.height / K.HERO_H, 2); rig['height_HH'] = round(C.height / K.HH, 2)
    rig['key'] = C.key
    # all objects get the cast tag; the rig is the collection's "owner"
    for o in C.col.objects: o['cast_v3'] = C.name
    print('built', C.name, 'H=%.2f BU' % C.height, 'objects', len(C.col.objects))
    REG.append(C)

REG = []
def want(key): return not ONLY or key in ONLY

# =============================================================================  1. THE OATHBOUND
def build_oathbound():
    C = Char('The Oathbound', 'oathbound')
    P = body_params('heroic_adult', sw=1.95, ww=1.3, hw=1.4, at=0.62, ad=0.66, td=1.1, lgw=0.68, lgd=0.7, idle_out=11)
    steel = metal('obsidian steel', (40, 44, 56), rough=0.28, scratch=0.6)
    trim = metal('gunmetal trim', (92, 100, 118), rough=0.3, scratch=0.4)
    gamb = cloth('oath gambeson', (38, 38, 46), weave=52, hem_dark=0.7, thread=(70, 80, 100))
    capem = cloth('oath cape', (26, 26, 34), weave=30, hem_dark=0.55, thread=(60, 70, 90), sheen=0.6)
    belt_l = leather('oath belt', (40, 30, 26), wear=0.4)
    ice = glow('ice glow', (140, 220, 255), 9.0)
    M = dict(UpperTorso=gamb, LowerTorso=gamb, UpperArm=gamb, LowerArm=steel, Hand=steel, UpperLeg=gamb, LowerLeg=steel, Foot=steel)
    build_body(C, P, M)
    # helmet head: rounded great-helm with the visor-slit decal (no face ever shown)
    face = dict(set='oathbound', exprs=['bright', 'dim', 'narrowed', 'flicker'], fs=0.92, voff=0.02, cut=0.99, emissive=10.0, metallic=0.9, rough=0.28, glow=1.0)
    make_head(C, P, (40, 44, 56), face)
    hz, hh = P['head_c'], P['head']
    # crest: a blade-like fin over the helmet, front to back
    prof = [(-0.5, -0.3), (-0.42, 0.12), (-0.1, 0.42), (0.35, 0.5), (0.7, 0.3), (0.62, -0.1), (0.45, -0.32)]
    bm = bmesh.new(); vs = [bm.verts.new((-0.06, y * hh, P['top'] - 0.08 + z * hh)) for y, z in prof]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0.12, 0, 0), verts=[e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    C.obj('Helmet_crest', bm, trim, 'Head', origin=(0, 0, hz), smooth=False, bevel=0.02)
    # swept side wings (knightly, not horns)
    for sg in (-1, 1):
        wp = [(0.0, 0.0), (0.38, -0.06), (0.8, 0.3), (1.02, 0.98), (0.62, 0.56), (0.26, 0.42)]
        bm = bmesh.new(); vs = [bm.verts.new((0, y * hh, z * hh)) for y, z in wp]; f = bm.faces.new(vs)
        ext = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0.08, 0, 0), verts=[e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        xform(bm, T(sg * 0.46 * hh, -0.08 * hh, hz + 0.02 * hh) @ Matrix.Rotation(R(sg * -38), 4, 'Z') @ Matrix.Rotation(R(sg * 12), 4, 'Y'))
        C.obj('Helmet_wing_%s' % ('L' if sg > 0 else 'R'), bm, trim, 'Head', origin=(0, 0, hz), smooth=False, bevel=0.015)
    # helmet brow ridge (adds an angular outline above the visor)
    bm = loft([(hz + hh * 0.08, hh * 1.08, hh * 1.06, 2.4, 0, -0.02), (hz + hh * 0.2, hh * 1.04, hh * 1.02, 2.4, 0, -0.02)], round_ends=0.02)
    C.obj('Helmet_brow', bm, trim, 'Head', origin=(0, 0, hz))
    # gorget (flared collar)
    bm = lathe([(P['sw'] * 0.42, P['sh_z'] - 0.12), (P['sw'] * 0.38, P['sh_z'] + 0.05), (hh * 0.5, P['neck_z'] + 0.12), (hh * 0.47, P['neck_z'] + 0.22)], 40)
    bmesh.ops.scale(bm, vec=(1, 0.85, 1), verts=bm.verts)
    C.obj('Gorget', bm, steel, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.05)
    # breastplate + glowing oath chevron
    w0, w1, td = P['ww'] + 0.12, P['sw'] + 0.1, P['td'] + 0.14
    shell(C, 'Breastplate', [(P['waist_z'] - 0.05, w0, td * 0.95, 4), (P['waist_z'] + P['ut'] * 0.55, w1 * 0.98, td, 4), (P['sh_z'] - 0.02, w1, td * 0.9, 5)], steel, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.1)
    zc = P['waist_z'] + P['ut'] * 0.58; yf = -td / 2 - 0.02
    for s in (-1, 1):
        bm = cube_bm(0.6, 0.04, 0.07); xform(bm, T(s * 0.24, yf, zc) @ Matrix.Rotation(R(s * 33), 4, 'Y'))
        C.obj('Oath_chevron_%d' % (s > 0), bm, ice, 'UpperTorso', origin=(0, 0, zc))
        bm = cube_bm(0.42, 0.045, 0.1); xform(bm, T(s * 0.2, yf - 0.005, zc + 0.22) @ Matrix.Rotation(R(s * 33), 4, 'Y'))
        C.obj('Oath_chevron_trim_%d' % (s > 0), bm, trim, 'UpperTorso', origin=(0, 0, zc))
    # belt + tassets (front plates ride the thighs)
    belt(C, P, P['waist_z'] - 0.05, belt_l, trim, h=0.24, extra=0.1)
    for side, s in (('Left', 1), ('Right', -1)):
        x = s * P['lx']
        for i in range(3):
            z = P['hip_z'] + 0.05 - i * 0.32
            bm = loft([(z - 0.36, P['lgw'] * 1.25 + 0.06 * i, 0.08, 6, x + s * 0.06 * i, -P['lgd'] / 2 - 0.08 - 0.02 * i), (z, P['lgw'] * 1.2 + 0.06 * i, 0.08, 6, x + s * 0.06 * i, -P['lgd'] / 2 - 0.06 - 0.02 * i)], round_ends=0.03)
            C.obj('%sTasset_%d' % (side, i), bm, steel if i % 2 == 0 else trim, side + 'UpperLeg', origin=(x, 0, P['hip_z']))
        bm = loft([(P['hip_z'] - 0.9, P['lgw'] * 1.3, P['lgd'] * 0.9, 6, x, 0.15), (P['hip_z'] + 0.05, P['lgw'] * 1.25, P['lgd'] * 0.9, 6, x, 0.15)], round_ends=0.04)
        C.obj('%sCuisse' % side, bm, steel, side + 'UpperLeg', origin=(x, 0, P['hip_z']))
        # knee cops + greave flare
        bm = ellipsoid(P['lgw'] * 0.62, P['lgd'] * 0.62, 0.26, 20, 10); xform(bm, T(x, -0.06, P['knee_z']))
        C.obj('%sKnee' % side, bm, trim, side + 'LowerLeg', origin=(x, 0, P['knee_z']))
        bm = loft([(P['fh'] + 0.05, P['lgw'] * 1.12, P['lgd'] * 1.12, 5, x, 0), (P['knee_z'] - 0.1, P['lgw'] * 1.08, P['lgd'] * 1.08, 5, x, 0)], round_ends=0.05)
        C.obj('%sGreave' % side, bm, steel, side + 'LowerLeg', origin=(x, 0, P['knee_z']))
        # vambrace flare + gauntlet cuff
        (l0, l1, _) = C.J[side + 'LowerArm']
        bm = loft([(l1[2] + 0.05, P['at'] * 1.12, P['ad'] * 1.12, 5, l0[0], 0), (l1[2] + 0.28, P['at'] * 1.25, P['ad'] * 1.25, 5, l0[0], 0)], round_ends=0.04)
        C.obj('%sGauntlet_cuff' % side, bm, trim, side + 'LowerArm', origin=l0)
        # pauldrons: 3 lames, out to ~3 W
        pauldron(C, side, s, s * P['sx'], P['sh_z'] + 0.02, 0.62, layers=3, mat=steel, rim=trim, tilt=16, flare=1.06)
    # torn cape from behind the pauldrons to mid-calf
    cp = cape(C, 'Cape', 1.05, 1.55, P['sh_z'] - 0.05, 1.05, P['td'] / 2 + 0.1, capem, torn=0.55, flare_back=0.55, curve=0.32, cols=16, rows=14)
    C.hem(cp, 1.05, 0.0)
    # greatsword on the back, hilt over the right shoulder (character's right = -X)
    Mx = T(-0.35, P['td'] / 2 + 0.42, P['sh_z'] - 0.1) @ Matrix.Rotation(R(-24), 4, 'Y') @ rotx(180)
    sword(C, 'Greatsword', 4.3, 0.42, 1.25, 0.95, metal('oath blade', (70, 76, 92), rough=0.22, scratch=0.7), trim, belt_l, Mx, 'UpperTorso', (0, 0, P['waist_z']), rune=ice)
    C.height = P['top']
    over = {'idle': {'LeftUpperLeg': (0.09, 0, -1), 'LeftLowerLeg': (0.09, 0, -1), 'RightUpperLeg': (-0.09, 0, -1), 'RightLowerLeg': (-0.09, 0, -1)}}
    finish(C, 'idle', overrides=over, record=dict(role='Bonded guardian: oath-bound dark knight, serves only the hero', body='heroic_adult (armoured)',
           signature='obsidian black steel + ice-blue glow', face_style='no face: visor slit (bright, dim, narrowed, flicker)', silhouette='crested helm, 3-lame pauldrons, torn cape, greatsword hilt over right shoulder'))
    return C

# =============================================================================  3. FIRST RANK
def spiky_hair(C, P, rgb, label='Hair'):
    """anime rival spikes: a rounded cap + tapered blob spikes sweeping up and back (no hair cards)"""
    hz, h = P['head_c'], P['head']; bm_all = bmesh.new(); me = bpy.data.meshes.new('tmp')
    cap = ellipsoid(0.54 * h, 0.56 * h, 0.27 * h, 32, 16); xform(cap, T(0, 0.11 * h, hz + 0.33 * h)); cap.to_mesh(me); bm_all.from_mesh(me); cap.free()
    spikes = [  # base (x,y,z) in h, direction, length h, radius h
        ((0.0, -0.22, 0.42), (0, 0.25, 1), 0.62, 0.17), ((-0.24, -0.18, 0.4), (-0.35, 0.3, 1), 0.52, 0.15), ((0.24, -0.18, 0.4), (0.35, 0.3, 1), 0.52, 0.15),
        ((0.0, 0.08, 0.5), (0, 0.75, 0.85), 0.66, 0.18), ((-0.3, 0.06, 0.42), (-0.7, 0.6, 0.6), 0.55, 0.15), ((0.3, 0.06, 0.42), (0.7, 0.6, 0.6), 0.55, 0.15),
        ((0.0, 0.36, 0.32), (0, 1, 0.3), 0.55, 0.18), ((-0.3, 0.3, 0.25), (-0.5, 1, 0.05), 0.48, 0.15), ((0.3, 0.3, 0.25), (0.5, 1, 0.05), 0.48, 0.15),
        ((-0.46, -0.04, 0.12), (-0.25, 0.05, -1), 0.3, 0.1), ((0.46, -0.04, 0.12), (0.25, 0.05, -1), 0.3, 0.1)]
    for (bx, by, bz), d, L, r in spikes:
        bm = lathe([(0, -0.05 * h), (r * h, 0.0), (r * h * 0.82, L * h * 0.38), (r * h * 0.42, L * h * 0.74), (0, L * h)], 14)
        q = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
        xform(bm, T(bx * h, by * h, hz + bz * h) @ q.to_matrix().to_4x4())
        bm.to_mesh(me); bm_all.from_mesh(me); bm.free()
    bpy.data.meshes.remove(me)
    return C.obj(label, bm_all, hair_mat(C.name + ' hair', rgb), 'Head', origin=(0, 0, hz))

def build_first_rank():
    C = Char('First Rank', 'first_rank')
    P = body_params('heroic_teen', sw=1.7, ww=1.1, hw=1.15, td=0.78, at=0.48, ad=0.5, idle_out=8)
    skin = (232, 190, 160)
    gold = metal('rank gold', (255, 192, 70), rough=0.2, scratch=0.25)
    white = cloth('rank white', (232, 228, 218), weave=40, hem_dark=0.86, thread=(230, 190, 90), sheen=0.5)
    trous = cloth('rank trousers', (52, 50, 60), weave=44, hem_dark=0.7)
    boot = leather('rank boots', (112, 66, 36), wear=0.5)
    navy = plain('rank enamel', (28, 40, 96), rough=0.25, coat=0.6)
    M = dict(UpperTorso=white, LowerTorso=white, UpperArm=white, LowerArm=white, Hand=skin_mat('first rank skin', skin), UpperLeg=trous, LowerLeg=boot, Foot=boot)
    build_body(C, P, M)
    face = dict(set='first_rank', exprs=['smug', 'sneer', 'shocked', 'furious', 'humiliated', 'respect', 'neutral'], fs=1.12, voff=0.02, cut=0.575,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    spiky_hair(C, P, (34, 36, 54))
    # gold breastplate, high collar, pauldrons, vambraces, greave caps
    td = P['td'] + 0.12
    shell(C, 'Breastplate', [(P['waist_z'] - 0.04, P['ww'] + 0.1, td * 0.95, 4), (P['waist_z'] + P['ut'] * 0.6, P['sw'] * 0.98 + 0.08, td, 4), (P['sh_z'] - 0.02, P['sw'] + 0.06, td * 0.92, 5)], gold, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.08)
    bm = lathe([(P['head'] * 0.5, P['sh_z'] - 0.06), (P['head'] * 0.46, P['sh_z'] + 0.14), (P['head'] * 0.5, P['neck_z'] + 0.1)], 40); bmesh.ops.scale(bm, vec=(1.1, 0.95, 1), verts=bm.verts)
    C.obj('Collar', bm, gold, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.05)
    for side, s in (('Left', 1), ('Right', -1)):
        pauldron(C, side, s, s * P['sx'], P['sh_z'] + 0.02, 0.44, layers=2, mat=gold, rim=None, tilt=14)
        (l0, l1, _) = C.J[side + 'LowerArm']
        shell(C, side + 'Vambrace', [(l1[2] + 0.02, P['at'] * 1.12, P['ad'] * 1.12, 5, l0[0], 0), (l0[2] - 0.05, P['at'] * 1.08, P['ad'] * 1.08, 5, l0[0], 0)], gold, side + 'LowerArm', l0, round_ends=0.04)
        x = s * P['lx']
        bm = ellipsoid(P['lgw'] * 0.6, P['lgd'] * 0.6, 0.2, 18, 9); xform(bm, T(x, -0.05, P['knee_z']))
        C.obj(side + 'Knee', bm, gold, side + 'LowerLeg', origin=(x, 0, P['knee_z']))
        bm = loft([(0.0, P['lgw'] * 1.06, 0.3, 5, x, -P['fl'] * 0.42), (P['fh'] + 0.06, P['lgw'] * 1.06, 0.3, 5, x, -P['fl'] * 0.42)], round_ends=0.04)
        C.obj(side + 'Toecap', bm, gold, side + 'Foot', origin=C.J[side + 'Foot'][0])
    # "1" rank medallion: gold rim, navy enamel, raised gold numeral
    zc = P['waist_z'] + P['ut'] * 0.55; yf = -td / 2 - 0.03
    bm = lathe([(0, -0.05), (0.42, -0.05), (0.42, 0.03), (0.36, 0.06), (0, 0.06)], 48); xform(bm, T(0, yf, zc) @ rotx(90))
    C.obj('Medallion', bm, gold, 'UpperTorso', origin=(0, 0, zc))
    bm = lathe([(0, 0.0), (0.34, 0.0), (0.34, 0.075), (0, 0.075)], 48); xform(bm, T(0, yf, zc) @ rotx(90))
    C.obj('Medallion_enamel', bm, navy, 'UpperTorso', origin=(0, 0, zc))
    bm = text_bm('1', 0.5, 0.06); xform(bm, T(0.0, yf - 0.1, zc) @ rotx(90))
    C.obj('Medallion_1', bm, gold, 'UpperTorso', origin=(0, 0, zc), smooth=False)
    # white tabard skirt with gold hem trim
    z0 = P['hip_z'] - 0.95
    sk = shell(C, 'Tabard_skirt', [(z0, P['hw'] + 0.36, P['td'] + 0.3, 4), (P['waist_z'] - 0.02, P['hw'] + 0.1, P['td'] + 0.1, 4)], white, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
    C.hem(sk, z0, 0.12)
    bm = loft([(z0 - 0.01, P['hw'] + 0.4, P['td'] + 0.34, 4), (z0 + 0.07, P['hw'] + 0.39, P['td'] + 0.33, 4)], cap=(False, False)); C.obj('Tabard_trim', bm, gold, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.03)
    belt(C, P, P['waist_z'] - 0.02, leather('rank belt', (120, 74, 40)), gold, h=0.18, extra=0.12)
    # white cape with gold clasps
    cp = cape(C, 'Cape', 0.82, 1.25, P['sh_z'] - 0.02, 0.85, P['td'] / 2 + 0.1, white, torn=0.0, flare_back=0.45, curve=0.3)
    C.hem(cp, 0.85, 0.14)
    for s in (-1, 1):
        bm = ellipsoid(0.13, 0.08, 0.13, 16, 8); xform(bm, T(s * 0.7, -td / 2 + 0.06, P['sh_z'] - 0.12)); C.obj('Clasp_%d' % (s > 0), bm, gold, 'UpperTorso', origin=(0, 0, P['sh_z']))
    # ceremonial sword at the left hip (scabbard)
    Mx = T(P['hw'] / 2 + 0.22, 0.05, P['waist_z'] - 0.1) @ Matrix.Rotation(R(-12), 4, 'Y') @ rotx(176)
    sword(C, 'Sword', 2.2, 0.24, 0.62, 0.42, cloth('rank scabbard', (240, 236, 228), weave=60), gold, leather('rank grip', (90, 50, 30)), Mx, 'LowerTorso', (0, 0, P['hip_z']))
    C.height = P['top']
    over = {'idle': {'Head': (0, 0.22, 1), 'UpperTorso': (0, 0.06, 1), 'LeftUpperArm': (0.62, 0.2, -0.76), 'LeftLowerArm': (-0.6, -0.05, -0.8), 'LeftHand': (-0.55, 0, -0.85)}}
    finish(C, 'idle', overrides=over, record=dict(role="Officially ranked number-one heir; mocks the hero in public, demoted at the end", body='heroic_teen',
           signature='polished gold + white', face_style='sharp rival set (new): smug, sneer, shocked, furious, humiliated, grudging respect, neutral; blink; talk closed/half/open',
           silhouette="dark anime spikes, gold plate + high collar, white cape, big '1' medallion, sheathed sword"))
    return C

# =============================================================================  5. THE RIGGER
def rune_image():
    from PIL import Image, ImageDraw, ImageFilter
    p = '/tmp/claude-0/cast3/faces/_rune.png'
    if not os.path.exists(p):
        S = 512; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = (170, 255, 60, 255)
        d.ellipse([40, 40, S - 40, S - 40], outline=c, width=26); d.ellipse([120, 120, S - 120, S - 120], outline=c, width=14)
        for a in range(0, 360, 60):
            x, y = S / 2 + 170 * math.cos(math.radians(a)), S / 2 + 170 * math.sin(math.radians(a)); d.line([S / 2, S / 2, x, y], fill=c, width=16)
        d.polygon([(S / 2, 150), (S / 2 + 70, S / 2 + 60), (S / 2 - 70, S / 2 + 60)], outline=c, width=14)
        g = im.filter(ImageFilter.GaussianBlur(14)); g.alpha_composite(im); g.save(p)
    return p

def decal_mat(name, path, strength=8.0):
    m = bpy.data.materials.new('CV3 ' + name); nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.image.name = 'CV3 ' + name; t.extension = 'CLIP'
    tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['UV'], t.inputs[0])
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = strength; nt.links.new(t.outputs['Color'], e.inputs['Color'])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(t.outputs['Alpha'], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
    return m

def quad_decal(C, label, center, size, normal_axis, mat, bone, origin):
    """flat square decal with UVs; normal_axis '-Y' faces the camera"""
    bm = bmesh.new(); h = size / 2
    vs = [bm.verts.new(v) for v in [(-h, 0, -h), (h, 0, -h), (h, 0, h), (-h, 0, h)]]
    f = bm.faces.new(vs); uvl = bm.loops.layers.uv.new('UVMap')
    for l, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]): l[uvl].uv = uv
    rot = {'-Y': Matrix.Identity(4), '+X': rotz(90), '-X': rotz(-90)}[normal_axis]
    xform(bm, Matrix.Translation(center) @ rot)
    return C.obj(label, bm, mat, bone, origin=origin, smooth=False)

def build_rigger():
    C = Char('The Rigger', 'rigger')
    P = body_params('slender_tall', idle_out=6)
    skin = (178, 142, 96)
    char_ = cloth('rigger charcoal', (46, 48, 54), weave=44, hem_dark=0.65, thread=(150, 230, 40))
    dark = cloth('rigger tunic', (32, 34, 38), weave=50, hem_dark=0.6, thread=(150, 230, 40))
    lime = cloth('rigger lime', (150, 232, 40), weave=40, hem_dark=0.75, sheen=0.3)
    boot = leather('rigger boots', (30, 28, 30), wear=0.5)
    M = dict(UpperTorso=dark, LowerTorso=dark, UpperArm=char_, LowerArm=char_, Hand=skin_mat('rigger skin', skin), UpperLeg=dark, LowerLeg=boot, Foot=boot, Neck=skin_mat('rigger skin', skin))
    build_body(C, P, M, hand_taper=0.42)
    face = dict(set='rigger', exprs=['sneer', 'innocence', 'gloat', 'panic', 'caught', 'sulk', 'neutral'], fs=1.12, voff=0.02, cut=0.575,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    # dark fringe peeking out of the hood
    bm = ellipsoid(h * 0.5, h * 0.3, h * 0.16, 20, 10); xform(bm, T(0.06, -h * 0.28, hz + h * 0.42) @ Matrix.Rotation(R(-14), 4, 'Y'))
    C.obj('Fringe', bm, hair_mat('rigger hair', (24, 22, 26)), 'Head', origin=(0, 0, hz))
    # pointed hood (open face) lined in lime
    bm = ellipsoid(h * 0.66, h * 0.66, h * 0.66, 32, 18)
    for v in bm.verts:
        if v.co.z > 0: v.co.y += (v.co.z / (h * 0.66)) ** 2 * h * 0.55; v.co.z *= 1 + 0.5 * (v.co.z / (h * 0.66)) ** 3
    kill = [f for f in bm.faces if f.calc_center_median().y < -h * 0.22 and f.calc_center_median().z > -h * 0.62]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    xform(bm, T(0, 0.04, hz + 0.04))
    hood = C.obj('Hood', bm, char_, 'Head', origin=(0, 0, hz), solid=0.06)
    hood.data.materials.append(lime); hood.modifiers['solidify'].material_offset = 1
    # tiny crooked crown perched on the hood
    prof = []
    bm = bmesh.new(); n = 20; rr = h * 0.27
    ring_b = [bm.verts.new((rr * math.cos(2 * math.pi * i / n), rr * math.sin(2 * math.pi * i / n), 0)) for i in range(n)]
    ring_t = [bm.verts.new((rr * math.cos(2 * math.pi * i / n), rr * math.sin(2 * math.pi * i / n), (0.3 if i % 4 == 0 else 0.12) * h)) for i in range(n)]
    for i in range(n): bm.faces.new((ring_b[i], ring_b[(i + 1) % n], ring_t[(i + 1) % n], ring_t[i]))
    xform(bm, T(-0.1, 0.18, hz + h * 0.74) @ Matrix.Rotation(R(-24), 4, 'Y') @ Matrix.Rotation(R(10), 4, 'X'))
    C.obj('Crooked_crown', bm, metal('tarnished gold', (178, 140, 56), rough=0.4, scratch=0.8), 'Head', origin=(0, 0, hz), solid=0.03)
    bm = ellipsoid(0.06, 0.06, 0.06, 12, 6); xform(bm, T(-0.1 + 0.02, 0.18 - rr - 0.01, hz + h * 0.8)); C.obj('Crown_gem', bm, glow('lime glow', (150, 255, 50), 6.0), 'Head', origin=(0, 0, hz))
    # slim cloak: narrow mantle over the back, open front, lime trim
    cp = cape(C, 'Cloak', 0.62, 0.85, P['sh_z'] + 0.02, 1.0, P['td'] / 2 + 0.04, char_, torn=0.0, flare_back=0.35, curve=0.42, cols=14, rows=14)
    C.hem(cp, 1.0, 0.1)
    for s in (-1, 1):
        pts = [(s * (0.62 + (0.85 - 0.62) * t), P['td'] / 2 + 0.04 + 0.35 * t * t, P['sh_z'] + 0.02 + (1.0 - P['sh_z'] - 0.02) * t) for t in [i / 10 for i in range(11)]]
        C.obj('Cloak_trim_%d' % (s > 0), tube_bm(pts, 0.035, 8), lime, 'UpperTorso', origin=(0, 0, P['waist_z']))
    bm = lathe([(P['head'] * 0.46, P['sh_z'] - 0.04), (P['head'] * 0.36, P['sh_z'] + 0.1)], 32); C.obj('Collar', bm, char_, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.04)
    # tunic skirt with lime piping, belt with a coin pouch
    z0 = P['hip_z'] - 0.7
    sk = shell(C, 'Tunic_skirt', [(z0, P['hw'] + 0.18, P['td'] + 0.16, 4), (P['waist_z'] - 0.02, P['hw'] + 0.06, P['td'] + 0.06, 4)], dark, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
    C.hem(sk, z0, 0.08); C.seam(sk, 0.0)
    belt(C, P, P['waist_z'], leather('rigger belt', (60, 48, 36)), metal('rigger buckle', (150, 230, 40), rough=0.35), h=0.13, extra=0.08)
    bm = ellipsoid(0.16, 0.12, 0.2, 16, 8); xform(bm, T(-P['hw'] / 2 - 0.1, -0.12, P['waist_z'] - 0.22)); C.obj('Coin_pouch', bm, leather('rigger pouch', (90, 70, 40)), 'LowerTorso', origin=(0, 0, P['hip_z']))
    # glowing cheat rune on the right hand (front face) + spark bits
    (a0, a1, _) = C.J['RightHand']
    rm = decal_mat('rigger rune', rune_image(), 9.0)
    quad_decal(C, 'Palm_rune', Vector((a0[0], -P['ad'] * 0.44, (a0[2] + a1[2]) / 2 + 0.03)), 0.3, '-Y', rm, 'RightHand', a0)
    sp = glow('lime spark', (180, 255, 70), 14.0); bm_all = bmesh.new(); me = bpy.data.meshes.new('tmp')
    for i in range(9):
        a = random.random() * 6.28; rr_ = 0.18 + random.random() * 0.25; z = (a0[2] + a1[2]) / 2 + random.uniform(-0.2, 0.35)
        bm = ellipsoid(0.025, 0.025, 0.05, 6, 4); xform(bm, T(a0[0] + rr_ * math.cos(a) * 0.8, -0.3 + rr_ * math.sin(a) * 0.5, z))
        bm.to_mesh(me); bm_all.from_mesh(me); bm.free()
    bpy.data.meshes.remove(me); C.obj('Cheat_sparks', bm_all, sp, 'RightHand', origin=a0)
    C.height = P['top']
    over = {'idle': {'UpperTorso': (0, -0.13, 1), 'Head': (0, -0.05, 1), 'RightUpperArm': (-0.3, -0.45, -0.84), 'RightLowerArm': (0.05, -0.95, 0.3), 'RightHand': (0.0, -0.9, 0.42),
                     'LeftUpperArm': (0.55, 0.22, -0.8), 'LeftLowerArm': (-0.5, -0.1, -0.85), 'LeftHand': (-0.45, 0, -0.9)}}
    finish(C, 'idle', overrides=over, record=dict(role='Rival who wins by a visible cheat and gets exposed', body='slender_tall (slight hunch)',
           signature='toxic lime on charcoal', face_style='sharp rival set (new): sneer, fake innocence, gloat, panic, caught, sulk, neutral; blink; talk closed/half/open',
           silhouette='pointed hood + tiny crooked crown, long thin limbs, pointed hands, slim cloak, glowing palm rune'))
    return C

# =============================================================================  7. THE JAILER
def build_jailer():
    C = Char('The Jailer', 'jailer')
    P = body_params('brute', idle_out=10)
    rust = leather('jailer jerkin', (142, 72, 36), wear=0.75)
    dkl = leather('jailer leather', (70, 46, 32), wear=0.6)
    sleeve = cloth('jailer sleeves', (66, 50, 42), weave=40, hem_dark=0.7)
    trous = cloth('jailer trousers', (56, 44, 38), weave=36, hem_dark=0.7)
    glove = leather('jailer gloves', (30, 26, 24), wear=0.35)
    iron = metal('rust iron', (96, 84, 76), rough=0.55, scratch=0.9)
    hoodm = cloth('jailer hood', (20, 18, 22), weave=30, hem_dark=0.6, thread=(80, 70, 60), sheen=0.0)
    M = dict(UpperTorso=rust, LowerTorso=dkl, UpperArm=sleeve, LowerArm=sleeve, Hand=glove, UpperLeg=trous, LowerLeg=glove, Foot=glove)
    build_body(C, P, M, fist=True)
    face = dict(set='jailer', exprs=['glare', 'angry', 'surprised', 'squint'], fs=1.15, voff=-0.02, cut=0.99, emissive=14.0, rough=1.0, glow=1.0, spec=0.0)
    make_head(C, P, (5, 4, 6), face)
    hz, h = P['head_c'], P['head']
    # hood: rounded cowl with a deep face opening + a broad flat-topped mantle over the shoulders
    bm = ellipsoid(h * 0.9, h * 0.86, h * 0.84, 32, 18)
    for v in bm.verts:
        if v.co.z > 0: v.co.y += (v.co.z / (h * 0.84)) ** 2 * h * 0.3; v.co.z *= 1 + 0.25 * (v.co.z / (h * 0.84)) ** 4
    kill = [f for f in bm.faces if f.calc_center_median().y < -h * 0.42 and f.calc_center_median().z > -h * 0.5 and f.calc_center_median().z < h * 0.46]
    bmesh.ops.delete(bm, geom=kill, context='FACES'); xform(bm, T(0, 0.1, hz + 0.1))
    hd = C.obj('Hood', bm, hoodm, 'Head', origin=(0, 0, hz), solid=0.08)
    hd.data.materials.append(plain('hood void', (6, 5, 7), rough=1.0)); hd.modifiers['solidify'].material_offset = 1
    sz = P['sh_z']
    bm = loft([(sz - 0.75, P['sw'] + 0.55, P['td'] + 0.5, 5), (sz - 0.1, P['sw'] + 0.5, P['td'] + 0.45, 5), (sz + 0.12, P['sw'] + 0.2, P['td'] + 0.25, 4), (sz + 0.3, h * 1.0, h * 0.95, 2.5)], cap=(False, True), round_ends=0.0)
    mt = C.obj('Mantle', bm, hoodm, 'UpperTorso', origin=(0, 0, sz), solid=0.06); C.hem(mt, sz - 0.75, 0.1)
    # iron chest bands + studs, big belt, bracers
    for i, zz in enumerate([P['waist_z'] + P['ut'] * 0.25, P['waist_z'] + P['ut'] * 0.5]):
        bm = loft([(zz - 0.06, P['ww'] + 0.06 + 0.06 * i, P['td'] + 0.06, P['p']), (zz + 0.06, P['ww'] + 0.06 + 0.06 * i, P['td'] + 0.06, P['p'])])
        C.obj('Chest_band_%d' % i, bm, iron, 'UpperTorso', origin=(0, 0, P['waist_z']))
    belt(C, P, P['waist_z'] - 0.05, dkl, iron, h=0.32, extra=0.08)
    for side, s in (('Left', 1), ('Right', -1)):
        (l0, l1, _) = C.J[side + 'LowerArm']
        shell(C, side + 'Bracer', [(l1[2] + 0.05, P['at'] * 1.14, P['ad'] * 1.14, 6, l0[0], 0), (l0[2] - 0.12, P['at'] * 1.1, P['ad'] * 1.1, 6, l0[0], 0)], iron, side + 'LowerArm', l0, round_ends=0.04)
    # chains over the left shoulder, front and back
    sx = P['sw'] / 2; yf = -P['td'] / 2 - 0.12; yb = P['td'] / 2 + 0.12
    front = [(sx * 0.8, yf * 0.3, sz + 0.18), (sx * 0.5, yf, sz - 0.2), (0.0, yf - 0.02, P['waist_z'] + P['ut'] * 0.45), (-sx * 0.55, yf, P['waist_z'] + 0.15), (-sx * 0.8, yf * 0.8, P['waist_z'] - 0.1)]
    back = [(sx * 0.8, yb * 0.3, sz + 0.18), (sx * 0.5, yb, sz - 0.2), (0.0, yb + 0.02, P['waist_z'] + P['ut'] * 0.45), (-sx * 0.6, yb, P['waist_z'] + 0.1)]
    ironc = metal('chain iron', (110, 104, 100), rough=0.45, scratch=0.8)
    chain_path(C, 'Chain_front', front, ironc, 'UpperTorso', (0, 0, P['waist_z']), R_=0.12, r_=0.04, step=0.2)
    chain_path(C, 'Chain_back', back, ironc, 'UpperTorso', (0, 0, P['waist_z']), R_=0.12, r_=0.04, step=0.2)
    # giant key ring on the right hip
    kx, ky, kz = -P['hw'] / 2 - 0.3, -0.25, P['waist_z'] - 0.62
    bm = torus_bm(0.5, 0.075, 32, 10); xform(bm, T(kx, ky, kz) @ rotz(90) @ rotx(90)); C.obj('Key_ring', bm, ironc, 'LowerTorso', origin=(0, 0, P['hip_z']))
    brass = metal('old brass', (170, 130, 60), rough=0.4, scratch=0.8)
    for i, a in enumerate([-50, -20, 15, 45]):
        L = 1.05 + 0.2 * (i % 2); bm_all = bmesh.new(); me = bpy.data.meshes.new('tmp')
        parts = [xform(torus_bm(0.17, 0.05, 18, 8), rotx(90)), loft([(-L, 0.09, 0.09, 4), (-0.13, 0.09, 0.09, 4)]), xform(cube_bm(0.26, 0.06, 0.14), T(0.14, 0, -L + 0.16)), xform(cube_bm(0.17, 0.06, 0.11), T(0.1, 0, -L + 0.42))]
        for bm in parts: bm.to_mesh(me); bm_all.from_mesh(me); bm.free()
        bpy.data.meshes.remove(me)
        xform(bm_all, T(kx, ky, kz) @ Matrix.Rotation(R(a), 4, 'Y') @ T(0, 0, -0.5))
        C.obj('Key_%d' % i, bm_all, brass if i % 2 else ironc, 'LowerTorso', origin=(0, 0, P['hip_z']))
    C.height = P['top'] + 0.2
    over = {'idle': {'UpperTorso': (0, -0.1, 1), 'Head': (0, -0.06, 1), 'LeftUpperLeg': (0.12, 0, -1), 'LeftLowerLeg': (0.12, 0, -1), 'RightUpperLeg': (-0.12, 0, -1), 'RightLowerLeg': (-0.12, 0, -1)}}
    finish(C, 'idle', overrides=over, record=dict(role="The cruel ruler's enforcer: chains, dungeons, banishment", body='brute',
           signature='rust-iron brown + black hood', face_style='no exposed face: hood shadow with amber eyes (glare, angry, surprised, squint)',
           silhouette='huge flat-topped block under a black hood, chains over the left shoulder, giant key ring'))
    return C

# =============================================================================  8. THE SQUIRE
def build_squire(turned=False):
    # turned=True -> row 16, THE TURNED FRIEND: the Squire's exact rig and face family, violet-black, cracked spiked pot, a dark banner instead of the pack
    C = Char('The Turned Friend', 'turned_friend') if turned else Char('The Squire', 'squire')
    P = body_params('lanky_kid', idle_out=6)
    skin = (245, 205, 48)
    if turned:
        teal = cloth('turned tunic', (46, 26, 62), weave=40, hem_dark=0.6, thread=(255, 60, 200))
        trous = cloth('turned trousers', (36, 30, 42), weave=36, hem_dark=0.7)
        boot = leather('turned boots', (30, 26, 32), wear=0.5)
    else:
        teal = cloth('squire teal', (18, 138, 142), weave=40, hem_dark=0.62, thread=(240, 200, 120))
        trous = cloth('squire trousers', (150, 112, 70), weave=36, hem_dark=0.7)
        boot = leather('squire boots', (98, 62, 34), wear=0.7)
    sk = skin_mat('classic yellow', skin, classic=True)
    M = dict(UpperTorso=teal, LowerTorso=teal, UpperArm=teal, LowerArm=sk, Hand=sk, UpperLeg=trous, LowerLeg=boot, Foot=boot, Neck=sk)
    build_body(C, P, M)
    for side in ('Left', 'Right'): C.hem(C.parts[side + 'UpperArm'], C.J[side + 'UpperArm'][1][2] - P['at'] * 0.3, 0.08)
    face = dict(set='squire', exprs=['neutral', 'grin', 'terrified', 'shocked', 'relieved', 'deadpan', 'awe', 'brave', 'sad'], fs=1.0, voff=0.0, cut=0.56,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink', coat=0.15, rough=0.42)
    face['fs'] = 1.16; face['voff'] = -0.03
    if turned: face.update(set='turned_friend', exprs=['cold', 'scowl', 'smirk', 'sad', 'shocked'], overlay='eye_glow', glow=1.0)
    make_head(C, P, skin, face, kind='classic')
    hz, h = P['head_c'], P['head']
    # brass saucepan helmet, handle out to the back-left, slightly askew
    brass = metal('pot brass', (206, 150, 62), rough=0.3, scratch=0.6) if not turned else metal('pot brass tarnished', (138, 98, 52), rough=0.45, scratch=0.9)
    r = h * 0.6
    bm = lathe([(r * 1.08, -0.02), (r * 1.1, 0.05), (r * 1.0, 0.06), (r * 0.98, 0.4 * h), (r * 0.9, 0.46 * h), (0, 0.47 * h)], 44)
    xform(bm, T(0.04, 0.03, hz + h * 0.33) @ Matrix.Rotation(R(9), 4, 'Y') @ Matrix.Rotation(R(-5), 4, 'X'))
    C.obj('Pot_helmet', bm, brass, 'Head', origin=(0, 0, hz), solid=0.04)
    bm = loft([(0, 0.13, 0.07, 6), (1.15, 0.11, 0.06, 6)], round_ends=0.03); xform(bm, T(-r * 0.92, 0.08, hz + h * 0.39) @ Matrix.Rotation(R(-74), 4, 'Y') @ rotz(-12))
    C.obj('Pot_handle', bm, wood('pot handle', (60, 40, 26)), 'Head', origin=(0, 0, hz))
    if turned:      # the same pot, now spiked and cracked (the crack glows magenta like his eye)
        potM = T(0.04, 0.03, hz + h * 0.33) @ Matrix.Rotation(R(9), 4, 'Y') @ Matrix.Rotation(R(-5), 4, 'X')
        bms = []
        for i in range(7):
            a = 2 * math.pi * (i + 0.5) / 7; v = Vector((math.cos(a), math.sin(a), 0))
            sp_ = lathe([(0.1, 0), (0.0, 0.42)], 10); q = Vector((0, 0, 1)).rotation_difference((v * 0.55 + Vector((0, 0, 1))).normalized())
            xform(sp_, potM @ T(v.x * r * 0.85, v.y * r * 0.85, 0.4 * h) @ q.to_matrix().to_4x4()); bms.append(sp_)
        C.obj('Pot_spikes', join_bms(bms), metal('spike iron', (52, 48, 56), rough=0.4), 'Head', origin=(0, 0, hz))
        pts = [(-0.18, -r * 1.02, 0.42 * h), (-0.08, -r * 1.03, 0.3 * h), (-0.16, -r * 1.03, 0.2 * h), (-0.04, -r * 1.05, 0.08 * h), (-0.1, -r * 1.06, 0.0)]
        bm = tube_bm(pts, 0.022, 6); xform(bm, potM); C.obj('Pot_crack', bm, glow('magenta glow', (255, 50, 200), 8.0), 'Head', origin=(0, 0, hz))
    # tunic skirt + belt
    z0 = P['hip_z'] - 0.55
    s_ = shell(C, 'Tunic_skirt', [(z0, P['hw'] + 0.2, P['td'] + 0.2, 4), (P['waist_z'] - 0.02, P['hw'] + 0.06, P['td'] + 0.06, 4)], teal, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
    C.hem(s_, z0, 0.1)
    belt(C, P, P['waist_z'], leather('squire belt', (90, 56, 30)), brass, h=0.13, extra=0.06)
    if turned:      # a dark banner on a pole strapped to his back instead of the pack
        dark = wood('banner pole', (34, 28, 36)); by = P['td'] / 2 + 0.16; ztop = P['top'] + 1.2
        C.obj('Banner_pole', tube_bm([(0.0, by, P['waist_z'] - 0.5), (0.0, by, ztop)], 0.06, 8), dark, 'UpperTorso', origin=(0, 0, P['waist_z']))
        C.obj('Banner_bar', tube_bm([(-0.75, by + 0.02, ztop - 0.12), (0.75, by + 0.02, ztop - 0.12)], 0.045, 8), dark, 'UpperTorso', origin=(0, 0, P['waist_z']))
        for s_ in (-1, 1):
            bm = ellipsoid(0.07, 0.07, 0.07, 10, 6); xform(bm, T(s_ * 0.8, by + 0.02, ztop - 0.12)); C.obj('Banner_finial_%d' % (s_ > 0), bm, metal('spike iron', (52, 48, 56), rough=0.4), 'UpperTorso', origin=(0, 0, P['waist_z']))
        rows = []
        for r_ in range(9):
            t = r_ / 8; z = ztop - 0.18 - 1.6 * t
            rows.append([(-0.68 + 1.36 * c_ / 6, by + 0.08 + 0.05 * math.sin(c_ * 1.1 + t * 2.0), z - (0.28 * (1 - abs(c_ - 3) / 3) if r_ == 8 else 0)) for c_ in range(7)])
        C.obj('Banner_cloth', grid_sheet(rows), cloth('banner violet', (40, 22, 54), weave=30, hem_dark=0.7, thread=(255, 60, 200)), 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.03)
        sig = [(0, 0.3), (0.2, 0), (0, -0.3), (-0.2, 0)]
        bm = bmesh.new(); vs = [bm.verts.new((x_, by + 0.135, ztop - 0.85 + z_)) for x_, z_ in sig]; bm.faces.new(vs[::-1])
        C.obj('Banner_sigil', bm, glow('magenta glow', (255, 50, 200), 8.0), 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.01, smooth=False)
        for s_ in (-1, 1):
            pts = [(s_ * 0.34, -P['td'] / 2 - 0.03, P['waist_z'] + 0.1), (s_ * 0.36, -P['td'] / 2 - 0.05, P['sh_z'] - 0.2), (s_ * 0.36, -0.05, P['sh_z'] + 0.06), (s_ * 0.1, P['td'] / 2 + 0.12, P['sh_z'] - 0.1)]
            C.obj('Banner_strap_%d' % (s_ > 0), tube_bm(pts, 0.05, 8), leather('turned strap', (40, 32, 40)), 'UpperTorso', origin=(0, 0, P['waist_z']))
    else:
        # mountain backpack (taller than his head) + bedroll, pan, rope, lantern; shoulder straps in front
        canvas = cloth('pack canvas', (172, 148, 98), weave=26, hem_dark=0.7, thread=(220, 200, 150))
        by = P['td'] / 2 + 0.38
        by = P['td'] / 2 + 0.55
        shell(C, 'Backpack', [(P['waist_z'] - 0.45, 1.75, 1.0, 5, 0, by), (P['sh_z'] + 0.1, 1.85, 1.05, 5, 0, by + 0.04), (P['top'] + 0.45, 1.25, 0.92, 4, 0, by + 0.08)], canvas, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.18)
        shell(C, 'Backpack_pocket', [(P['waist_z'] - 0.3, 1.2, 0.3, 5, 0, by + 0.55), (P['waist_z'] + 0.5, 1.2, 0.3, 5, 0, by + 0.55)], canvas, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.1)
        bm = loft([(-0.95, 0.5, 0.5, 2), (0.95, 0.5, 0.5, 2)], round_ends=0.08); xform(bm, T(0, by + 0.08, P['top'] + 0.72) @ roty(90))
        C.obj('Bedroll', bm, cloth('bedroll', (150, 52, 40), weave=24, hem_dark=0.7), 'UpperTorso', origin=(0, 0, P['waist_z']))
        for s in (-1, 1):
            bm = torus_bm(0.26, 0.05, 16, 6); xform(bm, T(s * 0.62, by + 0.08, P['top'] + 0.72) @ roty(90)); C.obj('Bedroll_strap_%d' % (s > 0), bm, leather('squire strap', (100, 64, 34)), 'UpperTorso', origin=(0, 0, P['waist_z']))
        iron = metal('pan iron', (60, 60, 66), rough=0.45)
        bm = lathe([(0, 0), (0.34, 0.0), (0.4, 0.1), (0.37, 0.1), (0.31, 0.02), (0, 0.02)], 32); xform(bm, T(1.08, by + 0.1, P['sh_z'] - 0.2) @ roty(90) @ rotz(90))
        C.obj('Pan', bm, iron, 'UpperTorso', origin=(0, 0, P['waist_z']))
        bm = loft([(0, 0.07, 0.04, 6), (0.6, 0.06, 0.04, 6)]); xform(bm, T(1.1, by + 0.1, P['sh_z'] + 0.15)); C.obj('Pan_handle', bm, wood('pan handle', (70, 46, 28)), 'UpperTorso', origin=(0, 0, P['waist_z']))
        bm = torus_bm(0.34, 0.08, 24, 8); xform(bm, T(-1.08, by, P['sh_z'] - 0.05) @ roty(90)); C.obj('Rope_coil', bm, cloth('rope', (190, 160, 100), weave=12), 'UpperTorso', origin=(0, 0, P['waist_z']))
        bm = lathe([(0, 0), (0.14, 0), (0.15, 0.06), (0.12, 0.08), (0.12, 0.3), (0.15, 0.33), (0.08, 0.42), (0, 0.44)], 16); xform(bm, T(-0.85, by + 0.5, P['waist_z'] - 0.2))
        C.obj('Lantern', bm, brass, 'UpperTorso', origin=(0, 0, P['waist_z']))
        for s in (-1, 1):
            pts = [(s * 0.34, -P['td'] / 2 - 0.03, P['waist_z'] + 0.1), (s * 0.36, -P['td'] / 2 - 0.05, P['sh_z'] - 0.2), (s * 0.36, -0.05, P['sh_z'] + 0.06), (s * 0.4, P['td'] / 2 + 0.05, P['sh_z'])]
            C.obj('Pack_strap_%d' % (s > 0), tube_bm(pts, 0.05, 8), leather('squire strap', (100, 64, 34)), 'UpperTorso', origin=(0, 0, P['waist_z']))
    # wooden practice sword through the belt at the left hip
    Mx = T(P['hw'] / 2 + 0.16, -0.12, P['waist_z'] + 0.25) @ Matrix.Rotation(R(-14), 4, 'Y') @ rotx(172)
    if turned: sword(C, 'Dark_sword', 1.45, 0.2, 0.42, 0.3, metal('dark blade', (44, 40, 52), rough=0.3), metal('spike iron', (52, 48, 56), rough=0.4), leather('turned grip', (60, 30, 70)), Mx, 'LowerTorso', (0, 0, P['hip_z']), rune=glow('magenta glow', (255, 50, 200), 8.0))
    else: sword(C, 'Wooden_sword', 1.45, 0.2, 0.42, 0.3, wood('practice wood', (196, 150, 90)), wood('practice guard', (120, 80, 44)), leather('squire grip', (110, 70, 36)), Mx, 'LowerTorso', (0, 0, P['hip_z']))
    C.height = P['top']
    over = {'idle': {'Head': (0.04, -0.06, 1), 'LeftUpperArm': (0.12, -0.18, -1), 'LeftLowerArm': (-0.25, -0.6, -0.5), 'RightUpperArm': (-0.12, -0.18, -1), 'RightLowerArm': (0.25, -0.6, -0.5),
                     'LeftHand': (-0.3, -0.6, -0.4), 'RightHand': (0.3, -0.6, -0.4)}}
    if turned:
        over = {'idle': {'UpperTorso': (0, 0.05, 1), 'Head': (0, -0.14, 1), 'LeftUpperArm': (0.04, 0.02, -1), 'RightUpperArm': (-0.04, 0.02, -1), 'LeftLowerArm': (0.02, -0.05, -1), 'RightLowerArm': (-0.02, -0.05, -1),
                         'LeftHand': (0, -0.05, -1), 'RightHand': (0, -0.05, -1), 'LeftUpperLeg': (0.07, 0, -1), 'LeftLowerLeg': (0.07, 0, -1), 'RightUpperLeg': (-0.07, 0, -1), 'RightLowerLeg': (-0.07, 0, -1)}}
        finish(C, 'idle', overrides=over, record=dict(role='The Squire after he takes the other side: a villain viewers care about, with a rescue arc', body='lanky_kid (the Squire\'s exact rig), straighter and colder',
               signature='violet-black + one glowing magenta eye', face_style="the Squire's toybox family: cold, scowl, smirk, sad, shocked; blink; talk; glowing magenta eye overlay (rig 'glow' 1 = on, 0 = turned back)",
               silhouette='the same saucepan helmet, now cracked and spiked; a dark banner on a pole instead of the backpack'))
        return C
    finish(C, 'idle', overrides=over, record=dict(role="Loyal best friend: cowardly-but-brave sidekick, the hero's dialogue partner", body='lanky_kid',
           signature='teal tunic + brass pot', face_style='toybox family pushed expressive (classic simple decal family): neutral, grin, terrified, shocked, relieved, deadpan, awe, brave, sad; blink; talk closed/half/open',
           silhouette='saucepan helmet with handle, mountain backpack with bedroll, wooden sword, thin yellow limbs'))
    return C

# =============================================================================  4. TRUE-FORM LEAD (Hero kid's power form)
def build_true_form():
    C = Char('True-Form Lead', 'true_form')
    P = body_params('true_form', idle_out=9, sw=2.3, ww=1.3, hw=1.35, td=1.0, at=0.6, ad=0.62, lgw=0.66, lgd=0.68)
    skin = (238, 196, 156)                           # = Hero kid
    orange = cloth('hero coat', (206, 76, 48), weave=32, hem_dark=0.62, thread=(255, 200, 90), sheen=0.5)   # = Hero kid shirt
    navy = cloth('hero navy', (52, 58, 82), weave=46, hem_dark=0.7, thread=(255, 200, 90))                     # = Hero kid trousers
    armor = metal('hero armor', (54, 62, 92), rough=0.26, scratch=0.5)
    gold = metal('hero gold', (240, 180, 70), rough=0.24, scratch=0.3)
    belt_l = leather('hero leather', (110, 68, 38), wear=0.6)        # = Hero kid belt / satchel strap
    power = glow('power glow', (255, 196, 70), 10.0)
    glove = leather('hero gloves', (46, 36, 32), wear=0.4)
    M = dict(UpperTorso=orange, LowerTorso=navy, UpperArm=orange, LowerArm=orange, Hand=glove, UpperLeg=navy, LowerLeg=armor, Foot=belt_l, Neck=skin_mat('hero skin', skin))
    build_body(C, P, M)
    face = dict(set='true_form', exprs=['locked_in', 'calm_smirk', 'bright', 'angry', 'shocked', 'scared'], fs=0.86, voff=0.0, cut=0.685,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink', overlay='eye_glow', glow=0.0)
    make_head(C, P, skin, face)
    add_hair(C, 'hero_crop', (74, 48, 32))
    # chest armour plate (front), shoulder guards with gold rims, vambraces, greave tops
    td = P['td']
    shell(C, 'Chest_plate', [(P['waist_z'] + 0.15, P['ww'] * 0.86, td * 0.7, 3.5, 0, -td * 0.2), (P['waist_z'] + P['ut'] * 0.62, P['sw'] * 0.78, td * 0.72, 3.5, 0, -td * 0.2), (P['sh_z'] - 0.06, P['sw'] * 0.6, td * 0.62, 3, 0, -td * 0.18)], armor, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.08)
    zc = P['waist_z'] + P['ut'] * 0.58
    bm = lathe([(0, 0), (0.2, 0), (0.2, 0.06), (0, 0.06)], 6); xform(bm, T(0, -td * 0.57 - 0.06, zc) @ rotx(90) @ rotz(30)); C.obj('Core_gem', bm, power, 'UpperTorso', origin=(0, 0, zc))
    bm = torus_bm(0.24, 0.04, 6, 6); xform(bm, T(0, -td * 0.57 - 0.04, zc) @ rotx(90) @ rotz(30)); C.obj('Core_rim', bm, gold, 'UpperTorso', origin=(0, 0, zc))
    for side, s in (('Left', 1), ('Right', -1)):
        pauldron(C, side, s, s * P['sx'], P['sh_z'] + 0.02, 0.5, layers=2, mat=armor, rim=gold, tilt=20)
        (l0, l1, _) = C.J[side + 'LowerArm']
        shell(C, side + 'Vambrace', [(l1[2] + 0.02, P['at'] * 1.16, P['ad'] * 1.16, 5, l0[0], 0), (l0[2] - 0.1, P['at'] * 1.1, P['ad'] * 1.1, 5, l0[0], 0)], armor, side + 'LowerArm', l0, round_ends=0.04)
        bm = torus_bm(P['at'] * 0.62, 0.035, 24, 6); bmesh.ops.scale(bm, vec=(1, P['ad'] / P['at'], 1), verts=bm.verts); xform(bm, T(l0[0], 0, l1[2] + 0.06)); C.obj(side + 'Vambrace_rim', bm, gold, side + 'LowerArm', origin=l0)
        x = s * P['lx']
        bm = ellipsoid(P['lgw'] * 0.62, P['lgd'] * 0.62, 0.22, 18, 9); xform(bm, T(x, -0.06, P['knee_z'])); C.obj(side + 'Knee', bm, gold, side + 'LowerLeg', origin=(x, 0, P['knee_z']))
    # long coat tails (open front), flared back like they're moving
    rows = []
    zt, zb = P['waist_z'] + 0.05, P['knee_z'] - 0.35
    for r in range(13):
        t = r / 12; z = zt + (zb - zt) * t
        rx = P['hw'] / 2 + 0.12 + t * 0.55; ry = P['td'] / 2 + 0.12 + t * 0.5
        row = []
        for c in range(25):
            a = R(32 + (360 - 64) * c / 24)          # 0 = front (-Y); leave the front open
            x = math.sin(a) * rx; y = -math.cos(a) * ry + t * t * 0.6 * max(0, -math.cos(a))
            row.append((x + t * t * 0.25, y, z + (0.18 * t * math.sin(a * 3) if r == 12 else 0)))
        rows.append(row)
    coat = C.obj('Coat_tails', grid_sheet(rows), orange, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.045)
    C.hem(coat, zb - 0.2, 0.16)
    bm = lathe([(P['head'] * 0.5, P['sh_z'] - 0.06), (P['head'] * 0.48, P['sh_z'] + 0.22), (P['head'] * 0.56, P['neck_z'] + 0.12)], 36); C.obj('Coat_collar', bm, orange, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.05)
    belt(C, P, P['waist_z'], belt_l, gold, h=0.2, extra=0.1)
    pts = [(0.62, -td / 2 - 0.06, P['sh_z'] - 0.04), (0.0, -td / 2 - 0.08, P['waist_z'] + P['ut'] * 0.45), (-0.6, -td / 2 - 0.05, P['waist_z'] + 0.12)]
    C.obj('Bandolier', tube_bm(pts, 0.07, 8), belt_l, 'UpperTorso', origin=(0, 0, P['waist_z']))
    # scarf streaming back from the collar (the "moving" piece)
    scarf = cape(C, 'Scarf_tail', 0.22, 0.32, P['sh_z'] + 0.05, P['waist_z'] - 0.4, P['td'] / 2 + 0.05, cloth('hero scarf', (176, 54, 36), weave=36, hem_dark=0.6), torn=0.35, flare_back=1.5, curve=0.1, cols=4, rows=10, sway=0.9)
    C.hem(scarf, P['waist_z'] - 0.4, 0.0)
    # the signature item, now huge: a greatsword on the back with a glowing rune fuller (hilt over the LEFT shoulder)
    Mx = T(0.4, P['td'] / 2 + 0.36, P['sh_z'] - 0.05) @ Matrix.Rotation(R(24), 4, 'Y') @ rotx(180)
    sword(C, 'Greatsword', 5.2, 0.5, 1.4, 1.0, metal('hero blade', (196, 204, 220), rough=0.18, scratch=0.5), gold, belt_l, Mx, 'UpperTorso', (0, 0, P['waist_z']), rune=power)
    # aura: a soft glowing ground ring (hide 'True-Form Lead | Aura' when not wanted)
    am = bpy.data.materials.new('CV3 aura ring'); nt = am.node_tree
    for n_ in list(nt.nodes):
        if n_.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n_)
    out_ = [n_ for n_ in nt.nodes][0]; tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    rr = _m(nt, 'SQRT', _m(nt, 'ADD', _m(nt, 'MULTIPLY', sep.outputs[0], sep.outputs[0]), _m(nt, 'MULTIPLY', sep.outputs[1], sep.outputs[1])))
    band = _m(nt, 'MULTIPLY', _m(nt, 'SUBTRACT', 1.0, _m(nt, 'MULTIPLY', _m(nt, 'ABSOLUTE', _m(nt, 'SUBTRACT', rr, 1.45)), 2.2), clamp=True), 1.0)
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = rgba((255, 196, 70)); em.inputs['Strength'].default_value = 5.0
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(_m(nt, 'POWER', band, 2.0), mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out_.inputs['Surface'])
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=2.0); xform(bm, T(0, 0, 0.02))
    C.obj('Aura', bm, am, 'Root', origin=(0, 0, 0), smooth=False)
    C.height = P['top']
    over = {'idle': {'LeftUpperLeg': (0.1, 0, -1), 'LeftLowerLeg': (0.1, 0, -1), 'RightUpperLeg': (-0.1, 0, -1), 'RightLowerLeg': (-0.1, 0, -1), 'Head': (0, -0.02, 1)}}
    finish(C, 'idle', overrides=over, record=dict(role="The Hero kid's true / power form (same person, same head and face set)", body='true_form (6.75 HH, 2.08x hero)',
           signature="Hero kid's burnt orange + navy, one power glow (edit material 'CV3 power glow' per story)",
           face_style="Hero kid's town-anime set + 2 new (locked_in, calm_smirk) + glowing-eye overlay for power moments (rig 'glow' 0 off .. 1 on); blink; talk closed/half/open",
           silhouette='same crop hair, long coat tails + scarf, pauldrons, giant greatsword hilt over the left shoulder, aura'))
    return C

# =============================================================================  6. EMBER (hatchling dragon; two stages)
def ember_colour(nt, kind='body'):
    """colour socket that follows the object's 'reskin' property: 0 ember orange, 1 storm blue, 2 crystal violet"""
    sets = {'body': [(242, 110, 28), (40, 110, 210), (140, 70, 214)], 'belly': [(255, 204, 112), (176, 220, 255), (222, 184, 255)],
            'horn': [(66, 40, 34), (30, 40, 70), (60, 30, 80)], 'flame': [(255, 150, 30), (90, 200, 255), (210, 120, 255)], 'core': [(255, 236, 150), (220, 250, 255), (250, 220, 255)]}[kind]
    rs = _attr(nt, 'reskin')
    c = _mixc(nt, rgba(sets[0]), rgba(sets[1]), _m(nt, 'COMPARE', rs, 1.0, 0.5))
    return _mixc(nt, c, rgba(sets[2]), _m(nt, 'COMPARE', rs, 2.0, 0.5))

def ember_mat(name, kind):
    m = bpy.data.materials.new('CV3 ' + name); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    col = ember_colour(nt, kind)
    if kind == 'body':
        tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
        bel = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', _m(nt, 'SUBTRACT', _m(nt, 'MULTIPLY', sep.outputs[1], -1.0), _attr(nt, 'belly_y')), 14.0, clamp=True), _attr(nt, 'belly'))
        col = _mixc(nt, col, ember_colour(nt, 'belly'), bel)
        vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 26; nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; nt.links.new(vo.outputs['Distance'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
        b.inputs['Roughness'].default_value = 0.45; b.inputs['Coat Weight'].default_value = 0.2
    elif kind == 'horn':
        b.inputs['Roughness'].default_value = 0.35
    nt.links.new(col, b.inputs['Base Color'])
    if kind in ('flame', 'core'):
        for n in list(nt.nodes):
            if n.bl_idname not in ('ShaderNodeOutputMaterial',) and n != col.node and n.bl_idname in ('ShaderNodeBsdfPrincipled',): nt.nodes.remove(n)
        out = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial'][0]
        e = nt.nodes.new('ShaderNodeEmission'); nt.links.new(col, e.inputs['Color']); e.inputs['Strength'].default_value = 9.0 if kind == 'flame' else 14.0
        if kind == 'flame':
            tr = nt.nodes.new('ShaderNodeBsdfTransparent'); lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.45
            mx = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(lw.outputs['Facing'], mx.inputs[0]); nt.links.new(e.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
            nt.links.new(mx.outputs[0], out.inputs['Surface'])
        else:
            nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m

def build_ember(stage):
    grown = stage == 'grown'
    C = Char('Ember (grown)' if grown else 'Ember (hatchling)', 'ember_grown' if grown else 'ember_hatchling')
    H = K.HERO_H if grown else 1.0 * K.HH
    s = H / 1.28 if not grown else H / 1.6          # grown is longer-bodied: built from its own proportions
    # proportions in units of s
    if not grown:
        body_c, body_r = (0.42, (0.37, 0.33, 0.36)); head_c, head_r = (0.96, (0.35, 0.31, 0.32)); leg_r, leg_l = 0.1, 0.14; arm_r, arm_l = 0.075, 0.2; horn_l = 0.17
    else:
        body_c, body_r = (0.56, (0.36, 0.33, 0.44)); head_c, head_r = (1.29, (0.33, 0.3, 0.31)); leg_r, leg_l = 0.11, 0.2; arm_r, arm_l = 0.08, 0.3; horn_l = 0.3
    bodym = ember_mat(C.name + ' body', 'body'); hornm = ember_mat(C.name + ' horn', 'horn')
    flm = ember_mat(C.name + ' flame', 'flame'); core = ember_mat(C.name + ' core', 'core')
    bz = body_c * s; hz = head_c * s; top = hz + head_r[2] * s
    neck = bz + body_r[2] * s * 0.7
    J = {'Root': ((0, 0, 0), (0, 0, bz * 0.5), None),
         'LowerTorso': ((0, 0, bz - body_r[2] * s * 0.5), (0, 0, bz), 'Root'),
         'UpperTorso': ((0, 0, bz), (0, 0, neck), 'LowerTorso'),
         'Head': ((0, 0, neck), (0, 0, top), 'UpperTorso'),
         'Tail': ((body_r[0] * s * 0.3, body_r[1] * s * 0.8, bz - body_r[2] * s * 0.45), (body_r[0] * s * 1.25, body_r[1] * s * 1.3, bz - body_r[2] * s * 0.62), 'LowerTorso'),
         'TailTip': ((body_r[0] * s * 1.25, body_r[1] * s * 1.3, bz - body_r[2] * s * 0.62), (body_r[0] * s * 1.75, body_r[1] * s * 0.9, bz + body_r[2] * s * 0.12), 'Tail')}
    for side, sg in (('Left', 1), ('Right', -1)):
        ax = sg * body_r[0] * s * 0.92; az = bz + body_r[2] * s * 0.35
        J[side + 'UpperArm'] = ((ax, -0.04 * s, az), (ax + sg * 0.05 * s, -0.06 * s, az - arm_l * s), 'UpperTorso')
        J[side + 'Hand'] = ((ax + sg * 0.05 * s, -0.06 * s, az - arm_l * s), (ax + sg * 0.06 * s, -0.08 * s, az - (arm_l + 0.08) * s), side + 'UpperArm')
        lx = sg * body_r[0] * s * 0.5; lz = bz - body_r[2] * s * 0.62
        J[side + 'UpperLeg'] = ((lx, 0, lz), (lx, 0, leg_r * s), 'LowerTorso')
        J[side + 'Foot'] = ((lx, 0, leg_r * s), (lx, -0.22 * s, 0.04 * s), side + 'UpperLeg')
    C.P = dict(p=4, td=body_r[1] * 2 * s, ua=arm_l * s, at=arm_r * 2 * s, ad=arm_r * 2 * s, head=head_r[2] * 2 * s, head_c=hz, top=top, idle_out=25)
    K.make_rig(C, J); C.J = J
    rig = C.rig; rig['reskin'] = 0
    try: rig.id_properties_ui('reskin').update(min=0, max=2, description='0 ember orange, 1 storm blue, 2 crystal violet')
    except Exception: pass
    rig['flame'] = 1.0
    def part(label, bm, mat, bone, origin, belly=0.0):
        o = C.obj(label, bm, mat, bone, origin=origin); o['reskin'] = 0; drive(o, 'reskin', rig, 'reskin'); o['belly'] = belly; o['belly_y'] = body_r[1] * s * 0.35; return o
    bm = ellipsoid(body_r[0] * s, body_r[1] * s, body_r[2] * s, 40, 20)
    for v in bm.verts:   # pear shape: fuller at the bottom
        if v.co.z < 0: v.co.x *= 1.06; v.co.y *= 1.04
    xform(bm, T(0, 0, bz)); part('UpperTorso_Geo', bm, bodym, 'UpperTorso', (0, 0, bz), belly=1.0)
    # head with the face decal
    k = head_r[2] * 2 * s / 1.2
    bm = ellipsoid(head_r[0] * s, head_r[1] * s, head_r[2] * s, 40, 20); xform(bm, T(0, -0.04 * s, hz))
    ho = C.obj('Head_Geo', bm, None, 'Head', origin=(0, 0, hz))
    hm = K.face_material(C, (242, 110, 28), 'ember', ['happy', 'curious', 'fierce', 'scared', 'proud'], k * 1.08, fs=0.82, voff=0.0, cut=0.99, rough=0.45,
                         base_override=lambda nt: ember_colour(nt, 'body'))
    ho.data.materials.append(hm); ho['reskin'] = 0; drive(ho, 'reskin', rig, 'reskin')
    rig['face'] = 0; rig['mouth'] = 0; rig['blink'] = 0; rig['glow'] = 1.0; rig['face_names'] = '0 happy, 1 curious, 2 fierce, 3 scared, 4 proud'
    for pr in ('face', 'mouth', 'blink', 'glow'): ho[pr] = rig[pr]; drive(ho, pr, rig, pr)
    try: rig.id_properties_ui('face').update(min=0, max=4, description=rig['face_names'])
    except Exception: pass
    C.head = ho
    # snout bump + nostrils (small, keeps the dragon read without hiding the face)
    # horns: stubby, curving back
    for sg in (-1, 1):
        pts = [(sg * head_r[0] * s * 0.5, 0.02 * s, hz + head_r[2] * s * 0.78)]
        for i in range(1, 6):
            t = i / 5; pts.append((sg * (head_r[0] * s * 0.5 + 0.05 * s * t), (0.02 + 0.16 * t * t) * s * (horn_l / 0.17), hz + head_r[2] * s * 0.78 + horn_l * s * t * (1 - 0.35 * t)))
        part('Horn_%s' % ('L' if sg > 0 else 'R'), tube_bm(pts, [0.065 * s * (1 - 0.85 * i / 5) for i in range(6)], 12), hornm, 'Head', (0, 0, hz))
        # ear fins
        bm = ellipsoid(0.03 * s, 0.1 * s, 0.07 * s, 12, 6); xform(bm, T(sg * head_r[0] * s * 0.98, 0.04 * s, hz + 0.04 * s) @ rotz(sg * 25)); part('Ear_%s' % ('L' if sg > 0 else 'R'), bm, bodym, 'Head', (0, 0, hz))
    # arms, legs, feet
    for side, sg in (('Left', 1), ('Right', -1)):
        (a0, a1, _) = J[side + 'UpperArm']; (h0, h1, _) = J[side + 'Hand']
        part(side + 'UpperArm_Geo', tube_bm([a0, a1], arm_r * s, 12), bodym, side + 'UpperArm', a0)
        bm = ellipsoid(arm_r * s * 1.25, arm_r * s * 1.15, arm_r * s * 1.2, 14, 8); xform(bm, T(*h1)); part(side + 'Hand_Geo', bm, bodym, side + 'Hand', h0)
        (l0, l1, _) = J[side + 'UpperLeg']
        part(side + 'UpperLeg_Geo', tube_bm([l0, (l1[0], l1[1], l1[2] + 0.02 * s)], leg_r * s, 14), bodym, side + 'UpperLeg', l0)
        bm = ellipsoid(leg_r * s * 1.25, leg_r * s * 1.9, leg_r * s * 0.85, 16, 8); xform(bm, T(l1[0], -leg_r * s * 0.7, leg_r * s * 0.85)); part(side + 'Foot_Geo', bm, bodym, side + 'Foot', J[side + 'Foot'][0])
        for t in (-1, 0, 1):
            bm = ellipsoid(0.03 * s, 0.04 * s, 0.03 * s, 8, 6); xform(bm, T(l1[0] + t * leg_r * s * 0.6, -leg_r * s * 2.45, leg_r * s * 0.5)); part('%sClaw%d' % (side, t + 1), bm, hornm, side + 'Foot', J[side + 'Foot'][0])
    # tail + flame
    (t0, t1, _), (u0, u1, _) = J['Tail'], J['TailTip']
    pts = [t0, ((t0[0] + t1[0]) / 2, (t0[1] + t1[1]) / 2 + 0.02 * s, (t0[2] + t1[2]) / 2 - 0.04 * s), t1]
    part('Tail_Geo', tube_bm(pts, [0.12 * s, 0.09 * s, 0.07 * s], 14), bodym, 'Tail', t0)
    pts = [u0, ((u0[0] + u1[0]) / 2, (u0[1] + u1[1]) / 2 + 0.05 * s, (u0[2] + u1[2]) / 2), u1]
    part('TailTip_Geo', tube_bm(pts, [0.07 * s, 0.055 * s, 0.035 * s], 12), bodym, 'TailTip', u0)
    fs_ = (0.5 if not grown else 0.62) * s
    for lab, sc, m in (('Tail_flame', 1.0, flm), ('Tail_flame_core', 0.55, core)):
        bm = lathe([(0, 0), (0.12 * sc, 0.04), (0.17 * sc, 0.16), (0.14 * sc, 0.34), (0.07 * sc, 0.55), (0, 0.78 * (0.8 + 0.2 * sc))], 18)
        bmesh.ops.scale(bm, vec=(fs_ / 0.5, fs_ / 0.5, fs_ / 0.5 * 1.0), verts=bm.verts)
        xform(bm, T(u1[0], u1[1] + 0.02 * s, u1[2] - 0.06 * s) @ rotx(-18))
        o = part(lab, bm, m, 'TailTip', u0)
    if grown:   # back ridge spikes hint at the next stage
        for i in range(5):
            t = i / 4; z = bz + body_r[2] * s * (0.55 - 0.9 * t); y = body_r[1] * s * (0.82 + 0.1 * math.sin(t * 3))
            bm = lathe([(0, 0), (0.08 * s, 0), (0.03 * s, 0.1 * s), (0, 0.2 * s * (1 - 0.3 * abs(t - 0.4)))], 10); xform(bm, T(0, y - 0.03 * s, z) @ rotx(-35 - 25 * t))
            part('Spike_%d' % i, bm, hornm, 'UpperTorso', (0, 0, bz))
    C.height = top
    over = {'idle': {}, 'laugh': {'Head': (0, 0.35, 1)}, 'fists_up': {'Head': (0, -0.2, 1), 'UpperTorso': (0, -0.15, 1)}}
    for nm in over:
        pass
    ex = {'roar': {'Head': (0, -0.3, 1), 'LeftUpperArm': (0.6, -0.6, 0.3), 'RightUpperArm': (-0.6, -0.6, 0.3), 'LeftHand': (0.6, -0.6, 0.4), 'RightHand': (-0.6, -0.6, 0.4), 'TailTip': (0, 0.4, 1)}}
    finish(C, 'idle', extra_poses=ex, record=dict(role='Mystical hatchling that answers only to the hero and grows each episode', body='mini/plushie creature on an R6-derived rig' + (' (hero-height stage)' if grown else ' (knee-high stage)'),
           signature='ember orange (reskins: rig "reskin" 1 storm blue, 2 crystal violet)', face_style='big-eye creature face, storybook family (new): happy, curious, fierce, scared, proud',
           silhouette='round blob, two stubby horns, tail flame' + (' + back spikes' if grown else '')))
    return C

# =============================================================================  2. THE CROWD SIX
def crowd_member(name, key, btype, over, skin, faceset, head_kind, outfit, accessories, pose_name, pose_dirs, face_default, record):
    C = Char(name, key)
    P = body_params(btype, **over)
    M = outfit(P)
    build_body(C, P, M, barrel=(btype == 'round_big'))
    face = dict(set=faceset, exprs=['neutral', 'shocked', 'laughing'], fs=0.9 if head_kind == 'refl' else 1.0, voff=0.0, cut=0.6, default=face_default,
                coat=0.15 if head_kind == 'classic' else 0.0, rough=0.42 if head_kind == 'classic' else 0.5)
    make_head(C, P, skin, face, kind=head_kind)
    accessories(C, P)
    C.height = record.pop('_height', P['top'])
    std = ('idle', 'point', 'laugh', 'shocked', 'fists_up', 'arms_crossed')
    if pose_name in std: finish(C, pose_name, overrides={pose_name: pose_dirs} if pose_dirs else None, record=record)
    else: finish(C, pose_name, extra_poses={pose_name: pose_dirs}, record=record)
    return C

def build_crowd():
    out = []
    earth = dict(ochre=(196, 150, 58), olive=(112, 120, 58), rust=(136, 84, 62), slate=(84, 96, 112))
    # 1 POINTER: tall-thin, tall felt hat, slate coat
    def o1(P):
        coat = cloth('pointer coat', earth['slate'], weave=36, hem_dark=0.65); tr = cloth('pointer trousers', (50, 48, 46), weave=40)
        b = leather('pointer boots', (52, 40, 32)); sk = skin_mat('pointer skin', (234, 192, 160))
        return dict(UpperTorso=coat, LowerTorso=coat, UpperArm=coat, LowerArm=coat, Hand=sk, UpperLeg=tr, LowerLeg=b, Foot=b, Neck=sk)
    def a1(C, P):
        coat = K._MATS['CV3 pointer coat']; felt = cloth('pointer hat', (58, 62, 72), weave=60, hem_dark=0.7)
        z0 = P['knee_z'] - 0.2
        sk = shell(C, 'Coat_skirt', [(z0, P['hw'] + 0.42, P['td'] + 0.36, 4), (P['waist_z'] - 0.02, P['hw'] + 0.08, P['td'] + 0.08, 4)], coat, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
        C.hem(sk, z0, 0.1); C.seam(sk, 0.0)
        hz, h = P['head_c'], P['head']
        bm = lathe([(0, 0), (h * 0.8, 0), (h * 0.8, 0.04), (h * 0.55, 0.06), (h * 0.5, 1.05), (h * 0.46, 1.12), (0, 1.12)], 40); xform(bm, T(0, 0.04, hz + h * 0.42) @ Matrix.Rotation(R(-6), 4, 'Y'))
        C.obj('Tall_hat', bm, felt, 'Head', origin=(0, 0, hz))
        bm = loft([(0.12, h * 1.02, h * 1.02, 2), (0.28, h * 1.0, h * 1.0, 2)], cap=(False, False)); xform(bm, T(0, 0.04, hz + h * 0.42) @ Matrix.Rotation(R(-6), 4, 'Y'))
        C.obj('Hat_band', bm, leather('pointer band', (110, 64, 34)), 'Head', origin=(0, 0, hz), solid=0.02)
        belt(C, P, P['waist_z'], leather('pointer belt', (80, 56, 36)), None, h=0.12, extra=0.06)
    out.append(crowd_member('Crowd Pointer', 'crowd_pointer', 'slender_tall', dict(H=5.5 * K.HH, head=0.86, sw=1.15, ww=0.95, hw=1.0, td=0.6, at=0.3, ad=0.32, lgw=0.36, lgd=0.38, hunch=0), (234, 192, 160),
                            'crowd_pointer', 'refl', o1, a1, 'point', None, 2, dict(role='Crowd Six: the pointer (points and laughs)', body='tall-thin 5.5 HH', signature='slate', face_style='storybook (blue-grey iris): neutral, shocked, laughing', silhouette='tall felt hat')))
    # 2 BELLY-LAUGHER: round gentle-big, barrel apron, beard
    def o2(P):
        tun = cloth('laugher tunic', earth['ochre'], weave=34, hem_dark=0.65); tr = cloth('laugher trousers', (74, 70, 50), weave=36)
        b = leather('laugher boots', (70, 48, 32)); sk = skin_mat('laugher skin', (112, 72, 48))
        return dict(UpperTorso=tun, LowerTorso=tun, UpperArm=tun, LowerArm=sk, Hand=sk, UpperLeg=tr, LowerLeg=b, Foot=b)
    def a2(C, P):
        for side in ('Left', 'Right'): C.hem(C.parts[side + 'UpperArm'], C.J[side + 'UpperArm'][1][2] - P['at'] * 0.3, 0.08)
        ap = leather('barrel apron', (100, 64, 40), wear=0.3)
        zc = P['hip_z'] - 0.1; z1 = P['sh_z'] - 0.35
        rows = []
        for r_ in range(11):
            t = r_ / 10; z = (zc - 0.5) + (z1 - zc + 0.5) * t
            wid = P['ww'] * (0.86 + 0.1 * math.sin(t * 3.0)); dep = P['td'] * (0.98 + 0.06 * math.sin(t * 3.0))
            row = []
            for c_ in range(13):
                a = math.radians(-40 + 80 * c_ / 12)
                row.append((math.sin(a) * wid / 2 * 1.03, -math.cos(a) * dep / 2 * 1.04 - 0.03, z))
            rows.append(row)
        sh = C.obj('Barrel_apron', grid_sheet(rows), ap, 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.04)
        iron = metal('hoop iron', (80, 76, 74), rough=0.5, scratch=0.9)
        for i, t in enumerate((0.18, 0.62)):
            z = zc - 0.55 + (z1 - zc + 0.55) * t
            wid = P['ww'] * (0.86 + 0.1 * math.sin(t * 3.0)); dep = P['td'] * (0.98 + 0.06 * math.sin(t * 3.0))
            pts = [(math.sin(math.radians(a)) * wid / 2 * 1.06, -math.cos(math.radians(a)) * dep / 2 * 1.07 - 0.03, z) for a in range(-38, 39, 5)]
            C.obj('Apron_hoop_%d' % i, tube_bm(pts, 0.045, 8), iron, 'UpperTorso', origin=(0, 0, P['waist_z']))
        for sg in (-1, 1):   # neck strap so it reads as an apron
            pts = [(sg * P['ww'] * 0.3, -P['td'] * 0.5, z1 - 0.05), (sg * P['sw'] * 0.3, -P['td'] * 0.38, P['sh_z'] - 0.02), (sg * P['head'] * 0.3, -P['td'] * 0.1, P['sh_z'] + 0.04)]
            C.obj('Apron_strap_%d' % (sg > 0), tube_bm(pts, 0.05, 8), ap, 'UpperTorso', origin=(0, 0, P['waist_z']))
        add_hair(C, 'hero_medium_tousle', (30, 22, 18), offset=(0, 0.03, 0.1))
    out.append(crowd_member('Crowd Belly-laugher', 'crowd_laugher', 'round_big', dict(H=3.75 * K.HH, sw=2.05, arm_gap=0.0, idle_out=13), (112, 72, 48), 'crowd_laugher', 'refl', o2, a2, 'laugh', {'LeftUpperArm': (0.55, -0.3, -0.78), 'RightUpperArm': (-0.55, -0.3, -0.78), 'LeftLowerArm': (-0.45, -0.85, -0.2), 'RightLowerArm': (0.45, -0.85, -0.2), 'LeftHand': (-0.4, -0.8, -0.4), 'RightHand': (0.4, -0.8, -0.4), 'Head': (0, 0.45, 0.9), 'UpperTorso': (0, 0.12, 1)}, 2,
                            dict(role='Crowd Six: the belly-laugher (a brewer; competent and kind, laughs loudest)', body='round gentle-big 3.75 HH', signature='ochre', face_style='storybook (brown iris): neutral, shocked, laughing', silhouette='leather barrel apron with iron hoops, round body')))
    # 3 WHISPERER: classic-yellow R6, big bonnet, olive dress
    def o3(P):
        dr = cloth('whisperer dress', earth['olive'], weave=36, hem_dark=0.65); sk = skin_mat('classic yellow', (245, 205, 48), classic=True)
        return dict(UpperTorso=dr, LowerTorso=dr, UpperArm=dr, LowerArm=dr, Hand=sk, UpperLeg=dr, LowerLeg=sk, Foot=leather('whisperer shoes', (60, 44, 32)))
    def a3(C, P):
        dr = K._MATS['CV3 whisperer dress']
        z0 = 0.35
        sk = shell(C, 'Skirt', [(z0, P['hw'] + 0.55, P['td'] + 0.5, 6), (P['waist_z'] - 0.02, P['hw'] + 0.06, P['td'] + 0.06, 10)], dr, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
        C.hem(sk, z0, 0.12)
        hz, h = P['head_c'], P['head']; bon = cloth('bonnet', (150, 70, 46), weave=48, hem_dark=0.8)
        bm = ellipsoid(h * 0.84, h * 0.84, h * 0.95, 40, 24); xform(bm, rotx(90))   # poles on the Y axis -> the front cut follows a ring: clean edge
        kill = [f for f in bm.faces if f.calc_center_median().y < -h * 0.6]
        bmesh.ops.delete(bm, geom=kill, context='FACES'); xform(bm, T(0, 0.0, hz + 0.1))
        C.obj('Bonnet', bm, bon, 'Head', origin=(0, 0, hz), solid=0.12)
        for s in (-1, 1):
            pts = [(s * h * 0.62, -0.05, hz - h * 0.3), (s * h * 0.3, -h * 0.4, hz - h * 0.62), (s * 0.06, -h * 0.5, hz - h * 0.66)]
            C.obj('Bonnet_tie_%d' % (s > 0), tube_bm(pts, 0.04, 6), cloth('bonnet tie', (214, 196, 150), weave=50), 'Head', origin=(0, 0, hz))
    wh = {'RightUpperArm': (-0.25, -0.62, -0.5), 'RightLowerArm': (0.55, -0.3, 0.75), 'RightHand': (0.45, -0.25, 0.85), 'UpperTorso': ((0.12, -0.05, 1), 14), 'Head': ((0.1, 0, 1), 10)}
    out.append(crowd_member('Crowd Whisperer', 'crowd_whisperer', 'classic_r6', dict(), (245, 205, 48), 'crowd_whisperer', 'classic', o3, a3, 'whisper', wh, 0,
                            dict(role='Crowd Six: the whisperer (gossips behind her hand)', body='classic yellow R6 block 4.25 HH', signature='olive', face_style='classic-block: neutral, shocked, laughing', silhouette='big bonnet, long skirt')))
    # 4 GASPER: tiny kid, flat cap
    def o4(P):
        sh = cloth('gasper shirt', earth['rust'], weave=40, hem_dark=0.65); sht = cloth('gasper shorts', (176, 136, 64), weave=36, hem_dark=0.7); sk = skin_mat('gasper skin', (160, 110, 72))
        return dict(UpperTorso=sh, LowerTorso=sht, UpperArm=sh, LowerArm=sk, Hand=sk, UpperLeg=sht, LowerLeg=sk, Foot=leather('gasper shoes', (70, 46, 30)))
    def a4(C, P):
        for side in ('Left', 'Right'):
            C.hem(C.parts[side + 'UpperArm'], C.J[side + 'UpperArm'][1][2] - P['at'] * 0.3, 0.06); C.hem(C.parts[side + 'UpperLeg'], C.J[side + 'UpperLeg'][1][2] - P['lgw'] * 0.25, 0.06)
        add_hair(C, 'hero_medium_tousle', (40, 26, 20))
        hz, h = P['head_c'], P['head']; capm = cloth('flat cap', (96, 86, 74), weave=50, hem_dark=0.7)
        bm = ellipsoid(h * 0.62, h * 0.66, h * 0.22, 32, 12)
        for v in bm.verts:
            if v.co.z < 0: v.co.z *= 0.3
        xform(bm, T(0, -0.02, hz + h * 0.46) @ rotx(-6)); C.obj('Flat_cap', bm, capm, 'Head', origin=(0, 0, hz))
        bm = ellipsoid(h * 0.5, h * 0.3, 0.04, 24, 6); xform(bm, T(0, -h * 0.6, hz + h * 0.4) @ rotx(-10)); C.obj('Cap_peak', bm, capm, 'Head', origin=(0, 0, hz))
    gp = {'LeftUpperArm': (0.75, -0.5, 0.2), 'RightUpperArm': (-0.75, -0.5, 0.2), 'LeftLowerArm': (-0.35, -0.35, 0.87), 'RightLowerArm': (0.35, -0.35, 0.87), 'LeftHand': (-0.3, -0.2, 0.93), 'RightHand': (0.3, -0.2, 0.93), 'Head': (0, 0.12, 1)}
    out.append(crowd_member('Crowd Gasper', 'crowd_gasper', 'mini', dict(), (160, 110, 72), 'crowd_gasper', 'refl', o4, a4, 'gasp', gp, 1,
                            dict(role="Crowd Six: the gasper (the crowd's tiny kid)", body='mini 2.25 HH', signature='rust', face_style='storybook (brown iris): neutral, shocked, laughing', silhouette='flat cap, tiny body')))
    # 5 CHEERER: classic-yellow R6, sleeveless tunic -> blocky yellow arms up
    def o5(P):
        tu = cloth('cheerer tunic', (150, 66, 40), weave=36, hem_dark=0.62); tr = cloth('cheerer trousers', earth['slate'], weave=36, hem_dark=0.7)
        sk = skin_mat('classic yellow', (245, 205, 48), classic=True)
        return dict(UpperTorso=tu, LowerTorso=tr, UpperArm=sk, LowerArm=sk, Hand=sk, UpperLeg=tr, LowerLeg=tr, Foot=leather('cheerer boots', (64, 44, 30)))
    def a5(C, P):
        C.hem(C.parts['UpperTorso'], P['waist_z'] - 0.02, 0.12)
        bm = torus_bm(P['head'] * 0.56, 0.06, 32, 8); bmesh.ops.scale(bm, vec=(1.02, 0.95, 1), verts=bm.verts); xform(bm, T(0, 0, P['head_c'] + P['head'] * 0.22))
        C.obj('Headband', bm, cloth('headband', (236, 234, 226), weave=50), 'Head', origin=(0, 0, P['head_c']))
        belt(C, P, P['waist_z'] + 0.02, leather('cheerer belt', (90, 60, 36)), None, h=0.16, extra=0.04)
    ch = {'LeftUpperArm': (0.62, -0.1, 0.78), 'RightUpperArm': (-0.62, -0.1, 0.78), 'LeftLowerArm': (0.45, -0.05, 0.9), 'RightLowerArm': (-0.45, -0.05, 0.9), 'LeftHand': (0.4, 0, 1), 'RightHand': (-0.4, 0, 1), 'Head': (0, 0.16, 1)}
    out.append(crowd_member('Crowd Cheerer', 'crowd_cheerer', 'classic_r6', dict(), (245, 205, 48), 'crowd_cheerer', 'classic', o5, a5, 'cheer', ch, 2,
                            dict(role='Crowd Six: the cheerer', body='classic yellow R6 block 4.25 HH', signature='rust + slate', face_style='classic-block: neutral, shocked, laughing', silhouette='blocky yellow arms up (sleeveless), headband')))
    # 6 BREAD-DROPPER: armoured townsman (watch), kettle helm, bread mid-fall
    def o6(P):
        mail = metal('mail', (120, 122, 128), rough=0.55, scratch=1.0); tab = cloth('dropper tabard', earth['slate'], weave=36, hem_dark=0.6, thread=(200, 170, 90))
        tr = cloth('dropper trousers', (60, 54, 46), weave=36); b = leather('dropper boots', (56, 42, 32)); sk = skin_mat('dropper skin', (206, 152, 106))
        return dict(UpperTorso=tab, LowerTorso=tab, UpperArm=mail, LowerArm=mail, Hand=sk, UpperLeg=tr, LowerLeg=b, Foot=b, Neck=sk)
    def a6(C, P):
        tab = K._MATS['CV3 dropper tabard']; iron = metal('kettle iron', (128, 132, 140), rough=0.38, scratch=0.7)
        z0 = P['hip_z'] - 0.8
        sk = shell(C, 'Tabard_skirt', [(z0, P['hw'] + 0.2, P['td'] + 0.2, 6), (P['waist_z'] - 0.02, P['hw'] + 0.06, P['td'] + 0.06, 6)], tab, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
        C.hem(sk, z0, 0.12)
        hz, h = P['head_c'], P['head']
        bm = lathe([(h * 0.86, h * 0.2), (h * 0.88, h * 0.24), (h * 0.6, h * 0.3), (h * 0.58, h * 0.6), (h * 0.38, h * 0.86), (0, h * 0.94)], 44); xform(bm, T(0, 0.03, hz))
        C.obj('Kettle_helm', bm, iron, 'Head', origin=(0, 0, hz), solid=0.04)
        belt(C, P, P['waist_z'], leather('dropper belt', (74, 52, 34)), metal('dropper buckle', (190, 150, 70), rough=0.35), h=0.16, extra=0.06)
        # the bread, mid-fall in front of him (not parented to a hand: it's falling)
        crust = plain('bread crust', (198, 134, 62), rough=0.7)
        bm = ellipsoid(0.62, 0.28, 0.28, 24, 12)
        for v in bm.verts:
            if v.co.z > 0: v.co.z *= 1.2
        xform(bm, T(0.3, -1.35, P['knee_z'] + 0.1) @ Matrix.Rotation(R(35), 4, 'Y') @ rotz(20))
        C.obj('Bread', bm, crust, 'Root', origin=(0, 0, 0))
    dp = {'LeftUpperArm': (0.42, -0.72, -0.5), 'RightUpperArm': (-0.42, -0.72, -0.5), 'LeftLowerArm': (0.3, -0.9, -0.05), 'RightLowerArm': (-0.3, -0.9, -0.05), 'LeftHand': (0.25, -0.7, -0.5), 'RightHand': (-0.25, -0.7, -0.5), 'Head': (0, 0.08, 1), 'UpperTorso': (0, 0.02, 1)}
    out.append(crowd_member('Crowd Bread-dropper', 'crowd_dropper', 'heroic_adult', dict(H=5.0 * K.HH, head=0.86, sw=1.7, ww=1.45, hw=1.5, td=0.96, at=0.56, ad=0.58, lgw=0.62, lgd=0.64), (206, 152, 106),
                            'crowd_dropper', 'refl', o6, a6, 'drop', dp, 1,
                            dict(role='Crowd Six: the bread-dropper (town watchman, drops his loaf in shock)', body='armoured 5.0 HH', signature='slate + iron', face_style='storybook (grey iris): neutral, shocked, laughing', silhouette='brimmed kettle helm, tabard, falling bread')))
    return out

# =============================================================================  PHASE 2 (report rows 9-20), Claude 11-27
# Props in hands are modelled where they belong in the character's default pose and moved into rest space (to_rest), so they
# sit exactly in the hand in that pose; other poses carry them rigidly with the hand bone.
def full_spec(C, name, D=None):
    std = ('idle', 'point', 'laugh', 'shocked', 'fists_up', 'arms_crossed')
    base = base_pose_dirs(C, name if name in std else 'idle'); base.update(D or {}); return base

def pose_mats(C, spec):
    """armature-space 4x4 matrix of every bone in a pose (the rig is put back in rest pose afterwards)"""
    rig = C.rig; K.set_pose(rig, K.pose_quats(rig, spec)); bpy.context.view_layer.update()
    M = {pb.name: pb.matrix.copy() for pb in rig.pose.bones}
    K.set_pose(rig, {}); bpy.context.view_layer.update()
    return M

def to_rest(C, spec, bone):
    """matrix that moves geometry modelled in pose space (posed armature space) into the bone's rest space"""
    return C.rig.data.bones[bone].matrix_local @ pose_mats(C, spec)[bone].inverted()

def grip_point(M, C, bone, frac=0.5):
    """posed position along a bone (0 = head, 1 = tail)"""
    L = C.rig.data.bones[bone].length
    return M[bone] @ Vector((0, L * frac, 0))

def solve_twist(C, spec, bone, axis_rest, target):
    """twist (deg) for `bone` in `spec` so that a direction fixed to the bone (axis_rest, rest armature space) points along `target`"""
    rig = C.rig; d = spec[bone]
    if isinstance(d, tuple) and len(d) == 2 and isinstance(d[0], (tuple, list)): d = d[0]
    R0 = rig.data.bones[bone].matrix_local.to_3x3(); a = R0.inverted() @ Vector(axis_rest).normalized(); t = Vector(target).normalized(); best = (-9, 0.0)
    for i in range(72):
        tw = i * 5.0; sp = dict(spec); sp[bone] = (tuple(d), tw)
        Q = K.pose_quats(rig, sp); K.set_pose(rig, Q); bpy.context.view_layer.update()
        v = rig.pose.bones[bone].matrix.to_3x3() @ a
        if v.dot(t) > best[0]: best = (v.dot(t), tw)
    K.set_pose(rig, {}); bpy.context.view_layer.update()
    return best[1]

def ik_arm(C, spec, side, target, pole, hand_dir=None, grip=0.55):
    """two-bone IK: directions for <side>UpperArm / LowerArm / Hand that put the hand's grip point on `target` (pose space),
    elbow bent towards `pole`; hand_dir None = straight wrist"""
    M = pose_mats(C, spec); bones = C.rig.data.bones
    S = M[side + 'UpperArm'].translation.copy(); a = bones[side + 'UpperArm'].length; b = bones[side + 'LowerArm'].length; hl = bones[side + 'Hand'].length * grip
    target = Vector(target); hd = Vector(hand_dir).normalized() if hand_dir else (target - S).normalized()
    for _ in range(3):
        W = target - hd * hl; d = W - S; L = min(d.length, (a + b) * 0.995); dn = d.normalized()
        ca = max(-1.0, min(1.0, (a * a + L * L - b * b) / (2 * a * L))); sa = math.sqrt(1 - ca * ca)
        pv = Vector(pole) - dn * Vector(pole).dot(dn); pv.normalize()
        E = S + (dn * ca + pv * sa) * a; Wn = S + dn * L
        if not hand_dir: hd = (Wn - E).normalized()
    return {side + 'UpperArm': tuple(E - S), side + 'LowerArm': tuple(Wn - E), side + 'Hand': tuple(hd)}

def join_bms(bms):
    out = bmesh.new(); me = bpy.data.meshes.new('tmpj')
    for bm in bms: bm.to_mesh(me); out.from_mesh(me); bm.free()
    bpy.data.meshes.remove(me); return out

def prop_obj(C, label, bm, mat, bone, Mrest, solid=0.0, smooth=True, bevel=0.0):
    """geometry modelled in pose space -> rest space via Mrest -> object parented to bone"""
    xform(bm, Mrest)
    return C.obj(label, bm, mat, bone, origin=C.J[bone][0] if bone in C.J else (0, 0, 0), solid=solid, smooth=smooth, bevel=bevel)

def drive_expr(ob, path, rig, rprop, expr, index=-1):
    fc = ob.driver_add(path, index) if index >= 0 else ob.driver_add(path); d = fc.driver; d.type = 'SCRIPTED'
    v = d.variables.new(); v.name = 'v'; v.targets[0].id = rig; v.targets[0].data_path = '["%s"]' % rprop; d.expression = expr

def switch(objs, rig, prop, value):
    """show objs only while rig[prop] == value (drives hide_viewport / hide_render)"""
    for o in objs:
        for path in ('hide_viewport', 'hide_render'):
            drive_expr(o, path, rig, prop, 'v != %d' % value)

def index_colour(nt, prop, colours):
    """colour socket picked by an integer object property (driven from the rig): colours[0..n]"""
    p = _attr(nt, prop); c = rgba(colours[0])
    for i, col in enumerate(colours[1:], start=1):
        c = _mixc(nt, c, rgba(col), _m(nt, 'COMPARE', p, float(i), 0.5))
    return c

def index_glow_mat(name, prop, colours, strength=9.0, edge=None):
    """emission whose colour follows an integer property (rarity / class); edge = soft transparent rim"""
    m = bpy.data.materials.new('CV3 ' + name); nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]; e = nt.nodes.new('ShaderNodeEmission'); nt.links.new(index_colour(nt, prop, colours), e.inputs['Color'])
    e.inputs['Strength'].default_value = strength
    if edge:
        tr = nt.nodes.new('ShaderNodeBsdfTransparent'); lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = edge
        mx = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(lw.outputs['Facing'], mx.inputs[0]); nt.links.new(e.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs['Surface'])
    else: nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m

def prop_driven(o, rig, prop):
    o[prop] = rig[prop]; drive(o, prop, rig, prop)

def parchment(name='parchment'):
    """parchment with faint ink lines (space for the on-screen text)"""
    if 'CV3 ' + name in K._MATS: return K._MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3; nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    ln = _m(nt, 'GREATER_THAN', _m(nt, 'SINE', _m(nt, 'MULTIPLY', sep.outputs[2], 34.0)), 0.86)
    dash = _m(nt, 'GREATER_THAN', _m(nt, 'SINE', _m(nt, 'ADD', _m(nt, 'MULTIPLY', sep.outputs[0], 23.0), _m(nt, 'MULTIPLY', sep.outputs[2], 9.0))), -0.55)
    ink = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', ln, dash), 0.55)
    col = _mixc(nt, rgba((236, 218, 176)), rgba((206, 182, 132)), nz.outputs['Fac'])
    col = _mixc(nt, col, rgba((92, 66, 48)), ink)
    nt.links.new(col, b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.85
    K._MATS['CV3 ' + name] = m; return m

def stone_colour(nt, base, dark, scale=3.2):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    vc = nt.nodes.new('ShaderNodeTexVoronoi'); vc.inputs['Scale'].default_value = scale; nt.links.new(tc.outputs['Object'], vc.inputs['Vector'])
    sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(vc.outputs['Color'], sp.inputs[0])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 7; nz.inputs['Detail'].default_value = 5; nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    f = _m(nt, 'ADD', _m(nt, 'MULTIPLY', sp.outputs[0], 0.55), _m(nt, 'MULTIPLY', nz.outputs['Fac'], 0.45))
    return _mixc(nt, rgba(base), rgba(dark), f), tc

def stone_mat(name, base, dark, kind='slate', accent=None):
    """Horde stone: blocky voronoi chunks with dark seams; 'ash' adds glowing cracks, 'moss' green growth on top faces, 'frost' icy rime"""
    if 'CV3 ' + name in K._MATS: return K._MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); nt = m.node_tree; N = nt.nodes; L = nt.links; b = N['Principled BSDF']
    col, tc = stone_colour(nt, base, dark)
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 3.2; L.new(tc.outputs['Object'], vo.inputs['Vector'])
    seam = _m(nt, 'LESS_THAN', vo.outputs['Distance'], 0.045)
    col = _mixc(nt, col, rgba(tuple(int(c * 0.4) for c in dark)), _m(nt, 'MULTIPLY', seam, 0.8))
    geo = N.new('ShaderNodeNewGeometry'); gz = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], gz.inputs[0])
    nz2 = N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 4.5; nz2.inputs['Detail'].default_value = 4; L.new(tc.outputs['Object'], nz2.inputs['Vector'])
    rough = 0.82
    if kind == 'moss':
        mm = _m(nt, 'MULTIPLY', _m(nt, 'GREATER_THAN', nz2.outputs['Fac'], 0.5), _m(nt, 'GREATER_THAN', gz.outputs[2], -0.2))
        col = _mixc(nt, col, rgba(accent), mm)
    if kind == 'frost':
        fm = _m(nt, 'MULTIPLY', _m(nt, 'ADD', _m(nt, 'MULTIPLY', gz.outputs[2], 0.6), _m(nt, 'MULTIPLY', nz2.outputs['Fac'], 0.9)), 1.3, clamp=True)
        col = _mixc(nt, col, rgba(accent), _m(nt, 'MULTIPLY', _m(nt, 'GREATER_THAN', fm, 0.55), 0.85)); rough = 0.4
        b.inputs['Coat Weight'].default_value = 0.35
    L.new(col, b.inputs['Base Color']); b.inputs['Roughness'].default_value = rough
    if kind == 'ash':
        cr = _m(nt, 'MULTIPLY', _m(nt, 'LESS_THAN', vo.outputs['Distance'], 0.03), _m(nt, 'GREATER_THAN', nz2.outputs['Fac'], 0.47))
        L.new(_mixc(nt, (0, 0, 0, 1), rgba(accent), cr), b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 7.0
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35
    L.new(_m(nt, 'SUBTRACT', vo.outputs['Distance'], _m(nt, 'MULTIPLY', seam, 0.3)), bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    K._MATS['CV3 ' + name] = m; return m

def harlequin(name, c1, c2, scale=3.0):
    """diamond (harlequin) pattern in object space: two colours, thin dark seams"""
    if 'CV3 ' + name in K._MATS: return K._MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    u = _m(nt, 'ADD', sep.outputs[0], sep.outputs[1])                     # wraps round the body
    a = _m(nt, 'FLOOR', _m(nt, 'MULTIPLY', _m(nt, 'ADD', u, _m(nt, 'MULTIPLY', sep.outputs[2], 0.62)), scale))
    c = _m(nt, 'FLOOR', _m(nt, 'MULTIPLY', _m(nt, 'SUBTRACT', u, _m(nt, 'MULTIPLY', sep.outputs[2], 0.62)), scale))
    chk = _m(nt, 'MODULO', _m(nt, 'ADD', a, c), 2.0)
    chk = _m(nt, 'ABSOLUTE', chk)
    col = _mixc(nt, rgba(c1), rgba(c2), chk)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 0.25
    nt.links.new(col, mul.inputs['A']); nt.links.new(nz.outputs['Color'], mul.inputs['B'])
    nt.links.new(mul.outputs['Result'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.7; b.inputs['Sheen Weight'].default_value = 0.3
    K._MATS['CV3 ' + name] = m; return m

def leaf_ring(C, label, cx, cz, r, n, mat, bone, origin, tilt=0.0, leaf=(0.09, 0.03, 0.2), front_gap=0.0, up=40):
    """laurel: leaves along a ring, pointing up-out (front gap in degrees left open)"""
    bms = []
    for side in (-1, 1):
        for i in range(n):
            t = i / max(1, n - 1); ang = math.radians(90 + side * (front_gap / 2 + (180 - front_gap / 2) * t))   # from the front (-Y) round to the back
            x = r * math.cos(ang); y = -r * math.sin(ang)
            bm = ellipsoid(*leaf, 10, 6)
            outv = Vector((x, y, 0)).normalized()
            q = Vector((0, 0, 1)).rotation_difference((outv * math.sin(math.radians(up)) + Vector((0, 0, math.cos(math.radians(up))))).normalized())
            xform(bm, T(x, y, cz + (0.04 if i % 2 else 0.0)) @ q.to_matrix().to_4x4() @ T(0, 0, leaf[2] * 0.6))
            bms.append(bm)
    bm = join_bms(bms); xform(bm, Matrix.Rotation(R(tilt), 4, 'X'))
    return C.obj(label, bm, mat, bone, origin=origin)

# =============================================================================  17. THE HERALD
def build_herald():
    C = Char('The Herald', 'herald')
    P = body_params('small_hero', H=3.0 * K.HH, sw=1.12, ww=0.98, hw=1.04, td=0.6, at=0.36, ad=0.38, lgw=0.42, lgd=0.44, hand=0.3, idle_out=8)
    skin = (150, 100, 66)
    scarlet = cloth('herald scarlet', (214, 22, 30), weave=40, hem_dark=0.72, thread=(240, 190, 80))   # dE >= 20 from every Cast v2 + v3 colour (was (178,26,38) = Big kid's red, dE 5)
    under = cloth('herald undershirt', (236, 226, 204), weave=46, hem_dark=0.85)
    tights = cloth('herald tights', (44, 40, 48), weave=50, hem_dark=0.75)
    boot = leather('herald boots', (96, 58, 32), wear=0.6)
    gold = metal('herald gold', (236, 182, 62), rough=0.25, scratch=0.3)
    sk = skin_mat('herald skin', skin)
    M = dict(UpperTorso=under, LowerTorso=tights, UpperArm=under, LowerArm=under, Hand=sk, UpperLeg=tights, LowerLeg=tights, Foot=boot, Neck=sk)
    build_body(C, P, M)
    face = dict(set='herald', exprs=['announce', 'trumpet', 'stern', 'shocked', 'nervous'], fs=0.86, voff=0.0, cut=0.685,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink', default=1)
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    hm = hair_mat('herald hair', (30, 22, 18))           # short back-and-sides under the cap (keeps the brows clear)
    bm = ellipsoid(h * 0.55, h * 0.55, h * 0.3, 32, 14)
    kill = [f for f in bm.faces if f.calc_center_median().y < -h * 0.2]; bmesh.ops.delete(bm, geom=kill, context='FACES')
    xform(bm, T(0, 0.03, hz + h * 0.08)); C.obj('Hair', bm, hm, 'Head', origin=(0, 0, hz), solid=0.06)
    # oversized tabard: wider than him, down to the shins, gold border + crown badge
    td = P['td']; zb = 0.36
    shell(C, 'Tabard', [(P['waist_z'] - 0.06, P['ww'] + 0.22, td + 0.2, 5), (P['sh_z'] - 0.08, P['sw'] + 0.08, td + 0.18, 5), (P['sh_z'] + 0.04, P['sw'] - 0.1, td + 0.1, 4)], scarlet, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.05)
    sk_ = shell(C, 'Tabard_skirt', [(zb, P['hw'] + 0.66, td + 0.42, 5), (P['hip_z'], P['hw'] + 0.36, td + 0.28, 5), (P['waist_z'] - 0.02, P['ww'] + 0.24, td + 0.22, 5)], scarlet, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
    C.hem(sk_, zb, 0.0)
    bm = loft([(zb - 0.01, P['hw'] + 0.7, td + 0.46, 5), (zb + 0.07, P['hw'] + 0.69, td + 0.45, 5)], cap=(False, False)); C.obj('Tabard_border', bm, gold, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.03)
    belt(C, P, P['waist_z'] - 0.04, cloth('herald cord', (236, 182, 62), weave=20, hem_dark=0.9, sheen=0.6), gold, h=0.1, extra=0.14)
    # crown badge on the chest
    zc = P['waist_z'] + P['ut'] * 0.55; yf = -(td + 0.2) / 2 - 0.035
    cr = [(-0.26, -0.14), (0.26, -0.14), (0.3, 0.16), (0.15, 0.03), (0.0, 0.2), (-0.15, 0.03), (-0.3, 0.16)]
    bm = bmesh.new(); vs = [bm.verts.new((x, 0, z)) for x, z in cr]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, 0.05, 0), verts=[e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); xform(bm, T(0, yf - 0.02, zc))
    C.obj('Crown_badge', bm, gold, 'UpperTorso', origin=(0, 0, zc), smooth=False, bevel=0.01)
    bm = lathe([(0, 0), (P['head'] * 0.46, 0), (P['head'] * 0.5, 0.1), (P['head'] * 0.42, 0.12)], 32); xform(bm, T(0, 0, P['sh_z'] - 0.02))
    C.obj('Collar', bm, gold, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.02)
    # tall feathered cap (scarlet, gold band) + long white plume
    bm = lathe([(h * 0.57, 0), (h * 0.59, 0.06), (h * 0.55, 0.14), (h * 0.5, 0.42 * h), (h * 0.42, 0.78 * h), (h * 0.3, 1.0 * h), (h * 0.12, 1.1 * h), (0, 1.12 * h)], 40)
    capM = T(0.02, 0.05, hz + h * 0.28) @ roty(-7) @ rotx(-9)
    xform(bm, capM); C.obj('Cap', bm, scarlet, 'Head', origin=(0, 0, hz))
    bm = torus_bm(h * 0.58, 0.045, 36, 8); xform(bm, capM @ T(0, 0, 0.08)); C.obj('Cap_band', bm, gold, 'Head', origin=(0, 0, hz))
    pts = []
    for i in range(18):     # an ostrich plume: rises from the band, arcs back over the cap and droops
        t = i / 17; a = math.pi * 0.95 * t
        pts.append((h * (0.4 + 0.8 * (1 - math.cos(a)) * 0.6), h * (0.12 + 0.2 * t), h * (0.2 + 1.15 * math.sin(a) * (1 - 0.25 * t))))
    bm = tube_bm(pts, [h * (0.05 + 0.2 * math.sin(math.pi * min(1, t * 1.02)) ** 0.7) for t in [i / 17 for i in range(18)]], 12)
    bmesh.ops.scale(bm, vec=(1.0, 0.38, 1.0), verts=bm.verts); xform(bm, capM @ T(0, 0, 0.04))
    C.obj('Plume', bm, hair_mat('plume feather', (244, 240, 232)), 'Head', origin=(0, 0, hz))
    bm = tube_bm([(x_, y_ - 0.02, z_) for x_, y_, z_ in pts[:12]], 0.018, 6); xform(bm, capM @ T(0, 0, 0.04))
    C.obj('Plume_quill', bm, metal('herald gold', (236, 182, 62), rough=0.25, scratch=0.3), 'Head', origin=(0, 0, hz))
    # default pose 'trumpet': the long herald trumpet at his lips, banner hanging; scroll in the other hand down to the floor
    dpose = {'LeftUpperArm': (0.42, -0.1, -0.9), 'LeftLowerArm': (0.12, -0.5, -0.85), 'LeftHand': (0.05, -0.2, -1),
             'UpperTorso': (0, 0.06, 1), 'Head': (0, 0.1, 1)}
    spec = full_spec(C, 'trumpet', dpose); Mp = pose_mats(C, spec); hb = Mp['Head']
    # head bone runs neck -> top; the mouth is ~0.33 head below the head centre, at the face front
    hc = hb @ Vector((0, h / 2, 0)); fwd = (hb.to_3x3() @ Vector((0, 0, 1))).normalized(); up = (hb.to_3x3() @ Vector((0, 1, 0))).normalized()
    mouth = hc + fwd * (h * 0.47) - up * (h * 0.2)
    u = Vector((-0.66, -0.56, 0.5)).normalized()                       # out to his right, forward and up: reads from the front and 3/4
    dpose.update(ik_arm(C, spec, 'Right', mouth + u * 0.8 - Vector((0, 0, 0.07)), (-0.6, 0.4, -1), hand_dir=u))
    spec = full_spec(C, 'trumpet', dpose); Mp = pose_mats(C, spec)
    Lt = 1.7; bell_c = mouth + u * Lt
    tube = tube_bm([mouth + u * 0.04, bell_c - u * 0.18], 0.04, 10)
    bm_bell = lathe([(0.045, 0), (0.06, 0.1), (0.1, 0.22), (0.2, 0.3), (0.22, 0.31)], 28)
    q = Vector((0, 0, 1)).rotation_difference(u); xform(bm_bell, Matrix.Translation(bell_c - u * 0.3) @ q.to_matrix().to_4x4())
    bm_mp = lathe([(0.07, 0), (0.075, 0.03), (0.04, 0.08), (0.04, 0.12)], 16); xform(bm_mp, Matrix.Translation(mouth - u * 0.02) @ q.to_matrix().to_4x4())
    Mr = to_rest(C, spec, 'RightHand')
    trumpet = [prop_obj(C, 'Trumpet', join_bms([tube, bm_bell, bm_mp]), gold, 'RightHand', Mr)]
    # banner hanging under the tube (scarlet, gold fringe, gold crown)
    b0 = mouth + u * 0.75; b1 = mouth + u * 1.3; down = Vector((0, 0, -1)); side = u.cross(down).normalized()
    rows = []
    for r_ in range(7):
        tt = r_ / 6; rows.append([b0.lerp(b1, c_ / 6) + down * (0.62 * tt) + side * 0.03 * math.sin(c_ * 1.3 + tt * 2) * tt for c_ in range(7)])
    trumpet.append(prop_obj(C, 'Trumpet_banner', grid_sheet([[tuple(p) for p in row] for row in rows]), scarlet, 'RightHand', Mr, solid=0.025))
    fr = [b0 + down * 0.64, b1 + down * 0.64]
    bm = tube_bm([tuple(fr[0]), tuple(fr[1])], 0.035, 8); trumpet.append(prop_obj(C, 'Trumpet_fringe', bm, gold, 'RightHand', Mr))
    cc = (b0 + b1) / 2 + down * 0.3 - side * 0.035
    bm = bmesh.new(); vs = [bm.verts.new(tuple(cc + (b1 - b0).normalized() * x * 0.7 + down * -z * 0.7)) for x, z in cr]; bm.faces.new(vs)
    trumpet.append(prop_obj(C, 'Trumpet_badge', bm, gold, 'RightHand', Mr, solid=0.02, smooth=False))
    # scroll: top roller in the left hand, parchment unrolled down to the floor, rolled end + red seal
    gl = grip_point(Mp, C, 'LeftHand', 0.55); Ml = to_rest(C, spec, 'LeftHand')
    wdt = 0.8; x0 = gl.x + 0.06; y0 = gl.y - 0.04
    rows = []
    for r_ in range(9):
        tt = r_ / 8; z = gl.z - 0.06 - (gl.z - 0.2) * tt
        rows.append([(x0 - wdt / 2 + wdt * c_ / 4, y0 - 0.06 * math.sin(tt * 3.1) - 0.02 * (c_ - 2) ** 2 / 4, z) for c_ in range(5)])
    sc = prop_obj(C, 'Scroll_sheet', grid_sheet(rows), parchment(), 'LeftHand', Ml, solid=0.012)
    bm = tube_bm([(x0 - wdt / 2 - 0.08, y0, gl.z), (x0 + wdt / 2 + 0.08, y0, gl.z)], 0.05, 12); prop_obj(C, 'Scroll_roller', bm, wood('scroll wood', (120, 76, 40)), 'LeftHand', Ml)
    bm = tube_bm([(x0 - wdt / 2 - 0.01, y0 - 0.02, 0.24), (x0 + wdt / 2 + 0.01, y0 - 0.02, 0.24)], 0.09, 16); prop_obj(C, 'Scroll_rolled_end', bm, parchment(), 'LeftHand', Ml)
    bm = lathe([(0, 0), (0.09, 0), (0.09, 0.03), (0, 0.03)], 20); xform(bm, T(x0, y0 - 0.03, gl.z - 0.24) @ rotx(90)); prop_obj(C, 'Scroll_seal', bm, plain('wax red', (168, 20, 26), rough=0.3), 'LeftHand', Ml)
    C.height = P['top']
    keepL = {'LeftUpperArm': (0.42, -0.1, -0.9), 'LeftLowerArm': (0.12, -0.5, -0.85), 'LeftHand': (0.05, -0.2, -1)}
    lowR = {'RightUpperArm': (-0.25, -0.05, -1), 'RightLowerArm': (-0.1, -0.7, -0.7), 'RightHand': (-0.1, -0.85, -0.5)}
    over = {'idle': dict(keepL, **lowR), 'shocked': dict(keepL), 'laugh': dict(keepL, **lowR), 'fists_up': dict(keepL),
            'arms_crossed': {'RightUpperArm': (-0.3, -0.05, -1), 'RightLowerArm': (0.75, -0.6, -0.1), 'RightHand': (0.6, -0.7, 0.2)}}
    ex = {'trumpet': dpose,
          'proclaim': {'LeftUpperArm': (0.62, -0.62, 0.1), 'LeftLowerArm': (0.3, -0.5, 0.8), 'LeftHand': (0.1, -0.3, -1),
                       'RightUpperArm': (-0.2, 0.05, -1), 'RightLowerArm': (-0.05, -0.3, -1), 'Head': (0, 0.1, 1), 'UpperTorso': (0, 0.08, 1)}}
    finish(C, 'trumpet', extra_poses=ex, overrides=over, record=dict(role='Town crier: announces the "In this town..." rules, ranks and results (the medieval system announcement)', body='small page 3.0 HH in an oversized tabard',
           signature='scarlet with gold trim', face_style="Town Anime catalogue ('bold' family): announce, trumpet (puffed cheeks), stern, shocked, nervous; blink; talk closed/half/open",
           silhouette='tall feathered cap, long herald trumpet with a hanging banner, scroll unrolled to the floor, tabard to the shins'))
    return C

# =============================================================================  10. THE HORDE (four variants, R6 monsters)
def horn_set(C, kind, hz, h, mat):
    bms = []
    if kind == 'curl':                              # ram curls
        for s in (-1, 1):
            pts = []
            for i in range(22):
                t = i / 21; a = t * 1.8 * math.pi; r = h * 0.46 * (1 - 0.5 * t)
                pts.append((s * (h * 0.5 + h * 0.36 * t), h * 0.12 + r * math.sin(a) - h * 0.08 * t, hz + h * 0.1 + r * math.cos(a)))
            bms.append(tube_bm(pts, [h * 0.2 * (1 - 0.72 * t) for t in [i / 21 for i in range(22)]], 12))
    elif kind == 'spike':                           # two long straight spikes up and out
        for s in (-1, 1):
            bm = lathe([(h * 0.15, 0), (h * 0.12, h * 0.4), (h * 0.06, h * 0.8), (0, h * 1.05)], 14)
            q = Vector((0, 0, 1)).rotation_difference(Vector((s * 0.55, -0.15, 1)).normalized())
            xform(bm, T(s * h * 0.3, -h * 0.05, hz + h * 0.4) @ q.to_matrix().to_4x4()); bms.append(bm)
        bm = lathe([(h * 0.1, 0), (h * 0.05, h * 0.25), (0, h * 0.42)], 12); xform(bm, T(0, -h * 0.15, hz + h * 0.46) @ rotx(-20)); bms.append(bm)
    elif kind == 'antler':                          # branching antlers
        for s in (-1, 1):
            main = [(s * (h * 0.3 + h * 0.5 * t), h * 0.05 + h * 0.15 * t, hz + h * 0.42 + h * 0.9 * t - h * 0.25 * t * t) for t in [i / 10 for i in range(11)]]
            bms.append(tube_bm(main, [h * 0.08 * (1 - 0.6 * i / 10) for i in range(11)], 10))
            for j, (tt, ln) in enumerate([(0.35, 0.4), (0.62, 0.36), (0.85, 0.3)]):
                bx, by, bz = main[int(tt * 10)]
                tine = [(bx + s * h * 0.05 * k, by - h * 0.12 * k, bz + h * ln * k) for k in (0, 0.5, 1.0)]
                bms.append(tube_bm(tine, [h * 0.055, h * 0.04, h * 0.02], 8))
    elif kind == 'broken':                          # one full curved horn, one snapped stub
        pts = [(h * (0.35 + 0.45 * t), h * 0.05, hz + h * 0.35 + h * 0.75 * math.sin(t * 1.9)) for t in [i / 12 for i in range(13)]]
        bms.append(tube_bm(pts, [h * 0.13 * (1 - 0.8 * i / 12) for i in range(13)], 12))
        bm = lathe([(h * 0.14, 0), (h * 0.12, h * 0.22), (h * 0.11, h * 0.3)], 12)
        top = [v for v in bm.verts if v.co.z > h * 0.29]
        for i, v in enumerate(top): v.co.z += h * (0.06 if i % 3 == 0 else (-0.03 if i % 3 == 1 else 0.02))     # jagged break
        xform(bm, T(-h * 0.42, h * 0.05, hz + h * 0.32) @ Matrix.Rotation(R(-40), 4, 'Y')); bms.append(bm)
    return C.obj('Horns', join_bms(bms), mat, 'Head', origin=(0, 0, hz))

HORDE = {   # key: name, stone base / dark, kind, accent, eye set, horn kind, horn colour, height (HH), hunched
    'horde_slate': ('Horde Slate', (96, 102, 112), (58, 62, 70), 'slate', None, 'curl', (204, 192, 164), 4.25, False),
    'horde_ash': ('Horde Ash', (66, 62, 62), (34, 32, 34), 'ash', (255, 80, 30), 'spike', (32, 28, 30), 4.25, False),
    'horde_moss': ('Horde Moss', (104, 98, 80), (62, 60, 50), 'moss', (86, 120, 52), 'antler', (116, 84, 54), 4.0, True),
    'horde_frost': ('Horde Frost', (118, 146, 176), (70, 90, 116), 'frost', (226, 240, 252), 'broken', (196, 232, 250), 4.1, False),
}
def build_horde_one(key):
    name, base, dark, kind, accent, horns, hornc, hh_, hunched = HORDE[key]
    C = Char(name, key)
    P = body_params('classic_r6', H=hh_ * K.HH, head=0.96, neck=0.0, sw=1.65, ww=1.6, hw=1.6, td=0.9, at=0.62, ad=0.66, lgw=0.66, lgd=0.7, hand=0.5, f_leg=0.52 if not hunched else 0.5, idle_out=9)
    st = stone_mat('%s stone' % name.lower(), base, dark, kind, accent)
    stl = stone_mat('%s limb' % name.lower(), tuple(int(c * 0.86) for c in base), dark, kind, accent)
    M = dict(UpperTorso=st, LowerTorso=stl, UpperArm=st, LowerArm=stl, Hand=stl, UpperLeg=stl, LowerLeg=st, Foot=stl)
    build_body(C, P, M, fist=True)
    face = dict(set=key, exprs=['glare', 'roar', 'stunned'], fs=1.0, voff=0.0, cut=0.99, emissive=12.0, rough=0.85, glow=1.0, spec=0.3)
    make_head(C, P, base, face, kind='block', mat=K.face_material(C, base, key, ['glare', 'roar', 'stunned'], P['head'] / 1.2, fs=1.0, voff=0.0, cut=0.99, emissive=12.0, rough=0.85, spec=0.3,
                                                                    base_override=lambda nt: stone_colour(nt, base, dark)[0]))
    hz, h = P['head_c'], P['head']
    horn_set(C, horns, hz, h, plain('%s horn' % name.lower(), hornc, rough=0.35 if kind != 'frost' else 0.15, coat=0.3 if kind == 'frost' else 0.0))
    # stone shoulder chunks + a belt of rope / hide
    for side, s in (('Left', 1), ('Right', -1)):
        bm = cube_bm(P['at'] * 1.25, P['ad'] * 1.2, 0.36); xform(bm, T(s * P['sx'], 0, P['sh_z'] + 0.02) @ roty(-s * 14))
        C.obj(side + 'Shoulder_rock', bm, st, side + 'UpperArm', origin=C.J[side + 'UpperArm'][0], smooth=False, bevel=0.05)
    belt(C, P, P['waist_z'] - 0.08, leather('%s hide' % name.lower(), (70, 52, 40) if kind != 'frost' else (60, 70, 86), wear=0.8), None, h=0.2, extra=0.05)
    C.height = P['top']
    hunch = {'UpperTorso': (0, -0.72, 1), 'Head': (0, -0.12, 1), 'LeftUpperArm': (0.18, -0.35, -1), 'RightUpperArm': (-0.18, -0.35, -1),
             'LeftLowerArm': (0.08, -0.3, -1), 'RightLowerArm': (-0.08, -0.3, -1), 'LeftUpperLeg': (0.12, 0.1, -1), 'RightUpperLeg': (-0.12, 0.1, -1)}
    stomp = {'UpperTorso': (0, -0.1, 1), 'LeftUpperLeg': (0.16, 0, -1), 'LeftLowerLeg': (0.16, 0, -1), 'RightUpperLeg': (-0.16, 0, -1), 'RightLowerLeg': (-0.16, 0, -1),
             'LeftUpperArm': (0.32, -0.12, -1), 'RightUpperArm': (-0.32, -0.12, -1)}
    ex = {'roar': {'Head': (0, 0.25, 1), 'UpperTorso': (0, 0.1, 1), 'LeftUpperArm': (0.85, -0.2, 0.45), 'RightUpperArm': (-0.85, -0.2, 0.45), 'LeftLowerArm': (0.6, -0.3, 0.75), 'RightLowerArm': (-0.6, -0.3, 0.75)},
          'hunch': hunch}
    over = {'idle': hunch if hunched else stomp}
    finish(C, 'idle', extra_poses=ex, overrides=over, record=dict(role='The Horde: reusable small monster (R6 block, stone-shaded, horned); background threat, dungeon floors, invasions',
           body='classic R6 block %.2f HH%s' % (hh_, ', hunched' if hunched else ''), signature={'slate': 'slate stone', 'ash': 'ash with glowing red cracks', 'moss': 'moss on stone', 'frost': 'frost'}[kind],
           face_style='no face: glowing dot eyes + carved angry brows (glare, roar, stunned)', silhouette='blocky body + %s horns' % horns))
    return C

def build_horde():
    return [build_horde_one(k) for k in HORDE]

# =============================================================================  12. THE OLD LEGEND
def chipped_blade(L, W, T_, seed=4):
    """flat blade outline with notches knocked out of both edges, tip up (+Z), extruded in Y"""
    rnd = random.Random(seed); right = []; left = []
    n = 16
    for i in range(n + 1):
        z = L * 0.86 * i / n; w = W / 2 * (1 - 0.12 * i / n)
        right.append((w, z)); left.append((-w, z))
        if 0 < i < n and rnd.random() < 0.32: right.append((w - rnd.uniform(0.05, 0.12), z + L * 0.86 / n * 0.45))
        if 0 < i < n and rnd.random() < 0.3: left.append((-w + rnd.uniform(0.05, 0.12), z + L * 0.86 / n * 0.45))
    pts = right + [(0, L)] + left[::-1]
    bm = bmesh.new(); vs = [bm.verts.new((x, -T_ / 2, z)) for x, z in pts]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, T_, 0), verts=[e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def great_sword_parts(L=5.4, W=0.62):
    """chipped giant sword, built along +Z with the crossguard at z=0; returns [(bm, matkey)]"""
    parts = [(chipped_blade(L, W, 0.09), 'blade')]
    parts.append((loft([(0.05, W * 0.18, 0.11, 4), (L * 0.7, W * 0.12, 0.11, 4)]), 'fuller'))
    parts.append((loft([(-0.09, W * 2.1, 0.22, 6), (0.09, W * 2.1, 0.22, 6)], round_ends=0.05), 'guard'))
    parts.append((loft([(-1.0, 0.2, 0.2, 4), (-0.08, 0.18, 0.18, 4)]), 'grip'))
    bm = ellipsoid(0.17, 0.17, 0.17, 16, 8); xform(bm, T(0, 0, -1.1)); parts.append((bm, 'pommel'))
    return parts

def build_old_legend():
    C = Char('The Old Legend', 'old_legend')
    P = body_params('heroic_adult', H=5.25 * K.HH, head=0.96, sw=1.86, ww=1.45, hw=1.45, td=0.95, at=0.56, ad=0.58, lgw=0.6, lgd=0.62, idle_out=8)
    skin = (96, 62, 42)
    coat = cloth('legend coat', (104, 106, 110), weave=36, hem_dark=0.65, thread=(170, 170, 176))
    shirt = cloth('legend shirt', (70, 66, 64), weave=44, hem_dark=0.7)
    trous = cloth('legend trousers', (58, 54, 52), weave=40, hem_dark=0.7)
    boot = leather('legend boots', (60, 42, 30), wear=0.85)
    cloak_m = cloth('legend cloak', (122, 48, 56), weave=30, hem_dark=0.6, thread=(160, 110, 100), sheen=0.3)
    steel = metal('legend steel', (128, 132, 138), rough=0.42, scratch=0.95)
    belt_l = leather('legend belt', (78, 52, 34), wear=0.9)
    sk = skin_mat('legend skin', skin); white = hair_mat('legend white', (232, 230, 226))
    M = dict(UpperTorso=coat, LowerTorso=coat, UpperArm=coat, LowerArm=sk, Hand=sk, UpperLeg=trous, LowerLeg=boot, Foot=boot, Neck=sk)
    build_body(C, P, M)
    for side in ('Left', 'Right'): C.hem(C.parts[side + 'UpperArm'], C.J[side + 'UpperArm'][1][2] - P['at'] * 0.3, 0.1)
    face = dict(set='old_legend', exprs=['sly', 'fierce', 'kind', 'laughing', 'shocked', 'weary'], fs=0.9, voff=0.0, cut=0.6,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']; head = C.head
    bpy.context.view_layer.update(); from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get(); bvh = BVHTree.FromObject(head.evaluated_get(dg), dg)
    hc_local = Vector((0, 0, 0))                       # head object origin = head centre
    def surf(d, off=0.02):
        loc, nrm, idx, dist = bvh.ray_cast(hc_local + Vector(d).normalized() * 2.0, -Vector(d).normalized())
        return (head.matrix_world @ loc) + Vector(d).normalized() * off if loc else Vector((0, 0, hz))
    # eye patch over his right eye (image-left eye of the storybook decal) + strap up over the crown
    span = h * 0.9; ex_, ez_ = (0.342 - 0.5) * span, (0.553 - 0.5) * span
    pc = surf((ex_, -0.48, ez_), 0.0)
    bm = ellipsoid(0.15, 0.05, 0.12, 20, 10); xform(bm, Matrix.Translation(pc + Vector((0, -0.02, 0))))
    C.obj('Eye_patch', bm, leather('patch leather', (22, 18, 16), wear=0.2), 'Head', origin=(0, 0, hz))
    p = Vector((ex_, -0.48, ez_)).normalized(); q_ = Vector((0.18, 0.55, 0.82)).normalized()
    pts = []
    for i in range(25):
        t = i / 24 * 2.6; v = (p * math.cos(t) + (q_ - p * p.dot(q_)).normalized() * math.sin(t)); pts.append(tuple(surf(v, 0.025)))
    C.obj('Patch_strap', tube_bm(pts, 0.03, 6), leather('patch leather', (22, 18, 16), wear=0.2), 'Head', origin=(0, 0, hz))
    # white fringe (bald on top) + full white beard below the mouth
    bm = ellipsoid(h * 0.56, h * 0.56, h * 0.3, 32, 14)
    kill = [f for f in bm.faces if f.calc_center_median().y < -h * 0.12]; bmesh.ops.delete(bm, geom=kill, context='FACES')
    xform(bm, T(0, 0.02, hz - h * 0.02)); C.obj('Hair_fringe', bm, white, 'Head', origin=(0, 0, hz), solid=0.06)
    bm = ellipsoid(h * 0.44, h * 0.34, h * 0.52, 32, 16)          # full white beard from just under the mouth to the chest
    for v in bm.verts:
        if v.co.z < 0: v.co.y -= (v.co.z / (h * 0.58)) ** 2 * h * 0.12; v.co.x *= 1 - 0.5 * (v.co.z / (h * 0.58)) ** 2
    kill = [f for f in bm.faces if f.calc_center_median().z > h * 0.3 and f.calc_center_median().y < -h * 0.05]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    xform(bm, T(0, -h * 0.2, hz - h * 0.56)); C.obj('Beard', bm, white, 'Head', origin=(0, 0, hz), solid=0.05)
    # long weathered coat (trapezoid), one worn steel pauldron, bracers, belt, faded burgundy cloak
    z0 = P['knee_z'] - 0.55
    ck = shell(C, 'Coat_skirt', [(z0, P['hw'] + 0.62, P['td'] + 0.42, 5), (P['hip_z'], P['hw'] + 0.24, P['td'] + 0.2, 5), (P['waist_z'] - 0.02, P['ww'] + 0.12, P['td'] + 0.12, 5)], coat, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
    C.hem(ck, z0, 0.14); C.seam(ck, 0.0)
    belt(C, P, P['waist_z'] - 0.03, belt_l, steel, h=0.24, extra=0.14)
    pauldron(C, 'Left', 1, P['sx'], P['sh_z'] + 0.02, 0.5, layers=2, mat=steel, rim=belt_l, tilt=18)
    for side, s in (('Left', 1), ('Right', -1)):
        (l0, l1, _) = C.J[side + 'LowerArm']
        shell(C, side + 'Bracer', [(l1[2] + 0.04, P['at'] * 1.12, P['ad'] * 1.12, 5, l0[0], 0), (l0[2] - 0.14, P['at'] * 1.1, P['ad'] * 1.1, 5, l0[0], 0)], belt_l, side + 'LowerArm', l0, round_ends=0.04)
    cp = cape(C, 'Cloak', 1.0, 1.35, P['sh_z'] + 0.02, P['knee_z'] - 0.2, P['td'] / 2 + 0.08, cloak_m, torn=0.3, flare_back=0.35, curve=0.3, cols=14, rows=12)
    C.hem(cp, P['knee_z'] - 0.2, 0.0)
    bm = lathe([(P['head'] * 0.6, P['sh_z'] - 0.1), (P['head'] * 0.62, P['sh_z'] + 0.12)], 32); C.obj('Cloak_collar', bm, cloak_m, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.06)
    # the chipped giant sword: planted point-down at his right side (rig 'sword' 0) or in his right hand (rig 'sword' 1)
    rig = C.rig; rig['sword'] = 0
    try: rig.id_properties_ui('sword').update(min=0, max=1, description='0 planted beside him (lean on it), 1 in his right hand')
    except Exception: pass
    mats = dict(blade=metal('legend blade', (150, 156, 164), rough=0.36, scratch=1.0), fuller=metal('legend fuller', (92, 96, 104), rough=0.5), guard=steel,
                grip=leather('legend grip', (66, 40, 30)), pommel=steel)
    # planted: point in the ground at his front-right, blade 5.4 (the sword is taller than he is, hunched or upright); his hand IK'd onto the grip
    BL = 5.4; sxp, syp, tip = -(P['sx'] + 0.62), -0.62, -0.12; guard_z = tip + BL; target = Vector((sxp, syp, guard_z + 0.42))
    hunch = {'LowerTorso': (0, -0.14, 1), 'UpperTorso': (0, -0.62, 1), 'Head': (0, 0.12, 1),
             'LeftUpperLeg': (0.06, -0.34, -1), 'LeftLowerLeg': (0.06, 0.16, -1), 'RightUpperLeg': (-0.07, -0.24, -1), 'RightLowerLeg': (-0.07, 0.18, -1),
             'LeftFoot': (0.04, -1, -0.25), 'RightFoot': (-0.04, -1, -0.25)}
    dpose = dict(hunch); spec = full_spec(C, 'hunched', dpose)
    dpose.update(ik_arm(C, spec, 'Right', target, (-0.2, 0.7, -0.6), hand_dir=(0.55, -0.83, 0.0)))
    Mk = pose_mats(C, spec); kneeL = Mk['LeftLowerLeg'].translation
    dpose.update(ik_arm(C, spec, 'Left', kneeL + Vector((0.0, -0.32, 0.38)), (1, 0.6, 0.2), hand_dir=(0, -0.4, -1)))
    spec = full_spec(C, 'hunched', dpose)
    planted = []
    for bm, mk in great_sword_parts(BL):
        xform(bm, T(sxp, syp, guard_z) @ rotx(180))
        planted.append(C.obj('Sword_planted_' + mk, bm, mats[mk], 'Root', origin=(0, 0, 0), smooth=(mk != 'blade'), bevel=0.012 if mk == 'blade' else 0.0))
    Mr = to_rest(C, spec, 'RightHand'); inhand = []
    for bm, mk in great_sword_parts(BL):
        xform(bm, T(sxp, syp, guard_z) @ rotx(180)); inhand.append(prop_obj(C, 'Sword_hand_' + mk, bm, mats[mk], 'RightHand', Mr, smooth=(mk != 'blade'), bevel=0.012 if mk == 'blade' else 0.0))
    switch(planted, rig, 'sword', 0); switch(inhand, rig, 'sword', 1)
    C.height = P['top']
    ex = {'hunched': dpose,
          'stand_tall': {'UpperTorso': (0, 0.05, 1), 'Head': (0, 0.1, 1), 'LeftUpperArm': (0.4, -0.1, -0.9), 'LeftLowerArm': (-0.4, -0.5, -0.7), 'LeftHand': (-0.5, -0.4, -0.6),
                         'LeftUpperLeg': (0.1, 0, -1), 'LeftLowerLeg': (0.1, 0, -1), 'RightUpperLeg': (-0.1, 0, -1), 'RightLowerLeg': (-0.1, 0, -1)},
          'raise_sword': {'RightUpperArm': (-0.3, -0.25, 1), 'RightLowerArm': (-0.1, -0.15, 1), 'RightHand': (0, -1, 0.15), 'LeftUpperArm': (0.45, -0.3, -0.85), 'LeftLowerArm': (0.2, -0.7, -0.4), 'Head': (0, -0.02, 1),
                          'LeftUpperLeg': (0.12, -0.15, -1), 'LeftLowerLeg': (0.12, 0.05, -1), 'RightUpperLeg': (-0.12, 0.15, -1), 'RightLowerLeg': (-0.12, 0.1, -1)}}
    st = full_spec(C, 'stand_tall', ex['stand_tall']); ex['stand_tall'].update(ik_arm(C, st, 'Right', target, (-0.6, 0.5, -0.6), hand_dir=(0.55, -0.83, 0.0)))   # hand stays on the planted sword
    tip_rest = Mr.to_3x3() @ Vector((0, 0, -1))                        # blade direction (tip) in rest space
    sp_r = full_spec(C, 'raise_sword', ex['raise_sword']); tw = solve_twist(C, sp_r, 'RightHand', tip_rest, (0, -0.15, 1))
    ex['raise_sword']['RightHand'] = (ex['raise_sword']['RightHand'], tw)
    finish(C, 'hunched', extra_poses=ex, record=dict(role='Forgotten champion and a mentor who fights: hunched until he stands; the "my grandfather was the legend" reveal',
           body='elder to heroic: 4.25 HH hunched, 5.25 HH upright', signature='weathered steel grey + faded burgundy cloak',
           face_style='storybook line-art (grey iris, elder lines): sly, fierce, kind, laughing, shocked, weary; blink; talk closed/half/open',
           silhouette="white beard, eye patch, chipped giant sword taller than he is (rig 'sword': 0 planted, 1 in hand)"))
    rig['pose_props'] = json.dumps({'_default': {'sword': 0}, 'raise_sword': {'sword': 1}})     # set_pose() in cast_v3_tools applies these
    return C

# =============================================================================  9. THE GOLDEN SISTER
def trophy_bms(hgt=1.0):
    k = hgt
    cup = lathe([(0.0, 0.0), (0.26 * k, 0.0), (0.26 * k, 0.06 * k), (0.12 * k, 0.12 * k), (0.06 * k, 0.2 * k), (0.05 * k, 0.42 * k), (0.12 * k, 0.5 * k), (0.32 * k, 0.62 * k),
                 (0.36 * k, 0.86 * k), (0.38 * k, 0.94 * k), (0.34 * k, 0.94 * k), (0.31 * k, 0.88 * k), (0.0, 0.84 * k)], 36)
    hs = []
    for s in (-1, 1):
        pts = [(s * 0.3 * k, 0, 0.84 * k), (s * 0.5 * k, 0, 0.84 * k), (s * 0.52 * k, 0, 0.68 * k), (s * 0.32 * k, 0, 0.62 * k)]
        hs.append(tube_bm(pts, 0.035 * k, 8))
    return join_bms([cup] + hs)

def build_golden_sister():
    C = Char('The Golden Sister', 'golden_sister')
    P = body_params('heroic_teen', H=4.5 * K.HH, head=0.96, sw=1.44, ww=1.1, hw=1.2, td=0.72, at=0.44, ad=0.46, lgw=0.5, lgd=0.52, idle_out=8)
    skin = (238, 196, 156)                                   # = Hero kid
    rose = cloth('golden rose', (138, 22, 64), weave=40, hem_dark=0.7, thread=(246, 200, 96), sheen=0.4)
    sash = cloth('family stripe', (206, 76, 48), weave=36, hem_dark=0.8, thread=(255, 200, 90))      # = Hero kid shirt colour
    leg_ = cloth('golden leggings', (52, 58, 82), weave=46, hem_dark=0.7)                              # = Hero kid trousers
    boot = leather('golden boots', (110, 68, 38), wear=0.5)                                           # = Hero kid belt leather
    gold = metal('laurel gold', (240, 186, 66), rough=0.22, scratch=0.25)
    sk = skin_mat('golden skin', skin)
    M = dict(UpperTorso=rose, LowerTorso=rose, UpperArm=rose, LowerArm=sk, Hand=sk, UpperLeg=leg_, LowerLeg=boot, Foot=boot, Neck=sk)
    build_body(C, P, M)
    for side in ('Left', 'Right'): C.hem(C.parts[side + 'UpperArm'], C.J[side + 'UpperArm'][1][2] - P['at'] * 0.3, 0.1)
    face = dict(set='golden_sister', exprs=['proud', 'kind', 'shocked', 'scared', 'determined', 'humbled'], fs=0.86, voff=0.0, cut=0.685,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    add_hair(C, 'hero_crop', (74, 48, 32), scale=0.93, offset=(0, 0.0, 0.02))                  # the hero's hair outline
    # laurel crown (gold leaves round the head, open at the front)
    leaf_ring(C, 'Laurel', 0, hz + h * 0.4, h * 0.56, 9, gold, 'Head', (0, 0, hz), tilt=-6, leaf=(0.09, 0.035, 0.24), front_gap=34, up=30)
    bm = torus_bm(h * 0.56, 0.035, 40, 8); xform(bm, Matrix.Rotation(R(-6), 4, 'X') @ T(0, 0, hz + h * 0.4)); C.obj('Laurel_band', bm, gold, 'Head', origin=(0, 0, hz))
    # tunic dress to the knee with gold hem, the family stripe (sash), belt
    z0 = P['knee_z'] - 0.1
    sk_ = shell(C, 'Dress_skirt', [(z0, P['hw'] + 0.46, P['td'] + 0.34, 4), (P['hip_z'], P['hw'] + 0.14, P['td'] + 0.12, 4), (P['waist_z'] - 0.02, P['ww'] + 0.08, P['td'] + 0.08, 4)], rose, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
    C.hem(sk_, z0, 0.12)
    bm = loft([(z0 - 0.01, P['hw'] + 0.5, P['td'] + 0.38, 4), (z0 + 0.06, P['hw'] + 0.49, P['td'] + 0.37, 4)], cap=(False, False)); C.obj('Dress_trim', bm, gold, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.03)
    td = P['td']
    pts = [(-0.56, -td / 2 - 0.04, P['sh_z'] - 0.02), (-0.1, -td / 2 - 0.06, P['waist_z'] + P['ut'] * 0.55), (0.48, -td / 2 - 0.04, P['waist_z'] + 0.06)]
    bm = tube_bm(pts, 0.1, 8); bmesh.ops.scale(bm, vec=(1, 0.35, 1), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, -td * 0.33, 0), verts=bm.verts)
    C.obj('Family_stripe', bm, sash, 'UpperTorso', origin=(0, 0, P['waist_z']))
    pts_b = [(0.56, td / 2 + 0.04, P['sh_z'] - 0.02), (0.0, td / 2 + 0.06, P['waist_z'] + P['ut'] * 0.55), (-0.48, td / 2 + 0.04, P['waist_z'] + 0.06)]
    bm = tube_bm(pts_b, 0.1, 8); bmesh.ops.scale(bm, vec=(1, 0.35, 1), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, td * 0.33, 0), verts=bm.verts)
    C.obj('Family_stripe_back', bm, sash, 'UpperTorso', origin=(0, 0, P['waist_z']))
    belt(C, P, P['waist_z'] - 0.02, leather('golden belt', (110, 68, 38)), gold, h=0.14, extra=0.1)
    bm = lathe([(P['head'] * 0.44, P['sh_z'] - 0.04), (P['head'] * 0.42, P['sh_z'] + 0.08)], 32); C.obj('Collar_trim', bm, gold, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.02)
    # the trophy, always in hand (held up beside her in the default pose)
    dpose = {'RightUpperArm': (-0.55, -0.1, -0.83), 'RightLowerArm': (-0.25, -0.4, 0.88), 'RightHand': (0.35, -0.9, 0.2),
             'LeftUpperArm': (0.62, 0.2, -0.76), 'LeftLowerArm': (-0.6, -0.05, -0.8), 'LeftHand': (-0.55, 0, -0.85), 'Head': (0, 0.05, 1)}
    spec = full_spec(C, 'trophy', dpose); Mp = pose_mats(C, spec); g = grip_point(Mp, C, 'RightHand', 0.55)
    bm = trophy_bms(1.55); xform(bm, T(g.x, g.y, g.z - 0.42))
    prop_obj(C, 'Trophy', bm, gold, 'RightHand', to_rest(C, spec, 'RightHand'))
    bm = lathe([(0, 0), (0.42, 0), (0.42, 0.2), (0, 0.2)], 6); xform(bm, T(g.x, g.y, g.z - 0.62))
    prop_obj(C, 'Trophy_base', bm, wood('trophy base', (70, 40, 26)), 'RightHand', to_rest(C, spec, 'RightHand'), smooth=False)
    C.height = P['top'] + h * 0.12
    ex = {'trophy': dpose,
          'trophy_up': {'RightUpperArm': (-0.3, -0.1, 1), 'RightLowerArm': (-0.1, -0.15, 1), 'RightHand': (0.4, -0.9, 0.1), 'LeftUpperArm': (0.4, -0.2, 0.9), 'LeftLowerArm': (0.1, -0.2, 1), 'Head': (0, 0.15, 1)}}
    C.height = P['top']
    # keep the trophy upright in the other poses: carried in front in idle, hand twisted so the cup points up
    cup_rest = to_rest(C, spec, 'RightHand').to_3x3() @ Vector((0, 0, 1)); over = {'idle': {'RightUpperArm': (-0.18, -0.12, -1), 'RightLowerArm': (0.12, -1, -0.05), 'RightHand': (0.2, -1, 0.05)}}
    for pn in ('idle', 'point', 'laugh', 'shocked', 'fists_up', 'trophy_up'):
        D = over.setdefault(pn, {}) if pn != 'trophy_up' else ex['trophy_up']; spn = full_spec(C, pn, D); hd0 = spn['RightHand']
        D['RightHand'] = (tuple(hd0[0]) if isinstance(hd0[0], (tuple, list)) else tuple(hd0), solve_twist(C, spn, 'RightHand', cup_rest, (0, 0, 1)))
    finish(C, 'trophy', extra_poses=ex, overrides=over, record=dict(role='The favoured older sister: the town praises her while the hero is "the unlucky one"; out-shone or rescued, never cruel',
           body='Rthro-normal teen 4.5 HH (same head, hair, face style and skin as the Hero kid)', signature="deep rose + gold laurel + the hero's family stripe (burnt orange)",
           face_style="Town Anime catalogue, the hero's own family (starry / sweet): proud, kind, shocked, scared, determined, humbled; blink; talk closed/half/open",
           silhouette="the hero's crop hair, taller, gold laurel crown, a trophy always in hand"))
    return C

# =============================================================================  13. THE ROLL MERCHANT
RARITY = [(200, 200, 210), (90, 230, 110), (70, 150, 255), (190, 90, 255), (255, 190, 50)]
def build_roll_merchant():
    C = Char('The Roll Merchant', 'roll_merchant')
    P = body_params('round_big', H=3.75 * K.HH, sw=2.05, arm_gap=0.0, idle_out=13)
    skin = (196, 150, 108)
    plum = cloth('merchant plum', (96, 36, 86), weave=36, hem_dark=0.66, thread=(236, 190, 90), sheen=0.5)
    shirt = cloth('merchant shirt', (214, 196, 160), weave=46, hem_dark=0.8)
    trous = cloth('merchant trousers', (70, 56, 48), weave=36, hem_dark=0.7)
    boot = leather('merchant boots', (88, 56, 34), wear=0.6)
    felt = cloth('merchant hat', (58, 34, 52), weave=60, hem_dark=0.7, sheen=0.3)
    gold = metal('merchant gold', (226, 176, 70), rough=0.28, scratch=0.4)
    sk = skin_mat('merchant skin', skin)
    M = dict(UpperTorso=plum, LowerTorso=plum, UpperArm=plum, LowerArm=plum, Hand=sk, UpperLeg=trous, LowerLeg=boot, Foot=boot)
    build_body(C, P, M, barrel=True)
    face = dict(set='roll_merchant', exprs=['knowing_grin', 'welcome', 'jaw_drop', 'curious', 'nervous', 'delighted'], fs=0.92, voff=0.08, cut=0.6,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    bm = ellipsoid(h * 0.54, h * 0.54, h * 0.2, 32, 14)              # short dark hair at the back under the hat
    kill = [f for f in bm.faces if f.calc_center_median().y < 0.0]; bmesh.ops.delete(bm, geom=kill, context='FACES')
    xform(bm, T(0, 0.03, hz + h * 0.18)); C.obj('Hair', bm, hair_mat('merchant hair', (46, 34, 30)), 'Head', origin=(0, 0, hz), solid=0.06)
    # wide-brim hat with a gold band + a little coin
    bm = lathe([(0, 0), (h * 0.9, 0.0), (h * 0.93, 0.05), (h * 0.62, 0.08), (h * 0.56, 0.42 * h), (h * 0.44, 0.58 * h), (0, 0.62 * h)], 48)
    hM = T(0, 0.12, hz + h * 0.34) @ rotx(-16); xform(bm, hM); C.obj('Hat', bm, felt, 'Head', origin=(0, 0, hz), solid=0.03)
    bm = loft([(0.1, h * 1.14, h * 1.14, 2), (0.2, h * 1.12, h * 1.12, 2)], cap=(False, False)); xform(bm, hM); C.obj('Hat_band', bm, gold, 'Head', origin=(0, 0, hz), solid=0.02)
    # long plum coat skirt, gold buttons, sash with coin pouches
    z0 = P['knee_z'] - 0.1
    ck = shell(C, 'Coat_skirt', [(z0, P['hw'] + 0.36, P['td'] + 0.3, 3), (P['hip_z'] - 0.1, P['hw'] * 0.92 + 0.16, P['td'] * 0.92 + 0.14, 3)], plum, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, False))
    C.hem(ck, z0, 0.12)
    for i in range(4):
        z = P['waist_z'] + 0.1 + i * 0.32; bm = ellipsoid(0.07, 0.04, 0.07, 12, 6)
        r_ = P['td'] * (0.5 if i else 0.52); xform(bm, T(0, -r_ - 0.05, z)); C.obj('Button_%d' % i, bm, gold, 'UpperTorso', origin=(0, 0, P['waist_z']))
    sashm = cloth('merchant sash', (214, 160, 52), weave=30, hem_dark=0.8)
    bm = loft([(P['hip_z'] + 0.12, P['ww'] * 0.9 + 0.12, P['td'] * 0.95 + 0.12, 3), (P['hip_z'] + 0.36, P['ww'] * 0.96 + 0.12, P['td'] * 0.98 + 0.12, 3)], cap=(False, False))
    C.obj('Sash', bm, sashm, 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.04)
    for s in (-1, 1):
        bm = ellipsoid(0.17, 0.13, 0.2, 14, 8); xform(bm, T(s * P['ww'] * 0.4, -P['td'] * 0.42, P['hip_z'] + 0.02)); C.obj('Pouch_%d' % (s > 0), bm, leather('merchant pouch', (120, 80, 44)), 'UpperTorso', origin=(0, 0, P['waist_z']))
    # the pack of wares on a wooden A-frame, towering over him, topped by the glowing mystery chest
    by = P['td'] / 2 + 0.3; frame = wood('pack frame', (126, 86, 50)); zt = P['top'] + 1.3
    for s in (-1, 1):
        C.obj('Frame_pole_%d' % (s > 0), tube_bm([(s * 0.95, by, P['waist_z'] - 0.6), (s * 0.75, by + 0.25, zt)], 0.07, 8), frame, 'UpperTorso', origin=(0, 0, P['waist_z']))
    for z in (P['waist_z'], P['sh_z'] + 0.2, zt - 0.25):
        C.obj('Frame_bar_%d' % int(z * 10), tube_bm([(-1.0, by + 0.05, z), (1.0, by + 0.05, z)], 0.055, 8), frame, 'UpperTorso', origin=(0, 0, P['waist_z']))
    canvas = cloth('wares canvas', (150, 128, 90), weave=24, hem_dark=0.7)
    bz0, bz1 = P['waist_z'] - 0.5, zt - 0.1; byc = by + 0.62
    shell(C, 'Wares_bundle', [(bz0, 2.1, 1.25, 3, 0, byc), (P['sh_z'] + 0.1, 2.5, 1.45, 3, 0, byc + 0.05), (bz1 - 0.35, 2.3, 1.35, 3, 0, byc + 0.05), (bz1, 1.7, 1.1, 3, 0, byc)], canvas, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.3)
    for z in (P['waist_z'] + 0.2, P['sh_z'] + 0.6):        # rope lashings
        bm = loft([(z - 0.05, 2.56, 1.5, 3, 0, byc + 0.05), (z + 0.05, 2.56, 1.5, 3, 0, byc + 0.05)], cap=(False, False)); C.obj('Lashing_%d' % int(z * 10), bm, cloth('rope', (190, 160, 100), weave=12), 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.04)
    # wares poking out: a long rolled rug across the top, copper pots hanging at the sides, a sword hilt, scroll tubes, a lantern
    rug = cloth('rug', (150, 50, 44), weave=18, hem_dark=0.6, thread=(230, 190, 90))
    bm = loft([(-1.7, 0.34, 0.34, 2), (1.7, 0.34, 0.34, 2)], round_ends=0.06); xform(bm, T(0, byc + 0.1, bz1 - 0.55) @ roty(90) @ rotx(4)); C.obj('Rolled_rug', bm, rug, 'UpperTorso', origin=(0, 0, P['waist_z']))
    pot = metal('pot copper', (184, 104, 60), rough=0.35, scratch=0.6)
    for i, (x, z, r_) in enumerate([(1.42, P['waist_z'] + 0.25, 0.34), (-1.42, P['waist_z'] + 0.55, 0.3), (1.38, P['sh_z'] + 0.55, 0.24)]):
        bm = lathe([(0, 0), (r_ * 0.7, 0), (r_, r_ * 0.6), (r_ * 0.8, r_ * 1.2), (r_ * 0.55, r_ * 1.35), (r_ * 0.6, r_ * 1.45)], 20); xform(bm, T(x, byc, z - r_) @ rotz(20 * i))
        C.obj('Pot_%d' % i, bm, pot, 'UpperTorso', origin=(0, 0, P['waist_z']))
    for i, (bl, gd) in enumerate(((0.06, 0.06), (0.42, 0.09))):
        bm = loft([(0, bl, 0.05, 4), (1.2, bl * 0.8, 0.04, 4)]) if i == 0 else loft([(-0.04, gd * 4.6, 0.08, 6), (0.04, gd * 4.6, 0.08, 6)])
        xform(bm, T(-0.75, byc - 0.1, bz1 - 0.3) @ roty(-24)); C.obj('Ware_sword_%s' % ('blade' if i == 0 else 'guard'), bm, metal('ware steel', (180, 186, 196), rough=0.3) if i == 0 else gold, 'UpperTorso', origin=(0, 0, P['waist_z']))
    bm = loft([(-0.04, 0.06, 0.06, 4), (-0.4, 0.07, 0.07, 4)]); xform(bm, T(-0.75, byc - 0.1, bz1 - 0.3) @ roty(-24)); C.obj('Ware_sword_grip', bm, leather('ware grip', (80, 50, 30)), 'UpperTorso', origin=(0, 0, P['waist_z']))
    for i, x in enumerate((0.55, 0.8)):
        bm = loft([(0, 0.15, 0.15, 2), (1.0, 0.15, 0.15, 2)], round_ends=0.03); xform(bm, T(x, byc + 0.25, bz1 - 0.45) @ roty(12 + 12 * i))
        C.obj('Scroll_tube_%d' % i, bm, leather('tube leather', (96, 60, 34)), 'UpperTorso', origin=(0, 0, P['waist_z']))
    bm = lathe([(0, 0), (0.16, 0), (0.17, 0.06), (0.13, 0.09), (0.13, 0.34), (0.17, 0.37), (0.08, 0.47), (0, 0.5)], 16); xform(bm, T(-1.35, byc - 0.3, P['waist_z'] - 0.35))
    C.obj('Lantern', bm, metal('lantern brass', (196, 150, 70), rough=0.35), 'UpperTorso', origin=(0, 0, P['waist_z']))
    # mystery chest on top: wood + gold bands, lid ajar, light in the gap + sparkles (rig 'rarity')
    rig = C.rig; rig['rarity'] = 3
    try: rig.id_properties_ui('rarity').update(min=0, max=4, description='chest glow: 0 common, 1 uncommon, 2 rare, 3 epic, 4 legendary')
    except Exception: pass
    cw, cd, ch = 1.55, 1.0, 0.72; cz = bz1 - 0.05; cy = byc
    chest_w = wood('chest wood', (96, 56, 34))
    box = cube_bm(cw, cd, ch); xform(box, T(0, cy, cz + ch / 2)); C.obj('Chest_box', box, chest_w, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False, bevel=0.03)
    lid = cube_bm(cw * 1.02, cd * 1.02, 0.26); xform(lid, T(0, cy + cd / 2, cz + ch + 0.02) @ rotx(-40) @ T(0, -cd / 2, 0.13))
    C.obj('Chest_lid', lid, chest_w, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False, bevel=0.03)
    for x in (-cw * 0.32, cw * 0.32):
        bm = cube_bm(0.12, cd + 0.04, ch + 0.02); xform(bm, T(x, cy, cz + ch / 2)); C.obj('Chest_band_%d' % (x > 0), bm, gold, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False)
        bm = cube_bm(0.12, cd * 1.06, 0.28); xform(bm, T(x, cy + cd / 2, cz + ch + 0.02) @ rotx(-40) @ T(0, -cd / 2, 0.13)); C.obj('Lid_band_%d' % (x > 0), bm, gold, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False)
    gm = index_glow_mat('chest glow', 'rarity', RARITY, strength=14.0)
    bm = cube_bm(cw * 0.94, cd * 0.94, 0.16); xform(bm, T(0, cy, cz + ch + 0.05)); o = C.obj('Chest_glow', bm, gm, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False); prop_driven(o, rig, 'rarity')
    spk = []
    for i, (x, z, sz) in enumerate([(-0.5, 0.55, 0.2), (0.12, 0.9, 0.27), (0.6, 0.5, 0.17), (-0.12, 1.3, 0.14)]):
        bm = bmesh.new(); vs = [bm.verts.new(v) for v in [(0, 0, sz), (sz * 0.3, 0, 0), (0, 0, -sz), (-sz * 0.3, 0, 0)]]; bm.faces.new(vs)
        vs = [bm.verts.new(v) for v in [(sz, 0, 0), (0, 0, sz * 0.3), (-sz, 0, 0), (0, 0, -sz * 0.3)]]; bm.faces.new(vs)
        xform(bm, T(x, cy - 0.1, cz + ch + z)); spk.append(bm)
    o = C.obj('Chest_sparkles', join_bms(spk), gm, 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.02, smooth=False); prop_driven(o, rig, 'rarity')
    bm = cube_bm(0.18, 0.06, 0.22); xform(bm, T(0, cy - cd / 2 - 0.03, cz + ch - 0.14)); C.obj('Chest_lock', bm, gold, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False)
    for s in (-1, 1):
        pts = [(s * 0.55, -P['td'] / 2 - 0.03, P['waist_z'] + 0.3), (s * 0.62, -P['td'] * 0.42, P['sh_z'] - 0.1), (s * 0.6, -0.05, P['sh_z'] + 0.1), (s * 0.7, by, P['sh_z'])]
        C.obj('Pack_strap_%d' % (s > 0), tube_bm(pts, 0.06, 8), leather('merchant strap', (100, 64, 34)), 'UpperTorso', origin=(0, 0, P['waist_z']))
    C.height = P['top']
    ex = {'welcome': {'LeftUpperArm': (0.8, -0.35, -0.55), 'RightUpperArm': (-0.8, -0.35, -0.55), 'LeftLowerArm': (0.55, -0.75, -0.05), 'RightLowerArm': (-0.55, -0.75, -0.05),
                      'LeftHand': (0.45, -0.75, 0.25), 'RightHand': (-0.45, -0.75, 0.25), 'Head': (0, 0.05, 1)},
          'offer': {'RightUpperArm': (-0.3, -0.75, -0.5), 'RightLowerArm': (-0.1, -1, 0.1), 'RightHand': (0, -1, 0.0), 'LeftUpperArm': (0.4, -0.3, -0.85), 'LeftLowerArm': (-0.5, -0.8, -0.1), 'LeftHand': (-0.6, -0.6, 0)}}
    finish(C, 'welcome', extra_poses=ex, overrides={'laugh': {'LeftUpperArm': (0.55, -0.3, -0.78), 'RightUpperArm': (-0.55, -0.3, -0.78), 'LeftLowerArm': (-0.45, -0.85, -0.2), 'RightLowerArm': (0.45, -0.85, -0.2)}},
           record=dict(role="The town's mystery-box trader: sells the roll, the junk sword or the egg, then reacts to the legendary result (the channel's namesake)", body='round gentle-big 3.75 HH (shrewd and kind; never a size or food joke)',
           signature='plum purple; the chest glows in rarity colours (rig "rarity" 0 common .. 4 legendary)', face_style='storybook line-art (amber iris): knowing grin, welcome, jaw drop, curious, nervous, delighted; blink; talk closed/half/open',
           silhouette='wide-brim hat, a towering A-frame pack of wares topped by a glowing mystery chest'))
    return C

# =============================================================================  14. THE MASTER SMITH
def build_master_smith():
    C = Char('The Master Smith', 'master_smith')
    P = body_params('broad_heroic', idle_out=10)
    skin = (100, 64, 44)
    shirt = cloth('smith shirt', (54, 44, 40), weave=40, hem_dark=0.7)
    trous = cloth('smith trousers', (60, 50, 44), weave=36, hem_dark=0.7)
    apron = leather('smith apron', (82, 50, 32), wear=0.45)
    boot = leather('smith boots', (40, 32, 28), wear=0.7)
    wrap = cloth('smith headwrap', (196, 84, 34), weave=36, hem_dark=0.7)
    iron = metal('smith iron', (84, 84, 90), rough=0.45, scratch=0.9)
    sk = skin_mat('smith skin', skin)
    M = dict(UpperTorso=shirt, LowerTorso=trous, UpperArm=sk, LowerArm=sk, Hand=sk, UpperLeg=trous, LowerLeg=boot, Foot=boot, Neck=sk)
    build_body(C, P, M)
    face = dict(set='master_smith', exprs=['judging', 'stern', 'impressed', 'shocked', 'laughing', 'doubtful'], fs=0.9, voff=0.0, cut=0.6,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    hairm = hair_mat('smith hair', (26, 20, 18))
    bm = ellipsoid(h * 0.55, h * 0.56, h * 0.3, 32, 14); xform(bm, T(0, 0.03, hz + h * 0.3)); C.obj('Hair_cap', bm, hairm, 'Head', origin=(0, 0, hz))
    bm = ellipsoid(h * 0.42, h * 0.4, h * 0.36, 24, 12); xform(bm, T(0, h * 0.18, hz + h * 0.78)); C.obj('Hair_puff', bm, hairm, 'Head', origin=(0, 0, hz))
    bm = loft([(0.0, h * 1.08, h * 1.1, 2.2), (0.17, h * 1.1, h * 1.12, 2.2)], cap=(False, False)); xform(bm, T(0, 0.02, hz + h * 0.28) @ rotx(-6))
    C.obj('Headwrap', bm, wrap, 'Head', origin=(0, 0, hz), solid=0.05)
    for s in (-1, 1):
        pts = [(s * 0.08, h * 0.55, hz + h * 0.36), (s * 0.22, h * 0.72, hz + h * 0.15), (s * 0.28, h * 0.78, hz - h * 0.12)]
        bm = tube_bm(pts, [0.09, 0.07, 0.04], 8); bmesh.ops.scale(bm, vec=(1.0, 0.45, 1.0), verts=bm.verts); C.obj('Wrap_tail_%d' % (s > 0), bm, wrap, 'Head', origin=(0, 0, hz))
    bm = ellipsoid(0.12, 0.1, 0.1, 12, 8); xform(bm, T(0, h * 0.56, hz + h * 0.36)); C.obj('Wrap_knot', bm, wrap, 'Head', origin=(0, 0, hz))
    for s_ in (-1, 1):
        bm = torus_bm(0.09, 0.022, 20, 6); xform(bm, T(s_ * h * 0.53, -h * 0.02, hz - h * 0.2) @ roty(90)); C.obj('Earring_%d' % (s_ > 0), bm, metal('earring gold', (232, 180, 70), rough=0.2, scratch=0.1), 'Head', origin=(0, 0, hz))
    # thick leather apron (bib + skirt to the shin) with straps and a tool pocket; wrist wraps; forge-scorched belt with tongs
    td = P['td']
    rows = []
    for r_ in range(9):
        t = r_ / 8; z = P['sh_z'] - 0.2 - (P['sh_z'] - 0.2 - P['waist_z'] - 0.05) * t
        wd = P['sw'] * 0.62 + (P['ww'] * 0.9 - P['sw'] * 0.62) * t
        rows.append([(wd / 2 * (c / 4 - 1), -td / 2 - 0.04 - 0.05 * (1 - (c / 4 - 1) ** 2), z) for c in range(9)])
    C.obj('Apron_bib', grid_sheet(rows), apron, 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.05)
    z0 = P['knee_z'] - 0.55
    rows = []
    for r_ in range(9):
        t = r_ / 8; z = P['waist_z'] + 0.02 - (P['waist_z'] + 0.02 - z0) * t
        wd = P['hw'] * 0.95 + 0.4 * t
        rows.append([(wd / 2 * (c / 5 - 1), -P['td'] / 2 - 0.06 - 0.12 * (1 - (c / 5 - 1) ** 2) - 0.08 * t, z) for c in range(11)])
    ap = C.obj('Apron_skirt', grid_sheet(rows), apron, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.06)
    bm = cube_bm(0.7, 0.08, 0.42); xform(bm, T(0.0, -P['td'] / 2 - 0.22, P['hip_z'] - 0.1)); C.obj('Apron_pocket', bm, leather('smith pocket', (66, 40, 26)), 'LowerTorso', origin=(0, 0, P['hip_z']), smooth=False, bevel=0.02)
    for s in (-1, 1):
        pts = [(s * P['sw'] * 0.3, -td / 2 - 0.05, P['sh_z'] - 0.2), (s * P['sw'] * 0.36, -0.05, P['sh_z'] + 0.06), (s * P['sw'] * 0.3, td / 2 + 0.05, P['sh_z'] - 0.3), (s * P['ww'] * 0.45, td / 2 + 0.04, P['waist_z'])]
        C.obj('Apron_strap_%d' % (s > 0), tube_bm(pts, 0.06, 8), apron, 'UpperTorso', origin=(0, 0, P['waist_z']))
        side = 'Left' if s > 0 else 'Right'; (l0, l1, _) = C.J[side + 'LowerArm']
        shell(C, side + 'Wrist_wrap', [(l1[2] + 0.02, P['at'] * 1.1, P['ad'] * 1.1, 6, l0[0], 0), (l1[2] + 0.36, P['at'] * 1.08, P['ad'] * 1.08, 6, l0[0], 0)], leather('wrist wrap', (120, 90, 64), wear=0.4), side + 'LowerArm', l0, round_ends=0.03)
    belt(C, P, P['waist_z'] - 0.06, leather('smith belt', (50, 34, 24), wear=0.8), iron, h=0.22, extra=0.14)
    for s in (-1, 1):
        C.obj('Tongs_%d' % (s > 0), tube_bm([(-P['hw'] / 2 - 0.2, -0.1 + s * 0.04, P['waist_z'] - 0.1), (-P['hw'] / 2 - 0.26, -0.1 + s * 0.07, P['waist_z'] - 1.1)], 0.035, 6), iron, 'LowerTorso', origin=(0, 0, P['hip_z']))
    # the hammer (big), head glowing orange-hot, resting on her right shoulder in the default pose (grip IK'd in front of the shoulder)
    dpose = {'LeftUpperArm': (0.55, 0.15, -0.8), 'LeftLowerArm': (-0.6, -0.05, -0.8), 'LeftHand': (-0.55, 0, -0.85), 'Head': (0, 0.04, 1)}
    spec = full_spec(C, 'shoulder', dpose)
    up = Vector((-0.22, 0.62, 0.75)).normalized()                       # handle runs up and back over the right shoulder
    gtarget = Vector((-P['sx'] * 0.78, -P['td'] / 2 - 0.42, P['sh_z'] - 0.55))
    hand_dir = Vector((0.75, -0.3, 0.1)); hand_dir = (hand_dir - up * hand_dir.dot(up)).normalized()
    dpose.update(ik_arm(C, spec, 'Right', gtarget, (-0.8, 0.2, -0.6), hand_dir=hand_dir)); spec = full_spec(C, 'shoulder', dpose)
    Mp = pose_mats(C, spec); g = grip_point(Mp, C, 'RightHand', 0.55)
    Lh = 2.5; top = g + up * (Lh * 0.72); bot = g - up * (Lh * 0.28)
    handle = tube_bm([tuple(bot), tuple(top)], 0.085, 10)
    side = up.cross(Vector((0, 0, 1))).normalized(); fwd = side.cross(up).normalized()
    Mh = Matrix((side.to_4d(), up.to_4d(), fwd.to_4d(), (0, 0, 0, 1))).transposed(); Mh.translation = top
    headb = cube_bm(0.56, 0.56, 1.2); xform(headb, Mh)                    # long axis across the handle
    hot = loft([(0, 0.6, 0.6, 6), (0.12, 0.58, 0.58, 6)], round_ends=0.05); xform(hot, Mh @ T(0, 0, 0.6))
    ring = torus_bm(0.33, 0.05, 24, 6); xform(ring, Mh @ T(0, 0, 0.42))
    Mr = to_rest(C, spec, 'RightHand')
    prop_obj(C, 'Hammer_handle', handle, wood('hammer handle', (96, 64, 40)), 'RightHand', Mr)
    prop_obj(C, 'Hammer_head', headb, iron, 'RightHand', Mr, smooth=False, bevel=0.04)
    prop_obj(C, 'Hammer_hot_face', hot, glow('forge glow', (255, 126, 30), 12.0), 'RightHand', Mr)
    prop_obj(C, 'Hammer_heat_ring', ring, glow('forge ember', (255, 70, 20), 6.0), 'RightHand', Mr)
    C.height = P['top']
    ex = {'shoulder': dpose,
          'strike': {'RightUpperArm': (-0.3, -0.3, 0.9), 'RightLowerArm': (-0.1, 0.2, 1), 'RightHand': (0, 0.6, -0.8), 'LeftUpperArm': (0.4, -0.5, -0.75), 'LeftLowerArm': (-0.1, -0.9, -0.3), 'UpperTorso': (0, 0.08, 1), 'Head': (0, -0.1, 1)}}
    finish(C, 'shoulder', extra_poses=ex, record=dict(role='Forge master and contest judge (can also be the hero\'s parent): forge contests, item verification, weapon awakenings',
           body='broad heroic 4.75 HH, head 0.9x, big arms', signature='charred leather brown + forge-orange glow',
           face_style='storybook line-art (copper iris): judging, stern, impressed, shocked, laughing, doubtful; blink; talk closed/half/open',
           silhouette='headwrap + hair puff, leather apron, bare thick arms, a hammer with an orange-hot head on her shoulder'))
    return C

# =============================================================================  15. THE STONE KEEPER
CLASSES = [(200, 230, 255), (255, 196, 60), (255, 70, 60), (80, 230, 120), (180, 110, 255), (120, 120, 130)]
def build_stone_keeper():
    C = Char('The Stone Keeper', 'stone_keeper')
    P = body_params('tall_elder', idle_out=6)
    skin = (132, 90, 62)
    robe = cloth('keeper robe', (226, 218, 198), weave=40, hem_dark=0.9, thread=(70, 70, 150), sheen=0.5)
    indigo = cloth('keeper indigo', (46, 44, 116), weave=40, hem_dark=0.75, thread=(220, 200, 140))
    sk = skin_mat('keeper skin', skin)
    M = dict(UpperTorso=robe, LowerTorso=robe, UpperArm=robe, LowerArm=robe, Hand=sk, UpperLeg=robe, LowerLeg=robe, Foot=leather('keeper shoes', (60, 46, 40)), Neck=sk)
    build_body(C, P, M)
    face = dict(set='stone_keeper', exprs=['solemn', 'stern', 'approving', 'stunned', 'sorrowful'], fs=0.9, voff=0.0, cut=0.6,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    bm = ellipsoid(h * 0.54, h * 0.5, h * 0.22, 28, 12); xform(bm, T(0, 0.04, hz + h * 0.34)); C.obj('Hair', bm, hair_mat('keeper hair', (214, 212, 208)), 'Head', origin=(0, 0, hz))
    # indigo hood whose point leans and curls back (about 1 HH above her head), open face, bone-white lining. Design rule: never an all-white
    # upright cone over a white robe (that reads as a hate-group costume) - the hood and mantle are indigo, the point bends back.
    hb = ellipsoid(h * 0.68, h * 0.68, h * 0.68, 36, 22)
    for v in hb.verts:
        if v.co.z > 0:
            t = v.co.z / (h * 0.68); sh = 1 - 0.8 * t ** 1.3
            v.co.x *= sh; v.co.y *= sh; v.co.z += t ** 1.8 * 0.62; v.co.y += t ** 2.6 * 1.25
    kill = [f for f in hb.faces if f.calc_center_median().y < -h * 0.22 and -h * 0.66 < f.calc_center_median().z < h * 0.48]
    bmesh.ops.delete(hb, geom=kill, context='FACES'); xform(hb, T(0, 0.05, hz + 0.02))
    tipv = max((v.co.copy() for v in hb.verts), key=lambda c_: c_.z + 0.6 * c_.y)
    hd = C.obj('Hood', hb, indigo, 'Head', origin=(0, 0, hz), solid=0.07); hd.data.materials.append(robe); hd.modifiers['solidify'].material_offset = 1
    silver = metal('keeper silver', (196, 200, 210), rough=0.3)
    bm = ellipsoid(0.09, 0.09, 0.09, 12, 8); xform(bm, Matrix.Translation(tipv)); C.obj('Hood_tassel', bm, silver, 'Head', origin=(0, 0, hz))
    for s_ in (-1, 1):       # grey locks framing her face inside the hood
        pts = [(s_ * h * 0.4, -h * 0.3, hz + h * 0.3), (s_ * h * 0.47, -h * 0.34, hz), (s_ * h * 0.45, -h * 0.3, hz - h * 0.38)]
        C.obj('Lock_%d' % (s_ > 0), tube_bm(pts, [0.07, 0.08, 0.05], 8), hair_mat('keeper hair', (214, 212, 208)), 'Head', origin=(0, 0, hz))
    # indigo shoulder mantle with a silver edge, over the white robe
    sz = P['sh_z']
    bm = loft([(sz - 0.62, P['sw'] + 0.75, P['td'] + 0.62, 3), (sz - 0.15, P['sw'] + 0.62, P['td'] + 0.5, 3), (sz + 0.1, P['sw'] + 0.2, P['td'] + 0.25, 3), (sz + 0.24, h * 0.95, h * 0.9, 2.5)], cap=(False, True))
    mt = C.obj('Mantle', bm, indigo, 'UpperTorso', origin=(0, 0, sz), solid=0.05); C.hem(mt, sz - 0.62, 0.0)
    bm = loft([(sz - 0.66, P['sw'] + 0.8, P['td'] + 0.67, 3), (sz - 0.57, P['sw'] + 0.79, P['td'] + 0.66, 3)], cap=(False, False)); C.obj('Mantle_edge', bm, silver, 'UpperTorso', origin=(0, 0, sz), solid=0.025)
    # floor-length robe (trapezoid 1.4 W -> 2.0 W), wide sleeves, indigo stole and hem band
    z0 = 0.06
    rb = shell(C, 'Robe_skirt', [(z0, 1.92, P['td'] + 0.62, 4), (P['knee_z'], 1.62, P['td'] + 0.42, 4), (P['hip_z'], P['hw'] + 0.16, P['td'] + 0.2, 4), (P['waist_z'] - 0.02, P['ww'] + 0.1, P['td'] + 0.12, 4)], robe, 'LowerTorso', (0, 0, P['hip_z']), round_ends=0.02, cap=(False, True))
    C.hem(rb, z0, 0.0)
    bm = loft([(z0 - 0.02, 1.96, P['td'] + 0.66, 4), (z0 + 0.2, 1.95, P['td'] + 0.65, 4)], cap=(False, False)); C.obj('Robe_hem_band', bm, indigo, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.03)
    for side, s in (('Left', 1), ('Right', -1)):
        (l0, l1, _) = C.J[side + 'LowerArm']
        shell(C, side + 'Sleeve', [(l1[2] - 0.05, P['at'] * 2.0, P['ad'] * 2.0, 3, l0[0], 0), (l0[2] + 0.08, P['at'] * 1.15, P['ad'] * 1.15, 3, l0[0], 0)], robe, side + 'LowerArm', l0, round_ends=0.02, cap=(False, True))
        bm = loft([(l1[2] - 0.07, P['at'] * 2.06, P['ad'] * 2.06, 3, l0[0], 0), (l1[2] + 0.05, P['at'] * 2.0, P['ad'] * 2.0, 3, l0[0], 0)], cap=(False, False))
        C.obj(side + 'Sleeve_cuff', bm, indigo, side + 'LowerArm', origin=l0, solid=0.03)
    belt(C, P, P['waist_z'] - 0.02, indigo, metal('keeper silver', (196, 200, 210), rough=0.3), h=0.12, extra=0.14)
    def skirt_front(z):       # front surface of the robe skirt at height z (matches the Robe_skirt sections)
        zs = [(0.06, P['td'] + 0.62), (P['knee_z'], P['td'] + 0.42), (P['hip_z'], P['td'] + 0.2), (P['waist_z'], P['td'] + 0.12)]
        for (za, da), (zb_, db) in zip(zs[:-1], zs[1:]):
            if za <= z <= zb_: return -(da + (db - da) * (z - za) / (zb_ - za)) / 2
        return -(P['td'] + 0.12) / 2
    rows = []                 # wide indigo front panel: chest part on the upper torso, skirt part on the hips (so the lean can't swallow it)
    for r_ in range(4):
        z = P['sh_z'] - 0.5 - (P['sh_z'] - 0.5 - P['waist_z']) * r_ / 3
        rows.append([(-0.34 + 0.68 * c_ / 4, -(P['td'] / 2 + 0.13), z) for c_ in range(5)])
    C.obj('Front_panel', grid_sheet(rows), indigo, 'UpperTorso', origin=(0, 0, P['waist_z']), solid=0.03)
    rows = []
    for r_ in range(10):
        t = r_ / 9; z = P['waist_z'] - (P['waist_z'] - 0.1) * t
        rows.append([(-0.34 - 0.14 * t + (0.68 + 0.28 * t) * c_ / 4, skirt_front(z) - 0.05, z) for c_ in range(5)])
    C.obj('Front_panel_skirt', grid_sheet(rows), indigo, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.03)
    for i, z in enumerate([P['hip_z'] - 0.2, P['knee_z'] + 0.3, P['knee_z'] - 0.7]):
        yy = skirt_front(z) - 0.08
        bm = bmesh.new(); vs = [bm.verts.new((x_, yy, z + z_)) for x_, z_ in [(0, 0.14), (0.1, 0), (0, -0.14), (-0.1, 0)]]; bm.faces.new(vs[::-1])
        C.obj('Rune_%d' % i, bm, silver, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.015, smooth=False)
    # the class stone, held in both hands at the chest (rig 'class' picks the glow colour)
    rig = C.rig; rig['class'] = 0
    try: rig.id_properties_ui('class').update(min=0, max=5, description='stone glow: 0 unread (white-blue), 1 legendary gold, 2 warrior red, 3 ranger green, 4 mage violet, 5 weakest (dim grey)')
    except Exception: pass
    dpose = {'UpperTorso': (0, -0.16, 1), 'Head': (0, -0.12, 1),
             'RightUpperArm': (-0.2, -0.45, -0.87), 'RightLowerArm': (0.38, -0.88, 0.25), 'RightHand': (0.45, -0.85, 0.2),
             'LeftUpperArm': (0.2, -0.45, -0.87), 'LeftLowerArm': (-0.38, -0.88, 0.25), 'LeftHand': (-0.45, -0.85, 0.2)}
    spec = full_spec(C, 'present', dpose); Mp = pose_mats(C, spec)
    gr = grip_point(Mp, C, 'RightHand', 0.6); gl = grip_point(Mp, C, 'LeftHand', 0.6); c = (gr + gl) / 2 + Vector((0, -0.12, 0.18))
    Mr = to_rest(C, spec, 'RightHand')
    sm = index_glow_mat('class stone', 'class', CLASSES, strength=7.0)
    bm = lathe([(0, -0.46), (0.4, -0.07), (0.4, 0.16), (0, 0.68)], 6)       # hexagonal crystal
    xform(bm, Matrix.Translation(c + Vector((0, 0, 0.05))) @ rotz(30)); o = prop_obj(C, 'Class_stone', bm, sm, 'RightHand', Mr, smooth=False); prop_driven(o, rig, 'class')
    bm = lathe([(0, 0), (0.3, 0), (0.34, 0.06), (0.26, 0.12), (0, 0.12)], 24); xform(bm, Matrix.Translation(c - Vector((0, 0, 0.46))))
    prop_obj(C, 'Stone_cradle', bm, metal('keeper silver', (196, 200, 210), rough=0.3), 'RightHand', Mr)
    C.height = P['top'] + 1.28
    ex = {'present': dpose,
          'raise_stone': {'RightUpperArm': (-0.2, -0.3, 0.93), 'RightLowerArm': (0.1, -0.2, 1), 'RightHand': (0.4, -0.8, 0.4), 'LeftUpperArm': (0.4, -0.1, -0.9), 'LeftLowerArm': (0.1, -0.4, -0.9), 'Head': (0, 0.1, 1)}}
    finish(C, 'present', extra_poses=ex, record=dict(role='Class-giver and academy master who judges, ranks, expels or crowns (the channel\'s teacher)',
           body='tall elder 6.0 HH + 1 HH pointed hood, robe trapezoid 1.4 -> 2.0 W, slight forward lean', signature="bone white + indigo trim; the stone glows (rig 'class' 0-5)",
           face_style='storybook line-art (indigo iris, elder lines): solemn, stern, approving, stunned silence, sorrowful; blink; talk closed/half/open',
           silhouette='tall pointed hood, floor-length trapezoid robe, a glowing class stone held in both hands'))
    return C

# =============================================================================  18. THE RIVAL HEIR
def build_rival_heir():
    C = Char('The Rival Heir', 'rival_heir')
    P = body_params('heroic_teen', H=4.5 * K.HH, head=0.96, sw=1.66, ww=1.02, hw=1.1, td=0.72, at=0.46, ad=0.48, lgw=0.5, lgd=0.52, idle_out=8)
    skin = (214, 168, 128)
    cobalt = metal('heir cobalt', (24, 54, 168), rough=0.26, scratch=0.4, metallic=0.55)
    cob_c = cloth('heir cobalt cloth', (26, 50, 150), weave=40, hem_dark=0.7, thread=(220, 226, 236))
    steel = metal('heir steel', (186, 192, 204), rough=0.22, scratch=0.45)
    trous = cloth('heir trousers', (52, 52, 64), weave=40, hem_dark=0.7)
    boot = leather('heir boots', (58, 44, 40), wear=0.5)
    sk = skin_mat('heir skin', skin)
    M = dict(UpperTorso=cob_c, LowerTorso=trous, UpperArm=cob_c, LowerArm=cob_c, Hand=leather('heir glove', (58, 44, 40), wear=0.3), UpperLeg=trous, LowerLeg=boot, Foot=boot, Neck=sk)
    build_body(C, P, M)
    face = dict(set='rival_heir', exprs=['cool', 'doubtful', 'smile', 'wink', 'determined', 'angry', 'shocked', 'scared'], fs=0.86, voff=0.0, cut=0.685,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    add_hair(C, 'hero_side_braid', (40, 28, 24), scale=0.92)
    # small tiara
    bm = bmesh.new(); n = 28; rr = h * 0.56
    rb_ = [bm.verts.new((rr * math.cos(math.pi * (0.15 + 0.7 * i / n)), -rr * math.sin(math.pi * (0.15 + 0.7 * i / n)), 0)) for i in range(n + 1)]
    rt_ = [bm.verts.new((rr * math.cos(math.pi * (0.15 + 0.7 * i / n)), -rr * math.sin(math.pi * (0.15 + 0.7 * i / n)), (0.07 + 0.22 * max(0, 1 - abs(i - n / 2) / 4.0) + 0.05 * (i % 4 == 0)) * h)) for i in range(n + 1)]
    for i in range(n): bm.faces.new((rb_[i], rb_[i + 1], rt_[i + 1], rt_[i]))
    xform(bm, T(0, 0.02, hz + h * 0.5) @ rotx(-12)); C.obj('Tiara', bm, steel, 'Head', origin=(0, 0, hz), solid=0.03)
    bm = ellipsoid(0.08, 0.05, 0.09, 12, 6); xform(bm, T(0, -rr * 0.98 - 0.02, hz + h * 0.62)); C.obj('Tiara_gem', bm, plain('cobalt gem', (40, 90, 255), rough=0.1, coat=1.0), 'Head', origin=(0, 0, hz))
    # practical armour, same coverage as the knights: cobalt cuirass with steel edges, pauldrons, faulds, greaves
    td = P['td'] + 0.12
    shell(C, 'Cuirass', [(P['waist_z'] - 0.05, P['ww'] + 0.1, td * 0.95, 4), (P['waist_z'] + P['ut'] * 0.6, P['sw'] * 0.95 + 0.06, td, 4), (P['sh_z'] - 0.02, P['sw'] * 0.9 + 0.06, td * 0.92, 5)], cobalt, 'UpperTorso', (0, 0, P['waist_z']), round_ends=0.08)
    bm = lathe([(P['head'] * 0.5, P['sh_z'] - 0.06), (P['head'] * 0.46, P['sh_z'] + 0.12)], 36); C.obj('Gorget', bm, steel, 'UpperTorso', origin=(0, 0, P['sh_z']), solid=0.04)
    for side, s in (('Left', 1), ('Right', -1)):
        pauldron(C, side, s, s * P['sx'], P['sh_z'] + 0.02, 0.4, layers=2, mat=steel, rim=None, tilt=14)
        x = s * P['lx']
        shell(C, side + 'Greave', [(P['fh'] + 0.05, P['lgw'] * 1.14, P['lgd'] * 1.14, 5, x, 0), (P['knee_z'] - 0.05, P['lgw'] * 1.1, P['lgd'] * 1.1, 5, x, 0)], steel, side + 'LowerLeg', (x, 0, P['knee_z']), round_ends=0.05)
        bm = ellipsoid(P['lgw'] * 0.6, P['lgd'] * 0.6, 0.18, 18, 9); xform(bm, T(x, -0.05, P['knee_z'])); C.obj(side + 'Knee', bm, steel, side + 'LowerLeg', origin=(x, 0, P['knee_z']))
    for i in range(2):
        z = P['hip_z'] + 0.05 - i * 0.26
        bm = loft([(z - 0.28, P['hw'] + 0.24 + 0.06 * i, P['td'] + 0.26 + 0.04 * i, 4), (z, P['hw'] + 0.2 + 0.06 * i, P['td'] + 0.22 + 0.04 * i, 4)], round_ends=0.03, cap=(False, False))
        C.obj('Fauld_%d' % i, bm, steel if i else cobalt, 'LowerTorso', origin=(0, 0, P['hip_z']), solid=0.04)
    belt(C, P, P['waist_z'] - 0.03, leather('heir belt', (60, 42, 34)), steel, h=0.14, extra=0.12)
    # right forearm: cobalt vambrace; LEFT forearm and hand: a steel prosthetic (normal gear, rivets + finger plates)
    (l0, l1, _) = C.J['RightLowerArm']
    shell(C, 'RightVambrace', [(l1[2] + 0.02, P['at'] * 1.12, P['ad'] * 1.12, 5, l0[0], 0), (l0[2] - 0.06, P['at'] * 1.08, P['ad'] * 1.08, 5, l0[0], 0)], steel, 'RightLowerArm', l0, round_ends=0.04)
    (l0, l1, _) = C.J['LeftLowerArm']; (a0, a1, _) = C.J['LeftHand']; x = l0[0]
    for k_ in ('LeftLowerArm', 'LeftHand'): me_ = C.parts[k_].data; bpy.data.objects.remove(C.parts[k_], do_unlink=True); bpy.data.meshes.remove(me_); C.parts.pop(k_)
    pm = metal('heir prosthetic', (176, 182, 192), rough=0.2, scratch=0.4); dk = metal('heir joint', (70, 74, 84), rough=0.35)
    for i in range(4):
        z1 = l0[2] - 0.02 - i * (l0[2] - l1[2]) / 4; z2 = z1 - (l0[2] - l1[2]) / 4 + 0.03
        C.obj('Steel_forearm_%d' % i, loft([(z2, P['at'] * (0.92 - 0.04 * i), P['ad'] * (0.92 - 0.04 * i), 6, x, 0), (z1, P['at'] * (0.96 - 0.04 * i), P['ad'] * (0.96 - 0.04 * i), 6, x, 0)], round_ends=0.03), pm, 'LeftLowerArm', origin=l0)
    bm = ellipsoid(P['at'] * 0.42, P['ad'] * 0.42, 0.09, 14, 8); xform(bm, T(x, 0, l1[2])); C.obj('Steel_wrist', bm, dk, 'LeftLowerArm', origin=l0)
    bm = loft([(a0[2] - P['hand'] * 0.5, P['at'] * 0.88, P['ad'] * 0.62, 6, x, 0), (a0[2] - 0.02, P['at'] * 0.9, P['ad'] * 0.7, 6, x, 0)], round_ends=0.03); C.obj('Steel_hand', bm, pm, 'LeftHand', origin=a0)
    for k in range(3):
        fx = x + (k - 1) * P['at'] * 0.28
        C.obj('Steel_finger_%d' % k, loft([(a1[2] + 0.02, P['at'] * 0.22, P['ad'] * 0.5, 4, fx, 0), (a0[2] - P['hand'] * 0.52, P['at'] * 0.24, P['ad'] * 0.52, 4, fx, 0)], round_ends=0.02), pm, 'LeftHand', origin=a0)
    for k in range(6):
        a = 2 * math.pi * k / 6; bm = ellipsoid(0.025, 0.025, 0.025, 6, 4); xform(bm, T(x + math.cos(a) * P['at'] * 0.47, math.sin(a) * P['ad'] * 0.47, l0[2] - 0.12)); C.obj('Rivet_%d' % k, bm, dk, 'LeftLowerArm', origin=l0)
    # rapier in the right hand (swept hilt), held low and forward in the default pose
    dpose = {'RightUpperArm': (-0.3, -0.25, -0.92), 'RightLowerArm': (-0.15, -0.75, -0.65), 'RightHand': (-0.1, -0.9, -0.4),
             'LeftUpperArm': (0.62, 0.2, -0.76), 'LeftLowerArm': (-0.6, -0.05, -0.8), 'LeftHand': (-0.55, 0, -0.85), 'Head': (0, 0.06, 1),
             'LeftUpperLeg': (0.08, 0, -1), 'LeftLowerLeg': (0.08, 0, -1), 'RightUpperLeg': (-0.1, 0, -1), 'RightLowerLeg': (-0.1, 0, -1)}
    spec = full_spec(C, 'ready', dpose); Mp = pose_mats(C, spec); g = grip_point(Mp, C, 'RightHand', 0.5)
    hd_ = (Mp['RightHand'].to_3x3() @ Vector((0, 1, 0))).normalized()
    bdir = Vector((-0.2, -0.75, -0.62)).normalized(); bdir = (bdir - hd_ * bdir.dot(hd_) * 0.6).normalized()
    q = Vector((0, 0, 1)).rotation_difference(bdir); Mx = Matrix.Translation(g + bdir * 0.12) @ q.to_matrix().to_4x4()
    blade = loft([(0, 0.1, 0.035, 4), (2.3, 0.06, 0.025, 4), (2.45, 0.01, 0.01, 2)]); xform(blade, Mx)
    bars = []
    for s in (-1, 1): bars.append(tube_bm([(0, 0, 0), (s * 0.18, -0.04, -0.06), (s * 0.12, -0.08, -0.32), (0, -0.04, -0.4)], 0.025, 6))
    bars.append(loft([(-0.03, 0.42, 0.06, 4), (0.03, 0.42, 0.06, 4)], round_ends=0.02))
    guard = join_bms(bars); xform(guard, Mx)
    grip = loft([(-0.42, 0.075, 0.075, 4), (-0.02, 0.07, 0.07, 4)]); xform(grip, Mx)
    pom = ellipsoid(0.07, 0.07, 0.07, 12, 6); xform(pom, Mx @ T(0, 0, -0.47))
    Mr = to_rest(C, spec, 'RightHand')
    prop_obj(C, 'Rapier_blade', blade, steel, 'RightHand', Mr); prop_obj(C, 'Rapier_guard', guard, steel, 'RightHand', Mr)
    prop_obj(C, 'Rapier_grip', grip, leather('rapier grip', (30, 40, 90)), 'RightHand', Mr); prop_obj(C, 'Rapier_pommel', pom, cobalt, 'RightHand', Mr)
    C.height = P['top']
    ex = {'ready': dpose,
          'en_garde': {'RightUpperArm': (-0.35, -0.85, -0.3), 'RightLowerArm': (-0.1, -1, 0.05), 'RightHand': (0, -1, 0.1), 'LeftUpperArm': (0.6, 0.3, 0.5), 'LeftLowerArm': (-0.2, 0.2, 1), 'LeftHand': (-0.3, 0, 1),
                       'UpperTorso': ((0, -0.04, 1), 25), 'Head': ((0, 0, 1), -20), 'LeftUpperLeg': (0.25, 0.2, -1), 'LeftLowerLeg': (0.15, 0.1, -1), 'RightUpperLeg': (-0.2, -0.35, -1), 'RightLowerLeg': (-0.1, 0.05, -1)}}
    finish(C, 'ready', extra_poses=ex, record=dict(role='A capable princess who doubts the hero, then backs him (never romance); steel prosthetic forearm worn as normal gear',
           body='heroic teen, lean 4.5 HH', signature='cobalt + steel', face_style="Town Anime catalogue ('calm' / 'cool' family) at lead level: cool, doubtful, smile, wink, determined, angry, shocked, scared; blink; talk closed/half/open",
           silhouette='side braid + small tiara, practical cobalt-and-steel armour, rapier, steel left forearm'))
    return C

# =============================================================================  20. THE JESTER
def build_jester():
    C = Char('The Jester', 'jester')
    P = body_params('slender_tall', H=5.5 * K.HH, head=0.86, sw=1.06, ww=0.8, hw=0.88, td=0.55, at=0.29, ad=0.3, lgw=0.31, lgd=0.33, hunch=0, idle_out=8)
    skin = (240, 206, 182)
    mus, blk = (226, 178, 24), (26, 24, 30)
    suit = harlequin('jester diamonds', mus, blk, scale=3.2)
    mus_c = cloth('jester mustard', mus, weave=40, hem_dark=0.75); blk_c = cloth('jester black', blk, weave=40, hem_dark=0.7, thread=mus)
    sk = skin_mat('jester skin', skin)
    M = dict(UpperTorso=suit, LowerTorso=suit, UpperArm=suit, LowerArm=suit, Hand=sk, UpperLeg=mus_c, LowerLeg=mus_c, Foot=blk_c, Neck=sk)
    build_body(C, P, M, hand_taper=0.6)
    for o in (C.parts['RightUpperLeg'], C.parts['RightLowerLeg']): o.data.materials[0] = blk_c     # motley legs
    C.parts['LeftFoot'].data.materials[0] = mus_c
    face = dict(set='jester', exprs=['sly_grin', 'cackle', 'wink', 'shocked', 'serious', 'innocence'], fs=1.12, voff=0.02, cut=0.575,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink')
    make_head(C, P, skin, face)
    hz, h = P['head_c'], P['head']
    bell = metal('bell gold', (236, 190, 60), rough=0.2, scratch=0.2)
    # three-pointed bell hat: a cap + three floppy points with bells
    bm = ellipsoid(h * 0.58, h * 0.58, h * 0.36, 32, 14); xform(bm, T(0, 0.03, hz + h * 0.3)); C.obj('Hat_cap', bm, blk_c, 'Head', origin=(0, 0, hz))
    bm = loft([(0.0, h * 1.18, h * 1.18, 2), (0.14, h * 1.18, h * 1.18, 2)], cap=(False, False)); xform(bm, T(0, 0.03, hz + h * 0.22)); C.obj('Hat_band', bm, mus_c, 'Head', origin=(0, 0, hz), solid=0.04)
    for i, (dx, col) in enumerate(((-1, mus_c), (0, blk_c), (1, mus_c))):
        pts = []
        for k in range(12):
            t = k / 11
            if dx == 0: pts.append((0, h * (0.05 + 0.55 * t), hz + h * (0.55 + 1.25 * t - 0.95 * t * t)))
            else: pts.append((dx * h * (0.3 + 1.25 * t), h * 0.05, hz + h * (0.45 + 1.05 * t - 1.35 * t * t)))
        C.obj('Hat_point_%d' % i, tube_bm(pts, [h * 0.27 * (1 - 0.8 * k / 11) for k in range(12)], 12), col, 'Head', origin=(0, 0, hz))
        bm = ellipsoid(h * 0.13, h * 0.13, h * 0.13, 12, 8); xform(bm, T(*pts[-1]) @ T(0, 0, -h * 0.06)); C.obj('Hat_bell_%d' % i, bm, bell, 'Head', origin=(0, 0, hz))
    # pointed ruff collar (alternating points) with bells
    bms = []
    for i in range(12):
        a = 2 * math.pi * i / 12; v = Vector((math.cos(a), math.sin(a), 0))
        bm = lathe([(0.13, 0), (0.0, 0.5)], 6); q = Vector((0, 0, 1)).rotation_difference((v + Vector((0, 0, -0.12))).normalized())
        xform(bm, T(v.x * 0.3, v.y * 0.26, P['sh_z'] + 0.08) @ q.to_matrix().to_4x4()); bms.append(bm)
    C.obj('Ruff_mustard', join_bms(bms[0::2]), mus_c, 'UpperTorso', origin=(0, 0, P['sh_z'])); C.obj('Ruff_black', join_bms(bms[1::2]), blk_c, 'UpperTorso', origin=(0, 0, P['sh_z']))
    # pointed curled shoes
    for side, s in (('Left', 1), ('Right', -1)):
        x = s * P['lx']; pts = [(x, -P['fl'] * 0.3, P['fh'] * 0.5), (x, -P['fl'] * 0.85, P['fh'] * 0.45), (x, -P['fl'] * 1.15, P['fh'] * 0.9), (x, -P['fl'] * 1.05, P['fh'] * 1.6)]
        C.obj(side + 'Shoe_curl', tube_bm(pts, [0.13, 0.1, 0.06, 0.03], 8), mus_c if s < 0 else blk_c, side + 'Foot', origin=C.J[side + 'Foot'][0])
        bm = ellipsoid(0.06, 0.06, 0.06, 10, 6); xform(bm, T(*pts[-1])); C.obj(side + 'Shoe_bell', bm, bell, side + 'Foot', origin=C.J[side + 'Foot'][0])
    # tunic points (dagged hem) over the hips
    bms = []
    for i in range(10):
        a = 2 * math.pi * i / 10; v = Vector((math.cos(a) * (P['hw'] / 2 + 0.08), math.sin(a) * (P['td'] / 2 + 0.08), 0))
        bm = lathe([(0.14, 0), (0.0, 0.42)], 4); xform(bm, T(v.x, v.y, P['hip_z'] + 0.06) @ rotx(180)); bms.append(bm)
    C.obj('Tunic_points', join_bms(bms), suit, 'LowerTorso', origin=(0, 0, P['hip_z']), smooth=False)
    belt(C, P, P['waist_z'], leather('jester belt', (60, 40, 30)), bell, h=0.1, extra=0.06)
    # puppet-on-a-stick (marotte) in his left hand, held up beside his face in the default pose; rig 'puppet' 0/1 opens its mouth
    rig = C.rig; rig['puppet'] = 0
    try: rig.id_properties_ui('puppet').update(min=0, max=1, description="puppet mouth: 0 closed, 1 open (key it to make the puppet 'talk')")
    except Exception: pass
    dpose = {'LeftUpperArm': (0.6, -0.3, -0.5), 'LeftLowerArm': (0.1, -0.4, 0.92), 'LeftHand': (-0.2, -0.95, 0.1),
             'RightUpperArm': (-0.62, 0.2, -0.76), 'RightLowerArm': (0.6, -0.05, -0.8), 'RightHand': (0.55, 0, -0.85),
             'UpperTorso': ((0.06, -0.02, 1), -10), 'Head': ((-0.12, 0, 1), 12)}
    spec = full_spec(C, 'puppet', dpose); Mp = pose_mats(C, spec); g = grip_point(Mp, C, 'LeftHand', 0.5)
    hd_ = (Mp['LeftHand'].to_3x3() @ Vector((0, 1, 0))).normalized(); up = Vector((0.15, -0.1, 1)).normalized(); up = (up - hd_ * up.dot(hd_)).normalized()
    stick_top = g + up * 1.15; stick_bot = g - up * 0.5
    Mr = to_rest(C, spec, 'LeftHand')
    prop_obj(C, 'Puppet_stick', tube_bm([tuple(stick_bot), tuple(stick_top)], 0.035, 8), wood('puppet stick', (150, 104, 60)), 'LeftHand', Mr)
    ph = stick_top + up * 0.26
    bm = ellipsoid(0.28, 0.26, 0.29, 20, 10); xform(bm, Matrix.Translation(ph)); prop_obj(C, 'Puppet_head', bm, sk, 'LeftHand', Mr)
    for k, dx in enumerate((-1, 1)):
        bm = ellipsoid(0.05, 0.03, 0.06, 8, 6); xform(bm, Matrix.Translation(ph + Vector((dx * 0.1, -0.245, 0.05)))); prop_obj(C, 'Puppet_eye_%d' % k, bm, plain('ink', (20, 16, 20), rough=0.3), 'LeftHand', Mr)
        pts = [ph + Vector((dx * 0.14, 0, 0.17)), ph + Vector((dx * 0.45, 0.02, 0.34)), ph + Vector((dx * 0.5, 0.02, 0.07))]
        prop_obj(C, 'Puppet_hat_%d' % k, tube_bm([tuple(p) for p in pts], [0.11, 0.07, 0.03], 8), mus_c if k else blk_c, 'LeftHand', Mr)
        bm = ellipsoid(0.055, 0.055, 0.055, 8, 6); xform(bm, Matrix.Translation(pts[-1])); prop_obj(C, 'Puppet_bell_%d' % k, bm, bell, 'LeftHand', Mr)
    pmm = plain('puppet mouth', (110, 24, 36), rough=0.5)
    bm = ellipsoid(0.11, 0.04, 0.025, 12, 6); xform(bm, Matrix.Translation(ph + Vector((0, -0.255, -0.11)))); m0 = prop_obj(C, 'Puppet_mouth_closed', bm, pmm, 'LeftHand', Mr)
    bm = ellipsoid(0.1, 0.05, 0.09, 12, 6); xform(bm, Matrix.Translation(ph + Vector((0, -0.245, -0.12)))); m1 = prop_obj(C, 'Puppet_mouth_open', bm, pmm, 'LeftHand', Mr)
    switch([m0], rig, 'puppet', 0); switch([m1], rig, 'puppet', 1)
    bm = lathe([(0, 0), (0.2, 0.0), (0.27, 0.15), (0.0, 0.17)], 6); xform(bm, Matrix.Translation(ph - up * 0.43)); prop_obj(C, 'Puppet_collar', bm, mus_c, 'LeftHand', Mr, smooth=False)
    C.height = P['top']
    ex = {'puppet': dpose,
          'bow': {'UpperTorso': (0, -0.75, 0.6), 'Head': (0, -0.4, 0.8), 'RightUpperArm': (-0.3, -0.8, -0.3), 'RightLowerArm': (0.6, -0.4, 0.2), 'LeftUpperArm': (0.5, 0.5, -0.4), 'LeftLowerArm': (0.4, 0.6, 0.4)}}
    finish(C, 'puppet', extra_poses=ex, record=dict(role='A truth-telling fool who looks weak and isn\'t: the "never let them know your next move" voice', body='tall slender 5.5 HH, head 0.9x, pointed shoes',
           signature='mustard with black diamonds', face_style='sharp rival set (violet iris, freckles): sly grin, cackle, wink, shocked, serious, fake innocence; blink; talk closed/half/open',
           silhouette="three-pointed bell hat, pointed ruff, diamond suit, curled shoes, a puppet-on-a-stick that 'talks' (rig 'puppet')"))
    return C

# =============================================================================  11. THE BOSS GIANT RIG (one reskinnable giant body)
GIANT_SKINS = {'base': [(120, 84, 62), (100, 106, 118), (30, 34, 52)], 'dark': [(74, 70, 72), (56, 60, 70), (12, 14, 26)],
               'glow': [(255, 110, 30), (200, 230, 255), (60, 160, 255)], 'glow_str': [0.0, 2.5, 9.0], 'weak': [(255, 150, 40), (180, 220, 255), (90, 200, 255)]}
def giant_mat(name):
    """giant skin: plated voronoi chunks whose colours and glowing seams follow the object's 'skin' (0 iron and rust, 1 storm grey, 2 blue fire)"""
    m = bpy.data.materials.new('CV3 ' + name); nt = m.node_tree; N = nt.nodes; L = nt.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord')
    vc = N.new('ShaderNodeTexVoronoi'); vc.inputs['Scale'].default_value = 0.9; L.new(tc.outputs['Object'], vc.inputs['Vector'])
    sp = N.new('ShaderNodeSeparateColor'); L.new(vc.outputs['Color'], sp.inputs[0])
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 0.9; L.new(tc.outputs['Object'], vo.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.0; nz.inputs['Detail'].default_value = 5; L.new(tc.outputs['Object'], nz.inputs['Vector'])
    col = _mixc(nt, index_colour(nt, 'skin', GIANT_SKINS['base']), index_colour(nt, 'skin', GIANT_SKINS['dark']), _m(nt, 'ADD', _m(nt, 'MULTIPLY', sp.outputs[0], 0.5), _m(nt, 'MULTIPLY', nz.outputs['Fac'], 0.5)))
    seam = _m(nt, 'LESS_THAN', vo.outputs['Distance'], 0.03)
    col = _mixc(nt, col, (0.01, 0.01, 0.012, 1), _m(nt, 'MULTIPLY', seam, 0.85))
    L.new(col, b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.6; b.inputs['Metallic'].default_value = 0.35
    gl = _m(nt, 'MULTIPLY', seam, _m(nt, 'GREATER_THAN', nz.outputs['Fac'], 0.5))
    L.new(_mixc(nt, (0, 0, 0, 1), index_colour(nt, 'skin', GIANT_SKINS['glow']), gl), b.inputs['Emission Color'])
    sk = _attr(nt, 'skin'); st = _m(nt, 'ADD', _m(nt, 'MULTIPLY', _m(nt, 'COMPARE', sk, 0.0, 0.5), GIANT_SKINS['glow_str'][0]),
                                    _m(nt, 'ADD', _m(nt, 'MULTIPLY', _m(nt, 'COMPARE', sk, 1.0, 0.5), GIANT_SKINS['glow_str'][1]), _m(nt, 'MULTIPLY', _m(nt, 'COMPARE', sk, 2.0, 0.5), GIANT_SKINS['glow_str'][2])))
    L.new(st, b.inputs['Emission Strength'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.4; L.new(vo.outputs['Distance'], bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def build_boss_giant():
    C = Char('The Boss Giant', 'boss_giant')
    H = 4.0 * K.HERO_H                                     # 16.64 BU = 4x the hero (report: 3-6x); small head = 14 % of its height
    P = body_params('brute', H=H, head=2.3, neck=0.35, f_leg=0.44, f_lt=0.14, sw=7.0, ww=5.2, hw=5.0, td=3.4, at=2.1, ad=2.2, lgw=2.4, lgd=2.5,
                    hand=2.0, fl=2.8, fh=0.7, reach='midthigh', p=6, idle_out=14)
    gm = giant_mat('giant skin')
    M = dict(UpperTorso=gm, LowerTorso=gm, UpperArm=gm, LowerArm=gm, Hand=gm, UpperLeg=gm, LowerLeg=gm, Foot=gm, Neck=gm)
    build_body(C, P, M)
    rig = C.rig
    for k_, v_, d_ in (('skin', 0, 'giant skin: 0 iron and rust, 1 storm grey, 2 blue fire'), ('weak', 1.0, 'weak-point glow 0..1 (0 = hidden / defeated)'),
                       ('horns', 0, 'show horns'), ('crown', 0, 'show the jagged crown'), ('chains', 1, 'show wrist manacles and chains')):
        rig[k_] = v_
        try: rig.id_properties_ui(k_).update(min=0, max=2 if k_ == 'skin' else 1, description=d_)
        except Exception: pass
    for o in list(C.col.objects):
        if o.type == 'MESH': prop_driven(o, rig, 'skin')
    face = dict(set='boss_giant', exprs=['glare', 'roar', 'hurt'], fs=1.0, voff=0.0, cut=0.99, emissive=14.0, rough=0.6, glow=1.0, spec=0.3)
    make_head(C, P, (110, 92, 82), face, kind='block', mat=K.face_material(C, (110, 92, 82), 'boss_giant', ['glare', 'roar', 'hurt'], P['head'] / 1.2, fs=1.0, voff=0.0, cut=0.99,
              emissive=14.0, rough=0.6, spec=0.3, base_override=lambda nt: index_colour(nt, 'skin', GIANT_SKINS['base'])))
    prop_driven(C.head, rig, 'skin')
    hz, h = P['head_c'], P['head']
    # heavy shoulder plates + brow ridge (part of the base body)
    for side, s in (('Left', 1), ('Right', -1)):
        for i in range(2):
            bm = cube_bm(P['at'] * 1.5 - 0.3 * i, P['ad'] * 1.45 - 0.3 * i, 0.9); xform(bm, T(s * (P['sx'] + 0.2 * i), 0, P['sh_z'] + 0.3 - 0.75 * i) @ roty(-s * (16 + 10 * i)))
            o = C.obj('%sShoulder_plate_%d' % (side, i), bm, gm, side + 'UpperArm', origin=C.J[side + 'UpperArm'][0], smooth=False, bevel=0.15); prop_driven(o, rig, 'skin')
    bm = cube_bm(h * 1.12, h * 0.3, h * 0.2); xform(bm, T(0, -h * 0.42, hz + h * 0.28)); o = C.obj('Brow_ridge', bm, gm, 'Head', origin=(0, 0, hz), smooth=False, bevel=0.08); prop_driven(o, rig, 'skin')
    # the glowing weak point: a cracked core in the chest (rig 'weak' = brightness, colour follows the skin)
    wm = bpy.data.materials.new('CV3 giant weak point'); nt = wm.node_tree
    for n_ in list(nt.nodes):
        if n_.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n_)
    out_ = [n_ for n_ in nt.nodes][0]; e = nt.nodes.new('ShaderNodeEmission'); nt.links.new(index_colour(nt, 'skin', GIANT_SKINS['weak']), e.inputs['Color'])
    nt.links.new(_m(nt, 'MULTIPLY', _attr(nt, 'weak'), 16.0), e.inputs['Strength']); nt.links.new(e.outputs[0], out_.inputs['Surface'])
    zc = P['waist_z'] + P['ut'] * 0.62; yf = -P['td'] / 2
    bm = lathe([(0, -0.7), (0.55, -0.2), (0.55, 0.2), (0, 0.7)], 6); xform(bm, T(0, yf - 0.05, zc) @ rotx(90) @ rotz(30))
    o = C.obj('Weak_point', bm, wm, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False); prop_driven(o, rig, 'weak'); prop_driven(o, rig, 'skin')
    cr = []
    for a in (20, 100, 160, 230, 300):
        r0 = 0.6; r1 = 1.5 + 0.4 * (a % 3); v = Vector((math.cos(math.radians(a)), 0, math.sin(math.radians(a))))
        cr.append(tube_bm([tuple(Vector((0, yf - 0.06, zc)) + v * r0), tuple(Vector((0, yf - 0.06, zc)) + v * r1 + Vector((0.2, 0, 0.15)))], [0.09, 0.03], 6))
    o = C.obj('Weak_point_cracks', join_bms(cr), wm, 'UpperTorso', origin=(0, 0, P['waist_z'])); prop_driven(o, rig, 'weak'); prop_driven(o, rig, 'skin')
    # per-story accessories (rig switches): horns, jagged crown, wrist manacles + chains
    hornm = plain('giant horn', (220, 206, 180), rough=0.4)
    hs = []
    for s in (-1, 1):
        pts = [(s * (h * 0.45 + h * 0.6 * t), h * 0.1 * t, hz + h * 0.25 + h * 0.95 * math.sin(t * 2.2)) for t in [i / 12 for i in range(13)]]
        hs.append(tube_bm(pts, [h * 0.16 * (1 - 0.85 * i / 12) for i in range(13)], 12))
    horns = C.obj('Horns', join_bms(hs), hornm, 'Head', origin=(0, 0, hz)); switch([horns], rig, 'horns', 1)
    bm = bmesh.new(); n = 24; rr = h * 0.56
    rb_ = [bm.verts.new((rr * math.cos(2 * math.pi * i / n), rr * math.sin(2 * math.pi * i / n), 0)) for i in range(n)]
    rt_ = [bm.verts.new((rr * math.cos(2 * math.pi * i / n), rr * math.sin(2 * math.pi * i / n), h * (0.55 if i % 3 == 0 else 0.25))) for i in range(n)]
    for i in range(n): bm.faces.new((rb_[i], rb_[(i + 1) % n], rt_[(i + 1) % n], rt_[i]))
    xform(bm, T(0, 0, hz + h * 0.42)); crown = C.obj('Crown', bm, metal('giant crown', (120, 100, 60), rough=0.5, scratch=0.9), 'Head', origin=(0, 0, hz), solid=0.12); switch([crown], rig, 'crown', 1)
    ch_ = []; ironc = metal('giant chain', (96, 92, 90), rough=0.5, scratch=0.8)
    for side, s in (('Left', 1), ('Right', -1)):
        (l0, l1, _) = C.J[side + 'LowerArm']; x = l0[0]
        bm = loft([(l1[2] + 0.2, P['at'] * 1.3, P['ad'] * 1.3, 4, x, 0), (l1[2] + 1.0, P['at'] * 1.3, P['ad'] * 1.3, 4, x, 0)], round_ends=0.1)
        ch_.append(C.obj(side + 'Manacle', bm, ironc, side + 'LowerArm', origin=l0, smooth=False, bevel=0.06))
        pts = [(x + s * 0.3, -P['ad'] * 0.7, l1[2] + 0.5), (x + s * 0.9, -1.0, l1[2] - 1.2), (x + s * 0.7, -0.6, 0.6), (x + s * 1.6, -1.6, 0.25)]
        ch_.append(chain_path(C, side + 'Chain', pts, ironc, side + 'LowerArm', l0, R_=0.38, r_=0.11, step=0.56))
    switch(ch_, rig, 'chains', 1)
    C.height = P['top']
    ex = {'stomp': {'UpperTorso': (0, -0.15, 1), 'Head': (0, -0.1, 1), 'LeftUpperArm': (0.45, -0.2, -0.9), 'RightUpperArm': (-0.45, -0.2, -0.9), 'LeftLowerArm': (0.3, -0.5, -0.8), 'RightLowerArm': (-0.3, -0.5, -0.8),
                    'LeftUpperLeg': (0.2, 0, -1), 'LeftLowerLeg': (0.2, 0, -1), 'RightUpperLeg': (-0.2, 0, -1), 'RightLowerLeg': (-0.2, 0, -1)},
          'reach': {'RightUpperArm': (-0.3, -0.85, -0.35), 'RightLowerArm': (-0.1, -1, -0.1), 'RightHand': (0, -1, 0.0), 'UpperTorso': (0, -0.25, 1), 'Head': (0, -0.2, 1)},
          'roar': {'Head': (0, 0.35, 1), 'UpperTorso': (0, 0.1, 1), 'LeftUpperArm': (0.85, -0.2, 0.45), 'RightUpperArm': (-0.85, -0.2, 0.45), 'LeftLowerArm': (0.6, -0.3, 0.75), 'RightLowerArm': (-0.6, -0.3, 0.75)}}
    finish(C, 'stomp', extra_poses=ex, record=dict(role='One reskinnable giant body for every huge threat (chain giant, storm giant, blue-fire knight)', body='giant: 4.0x hero (16.6 BU, 13 HH), small block head (14 % of its height), shoulders 3x its head, pillar legs, palms big enough to stand on',
           signature="one element per skin (rig 'skin': 0 iron and rust, 1 storm grey, 2 blue fire) + a glowing weak point in the chest (rig 'weak')",
           face_style='no face: glowing eyes + carved brows (glare, roar, hurt)', silhouette="a mass that overflows the 9:16 frame; per story: rig 'horns', 'crown', 'chains' (0/1)"))
    return C

# =============================================================================  19. THE MIRROR TWIN (data variant of the Hero kid)
HERO_KID = dict(body=('classic_r6', dict(H=4.16, head=0.96, neck=0.0, sw=1.6, ww=1.6, hw=1.6, td=0.8, at=0.8, ad=0.8, lgw=0.8, lgd=0.8, hand=0.4, fl=0.8, fh=0.2,
                                          f_leg=0.5, f_lt=0.11, arm_gap=0.0, lx=0.4, idle_out=6)),
                skin=(238, 196, 156), shirt=(206, 76, 48), trousers=(52, 58, 82), leather=(110, 70, 40), hair=('hero_crop', (74, 48, 32), 0.9), face='true_form')
def invert(c): return tuple(255 - v for v in c)
def build_mirror_twin():
    R_ = HERO_KID; btype, over = R_['body']
    C = Char('The Mirror Twin', 'mirror_twin')
    P = body_params(btype, **over)
    shirt = cloth('twin shirt', invert(R_['shirt']), weave=40, hem_dark=0.75, thread=(220, 230, 245), sheen=0.6)
    trous = cloth('twin trousers', invert(R_['trousers']), weave=44, hem_dark=0.75)
    lea = leather('twin leather', invert(R_['leather']), wear=0.3)
    sk = skin_mat('twin skin', R_['skin'])
    M = dict(UpperTorso=shirt, LowerTorso=shirt, UpperArm=shirt, LowerArm=shirt, Hand=sk, UpperLeg=trous, LowerLeg=trous, Foot=trous)
    build_body(C, P, M)
    face = dict(set='mirror_twin', exprs=['cold_smirk', 'bright', 'angry', 'shocked', 'scared'], fs=0.86, voff=0.0, cut=0.685,
                talk=('talk_closed', 'talk_half', 'talk_open'), blink='blink', spec=0.7, rough=0.35)
    make_head(C, P, R_['skin'], face)
    key, hc, hs = R_['hair']
    hair = add_hair(C, key, invert(hc), scale=hs)
    me = hair.data; me.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    try: me.flip_normals()
    except Exception: pass      # mirrored parting
    # belt + satchel strap, mirrored (the strap crosses the other way), and a silver crack line down the shirt
    bm = loft([(P['hip_z'] + 0.02, 1.65, 0.85, 12), (P['hip_z'] + 0.22, 1.65, 0.85, 12)], round_ends=0.03); C.obj('Belt', bm, lea, 'LowerTorso', origin=(0, 0, P['hip_z']))
    bm = cube_bm(0.22, 0.86, 2.08); xform(bm, T(0, 0, P['waist_z'] + 0.5) @ roty(-40)); C.obj('Satchel_strap', bm, lea, 'UpperTorso', origin=(0, 0, P['waist_z']), smooth=False, bevel=0.02)
    silver = metal('mirror silver', (220, 228, 240), rough=0.08, scratch=0.1)
    pts = [(-0.55, -0.42, P['sh_z'] - 0.1), (-0.3, -0.425, P['sh_z'] - 0.45), (-0.36, -0.425, P['sh_z'] - 0.6), (-0.05, -0.425, P['waist_z'] + 0.3), (0.12, -0.425, P['waist_z'] + 0.05)]
    C.obj('Shirt_crack', tube_bm(pts, 0.022, 6), silver, 'UpperTorso', origin=(0, 0, P['waist_z']))
    C.height = P['top']
    finish(C, 'idle', overrides={'idle': {'LeftUpperArm': (0.07, 0.0, -1), 'RightUpperArm': (-0.11, 0.0, -1)}},
           extra_poses={'mirror_cross': {'RightUpperArm': (-0.25, -0.62, -0.75), 'RightLowerArm': (0.95, -0.25, 0.1), 'LeftUpperArm': (0.25, -0.62, -0.75), 'LeftLowerArm': (-0.95, -0.25, 0.25), 'Head': (0, -0.08, 1)}},
           record=dict(role="The lead's shadow double: reflection and curse stories, 'the other me', identity swaps", body="identical to the Hero kid (data variant of the HERO_KID record: R6 blocks, 4.16 BU)",
           signature="the Hero kid's palette inverted (ice-cyan shirt, pale trousers, silver hair) + a silver crack", face_style="the Hero kid's own catalogue set, mirrored, with a cold smirk and a silver crack on every decal: cold smirk, bright, angry, shocked, scared; blink; talk",
           silhouette="the Hero kid's exact outline on purpose (crop hair mirrored, satchel strap the other way)"))
    return C

BUILDERS = [('oathbound', build_oathbound), ('crowd', build_crowd), ('first_rank', build_first_rank), ('true_form', build_true_form), ('rigger', build_rigger),
            ('ember_hatchling', lambda: build_ember('hatchling')), ('ember_grown', lambda: build_ember('grown')), ('jailer', build_jailer), ('squire', build_squire),
            # phase 2
            ('herald', build_herald), ('horde', build_horde)] + [(k, (lambda k_=k: build_horde_one(k_))) for k in HORDE] + [
            ('old_legend', build_old_legend), ('golden_sister', build_golden_sister), ('roll_merchant', build_roll_merchant), ('master_smith', build_master_smith),
            ('stone_keeper', build_stone_keeper), ('rival_heir', build_rival_heir), ('turned_friend', lambda: build_squire(turned=True)), ('mirror_twin', build_mirror_twin),
            ('jester', build_jester)]
if 'build_boss_giant' in globals(): BUILDERS.append(('boss_giant', build_boss_giant))
KEYNAMES = {'herald': ['The Herald'], 'horde': [v[0] for v in HORDE.values()], 'old_legend': ['The Old Legend'], 'golden_sister': ['The Golden Sister'],
            'roll_merchant': ['The Roll Merchant'], 'master_smith': ['The Master Smith'], 'stone_keeper': ['The Stone Keeper'], 'rival_heir': ['The Rival Heir'],
            'turned_friend': ['The Turned Friend'], 'mirror_twin': ['The Mirror Twin'], 'jester': ['The Jester'], 'boss_giant': ['The Boss Giant']}
KEYNAMES.update({k: [v[0]] for k, v in HORDE.items()})

def purge(name):
    """remove a character (collection, objects, meshes, its pose actions, its now-unused materials and face images) before rebuilding it"""
    col = bpy.data.collections.get('Cast v3 | ' + name)
    if not col: return
    mats, meshes, arms = set(), set(), set()
    for o in list(col.objects):
        if o.type == 'MESH': meshes.add(o.data); mats.update(m for m in o.data.materials if m)
        if o.type == 'ARMATURE': arms.add(o.data)
        bpy.data.objects.remove(o, do_unlink=True)
    for me in meshes:
        if me.users == 0: bpy.data.meshes.remove(me)
    for a in arms:
        if a.users == 0: bpy.data.armatures.remove(a)
    for a in list(bpy.data.actions):
        if a.name.startswith(name + ' | pose '): bpy.data.actions.remove(a)
    bpy.data.collections.remove(col)
    for m in mats:
        if m.users == 0: bpy.data.materials.remove(m)
    for im in list(bpy.data.images):
        if im.users == 0 and im.name.startswith('CV3 '): bpy.data.images.remove(im)
    print('purged', name)

if BASE:
    assert ONLY, 'BASE mode needs ONLY=<keys>'
    for k in ONLY:
        for n in KEYNAMES.get(k, []): purge(n)
    for m in bpy.data.materials:            # reuse the library's shared CV3 materials instead of making .001 copies
        if m.name.startswith('CV3 '): K._MATS[m.name] = m
    before = [c for c in bpy.data.collections if c.name.startswith('Cast v3 |')]

for key, fn in BUILDERS:
    if want(key): fn()

# tools text block (pose / face helpers) stored in the file
TOOLS = open('/tmp/claude-0/cast3/cast_v3_tools.py').read() if os.path.exists('/tmp/claude-0/cast3/cast_v3_tools.py') else ''
if TOOLS:
    t = bpy.data.texts.get('cast_v3_tools.py') or bpy.data.texts.new('cast_v3_tools.py'); t.clear(); t.write(TOOLS)

# lay the characters out side by side in the library file (each collection's rig stays at its own origin offset; reset X before use)
x = 0.0
if BASE:     # new ones go after everything already in the file
    bpy.context.view_layer.update()
    xs = [(o.matrix_world @ Vector(cn)).x for c in before for o in c.objects if o.type == 'MESH' for cn in o.bound_box]
    x = (max(xs) + 1.5) if xs else 0.0
for C in REG:   # side by side in the library file, in build order (each rig keeps this X offset when appended; zero it after appending)
    bpy.context.view_layer.update()
    xs = [ (o.matrix_world @ Vector(cn)).x for o in C.col.objects if o.type == 'MESH' for cn in o.bound_box]
    w = (max(xs) - min(xs)) if xs else 2.0
    C.rig.location.x = x - min(xs); x += w + 1.5
if os.environ.get('SAVE'):
    for c in bpy.data.collections:
        if c.name.startswith('Cast v3 |'): c['cast_v3'] = True
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVE'], compress=True)
    if os.path.exists(os.environ['SAVE'] + '1'): os.remove(os.environ['SAVE'] + '1')
    print('saved', os.environ['SAVE'])
import resource; print('NOTE peak RSS MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024)
