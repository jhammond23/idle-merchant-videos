# I TRADED MY ARMS FOR LIGHTNING: model kit

File: `lightning-models.blend` (Blender 5.3, Cycles, nothing linked, no image textures). Backups: `glb/<collection>.glb`.
Units: **1 m = 3.3 BU**. Front of every asset is **-Y**, up is +Z. All scales 1, rotations 0, origin at the base centre unless stated.
**Append:** File > Append > Collection, or by script with `src/la_helpers.py` (`import la_helpers as la`):
`c = la.append(blend, 'LA_WarBeast')`, `la.find(c, 'LA_WarBeast_Rig')`. Loop over `list(coll.all_objects)`.

| Collection | What | Size (BU) | Origin |
|---|---|---|---|
| `LA_GateOfOaths` | the gate (arch form), `eyes` 0..1, shake helper | 25.7 wide x 27.9 tall x 10 deep (walls 4.4 deep, arms poke out 2-3); opening 10 wide x 19 tall | ground, centre of the opening |
| `LA_WarBeast` | horned war beast, rigged, 7 poses, chains + cuff | shoulder hump 22.2, back 20, 23 wide at the horns, 47 long | ground, under the belly |
| `LA_LightningArms` | the kid's two arms of light, 4 bolt shapes each, `glow` | shell 0.96 x 0.96 x 1.7, bolts reach about 2 | shoulder pivot |
| `LA_SparkBurst` | a burst of sparks, 3 shapes, `glow` | about 7 across | its centre |
| `LA_GroundSplit` | glowing jagged crack, `amount` 0..1, `glow` | 48 long (along X) x up to 3.4 wide, slabs to 1 high | centre, on the ground |
| `LA_GateGiant` | the gate standing up: rigged giant, 3 poses, `eyes` | **134 tall**, 96 wide, 43 deep (the keep is 56) | ground, between the feet |
| `LA_IronCrown` | the Warlord's spiked iron crown | 2.3 across x 1.7 tall | centre of its base ring |
| `LA_GateChains` | rune chains: hanging on the gate, lashed to two wrists, 2 cuffs, a link | links 1.5 long; set 24 wide x 26 tall | the gate's origin |
| `LA_StoneArms` | stone arm shells, Kid size and Villain size, `stone` 0..1 | 1.0 x 1.0 x 1.7 / 1.1 x 1.2 x 2.9 | shoulder pivot |
| `LA_IronArms` | the Warlord's dark iron arm shells, `stone` 0..1 (iron turns to stone) | 1.06 x 1.27 x 2.9 | shoulder pivot |
| `LA_WristNumbers` | burned wrist bands, 3 switchable numbers, Kid and Villain size, `glow` | band 1.04 square x 0.56 / 1.08 x 1.19 x 0.56 | shoulder pivot |
| `LA_SkyNumber` | the huge number over the giant, `digits` 0..1 | 102 wide x 42 tall x 1.2 | bottom centre |

Previews (Cycles): `lineup.png`, `gate.png`, `gate-giant.png`, `beast-poses.png`, `arms.png`, `crown-chains.png`, `numbers.png` (single frames: `_pv_*.png`).
Kid-safe choices: the beast has no fangs and narrowed AMBER eyes; the gate and the giant have a calm carved mouth line, no teeth, calm amber eyes; the arms in the walls are carved grey stone in tidy rows.

## LA_GateOfOaths (gate form)
- `LA_Gate` (all the stone: plinths, pillars, round arch, shoulders, the carved head; carved grey stone arms in tidy rows, palms up, like trophies on a rack: 7 rows of 3 on the front and back of each pillar, 7 rows of 2 on the outer sides, 4 inside the opening; charred plaques). Custom properties **`eyes`** and `shake`.
- `LA_Gate_Lids`, `LA_Gate_Eyes`, `LA_Gate_EyeLight`: follow `eyes` by themselves (plain SUM drivers). **Default `eyes` = 0 (closed).** **`la.set_eyes(coll, v, frame)`**: 0 = closed carved lids, 0.15 = a faint glow under the lids (line 8), 1 = open, calm amber glow + a warm light on the square.
- `LA_Gate_Numbers`: the burned glowing numbers (`1 IN 2`, `1 IN 40` on the shoulders, `1 IN 9`, `1 IN 300` on the plinths; front and back). Emission 7.
- `LA_Gate_ShakeDust`: falling grit and dust puffs, **hidden by default**. **`la.set_shake(coll, amount, frame, seed)`** tilts and slides the gate a little (delta transforms; new seed every frame or two) and shows the dust; `amount=0` puts it back.
- Empties: `LA_Gate_Socket_HeadTop` (0, -0.7, 27.9), `LA_Gate_Socket_ChainL/R` (under the capitals), `LA_Gate_Socket_ChainTopL/R` (shoulder corners), `LA_Gate_Mark_KidAtGate` (0, -9, 0).
- Face: eyes at (+-2.45, -3.7, 23.75), each 2.6 wide. No teeth: a calm carved mouth line and a carved beard.
- Materials: `LA_Mat_GateStone`, `LA_Mat_GateArmStone`, `LA_Mat_GateDark`, `LA_Mat_GateMoss`, `LA_Mat_GateEye` (reads Object attribute `eyes`), `LA_Mat_GateNumber`, `LA_Mat_GateDust`, `LA_Mat_GateDustPuff`.

## LA_WarBeast
Dark brown hide, tan muzzle and belly, a broad lower jaw and jowls, heavy angled brow ridges over small deep-set narrowed amber eyes, dark iron plates with brass rims, red flank cloths, ivory horns (23 across) and a small nose horn, brass nose ring, No fangs, mouth closed, no red anywhere on the face.
- `LA_WarBeast_Rig` (armature), `LA_WarBeast_Body` (rigid chunks, one bone each).
- **Bones:** `LA_Root` > `LA_Body` (move / pitch the whole trunk) > `LA_Hips` > `LA_Tail`, `LA_RearUpperL/R` > `LA_RearLowerL/R` > `LA_RearHoofL/R`; `LA_Body` > `LA_Chest` > `LA_Neck` > `LA_Head`, `LA_FrontUpperL/R` > `LA_FrontLowerL/R` > `LA_FrontHoofL/R`. L = +X (its own left).
- **Poses** (one-frame Actions `LA_BEAST_<name>` on muted NLA tracks, also `poses.json` > `beast.poses`): `la.apply_pose(rig, 'LA_BEAST_KNEEL', frame)`. Absolute poses, key with constant interpolation.

| Pose | What it shows | Eyes socket (x, y, z) |
|---|---|---|
| `STAND` | standing square, head forward | (0, -22.6, 12.9) |
| `PULL` | straining at its chains: low, leaning in, legs driving | (-0.8, -25.1, 8.6) |
| `CHARGE` | full gallop, horns lowered, hooves off the ground | (0, -21.4, 8.8) |
| `SKID` | haunches down, front legs braced stiff ahead, head thrown up | (0.1, -19.2, 18.0) |
| `KNEEL` | front knees on the ground, head level and low: a kid 8-10 BU in front looks it in the eye | (0, -22.2, 8.1) |
| `BOW` | kneeling, head bowed deep, horns laid forward (for the gate giant: turn the rig to face it) | (0, -21.8, 7.6) |
| `BOW_TO_KID` | kneeling, head dipped to the kid | (0, -21.9, 7.8) |

  Its nose reaches y -28 to -33; stand the kid at about y -36. Hooves in PULL / SKID dig up to 0.5 BU into the ground on purpose.
- **Sockets** (empties on bones, they follow the poses; per-pose positions in `poses.json` > `beast.sockets`): `LA_WarBeast_Socket_Rear` (ring on the rump plate: the sister's chain), `_Collar` (lead ring under the neck: the Warlord's chain), `_FlankL` / `_FlankR` (girth rings), `_Eyes`, `_Back`.
- **Chains** (built for STAND, parented to the rig object, they do NOT follow the bones): `LA_WarBeast_SisterChain_Taut` (shown; rear ring to a wrist at (0, 29.5, 1.55)), `_Slack` (hidden; down to the ground, along it, up to the same wrist point), `_Dropped` (hidden; lying on the ground with an open cuff), `LA_WarBeast_Cuff` (closed wrist cuff, inner 0.72, fits the sister's 0.62 wrist; origin at its centre; `la.attach_center(cuff, sisHdL)`), `LA_WarBeast_LeadChain_Taut` (collar ring to a hand at (-11, -9, 8.2)), `_Dropped` (hidden). Each chain has an `..._End` empty.
  For any other pose or layout make the chain yourself: **`la.chain_between(la.find(c, 'LA_WarBeast_Link'), p0, p1, sag=1.0, ground=0.16)`** (linked copies of the hidden link object between two world points, e.g. a socket's `matrix_world.translation` and the sister's hand).
- Materials: `LA_Mat_BeastHide`, `_BeastHidePale`, `_BeastIron`, `_BeastBrass`, `_BeastHorn`, `_BeastHoof`, `_BeastCloth`, `_BeastLeather`, `_BeastEye` (amber, emission 2.2), `_BeastDark`, `_BeastGlint`, `_BeastChain`.

## LA_LightningArms, LA_SparkBurst
- `LA_LightningArm_L` / `_R` (roots, custom property **`glow`** 0..1) with children `_Halo`, `_Light` (12 W at glow 1), `_Bolts_A..D` (only A shown). Each arm is three blocks (upper arm, forearm, fist): blue faces, bright cyan edge bars, a white-hot core in the seams and in a slot on every face; a small tight halo; each bolt shape is four fat tapered blue-white bolts in a cyan sleeve.
- Built for the **Cast v2 Hero kid** arm (0.80 x 0.80, shoulder pivot +0.16 to hand bottom -1.46). Put them on: `la.attach_arm(la.find(c, 'LA_LightningArm_L'), la.cast_arm(hero_coll, 'L'))` (parents to `heroarmL`, hides `heroAL` + `heroHdL`; rotate the cast arm empty as usual and the lightning arm follows). `_L` / `_R` follow the Cast v2 names (`L` is the -X arm); both are the same shape.
- Flicker: `la.variant(root, 'A'|'B'|'C'|'D', frame)`; pick different letters for the two arms in a still. Glow: `la.set_prop(root, 'glow', v, frame)`.
- `LA_SparkBurst` (root, `glow`) with `_Halo`, `_Light` (70 W), `_Shape_A..C` (seven fat bolts and a few star sparks each): `la.variant(root, 'B', frame, tag='_Shape_')`. Origin at its centre: place it on a fist or between the kid and the Warlord.
- Set `scene.cycles.transparent_max_bounces = 32` (the helpers do it). Strengths are set so the kid's face and shirt stay readable at night exposure 0 (see `arms.png`); if a shot still clips, key `glow` to 0.6. In daylight at exposure -1 they still read. Halos and bolt sleeves are additive see-through shells: keep the camera 1.5 BU or more from an arm.
- Materials: `LA_Mat_LightningShell`, `_LightningEdge`, `_LightningCore`, `_LightningSleeve`, `_LightningBolt`, `_LightningSpark`, `_LightningHalo`, `_LightningHaloWide` (all read Object attribute `glow`).

## LA_GroundSplit
- `LA_GroundSplit` (root: dark gap, glowing heart, heaved slabs along both lips, rubble; properties **`amount`** and `glow`), `LA_GroundSplit_Bolts` (little bolts standing in the crack), `LA_GroundSplit_Light_1..3`.
- The crack lies along **X** from -24 to 24 and opens from -X to +X as `amount` goes 0 > 1 (six stretches, shape keys driven by plain SUM drivers). Closed stretches are folded under z = 0: **it needs your ground at z = 0** to hide them. Rotate the root about Z to lay it across the beast's path.
- Materials: `LA_Mat_SplitStone` (grey-brown cobble stone: change its colour to match your ground), `LA_Mat_SplitDark`, `LA_Mat_SplitGlow`.

## LA_GateGiant (the gate standing up)
The same arch, 2.3 times bigger, is the torso (you see sky through its chest) and the carved face is the head. Legs, arms, hands and feet are bundles of **446 stone arms** (320 in the limbs, 126 in the walls) round dark stone cores, with fist-studded knots at the knees, elbows and shoulders, five arm-toes per foot and four arm-fingers and a thumb per hand. A rune chain swags across its chest and a broken chain trails from each wrist.
- `LA_GateGiant_Rig`, `LA_GateGiant_Body` (properties **`eyes`**, default 1, and `glow` for the chain runes), `LA_GateGiant_Lids`, `_Eyes`, `_EyeLight`, `_Numbers` (bone-parented, they follow the poses). `la.set_eyes(coll, v, frame, base='LA_GateGiant_Body')`.
- **Bones:** `LA_Root` > `LA_Hips` > `LA_Spine` (the whole arch) > `LA_Head`; `LA_Spine` > `LA_ArmL/R` > `LA_ForearmL/R` > `LA_HandL/R`; `LA_Hips` > `LA_ThighL/R` > `LA_ShinL/R` > `LA_FootL/R`. L = +X.
- **Poses** (`LA_GIANT_<name>`, muted NLA tracks, `poses.json` > `giant.poses`): `la.apply_pose(rig, 'LA_GIANT_RISING', frame)`.

| Pose | What it shows | Head top (x, y, z) | Eyes |
|---|---|---|---|
| `STANDING` | upright, arms hanging, 134.2 tall | (0, -1.6, 134.2) | (0, -8.5, 124.6) |
| `RISING` | half up: knees deep, back bent, its left hand pushing off the ground at (45, -54), right hand on its knee, head lifting. 98 tall | (-3.8, -18.0, 95.9) | (-3.9, -22.0, 84.8) |
| `LOOKING_DOWN` | standing, bent a little, head tipped 26 degrees down to the square, left hand lifting | (0, -18.6, 129.9) | (0, -18.8, 118.1) |

- Sockets (follow the poses): `LA_GateGiant_Socket_HeadTop` (put `LA_SkyNumber` 8 BU or more above it), `_Eyes`, `_HandL`, `_HandR`.
- The swap: hide `LA_GateOfOaths` (and `LA_GateChains`), show `LA_GateGiant` at the same origin. Its feet stand 36 BU apart, where the gate's pillars were 15 apart, so cut on the shake / dust.
- Kneecaps reach 37, hips 70, shoulders 112, fingertips 35. Town roofs (about 46) reach its thighs; the keep (56) is under its hips.

## LA_IronCrown
`LA_IronCrown`: eight-sided dark iron band with worn bright rims and rivets, eight tapered spikes leaning out (front 1.25 tall, then 0.95 and 0.62), a bright ridge down every spike, a dark red jewel on a bright diamond plate at the front. Inner width 1.76, so it clears the Villain's hair.
- On the Villain: **`la.crown_on(crown, villain_coll)`** (parents it to `villainH`, 0.2 below the top of the head; `lift`, `tilt` to adjust). It stands upright on the ground by itself (origin at the base): for line 24 just place it at the kid's feet.
- Close-up: 50 mm about 3 BU away. Materials `LA_Mat_CrownIron`, `_CrownIronWorn`, `_CrownGem`.

## LA_GateChains
Thick iron links (1.5 long, 0.95 wide) with a small amber rune on both sides of every second link; all rune glow follows the object's **`glow`** property.
- `LA_GateChains_Hanging` (shown, `glow` 0.35): for the gate at the same origin. A chain down the front of each shoulder corner ending in a closed rune cuff, and a swag across the opening on the front and one on the back.
- `LA_GateChains_Lashed` (**hidden**, `glow` 1): the two corner chains lashed out to a person's wrists, for the **standard layout**: gate at the origin, Villain on `LA_GateChains_Mark_Villain` (0, -12, 0) facing -Y, arms hanging. Hide `_Hanging`, show `_Lashed` (see `crown-chains.png`).
- `LA_GateChains_Cuff_L` / `_R` (**hidden**): closed rune cuffs sized for the Villain's wrist over the iron or stone shell (inner 1.08 x 1.19, 0.5 high), origin at the centre, chain lug on +Y. **`la.cuff_on(cuff, la.cast_arm(villain, 'L'))`** closes one round his wrist (it follows the arm) and returns the lug position.
- Any other layout (arms raised, Villain elsewhere): `la.chain_between(la.find(c, 'LA_GateChain_Link'), anchor, lug, sag=1.5)` from `LA_GateChains_AnchorL/R` (the shoulder corners) to the lug each `cuff_on` returned.
- Materials `LA_Mat_ChainIron`, `LA_Mat_ChainRune` (reads Object attribute `glow`).

## LA_StoneArms, LA_IronArms
Arm shells in the Cast v2 arm frame, a touch bigger than the arm. Put on with `la.attach_arm(shell, la.cast_arm(char_coll, 'L'))`, exactly like the lightning arms.
- `LA_StoneArm_Kid_L` / `_R`: rough chiselled grey blocks (upper arm, forearm, fist with finger grooves) for any Hero-kid-size arm (0.80 square, 1.62 long): the crowd kids. `LA_StoneArm_Villain_L` / `_R`: the same for the Villain (0.84 x 0.945, 2.76 long).
- `LA_IronArm_Villain_L` / `_R`: dark iron plates, shoulder cap, elbow band, gauntlet with knuckle plates, rivets.
- **`stone`** 0..1 on each root (`la.set_prop(shell, 'stone', v, frame)`): the stone creeps from the fist up to the shoulder with a wobbly edge and a thin amber rim while it moves.
  - `LA_IronArm_*`: 0 = all iron (default), 1 = all stone. This is line 20: key 0 > 1.
  - `LA_StoneArm_*`: 1 = all stone (default); below 1 the part above the line is see-through, so use `la.attach_arm(..., hide_cast=False)` if you animate it. For "stone arms" as a fixed look leave it at 1.
- Kid-size shells on other cast: Big kid and others have other arm sizes; the shell is 0.90 across, so it fits arms up to about 0.85.
- Materials `LA_Mat_ArmStone`, `LA_Mat_ArmIronToStone` (read Object attribute `stone` and the mesh attribute `creep`).

## LA_WristNumbers, LA_SkyNumber
- `LA_WristBand_Kid_L` / `_R` and `LA_WristBand_Villain_L` / `_R`: a charred black band with ember edges round the forearm just above the hand (the Villain's sits above the chain cuff), the number on all four faces. Children `_N_2`, `_N_1M`, `_N_10M` and `_Light`.
  - Put on: `la.attach_arm(band, la.cast_arm(char, 'L'), hide_cast=False)`. They fit over the bare arm, the lightning arm and the stone / iron shells.
  - Switch: **`la.set_number(band, '1 IN 2' | '1 IN 1,000,000' | '1 IN 10,000,000', frame)`**. Defaults: Kid 10M, Villain 1M.
  - **`glow`** 0..1: 0 = black burned band, 1 = glowing number (key 0 > 1 for "burns a number on your wrists").
  - Close-up: 50 mm about 3-5 BU from the wrist; `1 IN` sits small over the big number on the two long ones.
- `LA_SkyNumber`: `1 IN` over two rows, `847,362,951,406,` and `283,715,069,524` (30 digits: too long to read on purpose). Glyphs 13 BU tall, facing -Y. **`digits`** 0..1 reveals it glyph by glyph in reading order (0.12 = `1 IN`, 0.55 = the first row, 1 = all); the newest glyph burns white-hot. `LA_SkyNumber_Light` warms the giant's head.
  - Place it at the giant's `Socket_HeadTop` + 8 BU up; turn it about Z to face the camera.
- Materials `LA_Mat_BandChar`, `_BandEmber`, `_BandNumber`, `LA_Mat_SkyNumber` (reads Object attribute `digits` and the mesh attribute `order`).

## Notes
- No Python drivers: properties reach children through SUM drivers with generator / limits modifiers. Materials read them with Attribute nodes (Object).
- The .glb files carry every state at once (all bolt shapes, dust, all chain variants): hide what you do not want. Glow fades and drivers are not in the .glb.
- Poppins Bold was used to cut the numbers; they are plain meshes now, no font is in the file.
- **Limits:** the beast's chains are built for STAND and do not follow the bones (use `la.chain_between`). The giant's `RISING` pose pushes its planted fingers and back foot up to 6 BU into the ground, and its limb arms overlap each other by design. The giant is 229k vertices with everything else: fine for stills. In the .glb every wrist number, both chain states and the whole sky number show at once, and `stone` / `digits` / `eyes` do not animate there.
- The `eyes` light of the gate (2500 W) and the giant (14000 W) and the sky number light (60000 W) are sized for night wides; scale `energy` drivers' generator if they clip.
- Rebuild: `python3 -I src/build.py`, then `python3 -I src/la_export.py`; previews `SHOT=<name> python3 -I src/la_previews.py`.
