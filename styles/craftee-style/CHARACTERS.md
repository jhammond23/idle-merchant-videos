# Toybox Blockfolk: the character kit for Toybox Fable (`craftee-style`)

This kit lets us build NEW characters of our own in the method used by Craftee Films. It never copies their characters, designs, outfits, faces or names. Everything below was measured from 6 of the account's videos (18 stills at 540x960, 385 mid-shot frames, 30 fps strips). The face parts on `charsheet.png` are our own vector drawings.

**In one line:** classic blocky R6 bodies that are all the same height, a rounded classic head, and a big thick-ink hand-drawn face that does all the acting and swaps on almost every shot. The hero wears bold two-colour stripes and has hair in a colour nobody else in the film has. Creatures are either plush-round or shaggy-huge, with glowing eyes.

---

## 1. Head shape and size
- **Classic rounded head:** a short cylinder with flat-ish top and bottom and a big bevel (reads as a rounded square from the front). It is 1.25 wide by 1.25 tall in torso units (torso is 2 wide). This fits the Studio Bible's "rounded head" rule. Our classic head mesh in Cast v2 (scaled to 1.3 wide) is the right shape.
- Head-to-body height: **0.24** (measured on a full-body front shot: head 70 px of a 290 px body without the hat; R6 theory 1.25/5.25 = 0.238).
- Same head size for kids and adults. No big-head chibi variants.

## 2. Face construction (measured on 4 large faces, head width = 1.0)
- **Ink:** near-black warm brown `#1E140E`. Stroke weight 3 to 4.5% of head width. Brush strokes taper at the ends. No coloured outlines.
- **Placement:** features fill the central 70 to 80% of the head's front. Eye line at about 42% of head height from the top, mouth centre at about 68%.
- **Eyes (four kinds):**
  1. Dots: black ovals 8% wide by 11% tall.
  2. Big round eyes: white circles 20 to 24% wide with an ink rim and a black pupil 7 to 11%. Pupils can sit at the top edge ("innocent, looking up") or shrink to 4% ("terrified").
  3. Squeezed `>` `<` chevrons for scream, sneeze and crying.
  4. Half-lid: a flat top lid over a half-dot for smug, angry or sleepy.
  - Eye centres are 30 to 34% of head width apart.
- **Brows:** thick tapered bars, 18 to 28% wide and 4 to 5% thick, 6 to 10% above the eyes. Angle ±20 to 35° (V for angry, ʌ for worried, one up and one down for smug). Most expressions have brows; neutral and happy may drop them.
- **Nose:** none.
- **Mouths:**
  - flat line (20% wide)
  - smile arc (36%)
  - open grin (a black D with pink tongue `#F2A0A8`)
  - "3" whistle
  - white "D" shock (24% wide with an ink rim)
  - scream (a black rounded box 55 to 65% wide by 38% tall, with white top and bottom teeth bands and a pink tongue)
  - frown arc with tick ends (32%)
  - smirk (an asymmetric S-curve, 40 to 50%)
  - red open crying mouth `#C0282E`
- **Extras:**
  - Tear drops `#4FA8E8` (2 per side, ink rim) for crying.
  - Sweat drops for panic.
  - Blush ellipses `#F4A0A0` at 40% alpha, used on soft or romantic characters only.
  - Creatures add thick expressive brows and a huge open mouth with tongue.
- **Two face families in one film:** most people use the thick line-art faces. The love interest or the "soft" character may use a smaller anime-style face with lashes and blush, so she reads as different at a glance. Keep it to at most 1 or 2 characters per film.

## 3. The expression set (14) and how often it changes
`neutral`, `happy` (^ ^ eyes plus open smile), `grin`, `innocent` (round eyes looking up plus a "3" mouth), `shocked` (round eyes, small pupils, white D mouth, raised brows), `terrified` (tiny pupils, wavy mouth, sweat), `scream` (squeezed eyes, giant mouth), `angry` (V brows, half-lid, frown), `furious` (V brows plus scream mouth), `smug` (one brow up, half-lid, smirk), `sad` (ʌ brows, frown), `crying` (squeezed eyes, tears, red mouth), `sleepy` (flat lids, small "o"), `sneeze` (squeezed eyes, small open red mouth). Each also needs `talk_open` and `talk_round` mouth variants and a `blink` version.

- A new expression appears in **about 70% of shots where a face is visible** (counted on the contact sheets).
- The swap is **instant** (1 frame, no in-betweens). It lands on the cut or on the stressed word of the line.
- Holds run 0.5 to 2 s. In a held shot, one swap at the punchline (for example, a whistle becomes a scream at 0.033 s).
- Reactions are BIG: scream and shocked faces are the most common reaction shots, smug and innocent the most common "hero" faces.

## 4. Body proportions (measured from frames)
| Measure | Value | Note |
|---|---|---|
| Head / total height | 0.24 | measured 0.24 on a front full-body shot |
| Torso / total height | 0.38 | torso 2 units tall |
| Legs / total height | 0.38 | legs 2 units tall |
| Shoulder width (arm to arm) / head width | 3.1 to 3.3 | measured 3.1 on a frontal medium shot |
| Torso width / head width | 1.6 | |
| Arm and leg thickness / head width | 0.8 | limbs 1 unit square |
| Arm length / leg length | 1.0 | hands are the bottom 20 to 25% of the arm, in skin colour |
| Torso height / head height | 1.6 | measured 1.67 |

Same numbers as our Cast v2 R6 rig (torso 2x1x2, limbs 1x1x2, head 1.2 to 1.3).

## 5. Body-type variety
- **Low by design:** everyone is the same R6 block at the same height. Kids, princesses, guards and dads all stand the same height. Age and role come from hair, face, beard, glasses, hats and clothes, not from scale.
- **Allowed variants:**
  - A layered flared dress or robe over the legs (princess, queen, wizard).
  - A cape.
  - Bulky winter coats (a printed texture plus a slightly thicker torso, 1.1x).
  - Babies and toddlers only at scale 0.6.
- **Creatures carry the size variety:**
  - Plush-round mascot creatures (1.6 to 2 times kid height, big head, round belly, short limbs, one humanising prop that tells its role, of our own choosing: an apron, a crown, a scarf, a satchel).
  - Shaggy giants (3 to 5 times kid height, fur cards, white fangs, glowing yellow eyes).
  - A hooded "something wrong" figure for eerie beats (black block with glowing red eyes and a jagged white grin; no weapon).

## 6. Skin tones (measured on lit faces)
`#FDD296` light · `#F8B383` peach · `#EAB494` rose · `#E0A46C` tan · `#C88A4C` golden · `#8D6C4C` brown · `#6B4A35` deep. Optional classic yellow `#F5CD30` (from our Cast v2; it was not seen in these six films). The cinematic variant used near-white blocky skins.

## 7. Hair
- **Chunky low-poly spike meshes:** 7 to 11 big spikes, 1.1 to 1.25 times head width, sitting 0.1 to 0.2 head-heights above the head top. Flat colour with soft shading (roughness about 0.6), no strand detail.
- Also: a fluffy anime mop (orange), side-swept "bacon" style, long straight hair for women (to the shoulders or past), a hair bun or tiara.
- **Vivid colours make the hero:** green `#3FA33A`, orange `#F26B1D`, blond `#F2D04A`. Supporting characters: brown `#6B4226`, grey `#8A8F96`, black `#1C1A1E`, platinum `#EDE6D0`.
- One unique hair colour and shape per named character in a film.

## 8. Clothing approach
- Printed 2D textures on the blocks, not modelled cloth.
- **Hero signature:** bold horizontal two-colour stripes (5 stripes on the torso, 5 on each arm), or one strong primary. Three of their six heroes wore stripes. The hero is the only fully saturated outfit in the shot.
- **Never copy their heroes' look.** Don't reuse their exact hair-plus-outfit combinations (green spiky hair with green/black stripes, grey spiky hair with a red tracksuit, blond hair with yellow/black stripes, orange mop with a cream knit). Our default hero is the Cast v2 hero kid (brown crop hair) in burnt-orange and cream stripes (`#CF3D13` / `#F3E6C8`).
- **Uniforms:** flat colour plus printed details (gold buttons, cuffs, belts, collar line).
- **Textured clothes for everyone else:** plaid flannel, Nordic or cable knit, star-pattern pyjamas, denim, robes. These satisfy the Studio Bible's textured-clothing rule.
- Pants are usually darker than the shirt (navy `#2E3A55`, black, brown).

## 9. Accessories
- One per role is enough to read the role:
  - tall bearskin or royal hat
  - crown, tiara or cape (royalty)
  - helmet or plate print (knight)
  - top hat with a long coat (hunter or villain)
  - glasses, beard or moustache (dads and elders)
  - backpack
  - pot or chef hat (comic)
- Props are handheld and oversized (1.3x): a fire extinguisher, flowers, a note, a photo frame, a lantern.

## 10. Materials and shading on characters
- Principled BSDF plastic: roughness 0.45 to 0.55, IOR level 0.5, no coat, no subsurface. A slight specular sheen on the torso blocks. Bevels 0.06 to 0.08 on the blocks (soft edges catch the light).
- Faces are part of the head material (an alpha decal over the skin colour), so they take scene lighting and shadow.
- No outlines, no toon ramps, no rim lights. Creatures: fur cards (shaggy) or a smooth satin vinyl look (plush mascot, roughness 0.35).

## 11. How characters move
- **Idle:** a gentle sway (about ±2°) with arms slightly out. Never fully frozen: in 5 of 6 films no 0.4 s stretch is without motion.
- **Walk and run:** stock blocky cycle. Legs and arms swing about ±40° in opposition with rigid limbs. It is brisk: a step every about 6 frames (0.2 s), a full cycle about 0.4 s (measured at 30 fps on a walk toward camera). A character walks into a close-up in about 0.8 s.
- **Gestures and emotes:** wave, point, cheer (both arms up), shrug, faint (fall flat), jump, "tickle", dance. Poses snap in over 3 to 6 frames and hold.
- **Timing:** snappy, linear-ish limb moves. The face swap is the main beat. Physics gags on props: a hat flies off in 6 frames; a visitor is blown back by puff rings.
- **Crowds:** dozens to hundreds of extras with staggered idles, never in unison.

## 12. How many characters, and how they are told apart
- **Short fable (37 to 39 s):** 3 to 5 named characters plus one crowd beat. Example counts: guard, princess, tourists and a sign man plus 100 or more extras; kid, creature, crush and 2 visitors.
- **Long fable (136 to 158 s):** 6 to 10 named characters plus crowds, and 1 to 3 creature designs.
- They are told apart by, in order of strength:
  1. Hair colour and shape (unique per character).
  2. Outfit pattern (only the hero wears stripes or the saturated primary).
  3. Skin tone (mixed in every scene).
  4. One role accessory.
  5. Face family (line-art versus the soft anime face).

## 13. Recipe: build a new Blockfolk character in our pipeline
Our rig: Cast v2 R6 (`cast-v2.blend`, collections `Cast v2 | <name>`; source `/tmp/claude-0/cast2/cast_v2.py`, also on scripts-inbox under `cast-v2/`). Our scene scale is 1 m = 3.3 Blender units. A Cast v2 person at `s=1.0` is about 6 units tall including hair; in this style everyone is at `s=1.0`. Only Claude creates new characters (Cast v2 rule); builders reuse them.

1. **Body:** call `person(name, shirt, pants, skin, face, hair, head='classic', s=1.0, fs=0.75)`.
   - Keep the default R6 sizes (`tw=2, td=1, th=2, lh=2, lw=1, aw=1, al=2`).
   - Use `s=1.0` for every adult and kid (remove the 0.8 kid scale). Use `s=0.6` for babies only.
2. **Head:** `head='classic'` (the classic mesh, scaled to 1.3 wide). Do not use the `'refl'` cylinder for this style.
3. **Face texture:** draw our own **Blockfolk line face set**, not Roblox decals and not the account's faces.
   - 1024x1024 transparent PNGs. Ink `#1E140E`, stroke 36 px (3.5%).
   - Eye line at y=430 px, mouth at y=700 px. Features inside the central 75%.
   - 14 expressions plus `talk_open`, `talk_round` and `blink`, following §2 and §3 and the shapes on `charsheet.png`.
   - Set `fs≈0.75` in `head_mat2` so the features fill about 75% of the head front and read in medium shots (eye width ≥ 40 px on screen at 1080 wide).
4. **Expression switching:**
   - Put the faces in an image sequence (`face_001.png` to `face_017.png`, in the order of the expression list in §3; `style_craftee_style.EXPRESSIONS` has the same order).
   - Call `face_set(head_material, '.../face_001.png')`. It sets the head's Image Texture to the sequence, holds one image and turns auto refresh on.
   - Call `face_swaps(head_material, [(frame, 'shocked'), ...])`. It keys `frame_offset` with **CONSTANT** interpolation, so each key is an instant swap on the stressed word. `cut_plan()` gives each shot's `f0` and a `face_swap_frame`. Tested in pass 2: the keys evaluate to the right image when the material is on a head.
5. **Outfit:**
   - Hero: an image texture of 5 horizontal stripes (two palette colours, for example `#CF3D13` and white) on the torso and arms. No bump.
   - Others: flat colour plus a printed pattern (plaid, knit or uniform trims) with `fabric()` bump 0.18 only on knit or plaid.
   - Pants darker than the shirt.
6. **Hair:** a chunky spike mesh (7 to 11 spikes, 1.1 to 1.25 times head width) in a vivid colour unique to this character. Use `tint_hair()` with roughness 0.6.
7. **Accessory:** one role prop (crown, helmet, hat, glasses or beard) as simple geometry (`cone`, `torus`, `box` helpers in `cast_v2.py`).
8. **Materials:** skin roughness 0.45; clothes 0.5 (smooth) to 0.85 (knit); bevel 0.06 to 0.08. No outline modifiers.
9. **Motion set:** idle sway, walk, run, wave, point, cheer, faint, jump. Limbs pivot only at the shoulder and hip empties (`arm L/R`, `leg L/R`). Snap poses over 3 to 6 frames. `walk_to_camera(person_dict, cam, f0)` in the pack keys the entrance walk: a step every 6 frames and limbs swinging ±40°.
10. **Checks:**
    - A front still beside the cast sheet: the head reads as a rounded square and the face is readable at phone size.
    - The silhouette and hair colour are unique in the cast for this film.
    - Only the hero is saturated.
    - The cast-check still goes to Claude and Jake before any full render (Studio Bible).

**Medieval translation for our "In this town" stories:**
- kid hero in striped tunic
- knight: plate printed on the blocks plus a helmet accessory
- king and queen: crown and cape
- peasants: knit and plaid
- wizard: pointed hat, robe over the legs
- guard: comic pot helmet

Creatures follow the plush-round or shaggy-giant rules with one humanising prop. Kid-safe: no blood, and no weapon pointed at a person. Menace comes from size, silhouette and glowing eyes.

## 14. What this kit changes in Cast v2
- Faces: the Pokémon-style and anime face sets are swapped for the line-art Blockfolk set on most characters. Keep at most 1 or 2 soft anime faces per film.
- Scale: the kid moves from 0.8 to 1.0, so everyone is the same height.
- Head: everyone uses the classic head (Cast v2 used both the classic head and the Reflection cylinder).
- Hero: bold stripes plus vivid spiky hair as the standing signature.
- Cast v2 outfits, skins and accessories otherwise carry over unchanged.
