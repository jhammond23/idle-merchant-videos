# Tiny Seed: build every model into tiny-seed-models.blend.   python3 -I build.py [tree,oak,bushes,trolls,props]
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from ts_lib import *
import ts_tree
OUT = os.path.join(HERE, '..', 'tiny-seed-models.blend')
only = sys.argv[1].split(',') if len(sys.argv) > 1 else ['tree', 'oak', 'bushes', 'trolls', 'props']
reset()
root = bpy.context.scene.collection
info = {}
if 'tree' in only:
    info['tree'] = ts_tree.build_tree(root)['poses']
if 'oak' in only: ts_tree.build_oak(root)
if 'bushes' in only: ts_tree.build_bushes(root)
if 'trolls' in only:
    import ts_troll; info.update(ts_troll.build(root))
if 'props' in only:
    import ts_props; ts_props.build(root)
json.dump(info, open(os.path.join(HERE, '..', 'poses.json'), 'w'), indent=1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT), relative_remap=True, compress=True)
for o in bpy.data.objects:
    if o.type == 'MESH':
        print(o.name, len(o.data.vertices), [round(x, 2) for x in o.dimensions])
