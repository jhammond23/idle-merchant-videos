# Comic Sticker Saga (style id `fourth-style`)

**Summary.** Our characters are blocky game avatars with oversized anime hair and flat line-art faces, filmed in clean, realistic-looking game sets with bright bloom on whites and true blacks in the shadows. The camera is locked and the edit carries the energy: a hard cut about every 1.45 s, a new face on the lead in almost every close-up, and only one or two real camera moves per film (a slow pull-out reveal, an orbit round a prop, a crane-down). The style is set apart from plain fast-cut game footage by a layer of comic "stickers" over the picture: a colour-coded name card the first time each character appears, white speech bubbles, tilted day and time tags, small icon gags (dizzy stars, "?" badges), and a closing question card with a red PART pill. The look is not glossy: colour is natural and medium-saturated (about 0.42), and the bright accents live in the graphics, not the grade. The method comes from Stickman.deadzone. Nothing of theirs is copied: no stories, lines, characters, names or footage.

Everything below was measured from 4 hit reels (and one weak reel for contrast) on Thu 11-26 by stepping through them at 10 frames a second, and at 30 frames a second around every key moment. The numbers table is at the end.

---

## 1. Look in one picture (words)
A kid hero with a cloud of jet-black spiky hair and a flat, bored two-dash face stands in a stone corridor lit by cool daylight from tall windows. The whites glow slightly, the shadows are true black, and the walls are slate blue-grey. Above him, a chunky teal name sticker with a white swoosh underline and a little four-point sparkle hangs at a slight tilt. Across the lower third, two huge white words with a black outline read "HE WAS", and the next word, "FIRST", pops in yellow.

## 2. Palette (hex, and where each colour is used)
**Scene colours** (k-means, 12 clusters per reel, shot-middle frames, merged across 4 reels):

| Hex | Name | Share | Use in our medieval sets |
|---|---|---|---|
| `#08080F` | Ink black | 15-21% of all pixels | Hero hair, dark tunics, shadows, caption outlines. Keep real blacks (luma p5 = 0-15). |
| `#2F4356` | Slate teal | 10-17% | Castle doors, lockers become armoury racks, night interiors, cold stone in shade |
| `#6E8287` | Blue-grey stone | 9-13% | Corridor walls, keep walls |
| `#A8B7C3` | Pale daylight grey | 6% | Sunlit walls, ceilings, window light |
| `#5EB1D5` | Sky blue | 3-6% | Exterior sky (clear, with a few cumulus) |
| `#EDE5D1` | Cream white | 7-11% | Parchment, notes, lit plaster, highlights |
| `#C7AE93` | Warm beige | 4-7% | Skin in shade, flagstones, sand |
| `#8E603A` | Oak brown | 4-11% | Floors, tables, benches, beams |
| `#DF9033` | Torch amber | 3-7% | Candles, torches, sunsets, autumn trees |
| `#488F47` | Grass green | 4% | Training yard, village green |
| `#5C1D0D` | Deep banner red | 5% | Shop and hall banners, curtains |
| `#D05D0F` | Rust orange | 3% | Accent props, lantern glass |

**Graphics palette** (overlays only, measured from captions and stickers):

| Hex | Use |
|---|---|
| `#FFFFFF` + `#0B0B10` | Caption fill and 6-7 px outline |
| `#FFD23F` | Keyword colour 1 (52% of coloured keywords) and all spoken dialogue (in quotation marks) |
| `#FF4757` | Keyword colour 2 (25%): danger, pain, "red" objects; the PART pill; vote option A |
| `#B48CFF` | Keyword colour 3. The account used pink here (23%) for romance words. We use lilac for magic words instead. |
| `#3FD0C9` | Name sticker (character colour 1) |
| `#FF5A6E` | Name sticker (character colour 2) |
| `#2F7DF6` | Vote option B |
| `#FFB627` | Day and time tags |

Rule: **the keyword colour matches the thing named** whenever it can. A red curtain gets a red word and a gold coin a yellow one.

## 3. Light and grade
- **Mean brightness (luma 0-255): 102 across the 4 reels** (113, 111, 89, 97). This is a mid-key look, between our house builds (95-100) and cannonanimates (140-155).
- **Full contrast range:** luma p5 = 0-15 and p95 = 222-232 in every reel. The standard deviation inside a shot is about 60. Shadows go to true black and whites clip to a soft glow.
- **Saturation (HSV mean): 0.42** (0.34 / 0.46 / 0.44 / 0.43). The colour is natural, not graded up. The overall balance is neutral (mean RGB 113,113,112 on the school reel) or warm on lamp-lit interiors (128,111,93).
- **Light is game "future lighting":** one hard sun with crisp shadows outdoors. Indoors, big soft ceiling panels (cool) or warm practical lamps at night. Bloom halos on every white surface (paper, plaster, road paint) plus a visible sun disc with glow in exteriors. There is no haze or fog. A vignette appears only under the question card.
- **Times of day:** mostly clear midday. There are a few night interiors lit only by warm lamps (luma 40-70), one golden sunset glare shot per film, and rain at dusk.
- **Mood grades used as story devices, never as the base look:**
  - Black-and-white (saturation 0.04) for a flashback or a realisation, 1-2 shots.
  - Sepia "old photo" for a childhood flashback: sepia tone, rounded white border, vignette and floating dust specks, 2 shots.
  - A light dim inside a held shot (luma -15 to -30 over 1 s) when time passes or a light goes out.

## 4. Camera and framing (numbers)
- **Framing mix** (68 shots, Russian Part 2 reel): wide 19%, medium 35%, medium close-up 24%, close-up and extreme close-up 18%, inserts (notes, props) 4%.
- **Angles:** eye level about 85%, top-down about 6% (someone lying on the grass, a note on a table), low-angle looming close-up about 1 per film, over-the-shoulder with a blurred foreground head 1-2 per film.
- **Inside a shot the camera is locked.** Measured global motion in normal shots is under 0.05 px a frame at 72 px wide, so under 1 px a frame at 1080 wide. Some shots creep by 1-2 px a frame (up to 60 px a second). There are no whips, swish pans, handheld drift or shake on impacts (0 in 4 reels).
- **The camera moves only on key beats, about 1-2 per film.** The moves are listed in the catalogue (section 12):
  - a slow pull-out reveal from an extreme close-up (about 2x scale change in 1.4 s);
  - an orbit round a hero prop (25-35° in 1.6 s);
  - a crane or tilt down into an over-the-shoulder (about 500 px a second after a 0.3 s ease-in);
  - a snap zoom punch-in (+17% in 5 frames).
- **Lens (estimated from perspective):** wides at about 70° vertical field of view (the game default; 26 mm on a 36 mm vertical sensor). Close-ups are flatter, about 40° (50 mm). There is no lens distortion, no chromatic aberration and no motion blur. Focus is deep everywhere except the over-the-shoulder shots and the blurred question-card background.

## 5. Cutting rhythm (numbers)
- **Average shot 1.45 s; median 1.3 s** (1.61/1.46/1.41/1.47 per reel; medians 1.4/1.2/1.3/1.4). That is **about 41 cuts a minute.**
- Shortest holds are 0.4-0.6 s (rapid reactions). The longest story shots are 2.5-3.1 s, and are always a camera move or a reveal. End cards hold 4-8 s.
- **About 5 words per shot, about 3 caption changes per shot.** A cut lands on a caption boundary, usually on the phrase that names something new.
- **Every cut is a hard cut.** The only transitions found are:
  - a 1-3 frame dip to black before the sponsor segment;
  - a background dim of luma -35% over 8 frames when the question card arrives;
  - jump cuts on the same subject (5-15% size change).
- **The edit varies distance, not angle.** Wide, then close-up, then medium close-up, with reaction close-ups of the lead after every reveal line (about 6-8 a minute).

## 6. Characters and faces (full kit in CHARACTERS.md)
- R6-style blocky bodies on the classic rounded block head. Heads have **flat 2D line-art face decals** in two families:
  - "line faces": round eyes with pupils, two-dash sleepy eyes, ^ ^ happy eyes, a single-stroke mouth;
  - "anime-lite faces": a half-lid lash line over a coloured iris, thin arched brows, a tiny mouth.
- **Oversized anime hair is each character's identity.** It is 1.3-1.8x the head width and adds 0.3-0.5 head heights on top. Long hair, twin tails, bobs and dense spikes all appear, with painted strand strokes.
- **The lead's face changes in almost every close-up.** Count 8-12 distinct expressions per film for the lead: alarmed, bored, smug, nervous with a sweat drop, shouting, happy, blank shock.
- **Special states swap the whole avatar's material in one cut.** For example, a character turns all-grey stone with ink crack lines.
- There are 3-5 featured people per film plus 6-20 extras. They are told apart by hair silhouette, then outfit colour, then a name sticker.

## 7. Shapes and proportions
- People: head block 23% of standing height (30-34% including hair). The torso is 1.6-1.7x the head width and the shoulder span 3.2-3.3x. Arms and legs are 1-stud blocks. Legs are 38% of height on teens and adults and 32% on kids.
- Kid variant (flashbacks, younger siblings): scale 0.8, head 1.15x bigger relative to the body.
- Props are chunky and readable at phone size: a box with a curtained window, letters, a football, an umbrella. Props get their own insert or orbit shot.
- Graphics shapes: rounded rectangles (radius 35-45% of their height), 6-8 px ink outlines, four-point sparkles, five-point stars. There are no sharp hard-edged boxes in the graphics.

## 8. Textures and materials
- Bodies and skin are smooth plastic (roughness about 0.5, low specular). There is no toon shading and there are no outlines on the 3D models.
- Clothes are flat colour plus one big printed graphic, with a light weave.
- Environments are realistic game maps with PBR-ish materials: brick, plaster, terrazzo, wood grain, glossy floors with reflections, and realistic shop shelves full of small props. They are dense and lived-in, not low-poly. There are no AI stills and no 2D painted backgrounds.
- Graphics are flat vector stickers with ink outlines and soft drop shadows (0 / 6 px, 35-40% black).

## 9. Environments (method, ported to medieval)
| What they use | Our medieval equivalent |
|---|---|
| School corridor: teal lockers, terrazzo floor, ceiling light panels | Castle corridor: slate-blue doors and armour racks, chequered flagstones, tall bright windows |
| Classroom: rows of desks | Great hall or scribe school: long benches, a teacher's lectern |
| Corner shop: dense shelves | Apothecary or general store: jars, sacks, hanging herbs |
| Night dinner: pendant lamp | Tavern or home table: candle chandelier, warm amber |
| Football pitch | Training yard: straw dummies, wooden swords, green turf |
| Brick terraced street, autumn tree | Timber-frame market street with an orange oak |
| Shrine at night | Lantern shrine or chapel, warm lamps, blue night |
| Sunset beach | Coast or dune at golden hour with sun glare |
Every set is full of small readable props. A new place gets an establishing wide (0.8-1.5 s) before the close-ups.

## 10. Animation (timing, easing, what moves)
- Characters use stock game animation: walk, run, idle sway, sit, lie flat, point, flinch with arms up, hands over the face. **Poses change between shots more than inside them.**
- Inside a held shot, one short reaction (6-8 frames, eased) then idle. Never a frozen still.
- Impacts are sold by physics, not the camera. In the ball-to-the-face beat, the ball travels 6 frames, the body drops flat, and the camera stays static. Then comes a cut about 0.7 s later to the aftermath with dizzy stars.
- Graphics motion (measured at 30 fps):
  - Captions pop in over 1 frame at about 108% scale, then sit at 100%.
  - Bubbles and tags pop in over about 5 frames with a small overshoot.
  - Dizzy stars orbit the head continuously.
- Their footage carries duplicate frames from game capture (20-28 fps inside a 30 fps file). **Do not copy that.** Render a true 30 fps.

## 11. Captions and on-screen text
- **Always on screen from frame 4-5 to the last story frame.** 1-3 words per caption (mean about 1.9). Median caption 0.5 s. **1.88-1.90 caption changes a second in all three reels measured**, which makes it the steadiest number in this style.
- Font look: heavy rounded geometric sans in ALL CAPS. Free match: **Poppins ExtraBold** (OFL), or Montserrat Black. Size about 110 px (cap height 70-95 px). Max line width 900 px. White fill, 6-7 px `#0B0B10` outline, drop shadow 0/6 px at 40% black.
- **Position:** centred, baseline at **y = 1290 px (67% down)**. When a face fills the frame, the caption drops to **y = 1515 px (79%)** so it never covers eyes or mouth (12% of captions).
- **Keyword colour on 35-50% of caption time:** yellow, then red, then a third colour. Spoken dialogue is always yellow in quotation marks ("NO!"). Narration is white.
- Pop-in: 1 frame at 108%, then 100%. No typewriter, no word-by-word highlight.
- **Sticker layer (this style's signature):**
  - **Name sticker:** used at a character's first appearance, 2-3 per film. Chunky display caps 120-160 px high in the character's own colour, with a 6-8 px ink outline, a white swoosh underline, a four-point sparkle at the top-left corner, rotated -3°, in the top third. It appears on the cut or pops mid-shot and stays 1-2 shots (1.5-3 s). Free font: **Lilita One** (OFL).
  - **Speech bubble:** 2-4 per film. White rounded rectangle, 5-6 px ink outline, a tail pointing at the speaker, 2-4 words in black caps (cap height about 80 px). Top third, 60-70% of frame width. Pops in over about 5 frames.
  - **Day and time tags:** 1-5 per film ("DAY THREE", "SIX HOURS"). Amber or white caps with an ink outline and a small icon, rotated -5°.
    - Their icons included a heart; ours are hourglass, sun, moon, candle and star.
    - Measured position: top-left at y 12-18%. Our handle owns the top-left (Studio Bible), so ours sit just below it at y 15-25%.
    - Never put a tag in the same shot as a name sticker.
  - **Icon gags:** "?" badges over a crowd's heads, five yellow dizzy stars round a knocked-down head, a sweat drop or anger mark beside a face.
  - **Question card** (last 4-8 s): the scene dims 35% over 8 frames with a soft blur. A small tracked-caps premise line sits at the top in light grey. Below it, a red rounded "PART 1" pill. Below that, a 2-line question in white heavy caps with the key word coloured. Vote episodes add two pills, red A and blue B. The card stays up across 2-4 cuts underneath it.
- Our own handle stays top-left (Studio Bible). Their small watermark under the caption is not used.

## 12. Camera and film technique catalogue (measured)
Units: px at 1080x1920. "/min" is per minute of story. Frame counts are at 30 fps. **"Seen"** says how much evidence each number rests on (4 hit reels, V1-V4).
- **Pack:** a function in `pack/style_fourth_style.py` (Blender).
- **Post:** an event type in `pack/post_fourth_style.py`.
- **Caption spec:** `pack/captions_fourth-style.json`.
The defaults in the code are the numbers in this table.

| # | Technique | Seen | How often | Timing and size | What triggers it | Recipe (pack, post, Roblox) |
|---|---|---|---|---|---|---|
| 1 | **Hard cut** | all 4 reels | ~41/min | Shot 1.45 s average, 1.3 s median, 0.4-3.1 s range | A new noun or phrase in the voice; a new caption | Pack `cut_plan(word_timings)`: cuts only on caption starts. Cost 0 at a line start, 0.3 after punctuation, 0.5 after a pause, 1.5 mid-phrase. Lengths are pulled toward 1.45 s (0.4-3.1 s; opening shot 1.5-2.4 s). |
| 2 | **Locked shot with micro-creep** | all 4 | ~90% of shots | Drift 0-2 px a frame (≤60 px/s), linear | Default | Pack `creep(cam, f0, f1)`: 0.3 px a frame, linear (or no keys at all). Roblox: Scriptable camera, CFrame fixed. |
| 3 | **Reaction close-up with face swap** | every reel (count not itemised) | 6-8/min | 0.5-1.2 s; a new face decal each time | After every reveal or insult line | Pack `set_face(head, png)` before each close-up; `face_swaps(head, [(f, png)])` for a 1-frame swap inside a shot. One 6-8 frame head turn or flinch, then idle. |
| 4 | **Cut-in plus snap zoom punch** | once (V2) | ~1 per film | Straight cut to a tighter close-up, then +5%, +5%, +5%, +2% (= +17% over frames 0-4, 0.15 s), hold to the cut | A shouted line or shock ("NO!") | Pack `snap_zoom(cam, f)`: lens keyed every frame 50 → 52.5 → 55 → 57.5 → 58.5 mm, then constant. Post `snap_zoom` event for a held render (not both). ffmpeg `zoompan=z='min(1.17,1+0.05*k-0.03*max(0,k-3))'` (printed by `post ... ffmpeg`). No shake and no flash with it. |
| 5 | **Slow pull-out reveal** | once (V1) | ~1 per film | 2.1 s shot. Hold 0.2 s (6 frames). Then the picture shrinks ~1.9% a frame for 30 frames and eases out over the last 12 (0.4 s): ≈2x in 1.4 s. Hold 0.15 s, cut. | A transformation reveal (someone turned to stone) | Pack `pull_out(cam, f0)`: lens 85 → 42 mm keyed every frame along that curve; `mode='dolly', target=...` backs the camera off instead. Roblox: TweenService on the camera CFrame, Quad Out, 1.4 s, after a 0.2 s wait. |
| 6 | **Orbit round a hero prop** | once (V3) | ~1 per film | 1.6 s (48 frames), 25-35° arc, lateral parallax 3-13 px a frame, ease in and out | The voice lists the prop's features | Pack `orbit(cam, prop_location, f0, deg=30)`: camera parented to a new empty at the prop; Z 0 → 30°, Bezier auto-clamped. |
| 7 | **Crane or tilt down into an over-the-shoulder** | once (V3) | ~1 per film | Ease in 0.3 s (3 → 16 px a frame), then a steady 16 px a frame (≈500 px/s) for 1.1 s: ≈600 px in all. Foreground hair enters at the bottom; luma drops 85 → 39. | Moving into a hiding or sneaking beat | Pack `crane_down(cam, f0)`: Z -0.65 m and X-rotation -8.5° over 42 frames, quad ease-in for 9 frames, then linear. That is ≈600 px for a subject 4 m away at 35 mm; halve `dz` at 2 m. |
| 8 | **Jump-cut reframe** | one set (V3) | ~1 per film | Same angle, 5-15% size change, 1.0-1.2 s segments, 2-3 in a row | Repeated or escalating lines ("waited... and waited") | Pack `jump_cuts(cam, f0)`: lens 100 / 110 / 121%, constant keys every 33 frames. Post `reframe` event (scale 1.10) on a held render. |
| 9 | **Fast-forward repetition with jitter** | once (V2) | rare (≤1 per film) | 1.6 s; action at about 3-4x speed (4 repeats); jitter ±27 px, roll blips ±0.9°; brightness pulse at 2.9 Hz | "I checked it four times" | Retime the action 3-4x (keys, or render every 3rd frame). Pack `ff_jitter(cam, f0, f1)` adds Noise F-modifiers (pitch and yaw ±27 px, roll ±0.9°, scale 2), only in that range. Post `ff_jitter` event adds the ±10 luma pulse at 2.9 Hz. Set its `px` and `roll` to 0 if the jitter is keyed in Blender. |
| 10 | **Impact without shake** | V4 | 1 per film | Hit, then the body falls in a static frame, then a cut 0.7 s later to the aftermath (dizzy stars). Keyword in red. | A hit or fall | Physics or a keyed fall; **no camera noise**. Post `gag` stars on the aftermath shot. |
| 11 | **Flash pulse** | once (V2) | rare | Luma +12, +24, +36, +24, +12 over frames 0-4 (77 → 113 at the peak) | A sudden realisation on a black-and-white shot | Post `flash` event (`f`, `luma` 36). ffmpeg: `eq=brightness='0.141*max(0,1-abs(n-(f+2))/3)':eval=frame`. |
| 12 | **Black-and-white cutaway** | not itemised | 0-2 per film | 0.5-1.9 s, saturation 0.04 | Flashback or a "what I just did" realisation | Post `bw` event (keeps 8% of the colour). ffmpeg `hue=s=0.08`. Blender: Hue/Saturation node, Saturation 0.1. |
| 13 | **Sepia old-photo flashback** | 2 shots, 1 film | 0-2 shots per film | 1.3-1.6 s each; sepia, rounded cream border (24 px, radius 40), vignette, floating dust | "When I was little" | Post `sepia` event: sepia matrix, border, vignette and 46 drifting dust specks, all drawn. ffmpeg (tone and vignette only): `colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,vignette=PI/4`. |
| 14 | **Light dim in a held shot** | 2 instances | ~1 per film | Luma -30 over 1.1 s (sunset) or -15 over 1.2 s | Time passing ("six hours later") | Pack `light_dim(light, f0)`: energy x0.55 over 33 frames, sine ease (≈-30 luma; check on two stills). Post `dim` event (amount 0.3 over 33 frames). Roblox: tween ClockTime. |
| 15 | **Dip to black** | V2 | 1 per film | 1-3 frames | Before the sponsor segment | Post `dip_black` event (`f`, `frames` 1-3). |
| 16 | **Question card** | V1, V3 (timed) | 1 per film | Background -35% over 8 frames plus a soft blur; holds 4-8 s across 2-4 cuts; music-only tail about 2 s | End of the story | Post `card` event: dim, 10 px blur and light vignette over 8 frames; the card pops 4 frames later. `cut_plan` adds 3 background shots under it. |
| 17 | **Name sticker** | not itemised | ~2/min | Appears on the cut or pops mid-shot (5 frames); holds 1.5-3 s | A character's first appearance | Post `name` event: scale 0 → 55 → 95 → 110 → 100% over frames 0-4, rotated -3°, the character's own colour. |
| 18 | **Speech bubble** | V2 frame 0; rest not itemised | 2-4 per film | Same 5-frame pop; holds to the end of the shot | A quoted line from another character | Post `bubble` event with `tail` pointing at the speaker. |
| 19 | **Day and time tag** | not itemised | 1-5 per film | Pop plus a +3, -3, +2, -1, 0° wiggle over 5 frames; holds 1-2 shots | A time skip | Post `time_tag` event, rotated -5°, with an icon. |
| 20 | **Icon gags** (dizzy stars, "?" badges, sweat drop) | not itemised | 1-3 per film | Stars orbit for ~1.5 s (one lap a second, our estimate); badges pop and hold for the shot | A knock-down, confusion, nerves | Post `gag` event: `stars`, `question` (with `points` for a crowd), `exclaim`, `sweat`, `anger`. |
| 21 | **Prop or note insert** | V4 mix (4% of shots) | 2-3 per film | 0.6-1.5 s, top-down, bright (luma 175-195) | "She wrote...", a found note or map | Pack `top_down(cam, spot)` plus `light_rig('insert')`. |
| 22 | **Over-the-shoulder with a blurred foreground head** | not itemised | 1-2 per film | Foreground hair covers 20-35% of the frame | A spying or confronting beat | Pack `ots(cam, far_subject)`: DOF f/2.8, focus on the far subject. |
| 23 | **Low-angle looming close-up** | not itemised | ~1 per film | Camera at chest height, about 20° up | An authority figure's first threat | Pack `low_angle(cam, head)`: 35 mm. |
| 24 | **Top-down shot** | V4 mix (~6%) | ~6% of shots | Straight down | Lying knocked out, letters on a table | Pack `top_down(cam, spot)`. |
| 25 | **Extreme close-up on an eye** | not itemised | ~1 per film | 0.5-1 s | A huge emotional beat | Pack `eye_ecu(cam, eyes)`: 85 mm, the face decal fills the frame. |
| 26 | **Caption pop and keyword colour** | 3 reels | constant | 1 frame at 108%, then 100%; keyword colour on 35-50% of caption time | Every phrase | Caption spec; `caption_groups()`; post `caption` event as the reference drawing. |
| 27 | **Weather and particles** | not itemised | 1-2 per film | Rain streaks, falling leaves, floating dust in flashbacks | Mood for a scene | Particle systems; rain at 30-45° slant (or the house `fx.py` dust/ash layers). |
| 28 | **Bloom on whites and the sun disc** | every reel (luma p95 222-232 in all 4) | constant | Halo on every white surface | Look | Pack `apply_look()`: Glare node type Bloom, Threshold 0.9, Strength 0.4, Size 0.25. Blender 5.x sizes are relative; 0.25 is the old integer size 7. |

**How sure these numbers are.**
- **Firm:** techniques 1, 2, 26 and 28 were measured on 3-4 reels. Technique 3 and the question card (16) appear in every reel, but only some instances were timed.
- **Frequencies only:** the first pass gave per-film ranges for 12 and 17-27 without listing which reel each came from ("not itemised").
- **One example each:** every camera move (4-9) was seen **exactly once** in the 4 reels. That is 6 moves in 4 films, hence "1-2 per film". Their timings and sizes come from that single instance, measured frame by frame at 30 fps. Treat them as a good recipe, not a law of the account. The same goes for the flash pulse (11), the sepia flashback (13) and the dip to black (15).
- **Estimated, not measured:**
  - words a second (3.6 = captions a second x words per caption);
  - the dizzy-star orbit speed;
  - the 2.9 Hz pulse depth (±10 luma is our choice);
  - the Blender energy factor for the light dim.
- In pass 2 I did not re-open the competitor videos: no new browsing, no new frames. The pack implements the numbers above, and the gaps are labelled.

**Measured as absent in all 4 films:**
- whip pans and swish transitions;
- crossfades, wipes, shape masks and zoom-through transitions;
- dutch angles, letterbox, film grain, light leaks, chromatic aberration and lens distortion;
- motion blur;
- white or black impact frames, and shakes on impacts;
- speed ramps into slow motion, freeze frames and reverse.

Leave all of these out. They are what makes other channels look different. The pack has no shake or whip function on purpose.

## 13. Sound
**The account's mix, as measured** (Web Audio analysis, with playback muted on Jake's PC):
- **Voice:** a single fast narrator from 0.16 s. Peaks at -10 to -14 dBFS. Pauses are only 0.1-0.45 s long. About **3.6 words a second** (estimated as 1.9 captions a second x 1.9 words per caption).
- **Music bed:** continuous, about 20-25 dB under the voice peaks.
  - It is thin with no bass for the first 6-15 s (pause floor about -40 dBFS, almost nothing under 150 Hz).
  - The bass enters after the hook (pause floor about -36 dBFS, 150 Hz band about -50 dB).
  - When the voice ends under the question card, the bed rises to about -27 dBFS for about 2 s.
- **Effects:** sparse to none. V1 has a low bass hit on only 4 cuts. V2 has **no** low hits at all: its snap zoom ("NO!") and flash pulse are carried by the voice alone. No whooshes were detected on cuts in either reel.
- The bed stops before the sponsor segment. The sponsor voice comes after the dip to black, dry with no bed.

**For our builds:**
- Keep our narrator (deep Adam), 3.4-3.9 words a second, -14 LUFS.
- **Keep the house rule of no music bed** unless Jake approves this style's bed (see Overrides).
- Use effects in its place:
  - a soft low "thump" on the 3-4 biggest cuts;
  - a small pop or tick when each sticker lands (our addition, not measured);
  - foley for impacts and falls.

## 14. Frame 0 and ending
- **Frame 0:** a mid-scene action picture that is already moving: people walking, a speech bubble already up, a prop on someone's back. There is no title card. The first caption is on screen by frame 4-5 (0.13-0.17 s) and the voice starts at 0.16 s. The opening shot is 1.5-2.4 s (4.6 s on a Part 2 recap).
- **Ending:** a question card (section 11) for 4-8 s, with a music-only or effects-only tail of about 2 s. Then the Instagram edition only gets a 1-3 frame dip to black and our own Flashloop sponsor ending. The film does not loop: it ends on the card.
- The weak reel (5.2K likes) opened on a text label and number cards rather than a character in action. That is the only clear difference I found, so treat it as a hint, not a rule.

## 15. Blender / Roblox Studio recipe (starting settings tuned to the measured targets)
**Targets:** mean luma 95-110, luma p5 under 15, p95 220-232, saturation 0.40-0.48, average shot 1.3-1.6 s.

**Blender (5.x, EEVEE)**
- **Output:** 1080x1920, 30 fps, motion blur OFF, EEVEE samples 64, shadows on (soft), ray-traced or screen-space reflections on for glossy floors.
- **Colour management:** AgX, look "High Contrast", exposure -1.3 for day exteriors (calibrated on our scene, below), gamma 1. Punchy compressed the whites too much for this style.
- **World:** exteriors use a Nishita sky (called Single Scattering in Blender 5.x) at strength 0.7-0.9 (the pack uses 0.8) with the sun disc on. Interiors use world colour `#1A2230` at strength 0.3. Night uses `#101828` at 0.15 (our value, not measured).
- **Lights:**
  - Day exteriors: one Sun at strength 6.0, angle 1.5°, colour `#FFF3E2`, elevation 48°, placed behind the camera's shoulder (`sun_rot_for(cam)`, 35° off the view axis).
  - Interiors: ceiling-panel or window area lights (200-400 W, `#EAF2FF`) plus warm practicals (point lights 50-150 W, radius 0.1, `#FFB866`).
  - Night: one moon sun (strength 0.3, `#9DB4FF`) plus warm practicals only.
- **Bloom:** compositor Glare node, type Bloom, Threshold 0.9, Strength 0.4, Size 0.25. Blender 5.x Glare sizes are relative; 0.25 is the old integer size 7, and Strength 0.4 is about the old mix -0.5. Every white surface should halo slightly. `apply_look()` builds this as the scene's compositing node group.
- **Grade:** Color Balance off. Bright/Contrast contrast +10. No saturation boost.
- **Materials:**
  - Skin and bodies: Principled, roughness 0.5, specular IOR level 0.3.
  - Stone: roughness 0.85 with noise bump 0.1.
  - Wood: roughness 0.6.
  - Floors: roughness 0.25-0.35 for soft reflections.
  - No Freestyle or outlines on 3D.
- **Faces:** Cast v2 `head_mat2()` decal on the classic head. Swap the image per shot for the expression.
- **Camera:** sensor fit Vertical, 36 mm. Wides 26 mm, mediums 35 mm, medium close-ups 42 mm, close-ups 50 mm, extreme close-ups 85 mm (`S.LENS`). Eye height at the character's eye line. DOF only on over-the-shoulder shots (f/2.8). One camera per shot with no keys (or only `creep`), except the 1-2 moves in the catalogue (techniques 4-9).

**Roblox Studio (if a build is filmed in-game)**
- **Lighting:** Technology Future, Brightness 2.5, ExposureCompensation 0.1, GlobalShadows on, Ambient (70,72,80), OutdoorAmbient (128,132,140), EnvironmentDiffuseScale 1, EnvironmentSpecularScale 0.6, ClockTime 13.5 for day, 18.2 for sunset, 0 for night.
- **Atmosphere:** Density 0.3, Offset 0.25, Haze 0.8, Glare 0.2.
- **Bloom:** Intensity 0.9, Size 32, Threshold 0.9.
- **SunRays:** Intensity 0.15, Spread 0.8.
- **ColorCorrection:** Contrast 0.12, Saturation 0.
- **DepthOfField (over-the-shoulder only):** FarIntensity 0.25, FocusDistance 12, InFocusRadius 10, NearIntensity 0.7.
- **Camera:** Scriptable, FieldOfView 70 for wides, 40 for close-ups, 25 for extreme close-ups. Record a 9:16 window at 60 fps and export at 30 fps.

**Finishing pass (Claude):** captions, stickers, question card and effects, all with `pack/post_fourth_style.py`.
- Fonts: Poppins ExtraBold for captions, Lilita One for name stickers and tags, Poppins Bold for bubble text. All are free under the OFL.
- The cloud sandbox cannot download them, so the code falls back to Poppins Bold and the house Fredoka One until they are placed in `pack/fonts/` (see `pack/README.md`).

### Calibrated on our scene (11-26, pass 3)
**Scene:** main's town-square look test (`/tmp/claude-0/kits/look_test.py`): Cast v2 kids and a guard, our cottages and fountain, a camera looking +Y, rendered in Cycles. **Scale: 1 m ≈ 3.3 units**, because Cast v2 people are about 6 units tall. The pack has `UNITS_PER_M = 3.3`.
- All distances are in metres x 3.3: camera defaults, creep, crane `dz` -2.15, low-angle, top-down and extreme-close-up placement.
- Point and area lights are multiplied by 3.3² = 10.9.
- The over-the-shoulder f-stop is divided by 3.3 (f/0.85), so the blur matches f/2.8 at real scale.
- Sun strength is unaffected.

**What was wrong:** the first pass gave luma 214 and saturation 0.10 (near white).
- Its physical sky ran at strength 0.8 with its own sun disc lighting the set on top of a 4.0 sun lamp, at exposure +0.15. That is about 8x over.
- The sun azimuth back-lit a +Y camera.

**Calibrated defaults (`CAL['day']`):**

| Setting | Value |
|---|---|
| View and look | AgX, look **High Contrast**, exposure **-1.3** |
| Sky (world) | Multiple Scattering sky, sun disc **off**. Visible to the camera at strength **0.12**; lights the set at only **0.04** (Light Path "Is Camera Ray" mix), so shade stays dark. |
| Sun lamp | strength **6.0**, elevation 48°, azimuth **35°** for a +Y camera; for other cameras use `sun_rot_for(cam)` |
| Compositor | Glare Bloom (threshold 0.9, strength 0.4, size 0.25), contrast +10, Hue/Sat saturation **0.95** (a trim to hit the measured 0.42, not a push) |

**Result:**
- 270x480 at 8 samples: mean luma **107.9**, p5 **0**, p95 **184**, saturation **0.418**. Targets: 95-110 (sunny exteriors measured 111-113), under 15, 220-232, and 0.40-0.48.
- Front three-quarter sun with crisp shadows falling away from the camera, true blacks under clothes and in shade, and a clear blue sky.
- p95 stays at 184 because this set has no true whites (paper, white plaster, road paint). Reaching 220+ here would wash out the frame. On sets with white props, the same settings should glow on the whites.

**Iterations (luma / saturation):**

| Settings | Luma / sat | Problem |
|---|---|---|
| Punchy, -3.0 | 49 / 0.41 | |
| Punchy, -1.6 | 86 / 0.36 | flat, back-lit |
| High Contrast, 0 | 153 / 0.32 | |
| High Contrast, -1.0 | 117 / 0.42 | |
| High Contrast, -1.5 | 98 / 0.45 | |
| High Contrast, -1.3, sat 0.95 | 108 / 0.42 | **chosen** |

**Not calibrated yet:**
- Sunset (exposure -1.0, sun 4.0) is extrapolated, not rendered.
- The interior, night and insert rigs are physical starting points, scaled for our units but not rendered.
- EEVEE was not test-rendered here. Its world uses the same camera-ray trick, so check one still with `post_fourth_style.py check`.
- The final 540x960 render was not run in this pass, because the permission system blocked it.

## 16. What changes against our current house style (and which Studio Bible rules it overrides)
| House rule (Studio Bible) | This style | Status |
|---|---|---|
| Evening 11-25 #1: lock the camera, cut every 1-1.5 s, slow moves only on the 1-2 biggest moments | Same: locked shots, 1.45 s average, 1-2 key moves | **Agrees** |
| Evening 11-25 #2: no freeze frames, held shots have idle life | Same: one reaction then idle | **Agrees** |
| Evening 11-25 #3/#4: weighted, staggered motion | Stock game motion. Keep our weighted, staggered animation. | Keep ours |
| Evening 11-25 #5: faces vary and fit the moment | Same, and stronger: a new face on the lead in almost every close-up | **Agrees** |
| House look: saturation 0.55-0.65, "deep, saturated colour" | **0.40-0.48 natural colour**, with true blacks and bloom; the colour accents go in the graphics | **Overrides** (needs Jake's yes) |
| "Frame 0 is one memorable picture with the title on it" | Frame 0 is mid-action **with no title**; the premise goes on the question card at the end | **Overrides** |
| Moth Wings finishing pass: shakes and zooms, a "shake-in" opening | **No shake-in, no added shakes**; only one snap zoom per film | **Overrides** |
| 11-23 camera structure (steady cuts, then one long glide) | Replaced by the cut rhythm all the way through (as in the 11-25 notes) | Overrides the old rule only |
| No music bed on story videos (11-23) | The account uses a continuous bed | **Not adopted by default**; optional only if Jake says yes |
| Captions: house font, keywords coloured | Keeps the idea and adds: dialogue in yellow quotes, the caption drops to 79% on face close-ups, a 1-frame pop | Extends |
| Handle top-left, sponsor ending in the Instagram edition | Unchanged | Keep ours |
| Cast v2, rounded or classic head, no new people from builders | Uses the classic head, an anime hair kit and line-art decals; new people only via Claude (CHARACTERS.md) | Agrees |

## 17. Do / Don't checklist
**Do**
- [ ] Hard cut every 1.3-1.6 s on average; nothing over 3.1 s except end cards.
- [ ] Lock the camera; use at most 2 moves (pull-out, orbit, crane or snap zoom), each on the biggest beats.
- [ ] Put the lead's face in a close-up after every reveal line, with a new expression each time.
- [ ] Give each featured character a name sticker in their own colour the first time they appear.
- [ ] Use captions with 1-3 words, white with a heavy outline, at y 67%, dropping to 79% on face close-ups. Show dialogue in yellow quotes and colour the keyword to match the object.
- [ ] Add 2-4 speech bubbles, 1+ time tag and 1 icon gag per film.
- [ ] Keep true blacks and a slight bloom on whites, with natural colour (saturation about 0.42).
- [ ] Make frame 0 a moving mid-scene picture, with the first caption by frame 5.
- [ ] End on the question card (tagline, red PART pill, 2-line question, plus A/B pills on vote episodes).
- [ ] Sell impacts with the body falling in a still frame, then cut.

**Don't**
- [ ] No whips, swish pans, crossfades, wipes, dutch angles, letterbox, grain, light leaks or chromatic aberration.
- [ ] No camera shake on impacts, and no shake-in opening.
- [ ] No title card on frame 0.
- [ ] No saturation push, no pastel, no haze.
- [ ] No duplicated game-capture frames; render a true 30 fps.
- [ ] No romance content: no crushes, kisses or love letters. Use quests, royal notes, siblings, rivals and friends.
- [ ] No blush on faces by default; use a sweat drop or anger mark instead.
- [ ] No copying of their stories, lines, characters, names, sticker designs or fonts as images. Build our own.

## 18. Style pack (code)
`pack/` turns this spec into code. Read `pack/README.md` first.
- **`style_fourth_style.py`** (Blender 5.3):
  - `apply_look`: AgX High Contrast at the calibrated exposure, EEVEE or Cycles, 30 fps, the bloom/contrast/saturation-trim node group, and a split world (visible sky plus a weak fill).
  - `light_rig` with five rigs: day, sunset, interior, night, insert.
  - `camera`, plus one function for each keyed technique in section 12: `creep`, `snap_zoom`, `pull_out`, `orbit`, `crane_down`, `jump_cuts`, `ff_jitter`, `light_dim`, `ots`, `low_angle`, `top_down`, `eye_ecu`.
  - `set_face` and `face_swaps` for the per-close-up expressions.
  - `caption_groups` and `cut_plan`.
  - Tested in bpy 5.3 on dummy cameras, without rendering. Each move hits its numbers: snap 50 → 58.5 mm; pull-out 1.9% a frame, 2.0x; orbit 30°; jitter peaks ±27 px; creep 0.3 px a frame.
  - `cut_plan` on three of our own stories gives an average shot of 1.53-1.63 s, about 37-40 cuts a minute, and captions of 2.05-2.13 words. The measured targets are 1.45 s, 41 a minute and 1.9 words; ours run a little long because our reads have built-in pauses.
- **`post_fourth_style.py`:** every post technique as a frame-range event, plus the sticker layer, all drawn by our code: name sticker, speech bubble, time tag, the five icon gags, reference captions and the question card. It also has these modes:
  - `run` (video) and `frames` (PNG sequence);
  - `ffmpeg` (a plain `-vf` chain);
  - `cues` (pops and thumps for the mix);
  - `check` (a still against the luma and saturation targets).
- **`captions_fourth-style.json`:** the caption and sticker text spec.
- **`preview/`:** our own stills of the sticker layer, the card, the 5-frame pop and wiggle, and each effect.

## 19. Style test (make this first, 10-15 s)
A short test so Jake can judge the style before a full film. Use any of our sets, two cast members and one line of narration per shot. Read the lines aloud at about 3.6 words a second, or use an existing word-timings file, and cut it with `cut_plan`.

| # | Length | Shot | What it tests |
|---|---|---|---|
| 1 | 1.8 s | **Frame 0, mid-action wide:** the hero walks through the castle corridor, `light_rig('interior')`. The caption is up by frame 5. No title. | Frame 0 rule, the look (bloom, true blacks), caption position at y 1290 |
| 2 | 1.3 s | Medium on a second character, **name sticker** in her colour | Name sticker pop (5 frames), the -3° tilt, colour identity |
| 3 | 0.9 s | **Reaction close-up** of the hero, new face (alarmed); caption drops to y 1515 | Face swap between shots, close-up caption drop |
| 4 | 1.4 s | Medium, the second character speaks: **speech bubble** with its tail on her | Bubble size (60-70% width), tail, 2-4 words |
| 5 | 1.0 s | **Cut-in plus snap zoom** on the hero shouting "NO!" (gold quoted caption) | +17% in 5 frames, with no shake |
| 6 | 2.1 s | **Pull-out reveal** from an 85 mm extreme close-up of a statue to a 42 mm medium | 6-frame hold, ~1.9% a frame, ease-out |
| 7 | 1.2 s | Top-down **note insert**, bright (`light_rig('insert')`), with a **time tag** "NEXT MORNING" | Insert brightness 175-195, tag tilt and wiggle |
| 8 | 0.6 s + 0.9 s | The hero is knocked flat (static camera), cut, then the aftermath with **dizzy stars** | Impact without shake; gag timing |
| 9 | 4-5 s | **Question card:** PART 1 pill, a 2-line question with a gold keyword, over 2 background cuts | Dim and blur over 8 frames, card layout, end hold |

**Compare against these targets:**
- `check` on 3 stills should give mean luma 95-110, p5 under 15, p95 220-232 and saturation 0.40-0.48.
- Average shot 1.3-1.6 s, captions 1-3 words.
- At most 2 camera moves in the whole test (here: shots 5 and 6).
- Stickers land on a cut or 5 frames into a shot.
- Then compare side by side with a recent house film, and with `pack/preview/` for the sticker layer.

The test answers two questions for Jake:
1. Does the natural 0.42 saturation look too flat next to our house 0.55-0.65?
2. Does the sticker layer read on a phone?

## 20. Evidence

**Account:** Stickman.deadzone. Instagram @stickman.deadzone has 98.9K followers on 11-26 (it was described as 77K). TikTok @stickman.deadzone has 74K followers and 3.4M likes. The account calls itself "Roblox Romance & Horror" and is itself a Flashloop creator. Instagram hides view counts from logged-out visitors, so likes are given as the hit measure. The account's top reels reach about 1.1M views (from the coordinator's brief; not re-checked).

**Why this account and not Yougplat.** I compared both for about 7 minutes using contact sheets of 3 Yougplat Shorts (on YouTube, 1.2M, 1.1M and 344K views) and 4 Stickman reels.
- Yougplat is plain R6 avatars in standard game maps with one-word captions. That is visually the same family as the cannonanimates style we already measured.
- Stickman adds anime-hair characters, line-art faces and a full comic sticker layer (name cards, bubbles, tags, icon gags, question card) over realistic-lit sets. It is far from plain fast cuts, far from glossy Blender renders, and it ports cleanly to kid-safe medieval stories once the romance is dropped.

**Reels studied.** Descriptors are ours, not their titles. All were posted 11-23 to 11-25.

| Reel | URL | Likes | Comments | Length |
|---|---|---|---|---|
| V1 "Lies turn you to stone", Part 1 | https://www.instagram.com/stickman.deadzone/reel/DgI3_cjIzWb/ | 88.9K | 434 | 93.4 s |
| V2 "The dangerous dad", Part 1 | https://www.instagram.com/stickman.deadzone/reel/DgI27o3IXFk/ | 70K | 693 | 89.3 s |
| V3 "Carried to school in a box", Part 1 | https://www.instagram.com/stickman.deadzone/reel/DgGbD0cIBhg/ | 54.1K | 363 | 86.3 s |
| V4 "Secret language", Part 2 | https://www.instagram.com/stickman.deadzone/reel/DgLUojxI7ns/ | 47.5K | 2,044 | 99.7 s |
| Weak reel, for contrast: "Time loop", Part 1 | https://www.instagram.com/stickman.deadzone/reel/DgLPEZhoEkj/ | 5.2K | 37 | 90.0 s |

**Measured numbers**

| | V1 | V2 | V3 | V4 | Style target |
|---|---|---|---|---|---|
| Shots | 57 | ~61 | ~61 | 68 | 55-65 per 90 s |
| Average shot (s) | 1.61 (1.48 before the card) | 1.46 | 1.41 | 1.47 | **1.45** |
| Median shot (s) | 1.4 | 1.2 | 1.3 | 1.4 | 1.3 |
| Longest hold (s) | 7.6 (question card) | 4.3 (sponsor) | about 6 (card) | 4.6 (opening) | 3.1 in the story |
| Brightness, mean luma | 113 | 111 | 89 | 97 | **102** |
| Saturation, HSV mean | 0.34 | 0.46 | 0.44 | 0.43 | **0.42** |
| Luma p5 / p95 | 15 / 230 | 1 / 232 | 0 / 226 | 2 / 222 | <15 / 225 |
| Contrast (luma SD in a shot) | 59 | n/m | n/m | 62 | about 60 |
| Captions a second / median caption | 1.90 / 0.5 s | 1.88 / 0.5 s | 1.89 / 0.5 s | n/m | **1.9 / 0.5 s** |
| Caption at y 65-70% / lower (75-85%) | 85% / 15% | 80% / 20% | 90% / 10% | n/m | 80-90% / 10-20% |
| Keyword-coloured caption time | n/m | 61% raw* | 50% raw* | 35% | 35-50% |
| Words a second | ≈3.6 (est.) | n/m | n/m | n/m | 3.4-3.9 (ours) |
| Camera moves (non-locked shots) | 1 pull-out | 1 snap zoom, 1 jittered fast-forward | 1 orbit, 1 crane, 1 set of jump cuts | 0 (static impact) | 1-2 |
| Voice start / first caption | 0.16 s / frame 5 | bubble on frame 0 | frame 3 | frame 3 | ≤0.17 s |
| Music bed under voice | yes, about -20 dB, swells at the end | yes, stops before the sponsor | yes, bass from about 15 s | n/m | optional |
| Low effect hits | 4 | 0 | n/m | n/m | 3-4 thumps |

n/m = not measured for that reel. \*Raw colour readings on V2 and V3 include warm props (orange products, sunset) behind the caption band, so the true keyword share is nearer the V4 figure. Framing mix (V4): wide 19%, medium 35%, medium close-up 24%, close-up/extreme close-up 18%, insert 4%.

**Method:** frames were drawn from the page's video element in the browser.
- **Cuts:** colour-histogram and pixel-difference thresholds at 10 fps, with dark scenes re-checked at a lower threshold.
- **Motion:** brute-force global shift, zoom and roll search with sub-pixel fit, at 30 fps around each key moment.
- **Palette:** k-means with 12 clusters on shot-middle frames.
- **Captions:** an outlined-text mask in the lower band at 10 fps.
- **Sound:** Web Audio analyser bands (with playback silent on the PC).

All competitor frames, numbers files and notes were deleted after this file was written.
