# Lightning Arms: build every model into lightning-models.blend.   python3 -I build.py [gate,beast,arms,props,giant]
import sys, os, json, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from la_lib import *
OUT = os.path.join(HERE, '..', os.environ.get('LA_OUT', 'lightning-models.blend'))
ALL = ['gate', 'beast', 'arms', 'props', 'giant']
only = sys.argv[1].split(',') if len(sys.argv) > 1 else [m for m in ALL if os.path.exists(os.path.join(HERE, f'la_{m}.py'))]
reset()
root = bpy.context.scene.collection
info = {}
for m in only:
    mod = importlib.import_module('la_' + m)
    info.update(mod.build(root) or {})
    print('BUILT', m)
drop_fonts()
full = os.environ.get('LA_OUT') is None
json.dump(info, open(os.path.join(HERE, '..', 'poses.json' if full else '_poses_part.json'), 'w'), indent=1)
bpy.ops.file.pack_all()
TMP = os.path.abspath(OUT) + '.tmp.blend'
bpy.ops.wm.save_as_mainfile(filepath=TMP, relative_remap=True, compress=True)
os.replace(TMP, os.path.abspath(OUT))        # swap in one step: the video builder may be appending from the old file
if os.path.exists(TMP + '1'):
    os.remove(TMP + '1')
tot = 0
for o in bpy.data.objects:
    if o.type == 'MESH':
        tot += len(o.data.vertices)
        print(o.name, len(o.data.vertices), [round(x, 2) for x in o.dimensions])
print('TOTAL VERTS', tot, 'size', os.path.getsize(os.path.abspath(OUT)))
