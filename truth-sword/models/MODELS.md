# Truth Sword props (`truth-sword-props.blend`)

Blender 5.3, style Toybox Fable (`craftee-style`). 1 m = 3.3 BU. All object scales are 1. No image textures (all
materials are procedural), no linked libraries, no scripted (Python) driver expressions, so nothing needs auto-run.
Rebuild with `python3 -I build_truth_sword_props.py` (edit `OUT` first).

## Append
File > Append > `truth-sword-props.blend` > Collection > pick the `SW_...` collections (one per prop). In Python:
```python
with bpy.data.libraries.load(path, link=False) as (src, dst):
    dst.collections = [c for c in src.collections if c.startswith('SW_')]
for c in dst.collections: scene.collection.children.link(c)
```
The props sit in a row in the file (clouds at y=160, z=40). Move each root object where you need it.
Append, do not link: the parameters are custom properties on the objects.

## Props
| Collection / root object | Size (BU) | Origin | Notes |
|---|---|---|---|
| `SW_TruthStone` | 7.0 wide, 1.5 high (collar around the slot rises to 1.65) | ground centre | Kid stands on top (z = 1.5). Slot is 1.1 x 0.42, long axis = X. Children: `SW_TruthStone_Cracks`, `SW_TruthStone_GlowLight`. |
| `SW_Sword_StableBoy` | 6.0 default (1 to 700+) | grip centre (the hand), blade along +Z, flat side faces +-Y | Rusty blade, leather grip. Hilt is 1.3 long: pommel bottom at z = -0.75, guard top at +0.55. |
| `SW_Sword_Golden` | 5.0 default (down to 0.5) | same | Gold blade, ruby guard, sapphire pommel. |
| `SW_Sword_Guard` | 4.5 default | same | Plain steel. |
| `SW_Scabbard_King` | belt 2.28 x 1.24 outside (2.12 x 1.08 inside), scabbard 3.4 long | belt centre (waist centre). Front (buckle) = -Y | Scabbard hangs on the wearer's left hip (+X), tip angled back (+Y). Open dark mouth, no hilt. Scale the object if the King's torso is not about 2.1 x 1.05. |
| `SW_Bell` (frame) | 4.3 wide, 1.9 deep, 4.5 high; bell 2.06 wide | ground centre | `SW_Bell_Pivot` (empty, at z = 3.45) carries `SW_Bell_Body` and `SW_Bell_Rope`. |
| `SW_Cloud_A`, `_B`, `_C` | about 110, 80, 60 wide; 30 to 40 high | flat bottom centre | Opaque white puffs, flat bottoms. One collection `SW_Cloud`. |
| `SW_Shovel` | 4.5 long, blade 1.04 wide | blade tip (z = 0), handle up +Z | Hold it on the shaft around z = 2.5 to 3.5. |

## Parameters (custom properties on the object; key them in the N panel > Item > Properties or by script)
**Swords** (`SW_Sword_StableBoy`, `SW_Sword_Golden`, `SW_Sword_Guard`):
- `sword_length`: total length in BU, pommel to tip. This is the one value to animate.
  `ob['sword_length'] = 6.0; ob.keyframe_insert('["sword_length"]', frame=f)`
  It drives the `SW_Grow` geometry-nodes modifier (group `SW_GN_SwordGrow`): the blade body gets longer, the tip and
  hilt keep their shape, nothing is scaled, so nothing stretches. Texture space is the unstretched attribute `sw_tex`.
- `width`: blade width multiplier, default 1. The blade already widens by itself as it grows
  (x (blade length / default blade length)^0.6): stable boy blade is 0.6 wide at 6 BU, 2.9 at 40, 12 at 700.
  Raise `width` to 1.5 or 2 if the 700 BU blade is too thin in a very wide shot.
- `glow`: blade glow multiplier, default 1 (0 = none).
- `clean` (stable boy only): extra rust-to-steel amount 0..1. Automatic part: rust up to 20 BU, patchy between 20 and
  60, clean bright steel with a faint glow from 60 up. Set `clean` = 1 to force steel at any length.

How each sword behaves:
- Stable boy: at or below 6 BU the whole sword scales evenly (1 BU = a spoon-sized copy, hilt 0.22). Above 6 the
  grip stays hand-sized and only the blade grows. Tested 1 -> 6 -> 40 -> 700 with linear keys (mesh length follows
  the property exactly at every frame checked).
- Golden: from 5 down to 2 BU only the blade shrinks and thins (hilt stays). Below 2 BU the whole sword shrinks in
  proportion. Toothpick = 0.75 (blade about 0.28) or 0.5 for smaller. Put the grip inside the Prince's fist so only the
  tiny guard and blade poke out (see `golden-shrink.png`).
- Guard: default 4.5; "grew a foot" = 5.5. Below 4.5 it scales evenly.
- For a hundred guards: duplicate the object (Shift+D or `ob.copy()`); the driver on each copy points at that copy,
  so every sword has its own `sword_length` (checked).

**Truth Stone:**
- `SW_TruthStone['glow']`: 0 = off (default), 1 = blue glow (runes, slot and a soft wash). It also drives the energy
  of `SW_TruthStone_GlowLight` (glow x 300 W, blue point light above the slot, lights the kid's legs). Delete the
  light if you do not want it.
- Lie: `SW_TruthStone_Cracks` is hidden by default (`hide_render` and `hide_viewport` are True). Set both to False
  on the crack frame (they can be keyframed). `SW_TruthStone_Cracks['glow']` (default 1) is the red-orange strength.

**Bell:** rotate `SW_Bell_Pivot` on its local X axis, about +-25 degrees, to swing the bell. The rope and clapper
swing with it; rotate `SW_Bell_Rope` the other way on X for a lagging rope.

## Caveats
- The 700 BU sword needs the camera's clip end raised (2000+).
- At 700 BU the guard is 2.9 BU wide and the blade flares to 12 BU over the first 44 BU. That is meant for wide
  shots; in a close shot of the hand use a length under about 40.
- The glow is plain emission. For a bloom halo use the pack's `tf.bloom(scene, True)` on those shots.
- Preview stand-ins (kid, cottages, ground) are not in the .blend.
- Previews were rendered with Cycles, 24 samples, the pack's day look and light rig. EEVEE was not tested here.
