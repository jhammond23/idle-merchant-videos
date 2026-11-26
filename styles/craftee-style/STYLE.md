# Toybox Fable (style id `craftee-style`)

Inspired by the method of Craftee Films (Instagram, about 661K followers). We copy the method only, never their stories, lines, characters, character designs, names, titles or footage.

**Summary.** Toybox Fable looks like a well-lit toy town that kids actually play in. The people are classic blocky R6 avatars, all the same height, with big hand-drawn black line-art faces that swap expression on almost every shot. They stand in detailed game-map towns lit by bright, neutral daylight (mean luma about 106 to 125, saturation only about 0.39 to 0.46), with dark night or black beats for the scary turns. The film is built from hard cuts: a new, mostly locked-off shot every 1.2 s in the 37 to 39 s format and every 1.3 to 1.5 s in the 136 to 158 s format, about 5 spoken words per shot. The camera does almost nothing inside a shot. The energy comes from the cut, the face swap and a prop gag. Each video opens on a whip-blur frame that lands in 3 frames, or on a frame that loops from the last frame. The captions are bold rounded white words with one keyword card in a single accent colour. A quiet music bed runs under a fast narrator (3.3 to 5.2 words a second; short films 4.7 to 4.9). The last word is the punchline, with no end card.

**Builder pack:** `pack/` has the Blender module, post script and caption spec that implement this document (start with `pack/README.md`). Section 18 is a 12-second style test to make before any full film.

**Units used in this document:**
- Our scenes use 1 m = 3.3 Blender units (BU).
- A Cast v2 person at `s=1.0` is H ≈ 6 BU tall including hair (kid about 5, adult about 6.3), and the head is 1.3 BU wide. Town models are in the same units (cottages 12-16, lamp 11).
- Frames run at 30 fps.
- Pixel sizes are at 1080 px wide (the competitor reels are 720x1280; their numbers were scaled by 1.5).
- Distances below are given in H or BU, with metres in brackets. Light watts and f-stops are for real scale; the pack multiplies watts by 3.3² and divides f-stops by 3.3.

Two formats, same rules:
- **Short fable (37 to 39 s):** a two-line caption in the upper third (white line plus a coloured UPPERCASE keyword line), 82 to 90% locked camera, about 49 cuts a minute, a punchline ending.
- **Long fable (136 to 158 s):** 1 to 2 word captions in the lower middle, a keyword card alone in an accent colour, more camera travel (about 21 fast moves a minute), prop close-ups, black beats, a loop ending.
- (Variant seen once: the "cinematic" long fable, which has a 3:4 letterbox, one yellow word at a time, realistic-render sets, 3.2 s shots and swing-and-settle camera moves. Use it only when Jake asks for it.)

---

## 1. Look in one picture (words)
A blocky kid in a bold two-colour striped shirt stands on a sunny cobbled square in front of a big plaster-and-timber building. The camera is at eye level, about 26 mm, so the whole kid fits with the building behind. His face is a white-and-black drawn decal: huge round eyes and a "3"-shaped whistle mouth. Two lines of fat rounded text sit in the upper third: "every kid gets" in white and **ONE WISH** in bright green. The sky is plain mid-blue. Shadows are crisp but soft-edged. Apart from a neutral game-engine contrast curve, nothing is graded, tinted or vignetted. It looks like a well-lit game screenshot, not a movie.

## 2. Palette (hex, where used)
Measured with k-means over 385 mid-shot frames from the 6 videos, then mapped to our use. Saturation is moderate. The colour comes from one hero outfit and one keyword colour, not from the grade.

| Hex | Use |
|---|---|
| `#5D8CD0` | Daytime sky (measured 4 to 9% of pixels). A flat gradient to `#A4AEC0` at the horizon. |
| `#E4E7E2` | White plaster walls, window frames, caption white base. |
| `#D3B78B` | Sunlit plaster, sand, light stone. |
| `#A98758` | Warm timber, beams, doors, market stalls. |
| `#6B5A41` | Darker wood, fences, furniture. |
| `#7C7C7E` | Cobbles, castle stone, roads (the biggest neutral). |
| `#48546D` | Shade side of buildings, slate roofs, dusk. |
| `#362B27` | Interior shadows, dark earth, tavern corners. |
| `#0B060A` | Night beats and the black "drop" shots (11 to 15% of all pixels across the long videos). |
| `#CF3D13` | Hero outfit primary (the one saturated colour in the frame). |
| `#2ECE30` | Keyword colour A (short format; measured `#2ECE30`). |
| `#42B4C7` | Keyword colour B (long format; measured `#42B4C7`). |
| `#E6B872` | Keyword colour C (night or winter stories; measured about `#E2B873`). |
| `#ECE648` | Cinematic variant: every caption word in this yellow. |

Rules: use one keyword colour per video, picked to contrast with that video's dominant colour (green against red and stone, cyan against warm wood, amber against night blue). The hero is the only character in a strong saturated primary. The crowd wears desaturated or patterned clothes.

## 3. Light and grade
Measured per video (mean luma 0 to 255 of the whole frame at 72x128, mean HSV saturation):

| Video | Luma | Saturation | Luma SD (contrast) | Dark frames (luma < 70) |
|---|---|---|---|---|
| Royal guard (short) | 106 | 0.39 | 61 | 3% |
| Dragon dad (short) | 125 | 0.46 | 64 | 0% |
| Glass world (long) | 108 | 0.36 to 0.39 | 49 | 13% |
| Perfect town (long, dusk and night) | 85 to 98 | 0.50 | 47 to 50 | 25% |
| Monster's child (long, winter night) | 97 to 99 | 0.46 | 68 | 11% |
| Middle one (cinematic, letterboxed) | 84 (about 112 inside the picture) | 0.27 to 0.31 | 67 | 22% |

- **Daytime target:** luma 106 to 125, saturation 0.38 to 0.46. That is brighter than our house (about 95 to 100) and less saturated (house 0.55 to 0.65).
  - **Luma SD:** 55 to 65 over a whole film. These pass 1 figures were probably pooled across shots and dark beats. A single daytime still of our town square reaches 44 to 49 at the calibrated settings, so a still passes at 42 or more. Don't push contrast further to chase 55.
  - **Highlights:** white walls land around 220 to 235 (`#E4E7E2`), and no more than 1% of pixels are blown white (luma 250+).
  - **Calibrated settings:** section 19 has the numbers that hit this on our own scene.
- **How to hit it:** these are measured on a rendered still with `pack` `measure()` (or `post_craftee-style.py check` on a film), the same way the teardown measured them (Rec.601 luma at 72x128).
  - **Luma:** fix it with exposure only (`suggest_exposure()` gives the change in stops).
  - **Saturation and contrast:** fix them with the sun-to-sky-fill balance first. A strong sun with a low fill gives crisp shadows, more SD and more colour. Then use the neutral Standard "High Contrast" tone curve (calibrated in section 19). After that, adjust set and outfit colours.
  - Never use a colour tint or a saturation grade.
- **Night and scary target:** luma 30 to 60 in the shot, moonlight blue `#3A5A9A` fill, warm `#FFB060` window and lamp points, glowing eyes as the brightest thing in frame.
- One strong sun with crisp, slightly soft shadows (Roblox "Future" lighting look), plus a low blue sky fill. The sky is seen at its exact hex. No haze, no fog except snow or night atmosphere, no lens flare except on fireworks and magic.
- **No vignette.** The corner-to-centre luma ratio is 0.98 to 1.23 (corners are as bright as the centre or brighter). The only exception is the cinematic variant (0.72).
- No film grain, no chromatic aberration, no light leaks, no colour tint. White stays white.
- Bloom only on emissive VFX (fireworks, fire, magic). The light pulse (T15) is 6 frames: 2 frames up to about +30 luma, then 4 frames down.
- Time of day changes by cut, not by grade: day, then dusk, then night in a locked-off montage (see technique T14).

## 4. Camera and framing
**Framing mix** (hand-counted from every mid-shot frame of the short films; the long films estimated from contact sheets):

| | Wide / establishing | Medium-wide (full body) | Medium (knees or waist up) | Close (head and shoulders) | Extreme close / prop insert |
|---|---|---|---|---|---|
| Short (Royal, Dragon) | 13 to 24% | 15 to 16% | 44 to 56% | 16 to 18% | 0% |
| Long (Glass, Town, Monster) | about 25% | about 15% | about 30% | about 20% | about 10 to 15% |

- **Angles (short):** about 75% eye level, about 15% low (creatures, the big reveal, someone walking toward camera), about 10% high or top-down (crowds, establishing).
- **Dutch angles:** 0% in the short films, about 18% of shots in Glass world, canted 10 to 30° on uneasy or "wrong world" beats.
- **Over-the-shoulder:** used for two-hander punchlines (2 of 34 shots in Royal guard).
- **Scale shots:** a tiny kid against something huge. The creature is 1.6 to 2 times kid height (dragon) or 3 to 5 times (winter beasts). The camera sits at kid-chest height looking up.
- **Lens:** standard 26 mm on a 36 mm vertical sensor (69.4° vertical FOV, the Roblox default 70). At 26 mm, 1° of pan moves the picture about 24 px at 1080 wide.
  - Comic close-ups: 18 mm (90° FOV), inside one head-width of the face, so the head swells and the arm foreshortens.
  - Two-shots: 35 mm (54°).
  - Prop inserts: 50 mm (40°).
  - Depth of field is mostly off. Long-format closes get a mild background blur at most: f/4 at real scale, which the pack converts to f/1.2 for our 3.3x scenes.
- **Movement inside a shot (optical flow, block matching at 10 fps):**
  - Short films: 82 to 90% of in-shot frames have zero camera motion, and only 6 to 18% of shots move at all.
  - Long films: 54 to 70% static, 18 to 29% slow drift (150 to 300 px/s at 1080 wide), 11 to 14% fast moves.
  - Cinematic variant: only 37% static, with frequent swing-and-settle moves (about 38 direction reversals a minute).
- **No handheld shake and no impact shake.** Direction reversals in the short films: 0 a minute. The style gets its energy from cuts, not shake. Do not add shake (see the technique catalogue).

## 5. Cutting rhythm
| Video | Length | Shots | Average | Median | 10th to 90th percentile | Longest | Cuts a minute |
|---|---|---|---|---|---|---|---|
| Royal guard | 38.8 s | 33 | 1.18 s | 1.1 s | 0.62 to 1.70 | 2.1 s | 49.5 |
| Dragon dad | 36.9 s | 31 | 1.19 s | 1.2 s | 0.70 to 1.70 | 2.1 s | 48.8 |
| Glass world | 157.7 s | 106* | 1.49 s | 1.4 s | 0.60 to 2.20 | 7.7 s | 40.0 |
| Perfect town | 151.6 s | 100* | 1.52 s | 1.2 s | 0.70 to 2.30 | 7.0 s | 39.2 |
| Monster's child | 155.8 s | 120 | 1.30 s | 1.2 s | 0.7 to 2.0 | 3.4 s | 45.8 |
| Middle one (cinematic) | 136.6 s | 43 | 3.18 s | 2.8 s | 0.50 to 7.10 | 12.9 s | 18.4 |

\*Fast fly-throughs register as a few extra cuts, so the true average there is about 1.6 s.

Pooled over the 5 main-style films (390 shots, 541 s): mean **1.39 s**, median **1.3 s**, 64% of shots between 0.8 and 1.6 s, nothing under 0.5 s except flash frames.

- **The cutting rule, as code:** `pack` `cut_plan(word_timings, fmt)` cuts on word onsets.
  - It prefers sentence starts, then clause starts and pauses (0.12 s or more), and avoids cutting right after "the", "my" and similar words.
  - It keeps each shot inside the format's range: short 0.6 to 2.1 s (target 1.2), long 0.6 to 2.3 s (target 1.4).
  - On three of our own voice tracks it gave means of 1.33 to 1.51 s and 39 to 44 cuts a minute, which matches the table above.
  - A shot runs over the maximum only where the voice track has a deliberate pause.
- **One shot per spoken phrase:** about 5 to 6 words per shot (Royal 5.5, Dragon 5.8, Glass 4.9) and 1.3 to 2.8 caption cards per shot. At our slower house voice speed this comes out nearer 3.5 to 5 words per shot; the time rule wins.
- **Cut on the caption change.** The cut lands within ±0.1 s of a new caption card, usually on the first word of a phrase. Checked: 7 of 7 cuts in Royal 12 to 20 s and 4 of 4 in Glass 4 to 10 s. About half of all caption changes are also cuts; the other half change the words over the same shot.
- Long holds (4 to 8 s) are rare: 1 to 4 per long film, only on a moving camera (fly-through, aerial) or a black beat.
- No freeze frames. The image never stops: no run of 0.4 s or more without change in 5 of 6 films (idle animation, crowd, particles or drift always moving).

## 6. Characters and faces (summary; full kit in `CHARACTERS.md`)
- Classic blocky R6 bodies, rigid limbs, a rounded classic head. Everyone is the same height (kids and adults alike). Age and role come from hair, face, beard, glasses, hats and clothes.
- **Faces carry the acting:** thick near-black (`#1E140E`) hand-drawn line art with big white eyes, brows and open mouths with teeth and tongue. About 14 distinct expressions. The face changes in about 70% of shots where it is visible, and swaps instantly on the punchline (1 frame, no in-betweens).
- **Hero signature:** bold horizontal two-colour stripes or one strong primary, plus chunky hair in a colour nobody else in the film has. Never reuse their heroes' exact combinations (see `CHARACTERS.md` §8). Our default is the Cast v2 hero kid in burnt-orange and cream stripes.
- **Crowds:** dozens to hundreds of extras in varied clothes for scale beats.
- **Creatures:** soft, round and readable (a plush mascot shape) or shaggy and huge (fur cards, white fangs, glowing yellow eyes). Always one clear silhouette and one humanising prop of our own choosing.

## 7. Shapes and proportions
- **R6 blocks** (measured on the royal guard): head 0.24 of body height, shoulders (arm to arm) 3.1 times head width, torso height 1.6 times head height, limbs 0.8 times head width thick. Same as our Cast v2 rig (torso 2x1x2, limbs 1x1x2, head 1.2 to 1.3).
- Buildings are big simple boxes with gabled roofs, chunky trims, arched doors and lanterns. Props are oversized, about 1.3 times real scale relative to the avatar (notes, drawings, cakes, fire extinguishers).
- Silhouettes read at phone size: one character or one prop dominates each shot.

## 8. Textures and materials
- Characters: smooth plastic (roughness about 0.5, mild specular). Clothing is printed 2D texture on the blocks: stripes, uniforms with gold buttons and cuffs, plaid, Nordic knit, cable knit. No sculpted cloth except a layered dress or cape.
- Environments: detailed game-map PBR-lite. Cobblestone and plank textures, painted plaster, slate roofs, glass with reflections, low-poly faceted trees (Glass world), fluffy pink blossom trees (Town), snow with fur-card creatures (Monster).
- No toon shading, no outlines on bodies or sets. The only "outline" is the drawn face and the caption stroke.

## 9. Environments
- A recognisable "game map" town: squares, palace gate, cottages, a lake town, a snowy village. Every world has a landmark (a gate, a wall, a tower) that becomes the story's set piece.
- Lived-in: crowds, pets, market props, lamp posts, fences, signs, plus foreground objects for wipes.
- Two to five locations per short film and eight to fifteen per long film. Interiors are warm-lit (`#FFB060` lamps). Exteriors are daylight. Night versions of the same set show time passing.

## 10. Animation (timing, easing, what moves)
- **Bodies:** stock R6-style idles (a slight sway), walks (arms and legs swing about ±40°), runs, waves, cheers, faints, jumps. Snappy, linear-ish starts. Limbs never bend.
- **Faces:** instant decal swaps, held 0.5 to 2 s. A reaction lands on the cut or on the stressed word.
- **Props and physics gags:**
  - A hat flies up 2 head-heights (2.6 BU) and spins 180° over 6 frames (0.2 s).
  - A visitor is blown back by 3 to 5 white puff rings over 15 frames.
  - Fire breath grows from nothing to full over 9 frames (0.3 s).
  - A paper note slides through a crack.
- **Crowds:** staggered and never in unison. Each extra has its own idle offset.
- **Camera keys** (when it moves): fast in, ease out (moves finish with a 4 to 8 frame settle), never a slow ease-in. Two exceptions:
  - Drifts (T4) are linear.
  - The swish pan (T8) is ease-in-out.
  - The pack's functions already use these curves.
- Nothing in these films looked AI-video-generated. Motion is game-engine animation and keyframes.

## 11. Captions and on-screen text
Font look: heavy rounded geometric sans, white fill, a 7 px near-black `#111111` stroke plus a soft drop shadow. **Poppins Bold** (free, SIL OFL) matches closely.

**Measured in pass 2** (Royal guard and Glass world, 720x1280 reels, scaled to 1080):
- **Size:** every caption line has a 63 px cap height. Both lines of the short card are the same size; pass 1's 70 px and 86 px were glyph-height guesses.
- **Font size:** with Poppins Bold that is 88 px as an em size (PIL, ffmpeg drawtext, Blender text). In an ASS file (libass) the same look needs Fontsize 156 with a +13 px y offset.
- **Line spacing:** the short card's two baselines are 88 px apart (line height 1.0).
- **Position:** the short block is centred at y 503 (26.2%), the long line at y 1402 (73%).
- **Spec and tools:** `pack/captions_craftee-style.json` holds the full spec. `pack/post_craftee-style.py captions` burns it, checked to land on these numbers.

| | Short fable | Long fable | Cinematic variant |
|---|---|---|---|
| Position | Upper third, block centred at y 503 px (26.2%) | Lower middle, line centred at y 1402 px (73%) (Town: 68%) | Lower middle of the letterboxed picture (about 70%) |
| Layout | 2 lines, both 88 px (63 px caps), 88 px apart: line 1 white lowercase; line 2 the KEYWORD in caps in the keyword colour. The card ends on its keyword, so reading order never changes. Or one keyword line alone | 1 line at 88 px, white, sentence case; a keyword card shows the keyword alone, in caps, in the keyword colour | 1 word, yellow `#ECE648`, about 84 px (estimate, not re-measured) |
| Words per card | 1 to 4 (mean 2.7; number or noun reveals get a keyword-only card) | 1 to 3, mostly 2 (mean about 1.8); Town 1 | 1 |
| Card hold | median 0.7 s (0.4 to 1.3) | median 0.5 s (0.2 to 0.8) | about 0.3 s |
| Animation | Hard swap, no pop | Hard swap or a 3-frame scale pop 85% → 100% | Hard swap |
| Keyword | Every card has one keyword (the noun or verb that carries the joke) | About 1 card in 3 is a keyword card | none |

- No title card and no emoji or stickers in the film. The first caption is already on screen at frame 0.
- In-world text is used as a story prop: drawn signs, notes, a calendar, a photo frame, "REPLAY" on a screen, all shown as inserts.
- Handle `@idlemerchantrng` top left stays (house rule). Keep it clear of the short-format caption band (y 400 to 600).

## 12. Sound
- **Music bed under the voice in every film.** The 1 s window floor sits at -25 to -28 dB against speech at about -18 dB, so the bed is about 7 to 10 dB under the voice and never drops to silence, except on purpose.
- **Silence drops:** the long films cut the music to near silence (-60 dB) for a beat at the scariest or saddest moment (Town at about 30.5 s), then hit the next line.
- **Effects:** 41 to 73% of cuts coincide (±0.15 s) with a sharp transient (whoosh, pop, impact or a voice onset): Town 41%, Royal 47%, Dragon 73%. The creature short also has a low-end boom about every 3 s (13 low-band bursts in 36.5 s), including one on the whip-in at 0.15 to 0.2 s. Effects come in cartoon-sized: puff, roar, fire whoosh, crowd murmur, fireworks.
- **Narration:** one first-person male narrator. Measured speeds:
  - Glass world: 3.3 words a second.
  - Dragon dad: 4.9 words a second.
  - Perfect town: 5.2 words a second.
  - Royal guard: 4.7 words a second (7.4 s window, 35 words).
  
  Target 4.5 to 5.0 for short films; long mystery films can slow to 3.5. Sentences run back to back with no pauses between them. (Voice timbre was not judged by ear: the audio was analysed silently. One comment mentioned that the account recently changed narrator.)
- Loudness and our rules: the voice stays on top, then -14 LUFS (house).

## 13. Frame 0 and ending
- **Frame 0:**
  - In 3 of 6 films it is a fully motion-blurred whip frame. The whip lands at 0.1 s, overshoots by about 30 to 60 px and is settled by 0.27 s (frame 8).
  - In 1 of 6 a 10° roll settles in 2 frames over an aerial of the town.
  - In 1 of 6 frame 0 is the same image as the last frame (a perfect loop).
  - In every case the first caption words ("if a royal GUARD", "in my", "my crush's DAD") are already up, and the first line states the weird premise within 1.5 s.
- **First second:** the premise subject in a medium shot, already acting (a face swap or a gesture) by about 0.1 to 0.3 s.
- **Ending:**
  - Short fable: the last line is a punchline on a close or medium two-shot, ending on the last word ("you're FIRED" style), with no outro or end card.
  - Long fable: the last shot pushes through a screen or frame and lands exactly on frame 0 (a seamless loop), or ends on an emotional close (a hug with drawn tears).

## 14. Camera and film technique catalogue
**How to read this table:**
- Frequencies are per minute of film, measured at 10 fps over the full videos and at 30 fps around 15 fast moments.
- Sizes are in pixels at 1080 wide.
- "Short" means the 37 to 39 s films, "long" the 136 to 158 s films.
- "Pack" is the function in `pack/style_craftee_style.py` (or the `post_craftee-style.py` command) that keys it with these numbers as defaults.
- "Seen" says how much evidence there is. Anything seen in only 1 or 2 films is a starting value, not a measured rule.

| # | Technique | How often | Timing (frames at 30 fps) | Size | Story trigger | Recipe = pack | Seen |
|---|---|---|---|---|---|---|---|
| T1 | **Whip-in opening** (motion-blurred frame 0) | 1 per film | f0 is mid-swing (full blur). Lands f3, overshoots to f5, settled f8. Whoosh plus low boom peaks at f4 to f6 | 25 to 35° yaw (or roll) swing; 2° overshoot (about 48 px; measured 30 to 60 px) | the very first word | `whip_in(cam, f0)`: Bezier keys +30° at f-3, 0 at f3, -2° at f5, 0 at f8; shutter 1.5 on f0 to f3 only. `post sfx` puts the whoosh on shot 1 and the boom at about f3 | 4 of 6 films |
| T2 | **Hard cut on the phrase** | 39 to 50 a minute | Cut on the first word's onset, ±3 frames | n/a | every new phrase (about 5 words) | `cut_plan(word_timings, fmt)` (S5). Hard cuts only, no dissolves | 6 of 6 |
| T3 | **Locked-off shot** | 82 to 90% of in-shot frames (short), 54 to 70% (long) | whole shot | 0 px of motion | default | `lock(cam, f0, f1)`. Life comes from idles, crowds and face swaps | 6 of 6 |
| T4 | **Slow drift** | 15 to 30% of in-shot frames (long) | whole shot, linear | 150 to 300 px/s lateral (5 to 10 px a frame) | establishing shots, aerials, tension | `drift(cam, f0, f1, px_per_s=200, direction='truck_left', subject=...)`: camera speed = px/s × distance ÷ 1387 px. 2D fallback: `post drift2d`. A push-in variant (+8% over the shot) is an estimate, not measured | long films |
| T5 | **Fly-through with foreground wipe** | long: part of the ~21 fast moves a minute | 0.6 to 1.0 s move (default 24 f). A foreground object covers the frame for 3 to 5 frames | objects cross the frame in about 9 frames (about 120 px a frame); camera 4 to 6 H/s (24 to 36 BU/s) | travelling through the world ("everyone here...") | `fly_through(cam, points, f0, 24, occluder=pole)`: a smooth path baked per frame; pass within 1.7 BU (0.5 m) of a tree, lamp or pillar. It returns `cut_window`, the frames to hide the next cut in | 2 long films |
| T6 | **Crane-out reveal with roll** | about 1 per long film (at the world rule) | 18 frames: fast first 9, ease-out last 9 | from 1.2 H to 18 H (108 BU, about 30 m) above the kid; 40° roll resolving to level; the kid shrinks about 15x | revealing the size or shape of the world | `crane_out(cam, kid, f0)` (CUBIC ease-out) | 1 to 2 films (estimate) |
| T7 | **Snap pull-out** | about 1 to 2 per film | 9 frames, ease-out | picture scale x2.5 (close to medium-wide) | revealing how big a gag is (pets everywhere) | `snap_pull(cam, f0, subject=kid)` dollies back to 2.5x the distance; `mode='zoom'` keys the lens 65 → 26 mm | 3 films |
| T8 | **Swish pan within a shot** | long: about 1 a minute | 9 to 12 frames (default 10), ease-in-out | about 90° pan; 60+ px a frame at the peak | following a boat, runner or projectile to a new composition | `swish(cam, f0)`: SINE ease-in-out, shutter 0.5 on those frames only | long films |
| T9 | **Follow-the-prop** | about 1 per long film | about 20 frames | camera rides about 1 BU (0.3 m) from the prop, rolling up to 15° | a note, letter or coin travels somewhere secret | Animate the prop first, then `follow_prop(cam, prop, f0, f1)` (baked per frame) | 1 film (estimate) |
| T10 | **Tracking truck with a runner** | long: about 1 a minute | 1 to 2 s | camera speed = runner speed, side-on at 2.4 H (14.4 BU, about 4 m), chest height 0.7 H | chases, running away | Animate the runner first, then `track_runner(cam, runner_root, f0, f1)`. Pass a pillar between them to wipe out | long films |
| T11 | **Face-swap punch** | about 70% of face shots; every punchline | 1-frame swap, no in-between; holds 0.5 to 2 s | n/a | a reaction, the stressed word | `face_set(head_mat, face_001.png)` then `face_swaps(head_mat, [(frame, 'shocked'), ...])` (CONSTANT keys on the image sequence). Frames come from `cut_plan` (`f0`, `face_swap_frame`) | 6 of 6 |
| T12 | **Prop physics gag** | 1 to 3 per film | 6 to 15 frames | prop travels 1 to 2 head-heights | sneeze, roar, slam | `hat_pop(hat, f0)`: up 2.6 BU (2 head-heights), 180° spin, 6 frames, ease-out | 1 example (estimate) |
| T13 | **Puff-ring / fire VFX** | 1 to 3 per creature film | rings: 15 frames expanding, 3 frames apart; fire: 9 frames to full | rings grow from 0.3 H to 0.9 H across and drift 0.6 H; fire 0 → 1.2 H (about 2 m) | a creature acts (roar, breath) | `puff_rings(mouth_loc, f0, facing=...)` (white emission 2.0, alpha 1 → 0). Fire: a particle system, `#FF8A2A` emission 5, with `bloom(scene)` on | 1 film (estimate) |
| T14 | **Locked-off time-skip montage** | about 1 per film | 3 to 4 beats of 0.8 to 1.2 s (default 1.0 s) | identical framing | "a week went by", "for a year" | `time_skip(cam, f0)` locks the camera and returns the beats. Render each beat with `light_rig('day')`, `'dusk'`, `'evening'` (lamps on), then `'night'`. Thin the crowd beat by beat | 3 films |
| T15 | **Light pulse** | 1 to 2 per long film | 6 frames: 2 up, 4 down | +30 luma on the environment | fireworks, magic, an explosion off-screen | `light_pulse(f, loc)`: a point light 0 → 2000 W (× 3.3² in our units) → 0. 2D: `post pulse --frames f` (eq brightness +0.12) | 1 to 2 films (estimate) |
| T16 | **Black beat** | 1 to 3 per long film | 1 to 3 s | luma below 12 | "and then nobody saw him", "I waited" | `light_rig('black')` plus one `practical(loc, 30)`. Drop the music to silence (T25) | 3 films |
| T17 | **Dutch tilt** | 0 in short; about 18% of long-film shots in one film | whole shot | 10 to 30° roll (default 15°) | wrong-world or uneasy beats | `dutch(cam, f0, f1, 15)`. Never on the hero's triumph shot | 1 film mainly |
| T18 | **Prop insert (ECU)** | long: about 10 to 15% of shots | 0.8 to 1.5 s | the prop fills 60 to 80% of the frame (default 70%) | notes, drawings, calendars, photos, clocks | `prop_insert(cam, prop, f0, f1)`: 50 mm; the distance is computed from the prop's size. Scale the prop 1.3x and light it flat | 3 long films |
| T19 | **Zoom-through loop** | 1 per long film (the ending) | last 6 frames, linear | a x1.4 push into a screen or frame until its border leaves the frame | the final reveal that links back to the opening | Put frame 0's image on an in-world screen, then `zoom_through(cam, screen, f_end)`. Check with `post loopcheck` (mean difference under 6). Write the last line so it flows into the first | 1 film (estimate) |
| T20 | **Mirror + white flash transition** (cinematic only) | 1 per film | 3 frames: 2 mirror, 1 white | a left-half mirror, then a white frame | jump from an extreme close-up to a world reveal | `post flash --frames f` | 1 film |
| T21 | **Swing and settle** (cinematic only) | about 38 reversals a minute | a 10 to 30 frame move, 10% overshoot, a 6-frame settle | 60+ px a frame at the peak | following a huge moving thing | `swing_settle(cam, f0)` | 1 film |
| T22 | **Letterbox 3:4** (cinematic only) | whole film | n/a | bars 240 px top and bottom (a 1080x1440 picture) | "movie" tone | `post letterbox` | 1 film |
| T23 | **Caption scale pop** (long only, optional) | about 1 in 3 cards | 3 frames, ease-out | 85% → 100% | a new card | built into `post captions --fmt long` (every 3rd card); ASS `{\fscx85\fscy85\t(0,100,\fscx100\fscy100)}` | long films |
| T24 | **Sound-synced cuts** | 41 to 73% of cuts (73% in the creature short) | the transient within ±4 frames of the cut | n/a | cuts into action or a new place | `post sfx --plan plan.json`: a whoosh or pop 2 frames before shot 1 and every 2nd cut (about 50%), or `--shots` by hand. Put impacts on the cut for physical gags | 3 films measured |
| T25 | **Music drop-out** | about 1 per long film | silence for 0.3 to 1.0 s, 30 ms ramps | -60 dB | the scariest or saddest beat | `post dropout music.wav out.wav --ranges a-b` on the music stem, before the mix | 1 film measured |
| T26 | **Walk-to-camera reframe** | 1 to 3 per film | 24 frames (0.8 s); a step every 6 frames | from full body filling 60% of the frame height to the head filling 40% of the frame width; no camera move. At 26 mm that is 7.2 → 4.2 BU | an entrance, "right in front of me" | Lock the camera, then `walk_to_camera(person, cam, f0)`: the root moves linearly and the limbs swing ±40°. Cut on the last frame | 1 walk measured (estimate) |

**Not used (measured as absent, do not add):**
- Camera shake, whether constant handheld or on impact (0 direction reversals a minute in the short films; the 3 to 7 a minute in the long films are travel moves, not shake).
- Zoom punches on words.
- Speed ramps, slow motion, freeze frames or stutter frames.
- Inverted or impact flash frames.
- Vignette, grain, chromatic aberration, lens distortion beyond the wide close-ups.
- Emoji, stickers, arrows or meme inserts.

If Jake wants shake anyway, keep it to one impact: 8 px, 12 Hz, decaying to 0 in 8 frames. Use `impact_shake(cam, f)` in Blender or `post shake --frame f` in 2D. It is off-style, so only with his yes.

## 15. Blender / Roblox Studio recipe
**Blender (our builders' default).** `pack/README.md` has the steps in order. Every value below is a pack default:
- **Render:** Cycles (house pipeline), 24 spp plus OpenImageDenoise, and 48 spp for hero closes. EEVEE (Blender 5, ray tracing on, soft shadows) is fine on a GPU machine. 1080x1920, 30 fps. This is `apply_look(scene, 'day')`.
- **Colour management:** view `Standard`, look `High Contrast` (a neutral tone curve with no tint), gamma 1. Exposure: day -1.0, dusk -0.75, night and black 0. Day was calibrated on our scene (section 19). For a new set, `measure()` one small still and add `suggest_exposure()`.
- **World:** a gradient sky, `#5D8CD0` at the top to `#A4AEC0` at the horizon.
  - Camera rays see the exact hex: their strength is 2^-exposure.
  - Lighting rays use a separate fill strength of 0.3 for day.
  - This is built by `light_rig()`.
- **Sun (day):** strength 6.0, angle 1.5°, colour `#FFF4E0`, elevation 50°, light travelling 35° off the camera axis so faces get light (`light_rig('day', cam=cam)`).
- **Dusk:** sun 3.0, `#FFB070`, elevation 8°; sky `#48546D` to `#E8A070`, fill 0.2. Not calibrated.
- **Night:** sun off; moon sun 0.6 `#9DB4FF`; world `#1A2440` at 0.3; practicals `#FFB060` at 50 to 200 W (`practical(loc, watts)` multiplies by 3.3² for our scale). Not calibrated.
- **Materials:**
  - Characters: Principled BSDF, roughness 0.5, IOR level 0.5, no coat.
  - Clothing: a flat colour plus a printed 2D pattern (stripes, plaid, knit) through an image texture.
  - Sets: Principled with tiling photo-like textures, roughness 0.7 to 0.9.
- **Outline:** none (no Freestyle, no inverted hull).
- **Camera:** `setup_camera(cam, kind)`: sensor fit Vertical 36 mm.
  - Lenses: standard 26 mm, comic close 18 mm, two-shot 35 mm, prop insert 50 mm.
  - Depth of field off. Long-film closes: f/4 real-scale = f/1.2 in our units.
  - Motion blur only on the T1 and T8 frames (the shutter is keyed, because `use_motion_blur` cannot be animated).
- **Compositor:** none. Only while emissive VFX are in frame, `bloom(scene)`: Glare Bloom, threshold 1.0, strength 0.15, size 0.5 (the Blender 5 equivalents of "size 6, mix -0.85"). No vignette or lens nodes.
- **Captions:** burnt in afterwards with `post_craftee-style.py captions` (ASS/libass), from `captions_craftee-style.json`.
  - Font: Poppins Bold, 88 px em (ASS Fontsize 156, +13 px y offset).
  - Stroke: 7 px `#111111`.
  - Shadow: 4 px, 35% black.
  - Colour: white `#FFFFFF`, plus the film's keyword colour (§2).
  - Positions as in §11.

**Roblox Studio** (only with Jake's permission; suggested starting values, verify against the luma and saturation targets):
- Lighting: Technology = Future, ClockTime 14, Brightness 3, EnvironmentDiffuseScale 1, EnvironmentSpecularScale 1, Ambient (70,70,70), OutdoorAmbient (128,128,128), ExposureCompensation 0.
- Atmosphere: Density 0.3, Haze 0, Glare 0.
- Bloom: Intensity 0.5, Size 24, Threshold 1.5.
- ColorCorrection: Contrast 0.08, Saturation 0.05.
- DepthOfField: off (long closes: FarIntensity 0.25).
- Camera: FieldOfView 70 (comic close 90, two-shot 54, insert 40).
- Avatars: R6, classic head, decal faces.

## 16. What changes vs our current house style
| House rule (Studio Bible) | Toybox Fable |
|---|---|
| Camera: 20 to 25 s of steady cut shots, then **one smooth glide** | **Overridden:** hard cuts all the way (median 1.2 to 1.3 s), no glide section |
| **Never** whips, swings or snaps | **Overridden:** a whip-in at frame 0 (8 frames) and, in long films, fast fly-throughs and swish pans (T1, T5, T8). Needs Jake's yes. |
| Deep saturated colour, saturation 0.55 to 0.65 | **Overridden:** 0.38 to 0.46 natural daylight; colour from the hero outfit and the keyword only |
| Banned: flat daylight | **Relaxed:** bright neutral daylight with sun shadows (not hazy, not pastel) |
| No looping music bed | **Overridden:** a music bed about 8 dB under the voice, with drop-outs |
| Frame 0 = memorable picture with the title | **Overridden:** frame 0 is a whip frame or the loop frame; no title card, first caption only |
| Narration 3.4 to 3.9 words a second | **Overridden:** 4.5 to 5.0 target for short films (measured 3.3 to 5.2; short films 4.7 to 4.9) |
| Opening shots 1.2 to 3 s, "camera never still", punch-ins | **Overridden:** shots 0.7 to 2.0 s, 82 to 90% locked, no punch-ins |
| Evening rules: steady cameras, eased movement, staggered timing, believable faces | Steady cameras **kept** inside shots but **overridden** for T1/T5/T8; eased movement **kept** for the camera (ease-out) but **overridden** for faces (instant swaps); staggered timing **kept**; believable faces **overridden** (cartoon line-art faces) |
| Cast v2 kid at scale 0.8 | **Overridden:** everyone at scale 1.0 (age shown by hair and clothes) |
Unchanged: rounded head (the classic head is rounded), handle top left, the sponsor ending rules, the quality checklist, kid-safe, no game words in the voice, cast built by Claude only.

## 17. Do / Don't
**Do**
- Cut every phrase (about 5 words): 0.8 to 1.6 s shots, median 1.2 s.
- Keep the camera locked in about 85% of the short film. Let the faces, props and crowds move.
- Swap the face on the stressed word in most shots, and make the expression obvious at phone size.
- Open on a whip-in (blur at f0, landed by f3, settled by f8) with the first caption already up.
- Light it bright and neutral: luma 106 to 125, saturation 0.38 to 0.46, one saturated hero outfit.
- Use one keyword colour per film. Short: two lines in the upper third. Long: 1 to 2 words in the lower middle with solo keyword cards.
- Run a music bed about 8 dB under a fast narrator (4.5 to 5.0 words a second in short films). Drop it to silence once for the big beat.
- Long films: prop inserts, a time-skip montage, one black beat, a loop ending that lands on frame 0.

**Don't**
- Don't add shake, zoom punches, speed ramps, freeze frames, vignette, grain or colour tints.
- Don't hold a static shot over 2.1 s in the short film.
- Don't make kids smaller than adults, and don't invent realistic faces. Use the line-art face set.
- Don't use dissolves (hard cuts only, except T20 in the cinematic variant).
- Don't put more than 4 words on a card, or a keyword without its colour.
- Don't end on an outro, logo or CTA inside the story (the sponsor ending stays separate, Instagram edition only).
- Don't show weapons pointed at people in scary beats. Menace comes from glowing eyes, size and silhouette (kid-safe).

## 18. Style test (make this first: about 12 s, short format)
Build this before any full film so Jake can judge the style. Use our own lines, cast and town square; the hero and everyone else are at `s=1.0`. Example voice, about 4.7 words a second, with caption keywords in caps: "In this town, every kid gets ONE WISH. I wished the guard had to OBEY me. He said NO. So I wished his HAT away. For a WEEK. Now he's my BUTLER."

Run `cut_plan(..., 'short')` and `caption_cards(..., keywords=...)` on the voice. Map the plan onto these shots:

| # | Shot | Lens | Technique | What to check |
|---|---|---|---|---|
| 1 | Medium of the hero kid in the square | 26 mm | T1 `whip_in`, first caption up on frame 0 | blur on f0; landed by f3; settled by f8 |
| 2 | Comic close of the hero, face `innocent` → `smug` on "OBEY" | 18 mm | T3 lock + T11 swap | the face reads at phone size (eye 40 px or more wide) |
| 3 | Wide of the square with 20+ staggered extras | 26 mm | T3 lock | `measure()` this still: luma 106 to 125, saturation 0.38 to 0.46 |
| 4 | Two-shot of hero and guard, guard `angry` | 35 mm | T11 | only the hero wears a saturated outfit |
| 5 | The guard's pot helmet flies off | 35 mm | T12 `hat_pop` + T24 pop SFX on the cut | 6 frames, ease-out |
| 6 | The guard walks at the lens | 26 mm | T26 `walk_to_camera`, locked | cut when the head is 40% of the frame width |
| 7-9 | "For a WEEK": 3 beats of 1.0 s, same frame: day, dusk, night | 26 mm | T14 `time_skip` + `light_rig` per beat | the camera is identical; dusk and night read correctly (those rigs are not calibrated yet) |
| 10 | Punchline: medium two-shot; the guard wears a butler apron; hero `grin`, guard `scream` on the last word | 35 mm | T11 on the last word; end on the word, with no end card | the last word lands on the cut |

**Then compare:**
- `plan_stats()`: mean about 1.2 s, nothing over 2.1 s.
- `post check`: luma and saturation pass, no vignette.
- The captions sit at 26% with the keyword line in green.
- Put the same wide shot rendered in our house style beside it.

**Jake's questions:** Does it feel faster and brighter than the house style? Do the drawn faces carry the jokes?

## 19. Calibrated on our scene (pass 3, 11-26)
**The test:** main's look test (`/tmp/claude-0/kits/look_test.py`, STYLE=craftee-style). It renders the town square with the Cast v2 hero kid, little sister and guard and the a1_* cottages, stall, lamp and fountain, on cobbles. Camera 30 mm at (-0.4, -15, 4.2), Cycles. The scene scale is 1 m = 3.3 units.

**Before** (the pass 2 defaults: look None, exposure -0.3, sun 3.0, sky fill 0.9):
- luma 117, saturation 0.29, SD 37.
- It looked hazy and grey, with weak shadows.

**Variants tried** at 270x480, 8 samples:

| Variant | Luma | Saturation | SD |
|---|---|---|---|
| Medium High Contrast look | 118 | 0.33 | 41 |
| Sun 5, fill 0.4 | 127 | 0.34 | 39 |
| Sun 5, fill 0.4, Medium High Contrast | 130 | 0.37 | 44 |
| Sun 6, fill 0.3, High Contrast, exposure -0.75 | 117 | 0.43 | 44 |

**Final defaults:**
- `apply_look(scene, 'day')`: Standard, look `High Contrast`, exposure **-1.0**.
- `light_rig('day', cam=cam)`: sun **6.0**, elevation 50°, 35° off the camera axis, angle 1.5°, `#FFF4E0`.
- Sky fill **0.3**; the camera sees the sky at its exact hex.

**Result** at 270x480, 8 samples: **luma 117.2, saturation 0.428, luma SD 49, 0% blown whites, no vignette**. The look is a crisp, sunny game screenshot: strong shadows, a clear blue sky and a saturated red hero shirt.

**Open items:**
- The 540x960, 16-sample confirmation render was not run here: the session's permissions blocked a render that size. Main can run it with: `STYLE=craftee-style RES=540x960 SAMP=16 OUT=/tmp/claude-0/kits/look/final_craftee-style.png python3 -I /tmp/claude-0/kits/look_test.py`
- Dusk, night and interior rigs are not calibrated yet.

## 20. Evidence
Analysed Thu 11-26-2026, 10:40 to 11:32 CT (52 min of measurement and writing), in the built-in browser, anonymously (Instagram public reel pages). Views were read from the account's public reels grid at about 10:43 CT. All frames and audio were analysed and then deleted.

| Title (theirs) | URL | Views | Length | Format |
|---|---|---|---|---|
| GLASS WORLD | https://www.instagram.com/craftee_films/reel/DgHmVeNv99g/ | 1.5M | 157.6 s | long, loop ending |
| ROYAL GUARD | https://www.instagram.com/craftee_films/reel/DgKDZWPJY-i/ | 1.1M (67.4K likes) | 38.7 s | short |
| THE PERFECT TOWN | https://www.instagram.com/craftee_films/reel/DgH2t9ohi73/ | 1.1M | 151.5 s | long, eerie |
| I'm The Middle One | https://www.instagram.com/craftee_films/reel/DgKUWogBMiZ/ | 795K | 136.6 s | cinematic variant |
| Monster's Child | https://www.instagram.com/craftee_films/reel/DgJoBIgv0_C/ | 647K | 155.8 s | long, winter night |
| Dragon Dad | https://www.instagram.com/craftee_films/reel/DgHOwcIt4NU/ | 551K | 36.8 s | short, creature |

The other recent reels on the grid (views): 431K (159.9 s), 444K (124.5 s), 355K, 256K, 145K, 121K (141.1 s, 2 h old).

**Pass 2 re-check** (11-26, about 11:53 CT, built-in browser, anonymous, own tab, closed afterwards):
- Caption-band frames from Royal guard (t = 3 s and 9 s) and Glass world (t = 12, 31 and 47 s), from the 720x1280 reels.
- **Measured:** cap height 42 px on both formats (63 px at 1080), with both short-format lines the same size; baseline pitch 59 px (88 at 1080); stroke about 5 px (7 at 1080); short block centre 26.2%; long line centre 73%; long cards in sentence case, up to 3 words.
- All frames and saved tool outputs were deleted afterwards.

**Method:**
- Cuts, brightness, saturation and optical flow: every 0.1 s of every film (6,770 frames), with block matching for camera motion.
- 30 fps strips around 15 fast moments.
- 385 mid-shot frames for framing and palette (k-means in Lab).
- 18 stills at 540x960 for faces and proportions.
- Caption bands at 10 fps for words a second.
- Two audio envelopes (Royal 30 s, Town 40 s), analysed with output gain 0.

**Measured numbers table:**
| | Royal | Dragon | Glass | Town | Monster | Middle (cin.) |
|---|---|---|---|---|---|---|
| Average shot (s) | 1.18 | 1.19 | 1.49 | 1.52 | 1.30 | 3.18 |
| Median shot (s) | 1.1 | 1.2 | 1.4 | 1.2 | 1.2 | 2.8 |
| Cuts a minute | 49.5 | 48.8 | 40.0 | 39.2 | 45.8 | 18.4 |
| Static in-shot frames | 82% | 90% | 54% | 70% | 90% | 37% |
| Fast camera moves a minute | 7.8 | 8.2 | 21.0 | 21.4 | 6.2 | 62.4 |
| Mean luma | 106 | 125 | 108 | 85 | 97 | 84 (bars) |
| Mean saturation (HSV) | 0.39 | 0.45 | 0.36 | 0.50 | 0.47 | 0.27 |
| Words a second | 4.7 | 4.9 | 3.3 | 5.2 | n/m | n/m |
| Caption position | top 26% | top 26% | bottom 73% | 68% | 70% | about 70% (in picture) |
| Keyword colour | green `#2ECE30` | green | cyan `#42B4C7` | (white only) | amber `#E2B873` | yellow `#ECE648` all |
| Frame 0 | whip blur | whip blur | loop frame | 10° roll-settle | whip blur | static low angle |

**k-means palettes (10 colours per video, largest share first; computed in Lab on the mid-shot frames):**
| Video | Palette |
|---|---|
| Royal | `#7E8387` `#A19B91` `#060A15` `#5D616C` `#BFBCB7` `#7F7049` `#4B473E` `#2E2B33` `#6A97C4` `#9D311E` |
| Dragon | `#D8BFA6` `#AC9786` `#76645E` `#452B1D` `#12090B` `#803619` `#73B26D` `#446A30` `#CB7C4A` `#578CC7` |
| Glass | `#3A3332` `#868080` `#6F5841` `#4D6380` `#E8EDE6` `#87A7CF` `#100E14` `#C8A367` `#E2360F` `#0D33D0` |
| Town | `#100407` `#B2A29C` `#847771` `#585051` `#3D1F19` `#DFC6AC` `#6F2B12` `#B99250` `#AA5A2A` `#558FED` |
| Monster | `#090711` `#A3B4D4` `#7687B1` `#605A5B` `#282B40` `#59331D` `#CCD9EE` `#A36C40` `#3D5894` `#DDB675` |
| Middle (cin.) | `#020202` `#4B4031` `#ABA9A6` `#2E261D` `#8F8B83` `#705D44` `#CFD0CB` `#657688` `#34557B` `#B48B3C` |
| All 6 (12 colours) | `#0B070D` `#342B29` `#7F8184` `#4D5569` `#A4AEC0` `#796144` `#AF8D60` `#D5B98D` `#66311A` `#E0E6E7` `#5783CE` `#CE3E13` |
