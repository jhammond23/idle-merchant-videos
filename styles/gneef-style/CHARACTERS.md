# Character kit: Inkface Blockfolk (for build style "Torchlit Blocktale")

*How the characters in @Gneef's shorts are constructed, measured from frames, so we can build **new characters of our own** the same way. Copy the construction only, never their characters: no orange-spiky-hair lead in a cream sweater, no porcelain-doll creature, no named designs. Every new person still goes through the Studio Bible cast check before a full render.*

## 1. Head
- **Shape:** the classic rounded block head (a cylinder-ish box with heavily rounded edges). It is never a sharp cube, which fits Jake's 11-24 rounded-head rule. One head mesh is used for every person, kid or adult.
- **Size:** head (without hair) = **25% of total body height** (measured on full-body frames: 105 px head in 420 px). Head width ≈ 0.62 x torso width, so the torso is 1.6 head-widths wide.
- **Hair** sits on top as a separate chunky mesh and adds **30-40% to head height**. It overhangs the sides by 10-15% and covers the forehead down to the brow line.
- **Matte plastic skin**, roughness about 0.5, smooth shading, no subsurface, no pores. The grade does the colour work: warm scenes push skin to orange-peach, nights to lilac.

## 2. Face construction (a flat ink "sticker" on the front of the head)
All features are flat vector shapes in black ink `#111111` on the skin colour. There is no nose, no 3D features, no eyelids and no highlights in the standard set.

| Part | Construction (as % of head width W / head height H) |
|---|---|
| Eyes | Solid black **vertical ovals**, about 9% W wide x 14% H tall, centres ±13% W from the midline, at about 45% H from the top of the face. No whites, no pupils, no shine |
| Eye variants | Happy: an upward arc (^) with 1-2 tiny lashes. Sleeping or sad: a downward arc. Shocked: an inverted V (^ ^). Squeezed shut: > <. **Terror:** white sclera ovals with a black outline and small pupils (the only time whites appear), paired with an open wavy mouth |
| Brows | Optional thick tapered strokes, 3-4% H thick, 18% W long. Flat = calm; inner ends down 20-25° = angry or determined; inner ends up 20° = scared or sad |
| Mouth | Centre at about 70% H. Shapes: flat dash (neutral), small closed arc (smile, frown), off-centre hook (smug), **open D with red fill `#D7262B` and pink tongue `#F06A6A`** (happy or shouting), black ring with red inside (shocked), rounded white rectangle with 3 vertical tooth lines (gritted), zigzag (scared), small black "o" (surprised or sleeping) |
| Line weight | 3-4% of W, slightly tapered ends, a hand-drawn feel |
| Extras | Blush: 3 short pink `#F59BB0` hatch lines under each eye (happy or shy). Tears: light-blue `#6EC3F4` drops under the eyes. Adult men: a dark stubble dot texture on the lower third. Sweat drop: one blue drop at the temple |

**Expression set** (all drawn on `charsheet.png`): neutral, smug/sure, happy, shocked, scared, angry, gritted (determined), crying. Add sleepy and surprised-o if needed.
- **How often faces change:** one expression per shot. It is swapped on the cut, never inside a shot: no lip sync, no blinks (checked in the 30 fps windows). A character's expression usually changes between consecutive close-ups (about every second close).
- A face's expression must read in **0.3 s on a phone**. Big mouth shapes do most of the work.

## 3. Body proportions (measured)
| Measure | Value |
|---|---|
| Head (no hair) : total height | **0.25** (0.31 with hair) |
| Torso height : total | 0.37 |
| Legs : total | 0.38 |
| Torso width : head width | **1.6** |
| Shoulder span with arms : head width | **3.7** |
| Arm width : torso width | 0.5 (arm length = torso height) |
| Leg width : torso width | 0.5 each (leg length = torso height) |

- **Blocky R6 boxes everywhere:** torso 2 x 2 x 1, arms and legs 1 x 2 x 1, hands the same width as the arm (a skin-coloured cuff at the bottom of each sleeve).
- **Kids vs adults:** the source uses the *same* body size for kids and adults and tells them apart by face (stubble, beard), hair and clothes. For our medieval cast we scale kids to **0.85** (little ones 0.62, like Cast v2's little sister) so a parent and child read at once. Keep the proportions identical; scale the whole root.
- **Babies:** a head-dominant small body (head ≈ 45% of height), usually framed inside a cradle or cart.

## 4. Body-type variety
The source has very little body variety among people (almost all classic R6). Variety comes from:
1. **Hair silhouette** (spiky, long sheet, bun, bald, hat).
2. **Clothing colour blocks** (one dominant colour per person).
3. **Size** (kids 0.85, adults 1.0, the occasional big guard 1.05-1.1 with a wider torso).
4. **Creatures and "big things"**, which are the real shape contrast: 1.5-2x adult height, thin or massive, pale or desaturated against the saturated cast, often with one uncanny detail or a different material (porcelain, carved wood with drawn eyes, bark). For kid-safe medieval use: a tall lantern-headed watchman, a walking tree, a carved wooden puppet-guard, a stone guardian.

Use Cast v2's body types (classic R6, slim tall, wide chunky, small kid, very tall adult, muscular) but **keep the R6 box construction and the classic head** for this style.

## 5. Skin tones
| Hex | Use |
|---|---|
| `#F6D2B0` | Light |
| `#F0BE8C` | Light warm (the measured kid skin reads `#FDAE63` lit / `#DE7F3B` shade under the ember grade) |
| `#E3A06C` | Tan |
| `#C98E5F` | Medium |
| `#8D5A3B` | Brown |
| `#5A3524` | Deep brown |
| `#F5CD30` | Classic bright yellow (the older format used it; good for comic villagers and guards) |

## 6. Hair
- **Chunky low-poly shards** (8-14 big spikes or locks), flat saturated colour, smooth shading, no strands and no texture. Long hair is a solid sheet to the chest with a side fringe over one eye.
- **One loud hair colour on the lead:** orange `#F56E02` is the source's choice; ours should be a different signature (e.g. our hero's brown crop plus his burnt-orange shirt).
- **Palette:** orange `#F56E02`, chestnut `#7A4A2A`, wheat blond `#E8C25A`, black `#1E1A1A`, grey `#B8B4B0`, rust `#A63A1E`.
- Hair overhangs the face to the brows. Expressions still read because the eyes sit below the fringe.

## 7. Clothing
- **Layers:** a base shirt and trousers (the R6 shirt and pants areas) plus one 3D layer (jacket, vest, apron, cloak, knit sweater) on leads and adults.
- **Textured fabric is the most detailed surface on screen:** cable knit, denim twill, worn leather with creases, fleece. Bump strength 0.18-0.30, visible in close-ups.
- **Colours:** one dominant mid or light colour per person (cream, teal, brown, black, sky blue). The lead's signature colour is unique in every shot.
- **Diegetic props on bodies:** a number plate on the chest, a sash, a badge. These carry the story rule (for us: a guild token, a rank sash, a glowing mark).

## 8. Accessories
Big, simple, readable at phone size: hats and helmets, satchels, lanterns, wooden swords, crowns, staves, ropes and knots, keys. Glowing magic accessories use emissive magenta `#E722BD` or ember `#E35214` with bloom.

## 9. Materials and shading on characters
- Skin and hair: plastic (roughness 0.5, specular 0.5), no outline. Clothing: fabric with bump and noise colour variation (Cast v2 `fabric()`). Metal: low roughness with strong highlights. Emissive for magic.
- **Lighting on characters:** one motivated key (lantern or moon), a warm-cool split on night exteriors, and no fill light (shadow sides go dark), so the face sticker is always readable.

## 10. How characters move
- **Mostly held poses:** idle or standing, arms raised to the sides ("what?!"), pointing, sitting, lying in bed, cowering, carrying. The camera supplies the motion.
- **Walks and runs** use plain game animations: legs swing as stiff boxes and arms counter-swing, about 1 step every 0.5 s on a walk. Ragdoll tumbles for falls.
- **Crowds** stand in rows doing the same simple thing. Offset their idles (Cast v2 rule) so they never move in sync.
- **No lip sync and no blinks.** The face changes only on cuts.

## 11. How many characters, and how they are told apart
- **6-15 distinct people per video** (Watcher's Knot about 8, Awake At Night about 6 plus a crowd, 1M Steps 15+, Love Chains about 8, Line Of Sight about 8), plus at most 1-2 creatures. The same lead recurs across videos (a series face).
- They are told apart by **hair colour and shape first**, clothing colour second, and size or creature silhouette third. Faces share one drawing style.
- **The lead is in about half of all shots** and always has the signature colour.

## 12. Recipe: build a new character in this style with Cast v2
Code: `/tmp/claude-0/cast2/cast_v2.py` (`person()`, `fabric()`, `head_mat2()`, hair keys via `hair_col()`), helpers in `/tmp/claude-0/cast2/src/lib.py`, package on `scripts-inbox` under `cast-v2/`.

1. **Body:** call `person(name, shirt, pants, skin, face, hair, head='classic', ...)` with the **R6 defaults**: `tw=2.0, td=1.0, th=2.0, lh=2.0, lw=1.0, aw=1.0, al=2.0, hs=1.0`. Set the size with the root scale `s`: adult 1.0, kid 0.85, little kid 0.62, big guard 1.05 with `tw=2.4`. Don't use the slim or tall overrides for people in this style (save those for creatures).
2. **Head:** `head='classic'` (the rounded Classic Roblox head mesh already loaded as `CMESH`), not the bevelled-cylinder `refl` head. Keep it rounded.
3. **Face texture:** draw a new 1024x1024 transparent PNG per expression with flat black vector shapes using the proportions in section 2. Eyes are solid ovals, 9% x 14% of width; mouth fills red `#D7262B`. Save it as `/tmp/claude-0/cast2/faces/face_<name>_<expression>.png` (picked up by the patched `lib.face_path`). Use `head_mat2(..., fs=0.80-0.86)` so the features are large enough to read in a full-body shot. Make all 8 expressions before the build.
4. **Skin:** pick from section 5 via `srgb(*rgb)`. Roughness 0.5 (the default in `mat`).
5. **Hair:** use an existing hair key (`hair_col(key)`) and tint it with `tint_hair(key, rgb)` from the hair palette. Scale `hair_s` 0.95-1.05 so it overhangs the head by 10-15%.
6. **Clothing:** `fabric(name, rgb, sc)` for shirt and trousers. Add one 3D layer with `box(...)` (vest, apron, jacket panel) using a knit, denim or leather fabric. Raise the bump strength to 0.25 for knits.
7. **Signature colour:** only the lead gets the hero colour. Check every other character's colours against it.
8. **Accessories:** `box`, `cone`, `torus` and `ball` helpers; emissive accessories via `mat(..., emit=..., estr=5-8)`.
9. **Rig and idle:** the R6 pivots (`armL`, `armR`, `legL`, `legR`) take held poses (`arms=`, `out=` angles). Add breathing (torso scale Z ±1%, 3 s period) and offset idles per character.
10. **Check:** render a cast-check still under the style's lighting (ember interior and moon night) at phone size. Confirm the face reads at 0.3 s and the lead's colour is unique. Push `proofs/<story>/cast-check.png` per the Studio Bible.

**What to change from our current Cast v2 defaults:** use the classic head, not `refl`; use flat ink sticker faces with solid oval eyes instead of the anime or line-art sets; keep R6 box proportions for all people; scale kids by root `s` instead of reshaping them; and make clothing the most textured surface.
