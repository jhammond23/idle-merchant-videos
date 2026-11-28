"""Switch the three sets to the CC0 photo-scans and re-save them.
python3 -I apply_cc0.py [pack_root] [--hdri] [--packed] [--sets=town_square,bridge_river,...]   (default: all six sets)

pack_root  default /mnt/user-data/uploads/3d-models/cc0-textures (the In This Town pack: one folder per
           material with color / normal / roughness / displacement / ao|metalness .jpg, hdri/, custom/).
Materials: folders named in mats.CC0_PICKS get the curated settings (tile size in metres, orientation,
           tint, anti-tiling, displacement depth) chosen from test renders; other packs fall back to
           keyword matching.  Materials not in CC0_PICKS stay procedural on purpose (see BACKLOT.md).
Art:       custom/ banner + sign images (Jake's own art, not CC0) are laid out for the banner meshes by
           cc0_art.py and replace the town-hall banners (crown -> gold lion, sun -> silver tower), the
           tavern sign (mug) and two hall banner designs (sun -> gold lion, tower -> black dragon).
Linking:   scan images are LINKED with paths relative to each .blend (//../../../../mnt/...): nothing of
           the 348 MB pack is copied.  The small art images stay packed.  --packed also writes
           <set>/<set>_packed.blend with every image packed (self-contained, for moving the set elsewhere).
--hdri:    put the pack's HDRIs behind the presets (name contains sunset/golden/dusk -> GOLDEN, night/moon
           -> NIGHT, else DAY).  Not used for the shipped sets: the pack's skies are cloudless/overcast and
           2K (soft behind an 18 mm lens at 1080x1920), and 'moonlit_night' is a daytime moon sky.
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
import mats, look
try:
    bpy.context.preferences.filepaths.save_version = 0      # no <set>.blend1 backups (disk is tight)
except Exception:
    pass

PACK = '/mnt/user-data/uploads/3d-models/cc0-textures'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict((a[2:].split('=', 1) + [''])[:2] for a in sys.argv[1:] if a.startswith('--'))
root = os.path.abspath(args[0] if args else PACK)
use_hdri = 'hdri' in opts
sets = opts['sets'].split(',') if opts.get('sets') else ['town_square', 'bridge_river', 'throne_hall', 'castle_courtyard',
                                                          'forest_edge', 'harbor']

# design swaps per set: old material -> (new material, art file in source/art, base surface)
ART_SWAPS = {
    'town_square': {
        'Banner crown': ('Banner gold lion', 'cc0_banner_gold_lion_town.jpg', 'Cloth White'),
        'Banner sun': ('Banner silver tower', 'cc0_banner_silver_tower_town.jpg', 'Cloth White'),
        'Sign mug': ('Sign tavern mug', 'cc0_sign_tavern_mug.jpg', 'Planks'),
    },
    'throne_hall': {
        'Banner sun': ('Banner gold lion', 'cc0_banner_gold_lion_hall.jpg', 'Cloth White'),
        'Banner tower': ('Banner black dragon', 'cc0_banner_black_dragon_hall.jpg', 'Cloth White'),
    },
}


# per-set: materials that stay procedural in that set even though they have a pick (test renders: the hall's
# clean pale masonry reads more 'royal' than the weathered ashlar scan, which went dark and blotchy there)
SET_KEEP_PROCEDURAL = {
    'throne_hall': ('Limestone',),
}


def ensure_art(custom):
    import cc0_art
    cc0_art.SRC = custom
    out = []
    for kind, name, asp, fn in cc0_art.JOBS:
        p = os.path.join(cc0_art.OUT, fn)
        if not os.path.exists(p) and os.path.exists(os.path.join(custom, name + '.jpg')):
            (cc0_art.banner if kind == 'banner' else cc0_art.sign)(name, asp, fn)
        out.append(p)
    return out


def swap_art(setname, log):
    done = []
    for old, (new, fn, base) in ART_SWAPS.get(setname, {}).items():
        m_old = bpy.data.materials.get(mats.PREFIX + old)
        path = os.path.join(HERE, 'art', fn)
        if not os.path.exists(path):
            continue
        lift = mats.ART_LIFT if new.startswith('Banner') else {}
        m_new = bpy.data.materials.get(mats.PREFIX + new) or mats.image_material(new, path, base=base, **lift)
        if m_old is not None and m_old != m_new:
            m_old.user_remap(m_new)
            bpy.data.materials.remove(m_old)
        if m_new.users:
            done.append('%s -> %s' % (old, new))
            log('art: %s -> %s (%s)' % (old, new, fn))
    return done


def link_relative():
    """Scan images: linked, path relative to this .blend.  Art images: packed."""
    for img in bpy.data.images:
        if img.source != 'FILE' or img.packed_file:
            continue
        fp = os.path.abspath(bpy.path.abspath(img.filepath))
        if fp.startswith(root + os.sep):
            img.filepath = bpy.path.relpath(fp)
        else:
            try:
                img.pack()
            except Exception:
                pass


custom = os.path.join(root, 'custom')
if os.path.isdir(custom):
    ensure_art(custom)
for name in sets:
    path = os.path.abspath(os.path.join(HERE, '..', name, name + '.blend'))
    bpy.ops.wm.open_mainfile(filepath=path)
    mats.reset_scans(root)                     # idempotent: re-applying starts from procedural
    done = mats.auto_image_sets(root, log=print)
    for m in SET_KEEP_PROCEDURAL.get(name, ()):
        if m in done:
            mats.use_procedural(m)
            done.pop(m)
            print('kept procedural in %s: %s' % (name, m))
    art = swap_art(name, print)
    lifted = mats.lift_art_materials()        # banner art brightness / saturation (idempotent rebuild)
    if lifted:
        print('art lift:', lifted)
    hd = mats.find_hdri(root) if use_hdri else []
    for f in hd:
        n = os.path.basename(f).lower()
        preset = 'GOLDEN' if any(k in n for k in ('sunset', 'golden', 'dusk')) else 'NIGHT' if any(k in n for k in ('night', 'moon')) else 'DAY'
        scn = [s for s in bpy.data.scenes if s.get('bl_preset') == preset][0]
        look.world_sky(scn, preset, scn.world.name, hdri=f)
    link_relative()
    coll = [c for c in bpy.data.collections if c.name.startswith('Backlot |')][0]
    coll['cc0_scans'] = ', '.join(sorted(done))
    coll['cc0_pack'] = root
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    print('SAVED', name, 'scans:', sorted(done), 'art:', art, flush=True)
    open(os.path.join(os.path.dirname(path), '.cc0_applied'), 'w').write('%s\n' % sorted(done))   # contact.py: older renders = v1
    if 'packed' in opts:
        for img in bpy.data.images:
            if img.source == 'FILE' and not img.packed_file:
                try:
                    img.pack()
                except Exception as e:
                    print('pack failed', img.name, e)
        pp = path[:-6] + '_packed.blend'
        bpy.ops.wm.save_as_mainfile(filepath=pp, compress=True, copy=True)
        print('PACKED COPY', pp, '%.1f MB' % (os.path.getsize(pp) / 1e6), flush=True)
