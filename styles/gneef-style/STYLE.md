# Torchlit Blocktale (build style `gneef-style`)

*Reverse-engineered from the method of the YouTube Shorts account @Gneef (2.26M subscribers when studied on 11-26). We copy techniques, numbers and settings only. Never their stories, lines, characters, character designs, names, titles or footage.*

**Summary.** It is shot in-engine, with plain block characters (classic R6 bodies, rounded heads and flat ink-line sticker faces) in lived-in maps lit like a film set. Ember-orange interiors, lilac-blue moonlit nights, golden hours and clear blue days, all pushed to deep saturation (mean 0.64) over crushed shadows (mean brightness 82/255; about 35% of pixels near-black). The camera never stops: about 7 in 10 shots are a slow push-in of +3 to +9% a second (default +6.5%), with a little roll and a soft handheld wobble, and no shot is ever locked off. Hard cuts land on the spoken word every 1.3 s (median; 1.1 s in the newest upload) for the whole video, not only the opening. The only text is one white word at a time in the lower-middle of the frame, synced to the voice at 3.2-3.5 words a second. A continuous sound bed sits about 10 dB under the narrator from the first frame to the last. Videos run 110 to 180 s, open on a moving establishing shot with the first word already on screen, and end mid-line so the loop restarts cleanly.

---

## 1. Look in one picture (words)
A blocky kid with one loud hair colour stands in a timber corridor lit by orange lanterns. The edges of the frame fall off into near-black, and a green-gold window behind him glows with bloom. The camera is already creeping toward his face and slowly leaning a degree or two. His face is a flat black-ink sticker: two black oval eyes, thick tilted brows, an open D-shaped red mouth. One white lowercase word ("lantern") sits just below his chest at 69% of the frame height. Cut: the same push, now outside under a periwinkle moon, the ship's hull a dark silhouette from below.

## 2. Palette (hex, where each is used)
Pooled k-means over 4 new-format videos (6,700 sampled frames, caption band removed), plus a saturated-accent pass. The newest upload (Line Of Sight) is golden-hour daylight in the same ember family (`#F1BC6F`, `#E5781D`, `#B43E12`, 81% warm).

| Hex | Name | Share | Where it goes |
|---|---|---|---|
| `#0E0810` | crushed shadow | 24% | Every shadow and the unlit background. Blacks are crushed, not lifted |
| `#372F69` | night indigo | 5% | Night sky, the shadow side of moonlit walls |
| `#636EB9` | moonlight | 5% | Moonlit faces and roofs, the rim on night exteriors |
| `#B6ACB4` | moonlit lilac | 6% | Pale stone, cloth and pale creatures under the moon |
| `#41110E` | oxblood wood | 8% | Interior timber in shadow |
| `#762810` | rust timber | 8% | Mid-tone wood, beams, floors |
| `#B9471C` | burnt orange | 6% | Lit wood, lantern spill on walls |
| `#E98B46` | lantern | 6% | Lit skin and cloth under warm light |
| `#EECE88` | candle cream | 6% | Highlights, candle flames, lit paper, knit sweaters |
| `#5E5B3B` / `#2A2F1D` | night moss / dark moss | 20% | Grass and foliage at dusk and night |
| `#E35214` | hero orange | accent | The lead's signature colour (hair or clothing); nobody else wears it |
| `#E9BF35` | gold | accent | Bells, coins, crowns, lamp cores |
| `#2089C9` / `#0F5BC7` | day sky / deep blue | accent | Day skies; blue clothing |
| `#E722BD` | magic magenta | accent, about 1% | Magic VFX only (glowing chains, runes). Never used on people |

Per video (measured): Watcher's Knot is 77% warm hues; Love Chains 80% warm; Awake At Night 46% cool (lilac night); 1,000,000 Steps is daylight (43% green, blue sky). **Pick one dominant temperature per scene and one opposite-temperature accent.**

## 3. Light and grade
| Measure (0-255 sRGB, from 54x96 frame grabs) | Watcher's Knot | 1M Steps | Awake At Night | Love Chains | Line Of Sight | **Target** |
|---|---|---|---|---|---|---|
| Mean brightness | 81 | 99 | 63 | 67 | 101 | **70-100** (night 60-75, interior 75-90, day or golden hour 95-105) |
| Mean saturation (HSV) | 0.77 | 0.52 | 0.59 | 0.69 | 0.63 | **0.60-0.72** |
| Share of pixels below 40 (shadow) | 35% | 17% | 45% | 49% | 29% | **30-45%** |
| Share above 220 (highlights) | 2.2% | 1.4% | 0.6% | 1.7% | 5.7% | **1-3%**: small hot spots only (golden-hour skies up to 6%) |
| Per-frame contrast (std of luma) | 46.5 | 51.6 | 46.5 | 52.6 | 59.2 | **45-60** |
| Edge-to-centre brightness | 0.72 | 0.82 | 0.72 | 0.72 | 0.87 | **0.72-0.85** (vignette 15-28% darker edges) |

- **Light:** one motivated key per shot (a lantern, a window, the moon, the sun) and hard shadows. Practical lights stay in frame and bloom.
- **Time of day:** night and lantern-lit interiors dominate (3 of the 5 new-format videos). The other two are a clean blue-sky day and a warm golden hour, both with no haze.
- **Grade:** saturation pushed hard. Warm interiors lean orange (gain toward red, blue pulled down). Nights lean lilac-blue (lift toward blue, warm practicals left warm). Blacks crushed.
- **Flashback and danger grades** are hard-switched on the cut. Sepia flashback (seen at 6.8-12.8 s in Watcher's Knot). Black and white with faint scan lines, and full red monochrome for danger, appear in the older format.
- **Bloom:** strong on emissive things (windows, lanterns, magic). **Fog/haze:** almost none. **Grain, chromatic aberration, light leaks, letterbox:** none.

## 4. Camera and framing (numbers)
Measured with dense optical flow on every shot of 6 videos (590 shots at 10 fps) plus 30 fps windows (Watcher's Knot 0-6.5 s and 115-131 s, Love Chains 88-97 s, Line Of Sight 0-30 s, Awake At Night 0-67 s at about 25 fps).

**Framing mix** (hand-classified, 140 shots of 1M Steps and Awake At Night):
| Wide (environment dominant) | Full body | Medium (waist up) | Close (head and shoulders) | Extreme close (eye, mouth, cloth) | Insert (clock, sign, calendar, counter) |
|---|---|---|---|---|---|
| 26% | 24% | 26% | 13% | 6% | 7% |

- **Angles:** eye level for people. About 12% low angles (looking up at big things: ships, creatures, a tall figure). About 6% straight top-down (a crossing, a bed, falling into a vortex). Dutch roll appears as a drift, not a fixed tilt.
- **Camera move inside the shot** (per-shot medians across the 6 videos):
  - **Push-in on 64-85% of shots** (pooled about 71%; 85% in the newest upload). Median rate +6 to +9% image scale per second (Soul Sucker gentler, +3.3%/s); quartiles about +1 and +13-15%/s; top 10% +12 to +25%/s.
  - Pull-out on 5-17% of shots, at about -6%/s.
  - **Locked-off shots: 0 of 590** (none drifted under 2 px per 0.1 s).
  - Net drift 33-90 px/s at 1080 wide (90th percentile 107-196 px/s).
  - Path/net ratio 1.2-1.6: a gentle handheld wander on top of the main move.
  - Roll drift above 1.5°/s on 30-65% of shots. The 10th-90th percentile is -3 to +4°/s, and boats rock at ±10-18°/s.
- **Handheld wobble amplitude** (30 fps, residual after smoothing): **1-3 px rms** on calm shots, **6-14 px rms** on action and boat shots, with direction reversals every 0.1-0.3 s (3-8 Hz). There were no impact-shake bursts.
- **Lens:** matches the game's default 70° vertical FOV on wides and mediums (about a 26 mm lens with a vertical 36 mm sensor fit). Closes are tighter (40-50 mm look). Shallow depth of field on day closes (background trees soft). No motion blur. No lens distortion.

## 5. Cutting rhythm (numbers)
| | Watcher's Knot | 1M Steps | Awake At Night* | Love Chains | Line Of Sight (newest) | Soul Sucker (2nd newest)** | **Pooled / target** |
|---|---|---|---|---|---|---|---|
| Length | 160.5 s | 112.3 s | 174.3 s | 169.6 s | 150.7 s | 177.5 s | **110-180 s** |
| Shots | 117 | 64 | 74 | 103 | 125 | 111 | 594 |
| Average shot | 1.37 s | 1.75 s | 2.01 s | 1.64 s | 1.20 s | 1.60 s | **1.54 s** |
| Median shot | 1.20 s | 1.60 s | 1.74 s | 1.31 s | 1.10 s | 1.40 s | **1.30-1.40 s** |
| 10th / 90th percentile | 0.6 / 2.3 | 0.9 / 2.4 | 0.9 / 3.1 | 0.6 / 3.0 | 0.6 / 1.8 | 0.7 / 2.7 | **0.6 / 2.6 s** |
| Longest hold | 5.4 s | 4.8 s | 8.1 s | 6.3 s | 5.5 s | 6.3 s | **5-8 s, about once a video** |
| Cuts per minute | 43 | 34 | 28 | 36 | 49 | 37 | **about 38** |
| First 30 s: average shot | 1.25 s | 1.80 s | 1.70 s | 1.94 s | **0.94 s** | 1.37 s | **1.0-1.3 s** (open fast) |
| Cuts landing on a word onset (±0.1 s) | 94% | 62% | 92% | 86% | 98% | n/m | **85%+** |
| Words per shot (median) | 4 | 5 | 6 | 4 | 4 | n/m | **4-6 (one shot per phrase)** |
| Words per second | 3.17 | 3.16 | 3.24 | 3.17 | 3.46 | n/m | **3.2-3.5** |

*16 s of Awake At Night (117-133 s) was under-sampled and left out of its cut stats. **Soul Sucker was added in pass 2 to check the rarer techniques. Seven false cuts from a ring VFX were merged back. Captions were not measured on it (n/m).

- **Distribution (first 483 shots):** 29% under 1 s, 49% from 1 to 2 s, 14% from 2 to 3 s, 7% over 3 s. Soul Sucker matches (10th/90th percentile 0.7/2.7 s).
- **Trend:** the newest upload is the fastest (1.20 s average; 0.94 s and 62 cuts/min over its first 30 s). The one before it opens at 1.37 s, so the fast opening is not settled. Build to 1.0-1.3 s per shot for the first 30 s, then 1.3-1.6 s (the `cut_plan` defaults give about 1.05 s, then about 1.45 s).
- **Hard cuts for the entire video.** No dissolves, wipes or fades. In the 25-30 fps windows (about 130 s) there were no flash frames, white or black impact frames, or inverted frames; none showed up at 10 fps elsewhere either.
- The push-in continues across a cut (shot B starts already moving), so the energy never drops.
- Longer holds (3-8 s) are reserved for one continuous reveal: a slow tilt up from cloth to a face, or a crane over a crowd.

## 6. Characters and faces (summary; full kit in `CHARACTERS.md`)
- Classic R6 block bodies with **rounded "classic" heads** and **flat ink sticker faces** (black oval eyes, thick tapered brows, no nose, red-filled open mouths). There are no 3D facial features, no lip sync and no blinks. **One expression per shot**, swapped on the cut.
- **Head = 1/4 of body height** (no hair). Hair adds 30-40% on top. Torso is 1.6 head-widths wide.
- The lead has **one signature colour nobody else wears** (in the source, the hair). Ours: the hero kid's burnt-orange.
- Clothing is **textured** (cable knit, denim, worn leather, fleece) and reads at phone size.
- Creatures and "big things" are the only shape variety: taller than people, a pale or desaturated silhouette against the saturated cast, shot from low.

## 7. Shapes and proportions
- People are boxes: torso 2x2, arms and legs 1x2 units, head about 1.2. Silhouettes come from hair and accessories (big chunky hair, hats, bags, aprons), not from body shape.
- Sets use big readable shapes: long corridors with repeated doors, ship hulls, houses with lit windows, a clock tower. Props are oversized for readability (a bell fills the frame; a clock face fills the frame).
- Diegetic text props carry the rules of the world: a number on a chest, a wall clock at midnight, a calendar with a circled date, a hand-painted sign. Each one gets its own 1-2 s insert.

## 8. Textures and materials
- **Surfaces:** smooth game plastic on skin and hair (roughness about 0.5, no subsurface). Wood planks with visible grain, stone and brick, grass, all at game-texture density.
- **Clothing is the most detailed material:** visible knit cables, denim twill, leather creases. Fabric bump shows in close-ups.
- No toon shading and no outlines on geometry. The only "ink" is in the face decal.
- Emissive materials for practicals and magic (window panes, lanterns, glowing chains, runes, ground cracks) with bloom.
- Environments are real 3D game maps (town streets, ship interiors and decks, bedrooms, forests). They are not painted backdrops, AI stills or 2D.

## 9. Environments (for our medieval stories)
- Use our town and world models: timber hall interiors, a ship or river barge, the market street, a castle corridor, a forest edge, a bedroom loft.
- Light each set with practicals: 2-4 lanterns or candles indoors, the moon plus one warm window outdoors at night.
- Every set needs **one long receding line** (a corridor, a street, a deck) for the push-ins and a top-down option (a floor, a table, a crossing).
- Daylight variant: blue sky, sun at 30-45° elevation, no haze, soft background depth of field on closes.

## 10. Animation (timing, easing, what moves)
- **The camera carries the motion.** Characters mostly hold one readable pose or emote for the whole shot (arms out, sitting, lying in bed, pointing, cowering). A slow idle is fine; no lip sync.
- **Camera easing:** linear push through the cut, so there is no ease-in at shot start. Snap pushes (+30% to +85%/s for 0.5-0.8 s) on reveal words, 1-4 per minute.
- **Character action, when it happens**, is game-physics simple: walking, running, a ragdoll tumble (camera follows at about 20 px/frame with a slight roll), falling.
- **VFX:** emissive magic (chains, runes, ground cracks glowing), a swirling vortex with streak particles, floating music notes, sparkles. VFX loop continuously while the camera pushes.
- **2D stickers** stepped at 10 fps ("on threes" at 30 fps): sleeping "Z z z" letters rising and jittering, music notes, teardrops drawn in the face decal.
- **Prop animation as a time skip:** a calendar page swings away (about 0.5 s), clock hands at midnight.

## 11. Captions and on-screen text
- **One word at a time**, lowercase as spoken (names capitalised; numbers as digits: "300", "11:20"; onomatopoeia capitalised: "Dong").
- **Size:** x-height about 48 px and a full box of 84 px including the outline, at 1080x1920. That matches **Poppins Bold at 72 px** (x-height 40 + 8 px of outline; box 78 + 8).
- **Position:** centred at x = 540, **baseline at y = 1330**. The measured glyph box including outline is y 1267-1351, 69% of the height. The daylight video sat about 50 px lower (y 1318-1400); use 1330 for everything.
- **Look:** pure white `#FFFFFF`, a thin black outline (about 4 px) and a soft black drop shadow (about 3 px down-right, 60% opacity). No coloured key words, no box, no background bar.
- **Timing:** each word appears exactly at its spoken onset and holds until the next word (median hold 0.30 s, 90th percentile 0.50 s). The text is never empty while the voice runs (captions on 99.3-99.9% of frames).
- **Animation:** a 2-frame pop-in (about 85% → 100% scale; caught on about 1 word in 3 at 10 fps). No fade, no shake, no bounce.
- **No title card**, no emoji, no arrows, circles or meme inserts, and no progress bar.
- Diegetic text (signs, chest numbers, clocks, calendars) does the explaining instead of overlays.
- **Our additions stay:** the handle `@idlemerchantrng` top left, small (Studio Bible).

## 12. Sound
Measured with the browser's Web Audio analyser while the video played silently (I could not listen; these are levels only), on 40 s of two videos.
- **A continuous bed under the voice:** the loudness floor is only 10-11 dB below the median. No 50 ms window ever falls more than 15 dB below the median, so there is no silence anywhere. Low and low-mid energy (under 400 Hz) persists in the quietest moments. It is music or tonal ambience; I cannot tell which by measurement.
- **Narration:** 3.2-3.5 words/s, measured on 5 videos (3.16-3.24; 3.46 on the newest). It runs from frame 0 to the last frame. Tight pauses: only 4-17 gaps over 0.6 s per video.
- **Effects:**
  - 7-22 low-frequency hits a minute (booms, thuds) and 15-35 high-frequency transients a minute (whooshes, chimes, clicks).
  - Effects follow on-screen events, **not** the cuts: only 8-30% of cuts have a hit within 0.15 s.
  - Onomatopoeia captions match a big effect ("Dong").
- **Mix** (`pack/post_gneef.py`): voice at full level (about -14 LUFS integrated), bed `bed_db: -10`, and each effect on its action frame (`sfx: [[file, frame, dB]]`).

## 13. Frame 0 and ending
- **Frame 0:** an establishing shot that is already moving (pushing or rising), with the first word of "In this town..." on screen at 0.00-0.09 s. Examples of the method: a low angle on a big shape at night; a street with a crowd walking at us.
- **3-frame pre-roll snap:** in 5 of the 6 videos, frames 0-2 (about 0.07 s) are a different, rolled (20-30°) or offset framing that snaps level into shot 1. It makes frame 0 look like motion and hides the loop seam. **No title card.**
- **The rule is spoken in the first 3 s**, and the first shot lasts 0.8-1.9 s (0.85 s in the newest upload).
- **Ending:** narration runs to the very last frame (a caption is on screen on the final frame of all 5 videos). There is no outro, end card or pause, so the video loops straight back into "In this town". The last shot is a wide or a reaction close. Whether the last word is clipped was not checked: write the last line so it leads back into the first.

## 14. Camera and film technique catalogue
Each row gives how often the technique appears, its measured size and timing, the story moment that triggers it, the pack call that keys it (`S` = `pack/style_gneef.py`), the post-plan key in `pack/post_gneef.py`, and **how many examples the numbers rest on**. Rates are per minute of video. Pixels are at 1080 wide. Frames are at 30 fps. Rows marked "low" were seen only once or twice: use the default, then judge it by eye. The pass-2 check video (Soul Sucker) showed no whip, plunge, tilt-up, calendar flip or flashback grade, so those stay "low". It added #31 and #32, each seen once.

| # | Technique | How often | Size / timing (default first) | Trigger | Pack call (Blender) | Post key | Based on |
|---|---|---|---|---|---|---|---|
| 1 | **Continuous slow push-in** | 64-85% of shots (pooled about 71%), about 27/min | +6.5%/s default (median +3 to +9; IQR about +1 to +15; top decile +12 to +25), linear, no ease | Every phrase | `S.push(cam, f0, f1, pct_per_s=6.5, dist=)` | `push: [[f0,f1,6.5]]` | 6 videos, 590 shots: high |
| 2 | **Snap push** | 1-4/min | +35% in 18 frames (measured +30 to +85%/s for 0.5-0.8 s), cubic ease-out | A shot that starts on a reveal or shock word | `S.snap_push(cam, f, frames=18, pct=35)` | `snap: [[f,18,35,f_end]]` | 5 videos at 10 fps, 3 at 30 fps: medium |
| 3 | **Slow pull-out reveal** | 5-17% of shots, 2-3/min | -6%/s (to -10%/s), linear | Showing scale: crowd, town, ship, creature size | `S.pull_out(cam, f0, f1, pct_per_s=6)` | `push: [[f0,f1,-6]]` | 5 videos: high |
| 4 | **Handheld micro-wobble** | Every shot | 2 px rms default (calm 1-3; action/boat 6-14), about 4 Hz, 3-8 reversals/s | Always; raise it in danger | `S.wobble(cam, f0, f1, px_rms=2.0, freq_hz=4.3)` (calibrated: 2.0 requested = 2.16 px measured) | `wobble: [[f0,f1,2.0]]` | 30 fps windows in 3 videos (about 60 shots): medium |
| 5 | **Roll drift (Dutch drift)** | 30-65% of shots (pack: every other shot) | ±2°/s default (1.5-4°/s, 2-6° per shot), level at the cut | Unease, travel, night | `S.roll_drift(cam, f0, f1, deg_per_s=±2)` | `roll: [[f0,f1,2]]` | 5 videos: medium (roll is the noisiest measurement at 54x96) |
| 6 | **Boat rock** | Boat and storm scenes only | Sine ±4°, 2.5 s period (peaks 10-18°/s) | Ship, storm, quake | `S.boat_rock(cam, f0, f1, amp_deg=4, period_s=2.5)` | n/a | 1 video: low |
| 7 | **Tilt-up reveal** | About 1 per video | Rise 1.5 m over 72 frames (measured ~830 px/s for 2.4 s), from a cloth or prop detail to the face | Introducing a character or the twist | `S.tilt_up_reveal(cam, f0, frames=72, rise=1.5, look_at=face)` | n/a | 1 clear example: low |
| 8 | **Fast lateral truck** | 2-4/min in openings | 700 px/s default (650-740) for 1-1.3 s, linear | Corridors, rows of doors, market stalls | `S.lateral_truck(cam, f0, f1, px_per_s=700, dist=)` | n/a | 2 examples (one opening): low |
| 9 | **Whip re-frame** | About 1 per video | A 3-frame jump to a tighter framing, then a push | Something notices the hero | `S.whip_reframe(cam, f, to_loc, to_look_at, frames=3)` | n/a | 1 example: low. Breaks the Bible rule: Jake's yes |
| 10 | **Plunge zoom (top-down)** | About 1 per video | +2.1%/frame (≈88%/s) for 24 frames, straight down | Falling into a portal, pit or well | `S.top_down(...)`, then `S.plunge(cam, f0, frames=24)` | `push: [[f0,f0+24,88]]` | 1 example: low |
| 11 | **Follow-tumble** | About 1 per video | Tracks the faller (~20 px/frame), +8° roll over the move | A character falls or is thrown | `S.follow_tumble(cam, target, f0, f1)` | n/a | 1 example: low |
| 12 | **Low-angle hero/creature** | 12% of shots | Camera 0.6 m high (0.4-0.8), looking up 20-35° | Big things, threat, awe | `S.low_angle(cam, target, dist=4, height=0.6)` | n/a | 140 hand-classified shots: medium |
| 13 | **Top-down** | 6% of shots | 90° down, 6 m up | Maps, beds, crossings, falls | `S.top_down(cam, target, height=6)` | n/a | 140 shots: medium |
| 14 | **Extreme close-up on a face sticker** | 6% of shots | 80 mm lens, 0.35 m from the head; the eye or mouth fills ~60% of the frame | Shock words | `S.ecu(cam, head_center, dist=0.35)`, plus push and wobble | n/a | 140 shots: medium |
| 15 | **Diegetic insert (clock, calendar, sign, counter)** | 7% of shots, 2-3/min | 0.7-1.5 s with a push; 60 mm lens | Stating a rule, a time or a number | `S.set_lens(cam, "insert")`, `S.push(...)` | n/a | 140 shots: medium |
| 16 | **Calendar page-flip time skip** | Rare | Page rotates 90° on its hinge in 15 frames, ease-in | "Days later" | `S.calendar_flip(page, f0, frames=15)` | n/a | 1 example: low |
| 17 | **Hard cut on the word** | Every transition, about 39/min (about 60/min in the newest opening) | 85%+ within ±0.1 s (3 frames) of a word onset | Every new phrase or object named | `S.cut_plan(word_timings)` | n/a (cuts are in the render) | 5 videos: high |
| 18 | **Motion-continuous cut** | Most cuts | The next shot is already moving on its first frame (no ease-in) | Keeps the energy up | `S.push` uses linear keys from f0 | n/a | 30 fps windows: medium |
| 19 | **Grade-switch flashback** | 1-2 per video | Sepia (or B&W with scan lines in the older format), hard switch on the cut, 4-6 s | Memory or "long ago" | `S.apply_look` per scene, plus post | `sepia: [[f0,f1]]`, `bw: [[f0,f1]]` | Sepia in 1 video, B&W in 1 older video: low |
| 20 | **Danger monochrome** | Rare (older format) | Full red tint over 2-4 shots | The threat appears | post only | `danger: [[f0,f1]]` | 1 older video: low |
| 21 | **Whiteout glow transition** | About 1 per video | +1 stop over the 3 frames before a hard cut (luma 145→155) | Entering magic | `S.whiteout(scene, f_cut, frames=3)` | `whiteout: [f_cut]` | 1 example: low |
| 22 | **Opening pre-roll snap** | 5 of 6 videos | Frames 1-3 rolled 25° (20-30°) or offset, then level | Frame 0 grab; the loop seam | `S.preroll_snap(cam, f_first=1, roll_deg=25)` | `preroll: true` (10° only) | 5 of 6 videos: high |
| 23 | **Soft background on day closes** | Day close-ups | Background blur, no focus pulls | Outdoor closes | Camera DOF on, f/2.8, focus on the face | n/a | 2 videos: medium |
| 24 | **Stepped 2D stickers ("Z z z", music notes)** | 1-2 per video | Redrawn every 3 frames (10 fps), drifting up 40-60 px/s | Sleep, music, magic hum | Animate, then `S.step_animation(obj, 3)` | n/a | 2 videos: low-medium |
| 25 | **Caption pop** | Every word | 85% → 100% scale in 2 frames | Word onset | n/a | `captions_gneef.json` | 5 videos: medium-high |
| 26 | **Onomatopoeia word** | Rare | Same caption style, capitalised | A big sound effect | n/a | caption on the effect frame | 1 example: low |
| 27 | **Effects on actions, not cuts** | 7-22 low + 15-35 high hits per min | Only 8-30% coincide with a cut | Impacts, magic, doors, bells | n/a | `sfx: [[file, frame, dB]]` | 2 videos x 40 s: low-medium |
| 28 | **Same-setup jump cut (expression swap)** | 0-1.4/min (≤4% of cuts) | Same framing; the face sticker changes on the cut | A reaction beat | Duplicate the shot, swap the face texture | n/a | 5 videos: high (that it is rare) |
| 29 | **Temperature smash cut** | Each scene change (4-8 per video) | Ember interior ↔ moonlit exterior, hard cut | A change of place | `S.apply_look(mood=...)` per scene | n/a | 3 videos: medium |
| 30 | **Continuous voice over cuts** | Every cut | Narration and bed never break at a cut | Always | n/a | continuous `voice` + `bed` | 5 videos: high |
| 31 | **Sound-ring VFX** | Rare (a bell or a loud call) | 2D white concentric rings expanding from the sound source, redrawn every 3 frames for about 3 s, through a slow push | A bell, horn or shout that matters | Rings as emissive circles scaled up over 9 frames, stepped with `S.step_animation(obj, 3)` | Overlay a PNG ring sequence at 10 fps | 1 video (Soul Sucker, bell): low |
| 32 | **Stepped jump-cut burst** | Rare (climax) | 3-4 cuts on one set-up, 0.2-0.5 s each, each a little tighter | The last beat before the reveal | Render one shot, then cut it with 3 `S.snap_push` steps of +10% | Cut list only | 1 video: low |

**Not used** (checked in the 25-30 fps windows, about 130 s in total, and at 10 fps over the rest of the 988 s studied): impact/flash frames, match cuts, inverted frames, speed ramps, slow motion, freeze frames, reverse, stutter, zoom-through, shape-mask or whip-pan transitions, chromatic aberration, grain, light leaks, letterbox, emoji or meme overlays, arrows or circles, shaking text.

## 15. Blender / Roblox Studio recipe
**Use the pack:** `pack/style_gneef.py` sets everything below. `pack/README.md` gives the order of work. The settings are listed here so they can be checked.

**Blender 5.3 (`S.apply_look(scene, mood)`, `S.light_rig(kind)`, `S.new_camera(framing)`)**
- **Render:** EEVEE (raytracing on), 1080x1920, **30 fps**, motion blur **off**. Cycles at 32-48 samples is fine if a scene needs it.
- **Colour management:** View `Standard`, Look `Medium High Contrast`, gamma 1.0. Exposure per mood is in the calibrated table below (ember -0.05, moon +0.15, golden +0.28, day -0.05).
- **Compositor** (node group `GNF_grade`):
  - Hue/Saturation/Value: saturation per mood (ember 1.18, moon 1.10, golden 1.32, day 1.38; 1.0 = unchanged).
  - Colour Balance (Lift/Gamma/Gain): lift and gain per mood (table below).
  - Glare `Bloom`: threshold 0.9, size 0.7, strength 0.05-0.12.
  - Vignette: Ellipse Mask 0.95 × 0.80, blur 300 px, mapped to 0.75-1.0, multiplied onto the image (edges 25% darker).
  - No grain.
- **World and lights:** see "Calibrated on our scene" below. Every mood has a coloured world fill (never black) and one key sun; ember adds 3 warm practicals and moon adds 1. Point energies are in W × 3.3² for our 3.3-units-per-metre scene. Put a visible emissive lantern or window (emission 10-20) on every practical.
- **Camera:** `new_camera()` makes a camera with sensor fit Vertical 36 mm inside a RIG empty. Moves key the rig; roll and wobble key the camera.
  - Lenses: wide 26 mm (69° vertical FOV, the game default), medium 30, close 45, insert 60, extreme close 80.
  - At 26 mm, 1° of rotation = 25.4 px at 1080 wide.
- **Materials:** skin and hair plastic (roughness 0.5); clothing Cast v2 `fabric()` with bump 0.18-0.30; wood, stone and brick from `noise_mat(..., voronoi=True)`; magic `glow_mat()` in `#E722BD` or `#E35214`. No outlines.
- **Captions:** `pack/captions_gneef.json`. Poppins Bold 72 px, white, 4 px black outline, 60% shadow at 3 px, baseline y 1330, 2-frame 85→100% pop.
  - ASS equivalent: `Style: Word,Poppins,72,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,4,3,2,40,40,570,1`
  - Event text: `{\fscx85\fscy85\t(0,66,\fscx100\fscy100)}word`.
- **Post:** `pack/post_gneef.py plan.json` handles flashback tints, whiteout, vignette, the bed at -10 dB and effects on action frames. Its push, roll and wobble options are only for shots rendered locked-off.

**Roblox Studio (if a shot is staged in-game)**
- `Lighting.Technology = Future`.
  - Night: `ClockTime = 0`, `Ambient = (25,20,35)`, `OutdoorAmbient = (70,62,110)`, Brightness 1.5.
  - Interior: `ClockTime = 20`, PointLights range 6-10, Brightness 2-3, colour (255,170,90).
- `ColorCorrectionEffect`: Saturation 0.35-0.45, Contrast 0.15-0.20, Brightness -0.03, TintColor (255,228,200) for ember or (215,220,255) for night.
- `BloomEffect`: Intensity 0.8, Size 30, Threshold 0.85.
- `DepthOfFieldEffect` on closes: FarIntensity 0.35, InFocusRadius 6, FocusDistance = subject.
- `Atmosphere`: Density 0.1-0.25, Haze 0.
- Camera: TweenService with linear easing, pushing 6.5%/s (CFrame along LookVector, or FieldOfView 70→65 over 1.5 s). Record at 60 fps and export at 30.

### Calibrated on our scene (11-26, pass 3)
Tested on main's town-square look test (`/tmp/claude-0/kits/look_test.py`: Cast v2 kids and guard, our cottages, lamp and fountain, Cycles, Standard + Medium High Contrast), measured as PIL mean L and mean HSV S.
- **Before:** the first pack rendered the frame solid red (luma 32, saturation 0.98). Three causes:
  - the world was almost black;
  - the only light was saturated 2700K points, scaled for metres when our scene is 3.3 units per metre;
  - the grade boosted it further.
- **Fixes:**
  - `UNITS_PER_M = 3.3`. All distance defaults are in metres times `U()`, and point energies are multiplied by `UNITS_PER_M**2`.
  - Every mood now has a coloured ambient world fill (never black).
  - `light_rig()` uses a low warm sun as the motivated key plus scaled practicals.
  - Milder grade.
- **Final presets** (`MOODS` in `pack/style_gneef.py`):

| Mood | World fill (colour, strength) | Key sun (colour, strength, elevation) | Practicals | Exposure | Saturation | Gain | Result (luma / sat / near-black) |
|---|---|---|---|---|---|---|---|
| ember (default) | (0.050, 0.045, 0.110), 0.65 | (1.0, 0.64, 0.38), 3.2, 16° | 3 points (1.0, 0.66, 0.40), 260 × 3.3² W, weights 1/0.6/0.4 | -0.05 | 1.18 | (1.05, 0.99, 0.92) | **77 / 0.67 / 37%** (540x960, 16 samples) |
| moon | (0.040, 0.045, 0.110), 1.15 | (0.55, 0.62, 1.0), 1.3, 38° | 1 warm point, 320 × 3.3² W | +0.15 | 1.10 | (0.92, 0.94, 1.08) | 69 / 0.61 / 39% |
| golden | (0.25, 0.38, 0.80), 0.7 | (1.0, 0.70, 0.42), 4.0, 14° | none | +0.28 | 1.32 | (1.07, 1.00, 0.88) | 94 / 0.55 / 7% |
| day | (0.22, 0.42, 0.95), 0.8 | (1.0, 0.96, 0.90), 3.5, 35° | none | -0.05 | 1.38 | (1.02, 1.00, 0.97) | 95 / 0.58 / 5% |

- **What it looks like:** ember is a lantern-lit dusk with an indigo sky, warm faces and cottages, and 37% of the frame near-black. That is the Watcher's Knot / Love Chains feel.
- **Use golden and day for daytime stories.** Their saturation (0.55-0.58) matches the source's daylight videos (0.52-0.63), not the night average.
- **Bloom:** 0.10 ember, 0.12 moon. Vignette 0.25 in all moods.
- **Final still:** `/tmp/claude-0/kits/look/final_gneef-style.png`.
- **How to call it:** `S.apply_look(scene, mood='ember')`, then `S.light_rig('ember_interior', target=(x, y, 4.0), spread=10.0)` in our units.

## 16. What changes vs our current house style (Studio Bible overrides)
| Studio Bible rule | This style | Status |
|---|---|---|
| **Camera 02:** steady cuts for the first 20-25 s, then one smooth glide | Cuts all the way through (about 39/min) and every shot pushes in | **Override: needs Jake's yes** |
| **Camera 02 / top-5 rule 3:** no swings, whips, snaps or shake | Soft handheld wobble 1-3 px rms, roll drift, about 1 whip re-frame and 1-4 snap pushes per minute | **Override: needs Jake's yes.** Safe version: wobble ≤3 px, no whip re-frames, snap pushes only |
| Gliding-part rule: no close→wide in under 3 s | Size changes happen on hard cuts | Compatible |
| **Sound 03:** no looping music bed | A continuous bed about 10 dB under the voice | **Override: needs Jake's yes.** Fallback: an effects-only ambience bed (wind, sea, crowd, fire crackle) at -10 dB, so the track is never silent |
| On screen: house caption font, keywords coloured | One white word at a time, no colour | **Override** |
| **Look 01:** frame 0 is one memorable picture with the title on it | Frame 0 is a moving establishing shot with the first caption word, no title | **Override** (put the title on the posting thumbnail and cover instead) |
| Look 01: saturation 0.55-0.65, no pastel or haze | 0.60-0.72, crushed blacks, no haze | Compatible (a little more saturated) |
| Brightness (ours about 95-100) | 70-100 (night darker) | Changes our numbers, no rule broken |
| Length: about 50-60 s or over 2 min | 110-175 s | Compatible ("over 2 min") |
| Handle top left | Not in the source | Keep ours |
| People only from the locked cast / Cast v2; rounded heads | Rounded classic heads, sticker faces | Compatible. New faces need Jake's OK (see CHARACTERS.md) |

**Our films on the same scale** (first 30 s, measured with `pack/measure_gneef.py`, 11-26):
| Film | Brightness | Saturation | Near-black share | Average shot | Shots pushing in |
|---|---|---|---|---|---|
| Crown Stag Part 2 (approved house look) | 82 | 0.56 | 30% | 1.9 s | 50% |
| Egg Army Day 1 | 113 | 0.40 | 13% | 2.1 s | 36% |
| Dungeon Called Me Master | 56 | 0.32 | 50% | 1.1 s | 15% |
| **This style (target)** | **60-100** | **0.60-0.72** | **30-45%** | **1.2-1.6 s** | **70%+** |

Crown Stag is the closest; the style needs more saturation, more pushes and faster cuts. Egg Army is too bright and flat. Dungeon is dark, but its colour is too grey.

## 17. Do / Don't checklist
**Do**
- [ ] Cut on the word for the whole video: about every 1.0 s for the first 30 s, then every 1.2-1.5 s; 4-6 words per shot.
- [ ] Push in on at least 70% of shots (+5 to +10%/s). No locked-off shot anywhere.
- [ ] Add a 1-3 px wobble and a 1-3° roll drift to most shots.
- [ ] Light every shot from one motivated source. Crush the blacks, keep 30-45% of the frame near-black, saturation 0.60-0.72.
- [ ] Show one white lowercase word at a time, Poppins Bold 72 px, baseline y 1330, with a 2-frame pop (`pack/captions_gneef.json`).
- [ ] Give every rule its own diegetic insert (sign, clock, number on the chest, calendar).
- [ ] Give the lead one signature colour nobody else wears.
- [ ] Open on a moving wide with the first word already on screen. End mid-line for the loop.
- [ ] Keep a continuous bed (or an ambience bed) under the voice. Place effects on actions, not cuts.
- [ ] Narrate at 3.2-3.5 words/s (Studio Bible's 3.4-3.9 also fits).
- [ ] Run `pack/measure_gneef.py` on the result and fix anything marked OFF.

**Don't**
- [ ] No title card, emoji, arrows, meme inserts, coloured keywords or caption boxes.
- [ ] No flash or impact frames, speed ramps, slow motion, freeze frames, dissolves or wipes.
- [ ] No hazy, pastel or flat-lit shots. No lifted blacks.
- [ ] No lip sync or 3D facial features. One face per shot.
- [ ] No more than one hold longer than 5 s per video.
- [ ] Never copy the source's stories, characters, hair and colour combinations, names or titles.

## 18. Style test (build this first: about 12 s, 10 shots, no full film)
**Goal:** show Jake the look, the camera and the cutting at phone size before committing a film.

- **Voice:** the first 3 lines of an approved script, already voiced (about 40 words at 3.4-3.5 words/s, so about 12 s).
- **Shot list:** run `S.cut_plan()` on it. It should give about 10-12 shots averaging 1.0-1.2 s. Stage them like this, in order:

| # | About | Framing / mood | Technique to prove | Pack calls |
|---|---|---|---|---|
| 1 | 0.0-1.2 s | Wide, low angle on the town or a big shape at night (moon) | Frame-0 pre-roll snap, moon grade, push | `preroll_snap`, `low_angle`, `push`, `wobble` |
| 2 | 1.2-2.2 s | Medium of the hero in a lantern-lit hall (ember) | Ember grade; signature colour; face sticker legible | `place`, `push`, `roll_drift(+2)` |
| 3 | 2.2-3.0 s | Insert of the rule prop (notice board, sign, mark) | Diegetic insert | `set_lens('insert')`, `push` |
| 4 | 3.0-4.0 s | Full, corridor or market row | Fast lateral truck at 700 px/s | `lateral_truck` |
| 5 | 4.0-4.6 s | Close of the hero, shocked face | Snap push on the reveal word; expression swap on the cut | `snap_push` |
| 6 | 4.6-5.6 s | Extreme close-up on the eye or mouth sticker | ECU at 80 mm | `ecu`, `wobble` |
| 7 | 5.6-7.0 s | Wide crowd (villagers, offset idles) | Pull-out reveal | `pull_out(-6)` |
| 8 | 7.0-8.0 s | Top-down on a table or map | Top-down | `top_down`, `push` |
| 9 | 8.0-10.5 s | From a cloak hem up to a guard's or creature's face, low | Tilt-up reveal (the one hold) | `tilt_up_reveal` |
| 10 | 10.5-12 s | Close reaction, a new expression; end mid-word | Loop ending | `push`, `roll_drift(-2)` |

- **Captions** from `captions_gneef.json`. The sound is the bed (or an ambience bed) at -10 dB plus 2-3 effects on actions, not on cuts.
- **Compare side by side on a phone, same size:**
  1. the test;
  2. the first 12 s of a reference reel (Line Of Sight or The Watcher's Knot, links in Evidence), for feel only, never as material;
  3. the first 12 s of our Crown Stag Part 2.
- **Pass if** `measure_gneef.py test.mp4` shows:
  - brightness 60-100, saturation 0.60-0.72, near-black 30-45%;
  - average shot 0.9-1.3 s, at least 7 of 10 shots pushing in;
  - and by eye: every face reads in 0.3 s, the wobble does not feel shaky, and the captions never cover a face.
- **Jake judges three things:**
  1. Does it feel like the reference's energy?
  2. Is the wobble and roll acceptable under his no-shake rule? If not, set wobble to 0 and roll to ±1°/s.
  3. Music bed or ambience bed?

## 19. Evidence
**Videos studied** (views read from the channel's Shorts tab on 11-26-2026):
| Title | URL | Views | Format | How it was studied |
|---|---|---|---|---|
| The Watcher's Knot | https://www.youtube.com/shorts/AFRNUv0a8SI | 8.6M (posted Nov 17, 2026) | new | Every 0.1 s for 160.5 s; 30 fps at 0-6.5 s and 115-131 s; 19 stills; audio levels 0-40 s |
| In This Town, You Get 1,000,000 Steps | https://www.youtube.com/shorts/gHBRuoHok6s | 36M (channel #1) | new | Every 0.1 s for 112 s; 15 stills; audio levels 0-40 s |
| Never Be Caught Awake At Night | https://www.youtube.com/shorts/J0OQXSo1chk | 35M (channel #2) | new | About 25 fps for 0-67 s; 10 fps for 67-174 s; 17 stills |
| Love Chains | https://www.youtube.com/shorts/2U7jPU0kw6Q | 8.6M (recent) | new | 10 fps for 169.5 s; 30 fps at 88-97 s; 18 stills |
| Line Of Sight | https://www.youtube.com/shorts/27ElpHj_aDw | 2.4M (newest upload) | new | 30 fps for 0-30 s; 10 fps for 30-150.7 s; 12 stills |
| Soul Sucker (pass 2) | https://www.youtube.com/shorts/l6uyKGKQALQ | 2.9M (2nd newest) | new | 10 fps for 177.5 s, to check the rarer techniques |
| In This Town, You Are Not Allowed To Speak | https://www.youtube.com/shorts/crvPRFMpKLA | 5.8M | older | Every 0.1 s for 42.9 s; 15 stills (contrast case: two-line captions, pull-outs, daylight suburbs) |

**Older format, for contrast** (Not Allowed To Speak, 42.9 s): 22 shots, average 1.95 s, 1.3 caption changes/s, and two-line captions (a small lowercase line plus a big UPPERCASE coloured key line in green, magenta, blue, red or orange). 77% of its shots pull out at about -10%/s. Classic yellow-skin avatars, red danger tint and a B&W flashback. The channel's current hits all use the new format, so this spec follows the new one.

**Analysis time:** pass 1 10:40-11:34 CST on 11-26 (54 min, 6 videos, 810 s); pass 2 11:40-11:58 (style pack, spec tightening, Soul Sucker added: 7 videos, 988 s in all).

**Method.** Frames were drawn from the page's video element into a canvas (54x96 strips for timing and colour, 432-540 px stills for looking at). Cuts came from frame-difference peaks; camera moves from dense optical flow with a similarity fit (zoom, roll, pan); captions from a white-with-black-outline mask in the lower band; palette from k-means in Lab; sound from a Web Audio analyser at 40 Hz. All competitor frames and stills were deleted after the analysis.
