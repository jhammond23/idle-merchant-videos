"""Shared set scaffolding: collections, presets, saving, reuse of the older Marches models."""
import os, math
import bpy
from mathutils import Vector, Matrix
import geo, mats, look, kit
try:
    bpy.context.preferences.filepaths.save_version = 0      # no <set>.blend1 backups (disk is tight)
except Exception:
    pass

M = geo.M
OUT = '/tmp/claude-0/backlot'


def start(code, title):
    sc = look.reset_scene()
    mats.global_group()
    master = geo.coll('Backlot | ' + title, sc.collection)
    master['bl_code'] = code
    cols = {
        'set': geo.coll('%s Set' % code, master),
        'marks': geo.coll('%s Marks' % code, master),
        'cams': geo.coll('%s Cameras' % code, master),
    }
    for p in look.PRESETS:
        cols[p] = geo.coll('%s Light %s' % (code, p), master)
    return sc, master, cols


def finish(sc, master, cols, title, code, default_cam, worlds, path, exposure=None):
    for p in look.PRESETS:
        master['world_' + p] = worlds[p]
        master['exposure_' + p] = (exposure or look.EXPOSURE)[p]
    scenes = look.make_preset_scenes(sc, master, title, {p: cols[p] for p in look.PRESETS}, worlds, default_cam)
    if exposure:
        for p, s in scenes.items():
            s.view_settings.exposure = exposure[p]
    for img in bpy.data.images:
        if img.source == 'FILE' and not img.packed_file:
            try:
                img.pack()
            except Exception as e:
                print('pack failed', img.name, e)
    try:
        bpy.context.window.scene = scenes['DAY']
    except Exception:
        pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        bpy.context.preferences.filepaths.save_version = 0
    except Exception:
        pass
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    return scenes


# ----------------------------------------------------------------------------------------------
# Older Marches models, re-skinned with the backlot library
# ----------------------------------------------------------------------------------------------
OLD = '/mnt/user-data/uploads/library/sets'
OLD_MAP = {
    'Chalk': 'Limestone', 'Ochre ashlar': 'Ashlar', 'Fieldstone': 'Rubble', 'Oak': 'Planks',
    'Juniper shingles': 'Roof Clay Old', 'Mulberry slate': 'Roof Slate', 'Lapis scales': 'Roof Slate',
    'Peacock copper': 'Copper Verdigris', 'Black oak': 'Timber Dark', 'Adze cut': 'Timber Oak',
    'Limewash': 'Plaster Cream', 'Limestone trim': 'Limestone', 'Iron': 'Iron Black', 'Brass': 'Brass',
    'Gold leaf': 'Gold', 'Lantern': 'Glass Leaded', 'Deep glass': 'Glass Leaded', 'Marine': 'Paint Green',
    'Oxblood': 'Paint Red', 'Wisteria': 'Paint Blue', 'Velvet': 'Paint Blue', 'Parchment': 'Cloth White',
    'Lichen': 'Leaf', 'Aquamarine': 'Glass Leaded', 'Rock': 'Rock', 'Sea basalt': 'Ashlar Grey',
    'Night stone': 'Ashlar Grey', 'Emberstone': 'Ashlar Grey', 'Ironstone': 'Iron Black', 'Salt trim': 'Limestone',
    'Star crystal': 'Glass Leaded',
}


def old_model(K, relpath, override=None, skip=('Studio floor',), lit_lantern=True):
    """Append an older Marches model into Kit K (metres), remapping its materials to the library.
    Faces whose old material was 'Lantern' also get a lit copy in the night builder."""
    mp = dict(OLD_MAP)
    mp.update(override or {})
    path = os.path.join(OLD, relpath)
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    count = 0
    for o in dst.objects:
        if o is None or o.type != 'MESH' or o.name.startswith(skip):
            continue
        me = o.data
        mw = o.matrix_world.copy()
        verts = [mw @ v.co for v in me.vertices]
        names = [m.name.split('.')[0] if m else 'Chalk' for m in me.materials] or ['Chalk']
        faces, fm = [], []
        lit_faces = []
        for p in me.polygons:
            old = names[p.material_index] if p.material_index < len(names) else names[0]
            faces.append(tuple(p.vertices))
            fm.append(mp.get(old, 'Limestone'))
            if old == 'Lantern' and lit_lantern:
                lit_faces.append(p)
        K.b.mesh(verts, faces, fm, None, False, None)
        for p in lit_faces:
            n = p.normal
            K.n.poly([verts[i] + (mw.to_3x3() @ n).normalized() * 0.012 for i in p.vertices], 'Glass Window Lit')
        count += len(faces)
    for o in dst.objects:
        if o is not None:
            me = o.data if o.type == 'MESH' else None
            bpy.data.objects.remove(o)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)
    for m in list(bpy.data.materials):
        if m.users == 0 and not m.name.startswith('BL '):
            bpy.data.materials.remove(m)
    for img in list(bpy.data.images):
        if img.users == 0:
            bpy.data.images.remove(img)
    return count
