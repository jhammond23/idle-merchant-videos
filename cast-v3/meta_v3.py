# dump per-character metadata from cast-v3.blend for the sheets / docs -> scratch/meta.json
import bpy, json, os
bpy.ops.wm.open_mainfile(filepath=os.environ.get('BLEND', '/tmp/claude-0/cast3/cast-v3.blend'))
PAL = {  # consistency lock: signature first, then support colours (sRGB)
    'oathbound': [(40, 44, 56), (140, 220, 255), (92, 100, 118), (26, 26, 34), (38, 38, 46)],
    'first_rank': [(255, 192, 70), (232, 228, 218), (28, 40, 96), (34, 36, 54), (232, 190, 160), (112, 66, 36)],
    'true_form': [(206, 76, 48), (52, 58, 82), (54, 62, 92), (255, 196, 70), (238, 196, 156), (110, 68, 38)],
    'rigger': [(150, 232, 40), (46, 48, 54), (32, 34, 38), (178, 140, 56), (178, 142, 96)],
    'jailer': [(142, 72, 36), (20, 18, 22), (96, 84, 76), (255, 176, 40), (70, 46, 32)],
    'squire': [(18, 138, 142), (206, 150, 62), (245, 205, 48), (172, 148, 98), (150, 112, 70)],
    'ember_hatchling': [(242, 110, 28), (255, 204, 112), (66, 40, 34), (255, 150, 30), (40, 110, 210), (140, 70, 214)],
    'ember_grown': [(242, 110, 28), (255, 204, 112), (66, 40, 34), (255, 150, 30), (40, 110, 210), (140, 70, 214)],
    'crowd_pointer': [(84, 96, 112), (58, 62, 72), (234, 192, 160)], 'crowd_laugher': [(196, 150, 58), (100, 64, 40), (112, 72, 48)],
    'crowd_whisperer': [(112, 120, 58), (150, 70, 46), (245, 205, 48)], 'crowd_gasper': [(156, 72, 40), (176, 136, 64), (160, 110, 72)],
    'crowd_cheerer': [(150, 66, 40), (84, 96, 112), (245, 205, 48)], 'crowd_dropper': [(84, 96, 112), (128, 132, 140), (206, 152, 106)],
    # phase 2
    'herald': [(214, 22, 30), (236, 182, 62), (236, 226, 204), (44, 40, 48), (150, 100, 66)],
    'horde_slate': [(96, 102, 112), (58, 62, 70), (204, 192, 164), (255, 170, 40)], 'horde_ash': [(66, 62, 62), (255, 80, 30), (32, 28, 30), (255, 70, 30)],
    'horde_moss': [(86, 120, 52), (104, 98, 80), (116, 84, 54), (200, 240, 60)], 'horde_frost': [(118, 146, 176), (226, 240, 252), (196, 232, 250), (40, 150, 255)],
    'old_legend': [(104, 106, 110), (122, 48, 56), (128, 132, 138), (232, 230, 226), (96, 62, 42)],
    'golden_sister': [(138, 22, 64), (240, 186, 66), (206, 76, 48), (52, 58, 82), (238, 196, 156)],
    'roll_merchant': [(96, 36, 86), (190, 90, 255), (226, 176, 70), (58, 34, 52), (196, 150, 108)],
    'master_smith': [(82, 50, 32), (255, 126, 30), (196, 84, 34), (84, 84, 90), (100, 64, 44)],
    'stone_keeper': [(226, 218, 198), (46, 44, 116), (200, 230, 255), (196, 200, 210), (132, 90, 62)],
    'rival_heir': [(24, 54, 168), (186, 192, 204), (52, 52, 64), (40, 28, 24), (214, 168, 128)],
    'turned_friend': [(46, 26, 62), (255, 50, 200), (138, 98, 52), (36, 30, 42), (245, 205, 48)],
    'mirror_twin': [(49, 179, 207), (203, 197, 173), (220, 228, 240), (181, 207, 223), (238, 196, 156)],
    'jester': [(226, 178, 24), (26, 24, 30), (236, 190, 60), (240, 206, 182)],
    'boss_giant': [(120, 84, 62), (255, 150, 40), (100, 106, 118), (30, 34, 52), (60, 160, 255)]}
ALIAS = {'The Oathbound': 'oathbound', 'First Rank': 'first_rank', 'True-Form Lead': 'true_form', 'The Rigger': 'rigger', 'The Jailer': 'jailer', 'The Squire': 'squire',
         'Ember (hatchling)': 'ember_hatchling', 'Ember (grown)': 'ember_grown', 'Crowd Pointer': 'crowd_pointer', 'Crowd Belly-laugher': 'crowd_laugher',
         'Crowd Whisperer': 'crowd_whisperer', 'Crowd Gasper': 'crowd_gasper', 'Crowd Cheerer': 'crowd_cheerer', 'Crowd Bread-dropper': 'crowd_dropper'}
META = {}
for c in bpy.data.collections:
    if not c.name.startswith('Cast v3 |'): continue
    n = c.name[10:]; rig = [o for o in c.objects if o.type == 'ARMATURE'][0]; k = rig.get('key') or ALIAS[n]
    names = [x.split(' ', 1)[1] for x in rig['face_names'].split(', ')]
    talk = [x.split(' ', 1)[1] for x in rig.get('mouth_names', '').split(', ')[1:]] if rig.get('mouth_names', 'no').startswith('0') else []
    fm = bpy.data.materials.get(n + ' | face'); imgs = [nd.image.name for nd in fm.node_tree.nodes if nd.type == 'TEX_IMAGE' and nd.image] if fm else []
    cells = names + ['talk ' + t for t in talk] + (['blink'] if any(i.endswith('| blink') for i in imgs) else []) + ((['glow off'] if float(rig['glow']) > 0.5 else ['glow on (power)']) if any('eye_glow' in i for i in imgs) else [])
    cells = [('glow off (turned back)' if (cl == 'glow off' and k == 'turned_friend') else cl) for cl in cells]
    META[k] = dict(name=n, role=rig.get('role', ''), body=rig.get('body', ''), signature=rig.get('signature', ''), face_style=rig.get('face_style', ''), silhouette=rig.get('silhouette', ''),
                   height_BU=rig['height_BU'], height_x_hero=rig['height_x_hero'], height_HH=rig['height_HH'], poses=list(json.loads(rig['poses']).keys()), default_pose=rig['default_pose'],
                   cells=cells, faces=names, talk=talk, swatches=PAL.get(k, []), objects=len(c.objects), bones=[b.name for b in rig.data.bones],
                   sockets=[o.name.split(' | ')[1] for o in c.objects if o.type == 'EMPTY'])
    if k == 'boss_giant': META[k]['variants_label'] = "VARIANTS  rig 'skin' 0 iron and rust + chains  /  1 storm grey + horns  /  2 blue fire + crown + horns  /  'weak' 0 (weak point out)" 
ORDER = ['Crowd Gasper', 'Ember (hatchling)', 'Little sister', 'Hero kid', 'Ember (grown)', 'The Squire', 'Crowd Belly-laugher', 'Crowd Whisperer', 'Crowd Cheerer',
         'First Rank', 'Crowd Bread-dropper', 'The Jailer', 'The Rigger', 'Crowd Pointer', 'The Oathbound', 'True-Form Lead']
META['_order'] = ORDER
META['_order2'] = ['The Herald', 'The Mirror Twin', 'Little sister', 'Hero kid', 'The Turned Friend', 'The Roll Merchant', 'Horde Moss', 'Horde Frost', 'Horde Slate', 'Horde Ash',
                   'The Golden Sister', 'The Rival Heir', 'The Master Smith', 'The Old Legend', 'The Jester', 'The Stone Keeper']
json.dump(META, open('/tmp/claude-0/cast3/scratch/meta.json', 'w'), indent=1)
print('meta', len(META) - 1)
