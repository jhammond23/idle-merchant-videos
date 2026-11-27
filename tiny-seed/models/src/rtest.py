# quick look: python3 -I rtest.py out.png "camx,camy,camz" "tx,ty,tz" lens [pose] [hide=a,b] [W]
import sys, os, math
sys.path.insert(0, '/home/claude/styles/craftee-style/pack'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, style_craftee_style as tf
from mathutils import Vector
from ts_lib import lin
bpy.ops.wm.open_mainfile(filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tiny-seed-models.blend'))
out = sys.argv[1]; cl = eval(sys.argv[2]); tg = eval(sys.argv[3]); lens = float(sys.argv[4])
opts = dict(a.split('=', 1) for a in sys.argv[5:])
s = bpy.context.scene
for name in opts.get('hide', '').split(','):
    c = bpy.data.collections.get(name)
    if c:
        for o in c.all_objects: o.hide_render = True
    elif name in bpy.data.objects: bpy.data.objects[name].hide_render = True
if 'only' in opts:
    keep = set()
    for name in opts['only'].split(','):
        keep |= set(bpy.data.collections[name].all_objects)
    for o in bpy.data.objects:
        if o not in keep: o.hide_render = True
if 'pose' in opts:
    arm = bpy.data.objects['TS_Tree_Rig']; arm.animation_data.action = bpy.data.actions[opts['pose']]
if 'blink' in opts:
    bpy.data.objects['TS_Tree_Face'].data.shape_keys.key_blocks['BLINK'].value = float(opts['blink'])
for k, v in opts.items():
    if k.startswith('face:'): bpy.data.objects[k[5:]]['face'] = int(v)
if 'exec' in opts: exec(opts['exec'])
bpy.ops.mesh.primitive_plane_add(size=4000); g = bpy.context.active_object
m = bpy.data.materials.new('g'); m.use_nodes = True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*lin(opts.get('ground', '#8DA05E')), 1)
m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.95; g.data.materials.append(m)
cd = bpy.data.cameras.new('c'); cam = bpy.data.objects.new('c', cd); s.collection.objects.link(cam); s.camera = cam
cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36; cd.clip_end = 20000; cd.clip_start = 0.05
cam.location = cl; tf.look_at(cam, Vector(tg))
tf.apply_look(s, 'day', samples=int(opts.get('spp', 12))); tf.light_rig('day', cam=cam)
W = int(opts.get('W', 540)); H = int(opts.get('H', W * 16 // 9))
s.render.resolution_x, s.render.resolution_y = W, H
s.frame_set(1)
s.render.filepath = out; bpy.ops.render.render(write_still=True)
print(tf.measure(out, 'day'))
