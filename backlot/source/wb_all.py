"""Workbench framing check of every camera of a set (with the preview cast): python3 -I wb_all.py <set>"""
import sys, os
sys.path[:0] = ['/tmp/claude-0/backlot/source']
import bpy, castref
from PIL import Image
setname = sys.argv[1]
bpy.ops.wm.open_mainfile(filepath='/tmp/claude-0/backlot/%s/%s.blend' % (setname, setname))
sc = [s for s in bpy.data.scenes if s.get('bl_preset') == 'DAY'][0]
code = [c for c in bpy.data.collections if c.name.startswith('Backlot |')][0]['bl_code']
CAST = {'MARK_HERO': 'Hero kid', 'MARK_RIVAL': 'Rich kid', 'MARK_SIBLING': 'Little sister', 'MARK_RULER': 'Queen',
        'MARK_CROWD_1': 'Newbie', 'MARK_CROWD_2': 'Bacon kid', 'MARK_CROWD_3': 'Big kid', 'MARK_CROWD_4': 'Girl hero',
        'MARK_CROWD_5': 'Slender teen', 'MARK_CROWD_6': 'Wizard', 'MARK_CROWD_7': 'Goofy guard', 'MARK_CROWD_8': 'Villain'}
castref.stage(sc, None, {'%s_%s' % (code, k): v for k, v in CAST.items()})
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_cavity = True; sh.show_shadows = True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 270, 480, 100
sc.render.image_settings.file_format = 'JPEG'
cams = sorted([o for o in bpy.data.objects if o.type == 'CAMERA' and o.name.startswith(code + '_')], key=lambda o: o.name)
tiles = []
for c in cams:
    sc.camera = c
    out = '/tmp/claude-0/backlot/tmp/wball_%s.jpg' % c.name
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True, scene=sc.name)
    tiles.append((c.name, out))
W = 270 * 5
H = 480 * ((len(tiles) + 4) // 5)
sheet = Image.new('RGB', (W, H))
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
for i, (n, f) in enumerate(tiles):
    x, y = (i % 5) * 270, (i // 5) * 480
    sheet.paste(Image.open(f), (x, y))
    d.text((x + 4, y + 4), n, fill=(255, 255, 0))
sheet.save('/tmp/claude-0/backlot/tmp/wball_%s.jpg' % setname)
print('done', len(tiles))
