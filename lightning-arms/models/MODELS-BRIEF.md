# I TRADED MY ARMS FOR LIGHTNING: model kit brief (Claude's model builder)

Build the big and important 3D models for this film first, so the video builder never spends its time modelling.
- Work fully in this cloud container.
- Don't touch Jake's PC, Metricool, social accounts or any paid generation service. Free only: procedural geometry and shaders.

## The story (final script): /tmp/claude-0/tv/lightning/final.txt
In this town every kid trades their arms once at the Gate of Oaths. The gate keeps the old arms in its stone and burns a rarity number on the wrists: half get stone arms (1 IN 2).

The kid got lightning arms (1 IN 10,000,000). The Warlord's law says the rarest arms wear the iron crown, and his iron arms are only 1 IN 1,000,000. He can't steal the kid's arms, because the gate's chains grab anyone who tries and turn their arms to stone, and then the gate itself wakes up.

So he chains the kid's little sister to his horned war beast, which kneels only to the rarest arms in sight. At midnight in the torchlit square the beast charges. The kid's lightning splits the ground, and the beast skids and kneels to him. The Warlord grabs the kid's wrists, so the gate's chains snap round his own wrists and his iron arms turn to stone.

The town takes his crown. Then the Gate of Oaths stands up on legs and arms made of every arm it ever kept, towers over the castle, and a huge number burns over its head. Kid-safe: nobody is hurt.

## Look and units
- **Style:** the house storybook look (/home/claude/STUDIO-BIBLE.md). Chunky, Roblox-like blocky shapes, soft bevels, readable silhouettes, textured (not flat) materials, bright and readable even at night.
- **Units:** 1 m = 3.3 BU.
  - Front of every asset = -Y, up = +Z.
  - All scales 1, rotations 0, origin at the base centre unless stated.
- **Cast for scale:**
  - Cast v2 (/tmp/claude-0/cast2/pkg/cast-v2.blend): Hero kid 4.16 BU, Little sister 3.37, Villain (the Warlord).
  - Cast v3 (/tmp/claude-0/cast3/cast-v3.blend; CAST-V3.md) has `Cast v3 | Boss Giant`: a reskinnable giant rig (skins, weak point, horns/crown/chains toggles). You may build the standing gate giant on it, scaled up.
- **Blender:**
  - python module bpy 5.3 (`python3 -I script.py`). Cycles only.
  - Jake's PC runs Blender 5.1, so ALSO export a .glb backup per collection.
  - Keep everything procedural or packed, with no Python drivers.
- **Reference for format and quality:** the last kits, /tmp/claude-0/tv/fakepower/models/ and /tmp/claude-0/tv/tinyseed/models/ (MODELS.md, src/, glb/, poses.json). Use the same structure, prefix `LA_`.
- **Shared machine:** 2 cores and 8 GB, shared with the video builder.
  - Run one Blender process at a time, under nice 19, and keep it under ~1.5 GB.
  - Check `free -m` before each render and wait if available memory is under 2.5 GB.
  - Never kill another process.
  - Keep disk use under ~600 MB (/tmp has about 2.8 GB free).

## Models (in priority order)
1. **`LA_GateOfOaths` (Huge): two forms in one file.**
   - **(a) GATE:** a huge carved stone arch about 25 BU tall in the town square.
     - Its walls are set with rows of stone arms, with old arms poking out of the stone like a wall of trophies.
     - It has big burned glowing numbers and heavy rune-carved chains hanging from it (see 5).
     - A carved stone face at the top, eyes closed. It needs an `eyes` property (0 closed, 1 glowing open) and a `shake` pose/flag.
   - **(b) GIANT:** the gate standing up as a towering giant at least 120 BU tall (taller than the backlot castle keep).
     - Its legs and arms are made of hundreds of stone arms, plus the arch-shaped torso with the face.
     - Rig: root, hips, spine, head, arms, legs.
     - Poses: RISING (half up), STANDING, LOOKING_DOWN.
     - Awe, not horror: calm glowing eyes, no teeth.
2. **`LA_WarBeast` (Huge).** A heavy blocky horned war beast (bull/rhino-like, armoured plates, big curved horns), about 18-22 BU at the shoulder.
   - A harness with chain points and a chain to a small wrist cuff, for the sister. Slack and taut chain variants.
   - Rigged, with poses as Actions on muted NLA tracks: STAND, PULL (straining), CHARGE, SKID (hooves dug in), KNEEL (head level with a kid), BOW (low bow toward something huge), BOW_TO_KID.
   - Fierce but kid-safe: no fangs, no red eyes.
3. **`LA_LightningArms` (Hero prop).**
   - Crackling blue-white lightning arms that replace the Hero kid's arms (measure his arm bones in the cast file).
   - Blocky arm shells of light, 3-4 alternate bolt shapes for flicker, and a `glow` 0..1 property.
   - Plus `LA_SparkBurst` (sparks off the arms) and `LA_GroundSplit`: a glowing jagged crack in the ground, with an `amount` property for how far it has opened.
4. **`LA_IronCrown` (Hero prop).** A heavy dark spiked iron crown that fits the Cast v2 Villain's head. It must read clearly as power in a close-up.
5. **`LA_GateChains` (Big).**
   - Thick iron chains with glowing runes and cuffs.
   - A version hanging from the gate, and a version lashed out and snapped round a person's two wrists (fit the Villain).
   - Plus two arm-shell sets, all with a `stone` 0..1 property (stone creeping up the arm):
     - `LA_StoneArms`: rough grey stone arm shells, to fit the Hero kid size (for the crowd kids) and the Villain.
     - `LA_IronArms`: the Warlord's dark iron arm shells, to fit the Villain.
6. **`LA_WristNumbers` (Hero prop).**
   - Burned glowing wrist bands with switchable text: **1 IN 2**, **1 IN 1,000,000**, **1 IN 10,000,000**. Readable in a close-up.
   - Plus `LA_SkyNumber`: a huge floating glowing number display for over the gate giant's head, with a `digits` property 0..1 (how many digits have appeared, climbing; the full number is too long to read on purpose).

## Deliver
- **/tmp/claude-0/tv/lightning/models/:**
  - `lightning-models.blend` (compressed, packed)
  - `glb/<collection>.glb`
  - `poses.json`
  - `src/` (rebuildable scripts)
  - `MODELS.md` (append instructions, sizes, origins, bones, poses, properties and materials, like the Fake Power MODELS.md)
- **Preview renders** (Cycles; enough samples to judge):
  - `lineup.png`: everything next to the Hero kid and sister for scale.
  - `gate.png`: gate form, eyes closed and open.
  - `gate-giant.png`: standing, with a tiny castle or kid for scale.
  - `beast-poses.png`
  - `arms.png`: lightning arms on the Hero kid; stone and iron arms on the Villain, stone 0 / 0.5 / 1.
  - `crown-chains.png`
  - `numbers.png`
- **Check yourself before finishing:**
  - scale true against the cast
  - nothing floating or intersecting
  - glb files open
  - MODELS.md matches the file
- **Final message:** what you built, the file paths, and anything you could not do.
