# MY TINY SEED HUGGED A GIANT TROLL: model kit

File: `tiny-seed-models.blend` (Blender 5.3, Cycles-ready, textures packed, no linked libraries). Backups: `glb/<collection>.glb`.
Style: Toybox Fable (`craftee-style`). Units: **1 m = 3.3 BU**. Front of every asset is **-Y**, up is +Z. All scales are 1, all rotations 0.
`L` = +X side (screen right when you look at the front), `R` = -X.

**Append:** File > Append > `tiny-seed-models.blend` > Collection > pick the collection. Or by script: `src/ts_helpers.py` (`append`, `find`, `stage`, `apply_pose`, `set_face`, `blink`). Appending twice gives a second copy with `.001` names.

| Collection | What | Size (BU) | Origin |
|---|---|---|---|
| `TS_Tree` | our tree, stages A-E in 5 child collections | A 0.3, B 40, C 100 tall x 91 wide | all stages at world (0,0,0), base centre |
| `TS_ChampionOak` | the champion's oak, gold rosette on the trunk | 40 tall x 42 wide | (0,0,0), base centre |
| `TS_Bushes` | `TS_Bush_01` / `_02` / `_03` | 4 / 5 / 3 tall | each at its own base centre; laid out at x = -8, 0, 8 |
| `TS_TrollBaby` | baby rock troll | 15.6 rock, 17.4 with flowers; 18.5 wide | (0,0,0), between the feet |
| `TS_TrollMother` | troll mother | 440 tall, 520 wide, 320 deep | (0,0,0), between the feet |
| `TS_Props` | pillar, pie table, squished table, apples | see below | each at its own base centre; laid out along X |

## TS_Tree
Child collections (toggle with `hide_render` / `hide_viewport`, or `ts.stage(coll, 'CDE')`):
- `TS_Tree_A_Dot`: object `TS_Tree_A_Dot` (soil patch 0.9 across, seedling 0.3 tall). No rig.
- `TS_Tree_B_Sprout`: object `TS_Tree_B_Sprout` (thin young trunk, 8 leaves, bud, soil). No rig. Scale it in Z for the "shot up" growth.
- `TS_Tree_C_Giant`: armature `TS_Tree_Rig` + `TS_Tree_Trunk` (trunk, roots, two arm branches), `TS_Tree_Canopy` (canopy + leafy hands), `TS_Tree_Face` (knothole rims, eye whites, lids, blush, mouth), `TS_Tree_Pupils`, empties `TS_Tree_Socket_HandL` / `_HandR` (parent props to these).
- `TS_Tree_D_Blossoms`: `TS_Tree_Blossoms` (white-pink clusters on canopy and hands), skinned to the same rig.
- `TS_Tree_E_Apples`: `TS_Tree_Apples` (about 30 glowing golden apples, 3.8 BU each, hanging from the canopy), same rig.
Roots dip to z = -2.5 so the base sits into the ground. For growth: swap A > B > C at the same spot and scale `TS_Tree_Rig` (C) up from about 0.4.

**Bones (`TS_Tree_Rig`):** `TS_Root` > `TS_Trunk1` (z 0-14) > `TS_Trunk2` (14-34, carries the face) > `TS_Trunk3` (34-50) > `TS_Canopy`; `TS_ArmL_01..10` and `TS_ArmR_01..10` (two 62 BU arm chains from `TS_Trunk3`, 6.2 BU a bone); `TS_Eyes` (move in local X / Y to steer both pupils, about +-1 BU).
**Poses** (one-frame Actions, marked as pose assets, parked on muted NLA tracks so they come with the armature on append; also in `poses.json`):
- `TS_TREE_REST`: arms raised into the canopy sides.
- `TS_TREE_HUG`: both arms wrap a troll standing at **(0, -18.5, 0)** in tree space (wraps at z 4.3 and 7.8, radius 7.6), slight lean, eyes down. Pose the troll's arms up (`TS_BABY_ARMS_UP`).
- `TS_TREE_GIVE`: the L arm reaches forward and down; `TS_Tree_Socket_HandL` lands at about **(15, -51, 13)**. Hang the apple under it; the kid stands at about (15, -56, 0).
- `TS_TREE_PROTECT`: trunk and canopy lean forward, arms curl round a kid at about **(0, -22, 0)**, a gap stays open at the front, eyes down.
- `TS_TREE_LEAN`: plain lean forward. `TS_TREE_LOOKDOWN`: eyes only (keys just `TS_Eyes`).
Use: assign the Action to `TS_Tree_Rig`, or `ts.apply_pose(arm, 'TS_TREE_HUG', frame)` to key it and blend from the previous key. Poses are absolute, so key `TS_TREE_REST` first.
**Face:** shape keys on `TS_Tree_Face` (datablock `TS_Tree_FaceKeys`): `BLINK` 0-1 (lids close; 0.25 is a soft look), `SMILE` 0-1 (wider smile). Pupils follow `TS_Eyes`.
**Materials:** `TS_Mat_TreeBark`, `TS_Mat_TreeLeaf`, `TS_Mat_TreeEyeRim`, `TS_Mat_TreeEyeWhite`, `TS_Mat_TreeEyePupil`, `TS_Mat_TreeEyeLid`, `TS_Mat_TreeBlush`, `TS_Mat_BlossomWhite`, `TS_Mat_BlossomPink`, `TS_Mat_BlossomCentre`, `TS_Mat_AppleGold` (emission 1.1; raise for more glow), `TS_Mat_Soil`, `TS_Mat_TreeBud`.

## TS_ChampionOak
One object `TS_ChampionOak`, no rig. Materials `TS_Mat_OakBark`, `TS_Mat_OakLeaf`, `TS_Mat_RosetteGold`, `TS_Mat_RosetteBlue`.

## TS_Bushes
`TS_Bush_01` (round), `TS_Bush_02` (tall, white flowers), `TS_Bush_03` (low, red berries). No rig; origin at the base, so rotate X / Y to lean them toward the tree. Materials `TS_Mat_BushLeaf`, `TS_Mat_OakBark`, `TS_Mat_BushBerry`, `TS_Mat_BlossomWhite`, `TS_Mat_BlossomCentre`.

## TS_TrollBaby
Objects: `TS_TrollBaby_Rig`, `TS_TrollBaby_Body` (rocks, moss, flowers, sprout), `TS_TrollBaby_Face` (decal patch on the head).
**Bones:** `TS_Root`, `TS_Body` (bob: move in Z), `TS_Head` (tilt), `TS_ArmL`, `TS_ArmR`, `TS_LegL`, `TS_LegR` (legs hang from `TS_Root`). Every part is rigid on one bone.
**Poses** (Actions, same method as the tree): `TS_BABY_REST`, `TS_BABY_STOMP_L`, `TS_BABY_STOMP_R` (alternate these two for the stomp walk), `TS_BABY_ARMS_UP`, `TS_BABY_HEAD_TILT`, `TS_BABY_SIT_ROLL`.
**Face swap:** custom property `TS_TrollBaby_Face["face"]`: **0 GRUMPY, 1 GIGGLE, 2 SNIFFLE, 3 SURPRISED**. The material `TS_Mat_TrollBaby_Face` reads it (Attribute node, type Object) and shifts the UVs across the packed atlas `TS_Face_TrollBaby_ATLAS` (4 cells of 1024x824). Key it with constant interpolation for 1-frame swaps: `ts.set_face(face_obj, 2, frame)`. Single PNGs are in `faces/` if you prefer the pack's `face_set` / `face_swaps` (image node `TS_FACE_TEX`).
**Materials:** `TS_Mat_TrollBabyRock`, `TS_Mat_Moss`, blossom materials, `TS_Mat_TrollBaby_Face`.

## TS_TrollMother
Objects: `TS_TrollMother_Rig`, `TS_TrollMother_Body` (boulders, moss, grass, five little trees), `TS_TrollMother_Face`.
**Bones:** `TS_Root`, `TS_Body`, `TS_Head` (turn / nod), `TS_ArmL` > `TS_ForearmL`, `TS_ArmR` > `TS_ForearmR`, `TS_LegL`, `TS_LegR`.
**Poses:** `TS_MOTHER_REST`, `TS_MOTHER_LOOK_DOWN`, `TS_MOTHER_HEAD_TURN_L`, `TS_MOTHER_STEP_L`, `TS_MOTHER_STEP_R`, `TS_MOTHER_REACH_R`.
**Face swap:** `TS_TrollMother_Face["face"]`: **0 STERN, 1 SOFT** (atlas `TS_Face_TrollMother_ATLAS`, 2 cells). SOFT reads best with `TS_MOTHER_LOOK_DOWN`.
**Materials:** `TS_Mat_TrollMotherRock`, `TS_Mat_MossOld`, `TS_Mat_TrollTreeLeaf`, `TS_Mat_OakBark`, `TS_Mat_TrollMother_Face`.
Set the camera clip end to 5000+ for her shots. Her fists rest on the ground in the rest pose.

## TS_Props
- `TS_MeasuringPillar` (5 x 4.5 x 8.3 tall, carved stone, ruler ticks, stone seed on top) with child `TS_MeasuringPillar_Panel`: the blank glowing panel, **1.62 wide x 2.56 tall, centre at local (0, -1.27, 3.75), facing -Y**. Track numbers to it in post. Materials `TS_Mat_PillarStone`, `TS_Mat_PillarStoneDark`, `TS_Mat_PillarPanelGlow` (emission 2.2), `TS_Mat_Moss`.
- `TS_PieTable` (9 x 3.6, top at 2.6) with five children `TS_Pie_01..05` (each can be moved or thrown on its own). This is also the FIXED version.
- `TS_PieTable_Squished` (12 x 8.8 x 1.1): snapped top, splayed legs, flat cloth, five splatted pies. Put it where the table was and swap visibility on one frame.
- `TS_Apple_Single` (kid-scale golden apple, 1.0 across, 1.1 tall, origin at its base) and `TS_Apple_Loose_01..03` (lying on their sides).
- Materials: `TS_Mat_TableWood`, `TS_Mat_TableWoodDark`, `TS_Mat_TableCloth` (packed `TS_Tex_Gingham`), `TS_Mat_PieCrust`, `TS_Mat_PieBerry`, `TS_Mat_PieCherry`, `TS_Mat_PiePumpkin`, `TS_Mat_PieCustard`, `TS_Mat_PieCream`, `TS_Mat_AppleGold`.

## Notes and limits
- **Materials** are matte Principled with one flat colour multiplied by the vertex colour layer `Col` (the shading variation). Change a colour on the Mix node's `A` input. No procedural textures, so the look is the same in Cycles, EEVEE and the .glb files.
- **Pose library:** I did not set up an asset-library catalog (not checked in the Asset Browser here). The poses are one-frame Actions marked as assets and parked on muted NLA tracks, plus `poses.json`. Do not unmute the NLA tracks; assign the Action or use `ts.apply_pose`.
- **Face index:** rendered and checked in Cycles only, not in EEVEE. The swap is the Attribute node `TS_FACE_INDEX` (Object attribute `face`) > round > divide by the cell count > added to U.
- The .glb files show face 0 only (GRUMPY / STERN) and carry the poses as animations and `BLINK` / `SMILE` as morph targets.
- Arm bends in HUG / PROTECT are tight; keep the camera off the inside of the elbows in close-ups, or ease the pose with a few degrees on `TS_Arm?_04..06`.
- Leaves and petals are single-sided sheets (fine in Cycles; turn backface culling off in EEVEE).
- Preview stills use a Cast v2 kid (5 BU) and a 14 BU cottage block; neither is in the .blend.
- Rebuild from source: `python3 -I src/build.py`, `src/ts_export.py`, previews `SHOT=hero W=1080 H=1920 python3 -I src/ts_previews.py` then `src/ts_compose.py`.
