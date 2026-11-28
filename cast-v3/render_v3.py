# Cast v3 check renders (Claude, 11-27). Cycles CPU, cheap settings.
#   MODE=preview KEYS=first_rank[,..] [VIEWS=front,34] OUT=...           quick look
#   MODE=lineup  OUT=/tmp/claude-0/cast3/lineup.png                        all new characters + Hero kid + Little sister
#   MODE=turn    KEY=first_rank OUT=...                                    5-view turnaround (front, 3/4, side, back, 3/4 back)
#   MODE=poses   KEY=first_rank OUT=...                                    every named pose side by side (clipping test)
#   MODE=faces   KEY=first_rank OUT=...                                    bust per expression (+ talk mouths, blink, glow)
#   MODE=silhouette OUT=...                                                black silhouettes (Workbench), orthographic, true scale
import os, sys, math, json
sys.path.insert(0, '/tmp/claude-0/cast3')
import bpy
from mathutils import Vector, Matrix, Quaternion

BLEND = os.environ.get('BLEND', '/tmp/claude-0/cast3/cast-v3.blend')
V2 = '/tmp/claude-0/cast2/pkg/cast-v2.blend'
MODE = os.environ.get('MODE', 'preview'); OUT = os.environ.get('OUT', '/tmp/claude-0/cast3/scratch/preview.png')
RES = tuple(map(int, os.environ.get('RES', '1200x900').split('x'))); SAMP = int(os.environ.get('SAMP', '16'))
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
import atexit, resource
atexit.register(lambda: print('NOTE peak RSS MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024))
TEXMAX = int(os.environ.get('TEXMAX', '0'))          # phase 2: shrink the face textures of the characters on screen (lineups; in memory only, never saved)
def shrink_textures(cols):
    if not TEXMAX: return
    ims = set()
    for c in cols:
        for o in c.all_objects:
            if o.type != 'MESH': continue
            for m in o.data.materials:
                if m and m.node_tree:
                    for nd in m.node_tree.nodes:
                        if nd.type == 'TEX_IMAGE' and nd.image: ims.add(nd.image)
    for im in ims:
        if im.size[0] > TEXMAX: im.scale(TEXMAX, TEXMAX)

def srgb(r, g, b):
    f = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
    return (f(r), f(g), f(b))

CHARS = {}
for c in bpy.data.collections:
    if c.name.startswith('Cast v3 |'):
        rig = [o for o in c.objects if o.type == 'ARMATURE'][0]
        CHARS[c.name[10:]] = (c, rig); rig.location = (0, 0, 0)
KEY2NAME = {}
for n, (c, rig) in CHARS.items():
    k = n.lower().replace('the ', '').replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
    KEY2NAME[k] = n
    if 'key' in rig: KEY2NAME[rig['key']] = n
ALIASES = {'oathbound': 'The Oathbound', 'first_rank': 'First Rank', 'true_form': 'True-Form Lead', 'rigger': 'The Rigger', 'jailer': 'The Jailer', 'squire': 'The Squire',
           'ember_hatchling': 'Ember (hatchling)', 'ember_grown': 'Ember (grown)', 'crowd_pointer': 'Crowd Pointer', 'crowd_laugher': 'Crowd Belly-laugher',
           'crowd_whisperer': 'Crowd Whisperer', 'crowd_gasper': 'Crowd Gasper', 'crowd_cheerer': 'Crowd Cheerer', 'crowd_dropper': 'Crowd Bread-dropper'}
def name_of(key): return ALIASES.get(key, KEY2NAME.get(key, key))

def hide_all_chars():
    for n, (c, rig) in CHARS.items():
        c.hide_render = True; c.hide_viewport = True
def show(n):
    c, rig = CHARS[n]; c.hide_render = False; c.hide_viewport = False; return c, rig

def set_pose(rig, name):
    table = json.loads(rig['poses'])
    for b, q in table[name].items():
        pb = rig.pose.bones.get(b)
        if pb: pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = Quaternion(q)
    if 'pose_props' in rig:          # e.g. the Old Legend's sword in hand for 'raise_sword'
        pp = json.loads(rig['pose_props'])
        for k, v in list(pp.get('_default', {}).items()) + list(pp.get(name, {}).items()): rig[k] = v

def dup_char(n, suffix):
    """full copy of a character (shares mesh data) so copies can hold different poses / faces"""
    c, rig = CHARS[n]; mp = {}
    newc = bpy.data.collections.new(c.name + suffix); sc.collection.children.link(newc)
    for o in c.objects:
        k = o.copy(); mp[o] = k; newc.objects.link(k)
    for o, k in mp.items():
        if o.parent in mp: k.parent = mp[o.parent]
        if k.animation_data:
            for d in k.animation_data.drivers:
                for v in d.driver.variables:
                    for t in v.targets:
                        if t.id in mp: t.id = mp[t.id]
    return newc, mp[rig]

def link_v2(names):
    with bpy.data.libraries.load(V2, link=False) as (src, dst): dst.collections = names
    out = {}
    for c in dst.collections:
        sc.collection.children.link(c)
        root = [o for o in c.objects if o.parent is None and o.type == 'EMPTY'][0]
        out[c.name] = root
    return out

# ------------------------------------------------------------------ look
def mat(name, rgb, rough=0.8):
    m = bpy.data.materials.new(name); b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*srgb(*rgb), 1); b.inputs['Roughness'].default_value = rough; return m
def noise_mat(name, c1, c2, scale=1.4, rough=0.85, bump=0.2, voronoi=True):
    m = bpy.data.materials.new(name); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexVoronoi' if voronoi else 'ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale
    nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (*srgb(*c1), 1); r.color_ramp.elements[1].color = (*srgb(*c2), 1)
    nt.links.new(n.outputs['Distance' if voronoi else 'Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = rough
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; nt.links.new(n.outputs['Distance' if voronoi else 'Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
def plane(name, size, loc, rot, m):
    me = bpy.data.meshes.new(name); s = size
    me.from_pydata([(-s[0] / 2, -s[1] / 2, 0), (s[0] / 2, -s[1] / 2, 0), (s[0] / 2, s[1] / 2, 0), (-s[0] / 2, s[1] / 2, 0)], [], [(0, 1, 2, 3)])
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; me.materials.append(m); return o
def boxo(name, size, loc, m):
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = loc; me.materials.append(m); return o

def sun(el, rot, energy, color=(1, 0.93, 0.82), angle=2.0, name='sun'):
    d = bpy.data.lights.new(name, 'SUN'); d.energy = energy; d.color = color; d.angle = math.radians(angle)
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.rotation_euler = (math.radians(90 - el), 0, math.radians(rot)); return o
def sky(strength=0.35, el=34, rot=150):
    w = bpy.data.worlds.new('W'); sc.world = w; nt = w.node_tree; s = nt.nodes.new('ShaderNodeTexSky')
    for t in ('MULTIPLE_SCATTERING', 'NISHITA'):
        try: s.sky_type = t; break
        except Exception: pass
    s.sun_elevation = math.radians(el); s.sun_rotation = math.radians(rot)
    bg = nt.nodes['Background']; bg.inputs['Strength'].default_value = strength; nt.links.new(s.outputs['Color'], bg.inputs['Color'])
def flat_world(rgb, strength=1.0):
    w = bpy.data.worlds.new('W'); sc.world = w; bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (*srgb(*rgb), 1); bg.inputs['Strength'].default_value = strength
def camera(loc, at, lens=50, ortho=None):
    c = bpy.data.cameras.new('cam'); c.lens = lens; c.clip_start = 0.1; c.clip_end = 1000
    if ortho: c.type = 'ORTHO'; c.ortho_scale = ortho
    o = bpy.data.objects.new('cam', c); sc.collection.objects.link(o); sc.camera = o; o.location = loc
    d = Vector(at) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return o
def render_setup(w, h, samples, exposure=-2.7):
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples; sc.cycles.use_denoising = os.environ.get('DENOISE', '1') == '1'
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transparent_max_bounces = 8; sc.cycles.transmission_bounces = 2
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.05
    sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.film_transparent = False
    vs = sc.view_settings; vs.view_transform = 'Standard'
    try: vs.look = 'Medium High Contrast'
    except Exception: pass
    vs.exposure = exposure
    sc.render.threads_mode = 'FIXED'; sc.render.threads = 2
    try: sc.cycles.use_auto_tile = True; sc.cycles.tile_size = int(os.environ.get('TILE', '512'))
    except Exception: pass
    try: sc.cycles.denoising_prefilter = os.environ.get('PREFILTER', 'FAST')   # phase 2: FAST keeps OIDN ~450 MB (ACCURATE ~600)
    except Exception: pass

def town_set(width=80, wall_y=14.0):
    """plain town backdrop like the Cast v2 sheet: cobbles, plaster wall with a timber band and banners"""
    g = plane('ground', (width * 4, 600, 1), (0, -250, 0), (0, 0, 0), noise_mat('cobble', (186, 170, 150), (150, 136, 120), scale=1.6, bump=0.25))
    wall = plane('wall', (width * 2, 30, 1), (0, wall_y, 12), (math.radians(90), 0, 0), noise_mat('plaster', (222, 200, 168), (196, 170, 136), scale=0.6, bump=0.15, voronoi=False))
    tim = mat('timber', (92, 62, 40), 0.8)
    boxo('beam_lo', (width * 2, 0.4, 0.5), (0, wall_y - 0.2, 4.2), tim); boxo('beam_hi', (width * 2, 0.4, 0.5), (0, wall_y - 0.2, 15.5), tim)
    for i, x in enumerate(range(-int(width), int(width) + 1, 7)):
        boxo('ban%d' % i, (2.2, 0.1, 5.0), (x, wall_y - 0.25, 10.6), mat('ban%d' % i, (176, 40, 46) if i % 2 else (40, 70, 150), 0.8))

def lights_day(rim=True):
    sky(0.35, 34, 150); sun(34, 150, 4.5)
    if rim: sun(28, -25, 2.2, color=(0.75, 0.85, 1.0), name='rim')

def write(path):
    sc.render.filepath = path; bpy.ops.render.render(write_still=True); print('WROTE', path)

def bbox_of(col):
    """world bbox of a character's meshes (evaluated, posed)"""
    dg = bpy.context.evaluated_depsgraph_get(); mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in col.objects:
        if o.type != 'MESH' or o.hide_render: continue
        if o.name.endswith('| Aura'): continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box:
            w = oe.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    return mn, mx

ORDER2 = ['The Herald', 'The Mirror Twin', 'Little sister', 'Hero kid', 'The Turned Friend', 'The Roll Merchant', 'Horde Moss', 'Horde Frost', 'Horde Slate', 'Horde Ash',
          'The Golden Sister', 'The Rival Heir', 'The Master Smith', 'The Old Legend', 'The Jester', 'The Stone Keeper']
ORDER = ['Crowd Gasper', 'Ember (hatchling)', 'Little sister', 'Hero kid', 'Ember (grown)', 'The Squire', 'Crowd Belly-laugher', 'Crowd Whisperer', 'Crowd Cheerer',
         'First Rank', 'Crowd Bread-dropper', 'The Jailer', 'The Rigger', 'Crowd Pointer', 'The Oathbound', 'True-Form Lead']
if os.environ.get('ROW') == '2': ORDER = ORDER2
elif os.environ.get('ROW') == 'all': ORDER = ORDER + [n for n in ORDER2 if n not in ORDER]
elif os.environ.get('ROW') == 'giant': ORDER = ['Little sister', 'Hero kid', 'The Oathbound', 'The Boss Giant']

# ================================================================== modes
if MODE == 'preview':
    keys = os.environ.get('KEYS', 'first_rank').split(','); views = os.environ.get('VIEWS', 'front,34').split(',')
    hide_all_chars(); x = 0.0; mxh = 0
    for k in keys:
        n = name_of(k); c, rig = show(n)
        if os.environ.get('POSE'): set_pose(rig, os.environ['POSE'])
        if os.environ.get('FACE'): rig['face'] = int(os.environ['FACE'])
        bpy.context.view_layer.update(); mn, mx = bbox_of(c); w = mx.x - mn.x
        rig.location.x = x - mn.x; x += w + 0.8; mxh = max(mxh, mx.z)
        if '34' in views:
            c2, rig2 = dup_char(n, ' 34'); rig2.location.x = x - mn.x + 0.3; rig2.rotation_euler.z = math.radians(-35); x += w + 1.2
            if os.environ.get('FACE'): rig2['face'] = int(os.environ['FACE'])
        if 'back' in views:
            c3, rig3 = dup_char(n, ' back'); rig3.location.x = x - mn.x + 0.3; rig3.rotation_euler.z = math.radians(180); x += w + 1.2
    cx = x / 2; town_set(); lights_day()
    hgt = mxh * 1.12; dist = max((x / 2) / 0.3, (hgt / 2) / (0.3 * RES[1] / RES[0])) + 2
    camera((cx, -dist, mxh * 0.52), (cx, 0, mxh * 0.48), lens=60)
    render_setup(RES[0], RES[1], SAMP); write(OUT)

elif MODE == 'lineup':
    hide_all_chars(); v2 = link_v2(['Cast v2 | Hero kid', 'Cast v2 | Little sister'])
    roots = {'Hero kid': v2['Cast v2 | Hero kid'], 'Little sister': v2['Cast v2 | Little sister']}
    for n in ORDER:
        if n in CHARS: show(n)
    shrink_textures([CHARS[n][0] for n in ORDER if n in CHARS] + list(v2.values()) and [CHARS[n][0] for n in ORDER if n in CHARS])
    bpy.context.view_layer.update()
    x = 0.0; gap = 0.55; tops = []
    for n in ORDER:
        if n in roots:
            r = roots[n]; w = 4.1 * r.scale.x; r.location = (x + w / 2, 0, 0); r.rotation_euler = (0, 0, 0); x += w + gap; tops.append(5.2 * r.scale.x); continue
        if n not in CHARS: continue
        c, rig = CHARS[n]; mn, mx = bbox_of(c); w = mx.x - mn.x
        if n.startswith('Ember'): w = max(w, 0.9)
        rig.location.x = x - mn.x; x += w + gap; tops.append(mx.z)
    town_set(width=x + 20); lights_day()
    cx = x / 2; H = max(tops)
    aspect = RES[0] / RES[1]; lens = 85
    half_w = x / 2 + 1.0; dist = half_w / math.tan(math.atan(36 / 2 / lens)) if aspect > 1 else 60
    th = math.tan(math.atan(18 / lens)) / aspect; dist = max(dist, H * 1.25 / 2 / th)
    cam = camera((cx, -dist, H * 0.62), (cx, 0, H * 0.5), lens=lens)
    render_setup(RES[0], RES[1], SAMP)
    parts = int(os.environ.get('PARTS', '1'))
    if parts > 1:     # phase 2: render the frame as vertical strips (same camera, narrower sensor + lens shift) so the denoiser stays small; stitch later
        i = int(os.environ['PART']); cam.data.sensor_fit = 'HORIZONTAL'; cam.data.sensor_width = 36.0 / parts
        sc.render.resolution_x = RES[0] // parts; cam.data.shift_x = (i - (parts - 1) / 2.0)
        if RES[1] > RES[0] // parts: cam.data.shift_x *= (RES[0] / parts) / RES[1]
    write(OUT)

elif MODE in ('turn', 'poses', 'faces', 'variants'):
    n = name_of(os.environ['KEY']); hide_all_chars(); c, rig = show(n)
    bpy.context.view_layer.update(); mn, mx = bbox_of(c); w = mx.x - mn.x; H = mx.z
    flat_world((70, 78, 92), 0.0)
    g = plane('floor', (3000, 3000, 1), (0, 0, 0), (0, 0, 0), mat('floor', (150, 150, 158), 0.9))          # phase 2: big enough for the giant's pose row
    bd = plane('backdrop', (3000, 1000, 1), (0, max(6, H) * 1.2 + 4, 250), (math.radians(90), 0, 0), mat('bd', (112, 124, 146), 0.95))
    sky(0.25, 40, 150); sun(40, 150, 4.2); sun(26, -30, 2.4, color=(0.75, 0.85, 1.0), name='rim'); sun(20, 250, 0.9, color=(1, 0.95, 0.9), name='fill')
    def fit_cam(X0, X1, H, lens=70, extra=1.0):
        aspect = RES[0] / RES[1]; tw = math.tan(math.atan(18 / lens)); th = tw / aspect
        dist = max((X1 - X0) / 2 / tw, H * 1.08 / 2 / th) * extra + 1.0
        cx = (X0 + X1) / 2; camera((cx, -dist, H * 0.5), (cx, 0, H * 0.5), lens=lens)
    POSEFACE = {'laugh': ['laughing', 'grin', 'gloat', 'happy', 'bright', 'cackle', 'delighted', 'proud', 'smile', 'announce', 'approving', 'roar'], 'cheer': ['laughing'],
                'shocked': ['shocked', 'panic', 'scared', 'surprised', 'terrified', 'jaw_drop', 'stunned'],
                'gasp': ['shocked'], 'drop': ['shocked'], 'fists_up': ['furious', 'angry', 'brave', 'fierce', 'locked_in', 'determined', 'stern', 'scowl', 'glare'],
                'point': ['laughing', 'smug', 'sneer', 'gloat', 'calm_smirk', 'curious', 'glare', 'sly_grin', 'knowing_grin', 'sly', 'cold_smirk', 'stern', 'doubtful', 'announce'],
                'arms_crossed': ['smug', 'sulk', 'deadpan', 'calm_smirk', 'proud', 'glare', 'neutral', 'cold', 'cool', 'judging', 'solemn', 'doubtful', 'serious', 'cold_smirk'],
                'roar': ['fierce', 'roar'], 'trumpet': ['trumpet'], 'proclaim': ['announce'], 'hunched': ['sly'], 'stand_tall': ['fierce'], 'raise_sword': ['fierce'],
                'trophy_up': ['proud'], 'welcome': ['welcome'], 'offer': ['knowing_grin'], 'strike': ['stern'], 'raise_stone': ['stunned'], 'en_garde': ['determined'],
                'puppet': ['sly_grin'], 'bow': ['wink'], 'mirror_cross': ['cold_smirk'], 'hunch': ['glare']}
    def face_for(r, pose):
        names = [x_.split(' ', 1)[1] for x_ in r.get('face_names', '').split(', ') if ' ' in x_]
        for want in POSEFACE.get(pose, []):
            if want in names: r['face'] = names.index(want); return
    if MODE == 'variants':    # phase 2: copies of one character with different rig properties (skins, switches), e.g. VARIANTS='[{"skin":0},{"skin":1}]'
        vs = json.loads(os.environ['VARIANTS']); step = w * 1.1 + 1.0
        for i, props in enumerate(vs):
            r = rig if i == 0 else dup_char(n, ' v%d' % i)[1]
            for k_, v_ in props.items(): r[k_] = v_
            r.location.x = i * step; r.rotation_euler.z = math.radians(-20)
        fit_cam(-step * 0.6, step * (len(vs) - 0.4), H * 1.05)
        render_setup(RES[0], RES[1], SAMP, exposure=-2.5); write(OUT)
    elif MODE == 'turn':
        angles = [0, -45, -90, 180, 135]; step = max(w, mx.y - mn.y) * 1.15 + 0.6
        for i, a in enumerate(angles):
            r = rig if i == 0 else dup_char(n, ' t%d' % i)[1]
            r.location.x = i * step; r.rotation_euler.z = math.radians(a)
        fit_cam(min(-step * 0.55, mn.x - 0.4), max(step * 4.55, 4 * step + mx.x + 0.4), H)
        render_setup(RES[0], RES[1], SAMP, exposure=-2.5); write(OUT)
    elif MODE == 'poses':
        names = list(json.loads(rig['poses']).keys())
        step = w * 1.15 + 0.9
        for i, p in enumerate(names):
            r = rig if i == 0 else dup_char(n, ' p%d' % i)[1]
            set_pose(r, p); face_for(r, p); r.location.x = i * step; r.rotation_euler.z = math.radians(-18)
        fit_cam(-step * 0.6, step * (len(names) - 0.4), H * 1.08)
        render_setup(RES[0], RES[1], SAMP, exposure=-2.5)
        print('POSES', ','.join(names)); write(OUT)
    else:  # faces: busts
        names = [x_.split(' ', 1)[1] for x_ in rig['face_names'].split(', ')]
        talk = [x_.split(' ', 1)[1] for x_ in rig.get('mouth_names', '').split(', ')[1:]] if rig.get('mouth_names', 'no').startswith('0') else []
        has_blink = 'blink' in [m.name for m in []] or any(nd.type == 'TEX_IMAGE' and nd.image and nd.image.name.endswith('| blink') for m in bpy.data.materials if m.name == n + ' | face' for nd in m.node_tree.nodes)
        cells = [('face', i, e) for i, e in enumerate(names)] + [('mouth', j + 1, 'talk ' + t) for j, t in enumerate(talk)]
        if has_blink: cells.append(('blink', 1, 'blink'))
        if 'eye_glow' in str([nd.image.name for m in bpy.data.materials if m.name == n + ' | face' for nd in m.node_tree.nodes if nd.type == 'TEX_IMAGE']): cells.append(('glow', 0, 'glow toggled'))
        hz = rig.data.bones['Head'].head_local.z; hh = rig.data.bones['Head'].length
        ember = n.startswith('Ember'); cols = len(cells)
        spacing = (mx.x - mn.x) * 1.15 if ember else hh * 2.3
        ch = (mx.z - mn.z) * 1.12 if ember else hh * 1.9
        for i, (prop, val, lab) in enumerate(cells):
            col_, r = (c, rig) if i == 0 else dup_char(n, ' f%d' % i)
            set_pose(r, 'idle' if 'idle' in r['poses'] else r['default_pose'])
            r.location = (i * spacing - (0 if not ember else 0), 0, 0); r.rotation_euler.z = math.radians(-6)
            if prop == 'face': r['face'] = val
            else: r[prop] = val
            if prop == 'glow': r['glow'] = 0.0 if float(rig['glow']) > 0.5 else 1.0; r['face'] = 0
            if not ember:
                for o in col_.objects:
                    if o.type == 'MESH' and not (o.parent_type == 'BONE' and o.parent_bone == 'Head'):
                        if o.animation_data: o.animation_data_clear()      # phase 2: driven prop visibility (e.g. a planted sword) must not override the bust crop
                        o.hide_render = True
        g.hide_render = True
        cell = int(os.environ.get('CELL', '400'))
        cz = (hz + hh * 0.6) if not ember else (mn.z + mx.z) / 2
        X = (cols - 1) * spacing
        camera((X / 2, -60, cz), (X / 2, 0, cz), lens=50, ortho=cols * spacing)
        render_setup(cols * cell, int(cell * ch / spacing), SAMP, exposure=-2.4)
        print('CELLS', '|'.join(l for _, _, l in cells)); write(OUT)

elif MODE == 'silhouette':
    hide_all_chars(); v2 = link_v2(['Cast v2 | Hero kid', 'Cast v2 | Little sister'])
    roots = {'Hero kid': v2['Cast v2 | Hero kid'], 'Little sister': v2['Cast v2 | Little sister']}
    for n in ORDER:
        if n in CHARS: show(n)
    bpy.context.view_layer.update(); x = 0.0; gap = 0.7; H = 0
    for n in ORDER:
        if n in roots:
            r = roots[n]; w = 4.1 * r.scale.x; r.location = (x + w / 2, 0, 0); x += w + gap; continue
        if n not in CHARS: continue
        c, rig = CHARS[n]
        for o in c.objects:
            if o.name.endswith('| Aura') or o.name.endswith('| Cheat_sparks'): o.hide_render = True
        mn, mx = bbox_of(c); w = mx.x - mn.x
        rig.location.x = x - mn.x; rig.rotation_euler.z = math.radians(float(os.environ.get('ROT', '0'))); x += w + gap; H = max(H, mx.z)
    sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
    sh.light = 'FLAT'; sh.color_type = 'SINGLE'; sh.single_color = (0, 0, 0); sh.show_object_outline = False; sh.show_shadows = False; sh.show_cavity = False
    sh.background_type = 'VIEWPORT'; sh.background_color = (1, 1, 1)
    sc.display.render_aa = '8'
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0
    sc.render.resolution_x = RES[0]; sc.render.resolution_y = RES[1]
    ortho = max(x + 1.0, (H + 0.6) * RES[0] / RES[1]); print('NOTE ortho %.3f' % ortho)
    if os.environ.get('ORTHO'): ortho = float(os.environ['ORTHO'])     # phase 2: one shared scale for both silhouette rows
    camera((x / 2, -100, H / 2 + 0.1), (x / 2, 0, H / 2 + 0.1), ortho=ortho)
    print('ORDER', '|'.join(n for n in ORDER if n in CHARS or n in roots)); write(OUT)
