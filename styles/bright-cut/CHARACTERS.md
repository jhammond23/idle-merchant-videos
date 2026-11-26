# Character kit: Sunny Block Folk (goes with build style `bright-cut`)

**One line:** Toy-block townsfolk with rounded block heads, flat 2D cartoon faces that swap every shot, and a single bright garment each. They're readable at phone size in a 0.7-second shot.

This kit tells Claude how to build **new characters of our own** in the measured style of cannonanimates' reels. It copies the method only: no character, name, hair design, outfit or face of theirs. Builders still never invent people. Per Cast v2 rules, only Claude creates new characters, and builders use what is in the cast files.

Evidence: 5 videos (21M, 15M, 7.9M, 6.5M and 5.4M views; URLs are in `STYLE.md` section 19). Measurements are from full-resolution 1080x1920 stills and 10 to 30 fps contact sheets.

---

## 1. Head shape and size
- **Shape:** a Roblox-style **rounded block** (a cube-ish cylinder with heavily beveled edges), about as wide as it is tall, with flat front faces. It's not a sphere, not a sharp cube and not a puppet head. This matches Jake's 11-24 "rounded head" rule.
- **Size (measured on a frontal full-body still):** head skin height **0.225** of body height without hair (180 px of 800 px). With hair it's **0.29** (255 of 875 px). The head is about 205 px wide against a shoulder line of about 300 px (3/4 view), so **shoulders are 1.4 to 1.7 head-widths**.
- Every person uses the same head mesh. Variety comes from hair, face and outfit, not head shape.

## 2. Face construction (flat decal on the head front)
The face decal covers the central **about 70% of head width and about 60% of head height**. Eyes sit on a line about 45% down from the top of the skin. The mouth sits about 75% down. There's no nose, no ears and no eyelashes, except on a few feminine line faces.

**Register A: line decals (wide and medium shots, about 70% of all faces)**
- Eyes are small black dots or vertical ovals (about 6 to 8% of face width), or arcs for closed, happy or sleepy eyes.
- The mouth is one black stroke: a smile arc, a frown arc, a flat line or a small open "D".
- The stroke is about 3% of face width (about 6 px on a 200 px face). No outline around the face.

**Register B: comic punch faces (close-ups and reactions)**
- **Eyes:** large round or oval whites, **each 25 to 30% of face width**, spaced about one eye-width apart. They have a thick black outline (about 5% of face width), a **tiny black pupil** (4 to 6% of face width, or a pinpoint for shock) and **no glossy highlights**.
- **Brows:** thick black strokes, angled for anger, raised for shock, tilted for worry. One brow up and one eye squinted for scepticism.
- **Mouth:** an open shape with a black outline: a gritted teeth row (a white band with a centre line), a "D" grin with a pink tongue (`#F06C8F`), a wobbly worried line, or a wide scream.
- **Extras:** stress hatching under the eyes (thin grey-brown lines), **blush hatching** (three diagonal pink strokes `#E86A7A` on each cheek for joy or embarrassment), and a tear drop for crying.
- **Shadowed eyes (special):** a dark gradient band covering the top 40% of the face, with a flat line mouth. Use it for ominous reveals.
- Faces are **flat, matte line art**. Jake rejected glossy puppet eyes with blush (the "Coraline" build). So never use 3D eyeballs, eye shine or soft-shaded blush.

## 3. The expression set and how often it changes
Each character needs at least these 10 faces (line and comic versions where marked):

| # | Expression | Line decal | Comic version |
|---|---|---|---|
| 1 | Neutral | dot eyes, flat mouth | n/a |
| 2 | Happy / laughing | arc eyes `^ ^`, open D-grin | closed arc eyes, open grin with tongue, blush hatch |
| 3 | Smug | half-lid eyes, side smirk | lidded eyes, one brow up, smirk |
| 4 | Shocked | big dots, small "o" | huge round whites, pinpoint pupils, raised brows, open mouth |
| 5 | Scared / worried | oval eyes, wobbly mouth | round whites, tilted brows, gritted wobbly teeth, stress hatch |
| 6 | Angry | slanted brows over dots | round whites, tiny pupils, V brows, grimace with teeth |
| 7 | Sad / crying | arc-down eyes, frown | brows up, frown, tear drop |
| 8 | Determined | brows down, flat mouth | narrowed eyes, V brows, gritted grin |
| 9 | Sceptical | one dot, one squint | one round eye, one squint, raised brow, small open mouth |
| 10 | Ominous | shadow band, flat mouth | n/a |

- **When faces change:** on the cut. A face never animates inside a shot: no lip sync and no blinks. A character who appears in consecutive shots usually gets a new face for each reaction. The exception is T4 in `STYLE.md`: during a crash push-in, the face swaps once at about 65% of the move (for example, blank stare to shocked-angry).
- **Mix:** wide and medium shots use line decals. Every close-up of a reacting face uses a comic face.

## 4. Body proportions (measured, in studs, matching the Cast v2 R6 rig)
| Part | Measured share of height (no hair) | Cast v2 value |
|---|---|---|
| Head (skin) | 0.225 | 1.2 of 5.2 = 0.23 |
| Torso | 0.36 | 2.0 of 5.2 = 0.38 |
| Legs | 0.41 | 2.0 of 5.2 = 0.38 |
| Shoulder width / head width | 1.4 to 1.7 | 2.0 / 1.2 = 1.67 |
| Arm width / torso width | about 0.5 | 1.0 / 2.0 = 0.5 |
| Arm length (shoulder to fingertip) / torso height | about 1.0 | 2.0 / 2.0 = 1.0 |
| Hair above the head | adds 25 to 45% of head height | hair scale 0.9 to 1.1 |

Limbs are straight rectangular blocks with slightly rounded edges. Hands are simple mitts or 4-finger cartoon hands in skin colour.

## 5. Body-type variety
Their towns use **almost one body size for everyone**. Adults and kids are the same height, and parents are told apart by clothes and hair, not size. Size variety comes from creatures and from a few classic blocky "newbie" figures in crowds. For us:
- **People:** scale 0.85 to 1.0. Kids 0.85 to 0.9, adults 1.0, the locked hero kid at 0.8 (unchanged).
- **Wide** (torso width 2.4) and **tall** (scale 1.1) only for guards, smiths and kings, and at most one per shot.
- **Classic yellow blockies** (`#F5CD30` skin, plain shirt and trousers) as crowd fillers and comic relief, as their reels do.
- **Creatures** are the opposite: detailed, organic, fur and feather textures, true scale (a fox at knee height, a dragon five times the height of a person).

## 6. Skin tones
Measured: `#F4D4B7` (light, lit), `#E9C4A3` (default, lit), `#E2B282` (warm), `#E6BA7E` (golden), `#CD9E79` (default in shade), and classic yellow `#F5CD30` for crowd blockies. Their casts are mostly light and default tones. **For our diversity rule, extend with** `#B07A55` (tan-brown), `#8A5A3C` (brown) and `#5E3B2A` (dark brown). Skin is flat, smooth plastic (roughness 0.45, low specular), with no subsurface scattering, freckles or texture.

## 7. Hair
- Chunky single-mesh "accessory" hair sits on the head like a helmet: spiky, swept fringe, side swoop, long straight, bun, twin tails. It's **saturated, glossy** (roughness 0.35, one strong highlight) with painted strand grooves.
- Colours seen: near-black `#13121B`, dark brown `#352D2C`, chestnut `#693610`, blonde `#E3C27A`, red `#B3261E`, pink `#B888C0`, blue-grey `#576574`.
- The silhouette is the ID: every character in a story must have a different hair outline at thumbnail size.
- Never reuse their specific hair designs. Use our own Cast v2 hair library (`hero_*`, `face_*` beards) tinted with these values.

## 8. Clothing
- **Printed 2D clothing** on the blocks (shirt and trousers textures): jackets over graphic tees, uniforms with lapels and ties, denim with a visible diagonal weave, sports kits, aprons and chef whites.
- **Colour rule:** neutral base (white, grey, black, denim, `#A2ABBB` grey) plus **one bright accent garment per character** (red, blue, pink or green). No two people in a shot share the accent.
- **Medieval translation:** tunic and trousers printed with a belt line, a laced collar, patches and stitching. A tabard in the house colour over grey mail print. An apron over a red shirt for the baker. A cloak as a 3D accessory in the accent colour.
- **Accessories** carry identity: glasses, headbands, hats (chef, crown, hood, pot helmet), satchels, a held prop (sword, broom, bread, a ball). Keep 1 or 2 per character.

## 9. Materials and shading on characters
- Skin: Principled, roughness 0.45, Specular IOR Level 0.35. Clothes: roughness 0.8, bump 0.05 to 0.08 (a subtle printed weave). Hair: roughness 0.35. Metal accessories: metallic 0.8, roughness 0.3.
- Lit by the noon sun plus sky fill (see `STYLE.md` section 15). No rim lights, no toon ramps and no outline on the body.
- Optional: the 2 to 4 px light halo from final sharpening (`unsharp=5:5:0.8`).
- Power state: the whole body swaps material (glowing translucent power colour, solid red, stone, steel, ice) and fades over 3 to 15 frames.

## 10. How characters move
- **Idle:** a gentle 2 to 3 s sway or breathing, offset per character so crowds never move in sync (Bible rule kept).
- **Walk and run:** stiff game cycles with limbs swinging from the shoulder and hip and no knee bend (R6). A walk is about 1 s per cycle, a run about 0.6 s.
- **Gestures and emotes:** point, wave, cross arms, hand on head, shrug, cheer, a kneeling slump. They snap into pose in 4 to 8 frames and hold while the camera drifts.
- **Timing:** key poses every 6 to 12 frames (estimated by eye from 30 fps strips), linear in-betweens. Snappy, not floaty.
- **Faces:** never animated inside a shot. They swap on the cut.

## 11. Cast per video and telling people apart
- 8 to 20 distinct people per video (Phase about 8, Material about 10 plus a crowd, Spirit Beasts about 12 plus 8 creatures, Borrow about 15, Tag about 15).
- People are told apart by, in priority order: hair silhouette and colour, accent garment colour, accessory, skin tone, and in close-ups the face style.
- The hero always wears the one colour nobody else wears (our burnt-orange `kid` keeps that role).

## 12. Recipe: building a new character with our pipeline (Cast v2)
Source: `/tmp/claude-0/cast2/cast_v2.py` (the copy at `/tmp/claude-0/tv/cast2/cast_v2.py` named in the brief does not exist; this one and `pkg/cast_v2.py` do), Blender 5.x, `scripts-inbox` `cast-v2/`.
1. **Head:** for every new character, call `person(..., head='classic')` so the character uses the library "Classic Roblox head" mesh (`CMESH`: rounded block, smooth shaded). Keep `hs=1.0` (1.1 only for comic relief).
2. **Proportions:** keep Cast v2's R6 blocks: `tw=2.0, td=1.0, th=2.0, lh=2.0, lw=1.0, aw=1.0, al=2.0`. People `s=0.85 to 1.0` (hero stays 0.8). Wide types `tw=2.4`. Tall types `s=1.1`.
3. **Faces:** make two decal sets per character as 1024x1024 PNG with alpha, black strokes only.
   - (a) Line set: the 10 expressions in section 3, stroke 3% of the face width.
   - (b) Comic set: expressions 2 to 9 in section 3, eyes 25 to 30% of face width, outline 5%, no shine.
   - Put them in `faces/` and use `head_mat2(name, skin, face, fs)` with **`fs=0.86` for line faces and `fs=0.78` for comic faces** (bigger on the head). Swap the image per shot, never inside a shot (except T4).
4. **Skin:** choose from section 6, and use `mat(name+'k', srgb(...), 0.45)` for the hands.
5. **Clothes:** `fabric(name, rgb)` with the bump lowered to 0.08 and the noise contrast reduced (ColorRamp stops 0.45 and 0.55). Choose a neutral base plus one accent garment from section 8, then add the printed details (belt, stitching) as a texture or thin boxes.
6. **Hair:** `tint_hair(key, rgb)` with a library hair (never a copy of theirs) and colours from section 7. Check that the silhouette differs from every other character in the story.
7. **Accessories:** 1 or 2 from the existing helpers (`cone`, `torus`, `ball`) or the Lunchbox packs: crown, hood, pot helmet, satchel, held prop.
8. **Idle:** add the shared idle with a random phase offset. Keep pose pivots on `armL/R` and `legL/R`.
9. **Check:** render a cast-check still (front, 35 mm, noon light from `STYLE.md` section 15) beside two existing Cast v2 people, at phone size (360 px wide). It passes if the character is readable in 0.7 s, differs from the others in at least 3 traits (Cast v2 rule), and the comic face reads at 200 px.

What changes from current Cast v2:
- The head mesh is classic for every new character, not the rounded cylinder. The locked hero `kid` keeps his Reflection head so old films still match.
- Faces move from Pokemon-style and anime sets to flat line plus comic decals.
- Clothing bump is lower (printed look).
- Size range narrows to 0.85 to 1.0.
- The hero gets the only bright colour in the shot.
