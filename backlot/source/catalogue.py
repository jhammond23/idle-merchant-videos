"""Material catalogue sheet: one labelled swatch per library material.
usage: python3 -I catalogue.py [check|render] [res_x] [samples] [subset] [--cc0[=pack_root]]
--cc0: switch the materials to their CC0 scan picks (mats.CC0_PICKS, 1K render proxies) like the sets;
       scanned swatches are labelled 'name *'."""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
import mats, geo, look
from mathutils import Vector

pos = [a for a in sys.argv[1:] if not a.startswith('--')]
mode = pos[0] if pos else 'check'
resx = int(pos[1]) if len(pos) > 1 else 900
samples = int(pos[2]) if len(pos) > 2 else 16
subset = pos[3] if len(pos) > 3 else ''
cc0 = [a for a in sys.argv[1:] if a.startswith('--cc0')]
CC0_ROOT = (cc0[0].split('=', 1)[1] if cc0 and '=' in cc0[0] else '/mnt/user-data/uploads/3d-models/cc0-textures') if cc0 else None

look.reset_scene()
sc = bpy.context.scene
names = [n for n in mats.all_names() if not n.startswith('Shaft')]
if subset:
    keys = subset.split(',')
    names = [n for n in names if any(k.lower() in n.lower() for k in keys)]
col = geo.coll('Catalogue', sc.collection)
LABEL = bpy.data.materials.new('LABEL')
LABEL.diffuse_color = (0.02, 0.02, 0.02, 1)
_p = LABEL.node_tree.nodes.get('Principled BSDF')
if _p:
    _p.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1)
    _p.inputs['Roughness'].default_value = 0.9
cols = 9
pitch = 1.25          # metres between swatches
rows = math.ceil(len(names) / cols)
for i, n in enumerate(names):
    r, c = divmod(i, cols)
    x = (c - (cols - 1) / 2) * pitch
    y = -((r - (rows - 1) / 2) * pitch) * 1.0
    b = geo.Builder('SW ' + n)
    if n.startswith(('Flame', 'Embers', 'Glow')):
        b.cbox((x, y, 0.25), (0.5, 0.5, 0.5), n)
    elif n.startswith(('Water',)):
        b.box(x - 0.45, y - 0.45, 0.0, x + 0.45, y + 0.45, 0.18, n)
    else:
        # a slab with a sloped front so both the top and a 'wall' face show the pattern
        b.cbox((x, y, 0.06), (0.95, 0.95, 0.12), n, 0.01)
        b.cbox((x, y + 0.34, 0.12 + 0.2), (0.95, 0.12, 0.4), n, 0.01)
    objs = b.finish(col)
    if n.startswith('Water'):
        for o in objs:
            me = o.data
            a = me.attributes.new('foam', 'FLOAT', 'POINT')
            a.data.foreach_set('value', [0.0] * len(me.vertices))
    t = bpy.data.curves.new('L ' + n, 'FONT')
    t.body = n
    t.size = 0.13 * geo.M
    t.align_x = 'CENTER'
    to = bpy.data.objects.new('L ' + n, t)
    to.location = (x * geo.M, (y - 0.57) * geo.M, 0.01)
    col.objects.link(to)
    to.data.materials.append(LABEL)

if CC0_ROOT:
    import backlot_api
    scanned = mats.apply_picks(CC0_ROOT, log=lambda m: None)
    for n in scanned:
        to = bpy.data.objects.get('L ' + n)
        if to:
            to.data.body = n + ' *'
    print('scanned swatches', len(scanned), 'proxies', backlot_api.use_texture_proxies())
ground = geo.Builder('Ground')
W = cols * pitch + 1.0
H = rows * pitch + 1.2
ground.box(-W / 2, -H / 2, -0.02, W / 2, H / 2, 0.0, 'Plaster White')
ground.finish(col)
look.render_settings(sc, 'preview', samples)
sc.render.resolution_percentage = 100
sun = look.sun_obj(col, 'DAY', 200.0)
look.world_sky(sc, 'DAY', sun_dir=look.sun_direction(sun))
cam = bpy.data.cameras.new('cat')
cam.type = 'ORTHO'
cam.ortho_scale = max(W, H * 1.0) * geo.M * 1.02
co = bpy.data.objects.new('cat', cam)
sc.collection.objects.link(co)
Z = 30 * geo.M
co.location = (0, -math.tan(math.radians(20)) * Z, Z)
co.rotation_euler = (math.radians(20), 0, 0)
cam.ortho_scale = max(W, H * math.cos(math.radians(20))) * geo.M * 1.02
sc.camera = co
sc.render.resolution_x = resx
sc.render.resolution_y = int(resx * H * math.cos(math.radians(20)) / W)
out = '/tmp/claude-0/backlot/previews/material_catalogue.jpg' if not subset else '/tmp/claude-0/backlot/tmp/cat_%s.jpg' % subset.replace(',', '_')[:30]
sc.render.filepath = out
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 90
print('materials', len(names))
if mode == 'render':
    bpy.ops.render.render(write_still=True)
    print('wrote', out)
