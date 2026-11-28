"""Preview helper: drop Cast v2 characters on the set marks (previews only; not saved into the sets)."""
import bpy, math
from mathutils import Vector

CAST = '/tmp/claude-0/cast2/pkg/cast-v2.blend'


def append_character(name, coll_parent):
    """Append 'Cast v2 | <name>' and return (collection, root empty)."""
    before = set(bpy.data.collections.keys())
    with bpy.data.libraries.load(CAST, link=False) as (src, dst):
        dst.collections = ['Cast v2 | ' + name]
    c = dst.collections[0]
    if c.name not in coll_parent.children:
        coll_parent.children.link(c)
    root = [o for o in c.objects if o.parent is None and o.type == 'EMPTY']
    if not root:
        root = [o for o in c.objects if o.parent is None]
    return c, root[0]


def place(root, mark):
    """Put a cast root on a mark: copy location; yaw = mark yaw (front -Y faces the mark's -Y)."""
    root.location = mark.location.copy()
    root.rotation_euler = (0, 0, mark.rotation_euler.z)


def stage(scene, marks, cast_map, parent_name='PREVIEW CAST'):
    """cast_map: {mark_name: character_name}.  Returns the preview collection."""
    pc = bpy.data.collections.get(parent_name) or bpy.data.collections.new(parent_name)
    if pc.name not in scene.collection.children:
        scene.collection.children.link(pc)
    for mk, who in cast_map.items():
        m = bpy.data.objects.get(mk)
        if m is None:
            continue
        c, root = append_character(who, pc)
        place(root, m)
    return pc
