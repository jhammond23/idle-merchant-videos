# glTF backups of Cast v3 (for Blender 5.1 or any other tool). Plain colours instead of the procedural cloth/leather/metal shaders,
# the default expression baked onto a face texture (all expression PNGs are copied next to the glb), poses + face tables as glTF extras.
#   python3 -I export_glb.py   -> /tmp/claude-0/cast3/glb/<key>.glb + glb/faces/<set>/*.png + glb/poses/<key>.json
import os, sys, json, shutil
import bpy
from PIL import Image

BLEND = os.environ.get('BLEND', '/tmp/claude-0/cast3/cast-v3.blend'); OUT = '/tmp/claude-0/cast3/glb'
FACES = '/tmp/claude-0/cast3/faces'
os.makedirs(OUT, exist_ok=True); os.makedirs(OUT + '/poses', exist_ok=True); os.makedirs(OUT + '/faces', exist_ok=True); os.makedirs('/tmp/claude-0/cast3/scratch/bake', exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BLEND)
KEYS = [k for k in os.environ.get('KEYS', '').split(',') if k]      # phase 2: export only these

def flat(m):
    """replace a node-group material with a plain Principled carrying the group's colour / roughness / metallic"""
    nt = m.node_tree
    g = [n for n in nt.nodes if n.type == 'GROUP']
    if not g: return
    g = g[0]; name = g.node_tree.name
    col = g.inputs['Color'].default_value[:]
    rough = {'CV3 Cloth': 0.85, 'CV3 Leather': 0.55, 'CV3 Metal': g.inputs['Roughness'].default_value if 'Roughness' in g.inputs else 0.35}.get(name, 0.6)
    metal = g.inputs['Metallic'].default_value if 'Metallic' in g.inputs else 0.0
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]; b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = col; b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    nt.links.new(b.outputs[0], out.inputs['Surface'])

def face_bake(head, rig):
    """composite the rig's current expression over the head colour -> image texture on the FaceUV map"""
    m = head.data.materials[0]; nt = m.node_tree
    texs = [n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.image]
    names = [x.split(' ', 1)[1] for x in rig['face_names'].split(', ')]
    expr = names[int(rig['face'])]
    img = [t.image for t in texs if t.image.name.endswith('| ' + expr)]
    b = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    skin = b.inputs['Base Color'].default_value[:] if not b.inputs['Base Color'].is_linked else None
    if skin is None:   # colour driven by a node chain: use the first Mix node's A colour (the skin / steel / hood colour)
        mixes = [n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'RGBA' and not n.inputs['A'].is_linked]
        skin = mixes[0].inputs['A'].default_value[:] if mixes else (0.6, 0.45, 0.35, 1)
    f = lambda c: int(255 * (c ** (1 / 2.2)))
    S = 1024; base = Image.new('RGBA', (S, S), (f(skin[0]), f(skin[1]), f(skin[2]), 255))
    if img:
        src = bpy.path.abspath(img[0].filepath) if img[0].filepath else None
        p = os.path.join(FACES, img[0].name.split(' ', 1)[1].split(' | ')[0], expr + '.png')
        if os.path.exists(p):
            dec = Image.open(p).convert('RGBA').resize((S, S)); base.alpha_composite(dec)
    path = '/tmp/claude-0/cast3/scratch/bake/%s.png' % rig['char'].replace(' ', '_')
    base.save(path)
    nm = bpy.data.materials.new(m.name + ' (baked)'); t = nm.node_tree; bb = t.nodes['Principled BSDF']
    ti = t.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(path)
    uv = t.nodes.new('ShaderNodeUVMap'); uv.uv_map = 'FaceUV'; t.links.new(uv.outputs[0], ti.inputs[0]); t.links.new(ti.outputs['Color'], bb.inputs['Base Color'])
    bb.inputs['Roughness'].default_value = b.inputs['Roughness'].default_value; bb.inputs['Metallic'].default_value = b.inputs['Metallic'].default_value
    head.data.materials[0] = nm
    # copy the decal set for builders
    for t_ in texs:
        sset = t_.image.name.split(' ', 1)[1].split(' | ')[0]; e = t_.image.name.split(' | ')[-1]
        p = os.path.join(FACES, sset, e + '.png')
        if os.path.exists(p): os.makedirs(os.path.join(OUT, 'faces', sset), exist_ok=True); shutil.copy(p, os.path.join(OUT, 'faces', sset, e + '.png'))

for m in bpy.data.materials:
    if m.node_tree and any(n.type == 'GROUP' for n in m.node_tree.nodes): flat(m)

for c in bpy.data.collections:
    if not c.name.startswith('Cast v3 |'): continue
    rig = [o for o in c.objects if o.type == 'ARMATURE'][0]
    ALIAS = {'The Oathbound': 'oathbound', 'First Rank': 'first_rank', 'True-Form Lead': 'true_form', 'The Rigger': 'rigger', 'The Jailer': 'jailer', 'The Squire': 'squire',
             'Ember (hatchling)': 'ember_hatchling', 'Ember (grown)': 'ember_grown', 'Crowd Pointer': 'crowd_pointer', 'Crowd Belly-laugher': 'crowd_laugher',
             'Crowd Whisperer': 'crowd_whisperer', 'Crowd Gasper': 'crowd_gasper', 'Crowd Cheerer': 'crowd_cheerer', 'Crowd Bread-dropper': 'crowd_dropper'}
    key = rig.get('key') or ALIAS[c.name[10:]]
    if KEYS and key not in KEYS: continue
    head = [o for o in c.objects if o.name.endswith('| Head_Geo')]
    if head and 'face_names' in rig: face_bake(head[0], rig)
    for o in c.objects:   # drivers would not survive anyway
        if o.animation_data: o.animation_data_clear()
    extra_props = {k: rig[k] for k in ('sword', 'rarity', 'class', 'puppet', 'reskin') if k in rig}
    json.dump({'character': rig['char'], 'poses': json.loads(rig['poses']), 'face_names': rig.get('face_names'), 'mouth_names': rig.get('mouth_names'),
               'height_BU': rig.get('height_BU'), 'default_pose': rig.get('default_pose'), 'pose_props': json.loads(rig['pose_props']) if 'pose_props' in rig else None,
               'rig_props': extra_props, 'note': 'quaternions (w,x,y,z) per bone, rest-relative, R15 bone names; +X = character left, -Y = forward. Switchable props (rig_props) are exported in their default state only.'},
              open(os.path.join(OUT, 'poses', key + '.json'), 'w'), indent=1)
    loc = rig.location.copy(); rig.location = (0, 0, 0)
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in c.objects:
        try: o.hide_set(False); o.select_set(o.type in ('MESH', 'ARMATURE', 'EMPTY'))
        except Exception: pass
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, key + '.glb'), export_format='GLB', use_selection=True, export_apply=True, export_extras=True,
                              export_animations=False, export_yup=True)
    rig.location = loc
    print('GLB', key)
