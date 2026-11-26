# Sticker Saga Cast: character kit for "Comic Sticker Saga" (`fourth-style`)

How this account builds its people, measured from 4 hit reels on 11-26, written so we can build **new characters of our own** in the same way. Their characters, designs and names are not copied. Only Claude adds new people to the cast (Studio Bible). Builders use this file to understand the look and to pose and dress what Claude provides.

## 1. Head shape and size
- **Classic rounded block head** (the Cast v2 `head='classic'` mesh): about 1.2 x 1.2 studs, soft-cornered. It is never a sharp cube and never a sculpted face.
- Head block = **23% of standing height** on teens and adults, and 28-30% on the kid or flashback variant.
- With hair, the head silhouette = **30-34% of height** and **1.3-1.8x the head width**. The hair, not the head, makes the character big-headed and anime-like.
- The head is the same size on everyone. Character comes from hair, face decal and clothes.

## 2. Face construction (flat decal, two families)
All faces are **flat 2D line-art decals**: black ink lines 3-4 px wide on a 1024 px texture, no shading, no gloss and no 3D eyes. The features sit low on the head: eyes at about 55% of the way down the face, mouth at about 78%. The forehead is usually hidden under the fringe.

**Family A, "line faces"** (most boys, adults, extras and comic characters):
- Eyes:
  - round whites with a small black pupil (alarm);
  - two short horizontal dashes (sleepy, bored, unimpressed);
  - single dots (blank);
  - ^ ^ arcs (happy).
- Eye width is about 16% of the head width. Eye spacing is about 40% of the head width, centre to centre.
- Brows: a short straight or tilted stroke, often missing.
- Mouth: one stroke. It can be flat, a small smile, a one-sided smirk, a small "o", or an open D-shape with a dark fill (shout).
- Extras: round wire glasses drawn on the decal or as a thin mesh. A sweat drop and an anger mark are separate 2D stickers.

**Family B, "anime-lite faces"** (featured characters: the rival, the mysterious newcomer, the mentor):
- **Half-lid eyes:** a heavy upper lash line over a coloured iris (green, blue, amber) with one white highlight dot, and lower lashes as 2 short ticks.
- Thin arched brows, set high.
- A tiny mouth (a short line or small arc).
- No nose.
- Closed variants: ^ ^ for a happy face, a single lid line with a lash flick for a calm face.
- Optional special-state marks, drawn on the decal: ink crack lines for a stone curse, glowing iris for magic.

**Blush:** the account uses small pink ovals. **We leave them out by default**, because Jake rejected blush on the old puppet heads. Use a sweat drop, an anger mark or a "!" sticker instead.

## 3. Expression set and how often it changes
Every featured person needs **8-10 expressions** as separate decals:

| Expression | Eyes | Brows | Mouth | Extra |
|---|---|---|---|---|
| Calm / bored | two dashes or half-lid | flat | flat | – |
| Alarmed | round, small pupils | up | small "o" | – |
| Happy | ^ ^ arcs | up | wide grin | – |
| Nervous | round | worried tilt | flat or wobble | sweat-drop sticker |
| Smug | half-lid | flat | one-sided smirk | – |
| Shouting | narrowed | angry V | open with a teeth bar | – |
| Blank shock | dots | up | "o" | – |
| Determined | narrowed | angry V | flat | – |
| Wink | one closed arc, one round | one up | smile | – |
| Sleepy | two dashes low on the face | none | tiny dot | – |

**Measured change rate:** the lead shows **8-12 different expressions per 90 s film**, and the face differs in almost every close-up (6-8 reaction close-ups a minute). Faces change **between** shots, not with animated mouths: there is **no lip sync**. Inside one shot a face holds. A visible face change inside a shot happens only as a 1-frame swap on a reaction beat.

## 4. Body proportions (measured from full-body frames, matched to the R6 rig)
| | Teen / adult | Kid (scale 0.8) |
|---|---|---|
| Head block / height | 0.23 | 0.29 |
| Head with hair / height | 0.30-0.34 | 0.36-0.40 |
| Torso / height | 0.39 | 0.39 |
| Legs / height | 0.38 | 0.32 |
| Torso width / head width | 1.6-1.7 | 1.5 |
| Shoulder span (torso + arms) / head width | 3.2-3.3 | 3.0 |
| Arm and leg thickness | 1 stud (half the torso width) | same |
| Arm length | = torso height (2 studs) | same |

## 5. Body-type variety
- **Standard teen R6:** most people, including the hero and the rivals.
- **Kid 0.8:** flashbacks ("when I was five") and younger siblings. The head is relatively bigger.
- **Tall slim adult:** teachers, parents, officials. Use Cast v2's tall settings (th 2.3, lh 2.3).
- **Broad adult:** shopkeeper, guard, blacksmith (tw 2.4).
- **Elder:** bald or with a bun, glasses, a slight forward lean in the pose.
There are 3-5 featured people per film, plus 6-20 extras in matching uniforms (school-uniform crowds there; for us, squire tunics or market folk).

## 6. Skin tones
`#F3D2B3` light · `#E2B48C` warm light · `#C8956A` tan · `#9A6A48` brown · `#6A4630` deep brown · `#F5CD30` classic game yellow (Cast v2's comic characters). Skin is flat plastic, so the tone does not change across the body.

## 7. Hair (how it is modelled)
- **Oversized anime hair meshes**, one per character, never shared within a film. Main shapes:
  - a dense cloud of 20-30 sharp spikes (the hero);
  - long straight hair to the hip with a heavy blunt fringe;
  - high twin tails with a hairband;
  - a chin-length bob with a blunt fringe;
  - a slicked side-part (adults).
- **Size:** 1.3-1.8x the head width. It adds 0.3-0.5 head heights on top, and the fringe covers the top third of the face.
- **Texture:** a flat base colour plus darker painted strand strokes (dashed lines following the flow, about 8-12 per side), with one soft highlight band. Roughness 0.6, no gloss and no transparency cards.
- **Palette:** `#0E0E14` jet black · `#3A2A22` dark brown · `#C9CDD6` silver · `#E8742A` copper orange · `#F2D57A` straw blonde · `#7A3B2E` auburn.
- **Rule:** no two people in a shot share a hair colour **and** shape.

## 8. Clothing
- **One dominant outfit colour per person**, readable at phone size. The account's examples:
  - a black tee or hoodie with a big white graphic print (the hero);
  - a blazer with a bow and a plaid skirt;
  - a navy tracksuit with red trim;
  - a green knit jumper (a parent).
- **Medieval mapping:**
  - the hero gets a black or charcoal tunic with one big white embroidered crest;
  - featured girls get a coloured surcoat over a cream undershirt with a sash;
  - adults get aprons, robes and jerkins;
  - extras get matching squire tabards.
- Layers: 2-3 (base, over-layer, belt, sash or chain). Prints are big shapes, not fine pattern.
- Clothing texture follows the Studio Bible 11-24 note: weave, seams and worn leather visible in the actual light.

## 9. Accessories
Round glasses · hairband or bow · pointed elf-style ears (for fae or magical folk) · satchel or a box carried on the back · umbrella or lantern · a carried hero prop that gets its own orbit shot. Comic marks (sweat drop, anger mark, "?" and "!") are 2D stickers added in the finishing pass, not geometry.

## 10. Materials and shading on characters
- Skin and body: Principled BSDF, roughness 0.5, specular IOR level 0.3. No subsurface and no toon ramp.
- Face: the decal is mixed over the skin colour (Cast v2 `head_mat2`). No bump and no emission.
- Clothes: `fabric()` with one colour, a printed graphic image and weave bump 0.1-0.18.
- **No outlines** on the 3D characters (the ink lines live only in the face decals and the graphics).
- **Special states swap the whole avatar's material in one cut.** For example, stone is all `#9A958C`, roughness 0.9, with crack lines in the face decal and a crack texture on the body.

## 11. How characters move
- Stock rigid-limb game motion: walk (arms swing ±30°), run, idle sway, sit, lie flat, point, both arms up to flinch, hands over the face, kneel.
- **Poses change between shots more than inside them.** Inside a held shot there is one quick reaction (6-8 frames with ease-in and ease-out) and then idle (breathing sway of 1-2° and blinks via a decal swap). Keep the Studio Bible's weighted, staggered motion: different people react at different moments.
- Falls and hits are physical: the body drops flat, the camera stays still, and a cut 0.7 s later shows the aftermath.
- Gestures read from the silhouette: arms well clear of the torso, and the head turned 20-30° toward the speaker.

## 12. Distinct characters per film and how they are told apart
3-5 featured people. In order of importance, they are told apart by:
1. hair shape and colour;
2. outfit colour;
3. an accessory (glasses, ears, bow);
4. a **name sticker in the character's own colour** on their first appearance. The colour stays the same for that character in every film.

## 13. Step-by-step recipe: a new character in this style with our pipeline
The Cast v2 R6 rig is on the `scripts-inbox` branch under `cast-v2/`. The code is at `/tmp/claude-0/cast2/cast_v2.py`; `/tmp/claude-0/cast2/pkg/cast_v2.py` is an identical copy.
1. **Body:** call `person(..., head='classic', ...)` with teen or adult defaults (tw=2, td=1, th=2, lh=2, aw=1, al=2).
   - Kid: s=0.8, hs=1.15.
   - Tall adult: th=2.3, lh=2.3.
   - Broad adult: tw=2.4.
2. **Head:** keep the classic head mesh. Do not use the Reflection cylinder head for this style.
3. **Face:**
   - Draw a new 1024x1024 transparent PNG in Family A or B (section 2) with 3-4 px ink lines.
   - Draw the eyes at 55% down the PNG and the mouth at 78%. Keep the default `voff=0`, so the decal maps straight onto the head and the features land at the same heights. The fringe can overlap the top.
   - Note that `person()` calls `head_mat2(name, skin, face, fs)` **without** `voff`, so `voff` cannot be set through `person()`. If a face needs nudging, redraw the PNG rather than patching the material. A positive `voff` moves the features down; a negative one moves them up. The first-pass value of -0.06 would have moved them up.
   - In a shoot, swap expressions per close-up with `set_face(head, png)` from `pack/style_fourth_style.py`.
   - Make the whole expression set (8-10 PNGs, same eye spacing) and name the files `<char>_<expression>.png`.
4. **Hair:**
   - Model or pick an oversized hair mesh: 1.3-1.8x head width, +0.3-0.5 head heights, fringe over the top third of the face.
   - Base colour from the hair palette, plus a strand-stroke texture (dark dashed strokes along the flow) and one highlight band.
   - Attach it like Cast v2 hair (instance on the head, `hair_s` 0.95-1.1) and tint it with `tint_hair()`.
5. **Clothes:** `fabric()` in one dominant colour. Add one big readable print or trim (a crest, stripe, sash or belt) and one silhouette accessory.
6. **Materials:** plastic skin (roughness 0.5). No outlines. No blush.
7. **Name colour:** pick the character's sticker colour (teal `#3FD0C9`, coral `#FF5A6E`, gold `#FFD23F`, sky `#5EB1D5`, lilac `#B48CFF`) and write it down with the character.
8. **Check still:** a turnaround (front, 3/4, side), the expression strip and a side-by-side with two existing cast members. Claude reviews it and adds the character to the cast.
9. **Before a shoot:** list which expressions each scene needs (one per close-up) so the builder can swap decals shot by shot.

## 14. What changes against Cast v2 today
- Cast v2 mixes Reflection-style rounded cylinder heads with classic heads. **This style uses classic heads for everyone.**
- Cast v2 faces come from several libraries. **This style uses one consistent flat line-art language** (the two families above) and needs **full expression sets** per featured character.
- Hair gets **bigger** (1.3-1.8x head width) and gets the painted strand texture.
- Each character gets a **permanent name-sticker colour**.
