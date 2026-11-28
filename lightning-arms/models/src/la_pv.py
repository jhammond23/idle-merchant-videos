# Lightning Arms: preview helpers (append kit collections + Cast v2 people, ground, camera, render with the Toybox look).
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/home/claude/styles/craftee-style/pack'); sys.path.insert(0, HERE)
import bpy, style_craftee_style as tf
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
import la_lib as L
import la_helpers as la

BLEND = os.path.abspath(os.path.join(HERE, '..', os.environ.get('LA_BLEND', 'lightning-models.blend')))
CAST = '/tmp/claude-0/cast2/pkg/cast-v2.blend'
PJ = os.path.join(HERE, '..', os.environ.get('LA_POSES', 'poses.json'))
POSES = json.load(open(PJ)) if os.path.exists(PJ) else {}
bpy.ops.wm.read_factory_settings(use_empty=True)      # the bpy module starts with the default cube, lamp and camera
S = bpy.context.scene
LABELS = []
W = int(os.environ.get('W', 1080)); H = int(os.environ.get('H', 1080)); SPP = int(os.environ.get('SPP', 32))


def new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global S
    S = bpy.context.scene
    LABELS.clear()


def append(name, blend=None):
    with bpy.data.libraries.load(blend or BLEND) as (s, d):
        d.collections = [name]
    c = d.collections[0]
    S.collection.children.link(c)
    return c


def find(c, base):
    return la.find(c, base)


def move(c, loc, rz=0.0):
    M = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(math.radians(rz), 4, 'Z')
    for o in list(c.all_objects):
        if o is not None and o.parent is None:
            o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()


def person(who, loc, rz=0.0, arms=None):
    """Cast v2 character. arms = {'L': (rx, ry, rz) deg, 'R': ...}; cast 'L' is the -X arm (the character's own right)."""
    c = append('Cast v2 | ' + who, CAST)
    root = [o for o in list(c.all_objects) if o.parent is None and o.type == 'EMPTY'][0]
    root.location = loc; root.rotation_euler = (0, 0, math.radians(rz))
    if arms:
        for o in list(c.all_objects):
            for sd in ('L', 'R'):
                if o.type == 'EMPTY' and o.name.split('.')[0].endswith('arm' + sd) and sd in arms:
                    o.rotation_euler = [math.radians(a) for a in arms[sd]]
    bpy.context.view_layer.update()
    return c


def hand(c, sd):
    for o in list(c.all_objects):
        if o.type == 'MESH' and o.name.split('.')[0].endswith('Hd' + sd):
            return o


def ground(hexcol='#7FA35C', size=4000, z=0.0, rough=0.95):
    m = L.mat('PV_Ground_' + hexcol[1:], hexcol, rough, vcol=False)
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z)); g = bpy.context.active_object; g.data.materials.append(m)
    return g


def camera_(loc, at, lens, fit='VERTICAL'):
    cd = bpy.data.cameras.new('PV_cam'); cam = bpy.data.objects.new('PV_cam', cd); S.collection.objects.link(cam); S.camera = cam
    cd.lens = lens; cd.sensor_fit = fit; cd.sensor_height = 36; cd.sensor_width = 36; cd.clip_start = 0.05; cd.clip_end = 30000
    cam.location = loc; tf.look_at(cam, Vector(at))
    return cam


def label(text, world, dy=0):
    LABELS.append((text, tuple(world), dy))


def render(cam, out, kind='day', sun_el=None, exposure=None, az_off=35.0, w=None, h=None, spp=None, auto=True):
    w = w or W; h = h or H; spp = spp or SPP
    tf.apply_look(S, kind if kind in ('day', 'dusk') else 'night', samples=spp)

    def rig():
        lights = tf.light_rig(kind, cam=cam, az_off=az_off)
        if sun_el is not None and lights:
            lights[0].rotation_euler[0] = math.radians(90 - sun_el)
    rig()
    S.render.image_settings.file_format = 'PNG'
    if exposure is not None:
        S.view_settings.exposure = exposure; rig()
    elif auto and kind == 'day':
        S.render.resolution_x, S.render.resolution_y = w // 4, h // 4
        S.cycles.samples = 6
        S.render.filepath = out; bpy.ops.render.render(write_still=True)
        m = tf.measure(out, 'day')
        S.view_settings.exposure += max(-0.8, min(0.8, m['exposure_change'])); rig()
    S.render.resolution_x, S.render.resolution_y = w, h
    S.cycles.samples = spp
    S.render.filepath = out; bpy.ops.render.render(write_still=True)
    try:
        print('MEASURE', os.path.basename(out), tf.measure(out, 'day'), 'exposure', S.view_settings.exposure)
    except Exception as e:
        print('measure failed', e)
    bpy.context.view_layer.update()
    lab = []
    for text, wpos, dy in LABELS:
        c = world_to_camera_view(S, cam, Vector(wpos))
        lab.append((text, c.x * w, (1 - c.y) * h + dy))
    json.dump(lab, open(out.replace('.png', '.json'), 'w'))

