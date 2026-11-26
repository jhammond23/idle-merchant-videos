# Build style: Bright Snap Cut (`bright-cut`)

**Summary.** Bright midday Roblox-town look, cut to the voice about once every 0.7 seconds, with a camera that never stops drifting. Plain blocky avatars with flat cartoon face decals stand in clean, high-key places: white walls, pale stone, blue sky, green grass. Colour stays light and only medium-saturated. Strong colour shows up only as small accents: one red keyword, one "power" colour. Every phrase of narration gets its own picture, and most get two or three. Each shot is a slow, constant-speed push-in, pull-out or slide, and the cut comes while the camera is still moving. The video opens on a motion-blurred whip that settles within about 5 frames. Captions are small, white and outlined, sit in the lower middle, and pop in with an overshoot. Big moments get a crash push-in to an extreme close-up, a face swap and a few frames of micro-shake. Power moments get a colour-tint fade, a solid-colour flash or an RGB-glitch transition. A soft music bed runs under a fast single narrator (3.5 to 4.2 words a second). The video is 45 to 55 seconds long, has no title card and no end card, and the last word lands in the final 0.3 seconds. Builder code (Blender look, lights, every camera move, cut and caption plans, ffmpeg post, a checker) is in `pack/` (start with `pack/README.md`). The style test is section 17. This file holds the method only. We use our own medieval "In this town" stories and our own characters.

Inspired by the method of: cannonanimates (YouTube @cannonanimates). Studied Thu 11-26, 10:40 to 11:35 AM (about 55 minutes, almost all of it frame-level measurement in the browser). Pass 2 (11:40 to 11:50 AM): builder pack, spec tightened, two more openings checked. Pass 3 (11:59 AM to 12:06 PM): look calibrated on our town-square scene.

---

## 1. Look in one picture
A sunny noon street in a toy town. The hero stands waist-up in the middle third, facing the camera and pulling a face. White plaster and pale stone are behind him, the sky above is a clean cyan-blue with fat white clouds, and the shadows are soft but real. Five words sit across his belt line in white block capitals with black outlines, and one word is red. The camera is creeping toward his face. Before you can study the frame it cuts to a close-up of whatever he just said.

## 2. Palette (measured, adapted for medieval)
Measured with k-means over 1,269 frames from 4 daylight videos (Lab, k=12). Mean brightness 145 of 255; mean HSV saturation 0.35; only **8% of pixels are vivid** (S > 0.67, V > 0.59). The base is pale and cool. Accents are small and primary.

| Hex | Measured share | Use in our builds |
|---|---|---|
| `#8BD0F4` | sky (median sky pixel) | Clear midday sky. World/sky colour. |
| `#E2E9E9` | 13% | Cloud white, plaster walls, castle whitewash, highlights. |
| `#C2D2E3` | 19% | Pale cool stone and walls in daylight; the general "air" colour. |
| `#A2ABBB` | 11% | Cobbles, stone in shade, grey uniforms and tabards. |
| `#4C586A` | 6% | Slate roofs, iron, armour shade, deep window glass. |
| `#13121B` | 8% | Ink: hair, boots, outlines, caption stroke. The darkest value (frame 5th percentile is about 32). |
| `#D4B588` | 6% | Light timber, straw, dirt paths, bread and market goods. |
| `#874137` | 7% | Brick, roof tiles, leather, red-brown cloth. |
| `#76C784` | 6% | Sunlit grass and hedges. |
| `#4E8F52` | 3% | Grass and tree shade. |
| `#E0262A` | under 1% (accent) | **Caption keyword red**: danger and emotion words, the hero's single bright garment, the "hit" flash. |
| `#27C4D0` | accent | **Power colour** (example: cyan). Magic tint, beam, aura and the keyword of the power word. Pick ONE power colour per story. |
| `#D4BE43` | accent | Gold: crowns, coins, sparks. |

Rules: the vivid accents together cover no more than about 10% of any frame. The power colour and the red keyword are the only things that pop.

## 3. Light and grade
- **Time of day:** midday sun (4 of the 5 videos). Night is used only when the story is about night (the Tag video: mean brightness 110, and 25 of its 176 shots are dark, under 70).
- **Brightness:** shot mean luma 131 to 154 on 0 to 255 (per video: 142, 148, 154, 131). Frame percentiles: 5th about 32, 95th about 229. Whites nearly clip and blacks are real, so the image uses the full range and is high-key.
- **Contrast:** luma standard deviation about 62 inside a frame. Hard-edged objects are crisp.
- **Saturation:** HSV mean 0.29 to 0.41. This is NOT our 0.55 to 0.65 house look.
- **Shadows:** soft-edged but present (sun angle about 3 to 5 degrees). Ambient occlusion in corners. No black crush.
- **No** fog, haze, god rays, vignette (corners are brighter than the centre: ratio 1.22), film grain, light leaks, letterbox or colour-graded teal-orange. Bloom is barely there: a slight glow on white sky (Blender 5: Glare node Fog Glow, threshold 1.0, size 0.5, strength 0.12; see `apply_look`).
- **Halo:** a 2 to 4 px light rim around characters, from heavy sharpening or upscaling. It's optional. If you want it, use `unsharp=5:5:0.8` in the final ffmpeg pass.

## 4. Camera and framing (numbers from 30 fps motion analysis of Phase and Borrow)
- **Lens (estimated from perspective):** wides look like Roblox's default 70 degree vertical field of view (about 26 mm on a 36 mm vertical sensor). Mediums about 35 mm, close-ups 50 mm, extreme close-ups 70 to 85 mm. No visible lens distortion. Depth of field is shallow only in close-ups (the background softens).
- **Framing mix, measured shot by shot on Material (82 shots):** medium (waist-up to full body, facing camera) 43%. Close-up of a face, an object or an insert (a hand, a crack, a TV, a brick) 27%. Wide establishing, or a high or low angle on a building or street, 23%. Over-the-shoulder 4%. Full-frame effect burst 4%. The other videos, judged by eye from their contact sheets, look the same: about 40% medium, about 25% close, the rest wide, group and low-angle creature shots. Eye level is the default. Creatures are filmed from their own height or lower.
- **The camera moves in about 85 to 90% of shots.** Only 10 to 16% of shots are static.
  - Push-in in 42 to 60% of shots. Pull-out in 31 to 42%. Lateral track or pan in the rest.
  - Median zoom speed **16 to 22% subject-scale per second**. Median drift **170 to 205 px/s** at 1080 wide (25% of shots slower than 95 px/s; 10% faster than 585 px/s).
  - **Constant speed, cut mid-motion.** Motion in the last 20% of a shot is equal to or higher than in the first 20% (Phase 7.6 vs 5.1 px/frame; Borrow 19.3 vs 7.5). There's no ease-out to a stop.
- **Snap-starts:** 34 to 43% of the fast frames (60 px or more per frame) fall within 0.1 s after a cut. A shot often begins with a 1 to 3 frame lurch, then drifts.
- **Rolls:** 5 to 7 short rolls per video (6 to 9 a minute), 1.5 to 2 degrees a frame for 3 to 5 frames, 4 to 7.5 degrees total. Big 90 to 180 degree rolls only when a character flips, falls or passes through something.

## 5. Cutting rhythm
| Measure | Value |
|---|---|
| Average shot | **0.56 to 0.94 s** (pooled median about **0.7 s**) |
| Median shot | 0.67 to 0.80 s |
| Shortest 10% | 0.13 to 0.37 s (flash inserts) |
| Longest shot | 1.6 to 2.6 s (no shot is ever longer than 2.6 s) |
| Cuts per minute | 64 to 108 (Phase 89, Borrow 64, Material about 108, Spirit Beasts about 97, Tag 74) |
| Shots of 0.4 s or less | 8 to 20% |
| Shots of 1.5 s or more | 3 to 15% |
| Words per shot | 2.3 to 3.4 |
| Shots per narration phrase | 1.5 to 2.6 |
| Phrases that start on a cut | **95 to 97%** (Phase, Tag) |
| Cut to nearest word onset | median **+0.6 to +1.6 frames** (the cut lands on the word). 55 to 72% of cuts are within 0.1 s of a word onset (Tag: 91% within 0.15 s) |

How to cut: the first word of every phrase gets a new shot. Inside a phrase, cut again on the stressed noun or verb ("a **rabbit**", "the **mark** moves"), so the picture always shows the word being said. Cut size changes with each cut (medium, insert close, medium-wide, reaction close).

## 6. Characters and faces (full kit: `CHARACTERS.md`)
Roblox-style blocky avatars with rounded-edge block heads and flat 2D face decals. Two registers:
1. **Line decals** for wide and medium shots: dot or oval eyes, arc eyes, thin-line mouths, black lines.
2. **Comic punch faces** for close-ups: big round white eyes with thick outlines and tiny pupils, heavy brows, hatch marks, open mouths with teeth or tongue.

The face swaps on the cut, not inside the shot. There's no lip sync and no blinking. A typical video has 8 to 20 distinct people, told apart by hair silhouette, one outfit colour and an accessory. Creatures are detailed, realistic-furred models at true scale next to the blocky people.

## 7. Shapes and proportions
- Blocks with rounded edges. The head is about 0.22 of body height (hair excluded) and about 0.28 with hair. Shoulders are about 1.4 to 1.7 head-widths. Arms and legs are straight rectangular blocks the same width as half the torso. Hands are simple mitts or 4-finger cartoon hands.
- Environments are boxy: rectangles, cylinders, beveled edges. The silhouettes are readable at phone size.
- Creatures are the only organic, high-detail shapes (fur, anatomy). This contrast is the point.

## 8. Textures and materials
- People: smooth plastic skin (low specular). Printed 2D clothing on the blocks: blazers, hoodies, graphic tees, denim with a visible diagonal weave, sports kits. Glossy mesh hair with painted strand texture and a specular highlight.
- Environments: Roblox-style materials. Smooth plastic walls, concrete, wood planks with real grain, brick, glass with reflections, textured grass, diamond-plate metal. They're clean, unweathered and well-lit.
- Power states: a material swap on the whole character. Translucent glowing cyan (ForceField-like), solid red silhouette, brick, steel plate, ice/glass.
- No toon shading, no outlines on 3D geometry, no painted backgrounds, no AI stills. Everything is a real 3D set.

## 9. Environments
Built game maps of ordinary places. Their videos use schools, homes, streets, gyms, parks, offices and shops. For us: **the medieval town at noon**. That means the market square, the castle gate and courtyard, tavern interior, smithy, a cottage bedroom, the training yard, the forest path and the throne room with windows letting in daylight. Sets are bright, tidy, lightly propped and open to the sky where possible. There's usually one clear landmark per location (well, gate, clock tower, banner) so a 0.7 s shot reads at once. Night only when the story says night. Then use a purple-navy sky (`#1B1830` to `#3A3358`), warm window light and the same fast cutting.

## 10. Animation
- **People:** game-style emotes and clips: idle sway, walk, run, jump, wave, point, crouch, sports and work actions (juggling, cooking, playing). The timing is snappy (key poses every 6 to 12 frames, linear in-betweens, rigid limbs; estimated by eye from 30 fps strips, not measured per clip). Poses are held while the camera moves. Background people idle, desynchronised.
- **Faces:** swap per shot (decal change), never animated inside a shot. On a shock beat the face swaps mid-push (see technique T4).
- **Creatures:** looping idle (breathing, tail, head turn), real walk cycles, mouth open on a reveal.
- **Effects:** particles for magic (sparks, glitter, lightning bolt, beams), simple explosions, debris cracks on landing, flying props (eggs, balls, papers) aimed at the lens.
- **Everything moves at once:** subject, camera and particles. A frame with nothing moving is rare: no freeze frames were found in 5 videos.

## 11. Captions and on-screen text
- **Font look:** heavy geometric sans, all caps, white fill, black outline 4 to 6 px plus a 1 to 2 px soft shadow. Free match: **Montserrat ExtraBold** (fallback: Poppins Bold).
- **Size:** cap height 30 to 40 px at 1080x1920 (about 46 to 56 px font size), so they're **small**. Text width is 50 to 88% of the frame. One line, or two if the phrase is long.
- **Position:** centred horizontally. Baseline at **66 to 74% of frame height** (y about 1270 to 1420).
- **Content:** the whole spoken phrase (3 to 7 words), not word-by-word. Ellipsis-style ".." on trailing phrases.
- **Keyword colour:** one word per caption at most, coloured by meaning. Red `#E0262A` for danger, emotion and results ("DEADLY", "GONE", "STRONGER"). The story's **power colour** for the power word (for example a cyan "PHASE"). Yellow `#F2D33A` for playful words ("BOUNCY").
- **Animation (measured at 30 fps on Phase and Material):** a damped spring. **In:** 40 to 50%, then 115 to 120% at frame 3 (long captions spill past the frame edges), 90% at frame 6, settled at 100% by frame 9. **Out:** a swell to 110 to 120% over the last 3 to 5 frames, then a shrink to about 40% over 2 to 3 frames. The next caption pops in on the next frame. **The caption changes 1 to 2 frames before the picture cut.** No typing effect, no bounce per word, no shake.
- **No title card, no emoji, stickers, arrows or circles.** There are a few in-world inserts (a TV news screen, a clock, a sign) that carry story information.
- House rule kept: handle `@idlemerchantrng` top left.

## 12. Sound
- **Narrator:** one calm male storyteller voice, **3.5 to 4.2 words a second** (Phase 4.2, Borrow 3.6, Spirit Beasts 3.5, Material 3.9, Tag 3.8). Pauses are short. Each video has 27 to 39 gaps longer than 0.45 s, and 5-second windows range from 2.8 to 4.8 words a second.
- **Music bed (measured on Phase, Borrow and Material):** continuous. Word gaps are only 3.6 to 5.5 dB quieter than speech (about -24 vs -20 dBFS RMS). The 20 to 150 Hz band is identical in speech and gaps (about -48.5 dB), so a steady low-end pulse runs under everything. Its period is about 0.99 s (60/120 BPM).
- **Effects:** whooshes on transitions and whip-ins, impacts on landings and explosions, a camera-flash click on the white flash, and power hums. Strong transients (a jump of 30 dB or more in the 6 to 16 kHz or 20 to 150 Hz band) come **20 to 24 times a minute, one every 2.5 to 3 s**. **82 to 88% of them land on a cut** (Phase, Material; Borrow 33%), so roughly one cut in four gets a whoosh or hit. Examples in Phase: 2.82, 4.55, 5.45 and 6.18 s. 52 to 71% of all cuts coincide with some audio transient (a word onset or an effect).
- **For us:** the voice speed fits our mix (aim for 3.8 to 4.0 words a second). The music bed conflicts with Jake's "no music bed" rule (11-23), so it's **off by default**. If Jake switches it on for this style: a soft 120 BPM sub-pulse at about -8 dB under the voice. Effects are always on.

## 13. Frame 0 and ending
- **Frame 0 (all 7 openings checked):** a motion-blurred whip-in. Five were checked at 30 fps (Phase, Material, Spirit Beasts, One Word, Gold) and two at 10 fps (Tag, Borrow). The blur is heavy and directional, usually horizontal, sometimes a vertical tilt. The first caption is already on screen mid-pop. The image settles into the first composition within **3 to 7 frames (0.1 to 0.23 s)** and keeps drifting, usually into a push-in that lasts until the first cut.
- **First second:** the hero and the rule. The first cut comes at 0.9 to 1.6 s (One Word 1.32 s, Gold 1.35 s). In 2 of 7 openings (both power stories) the first line ends with an RGB-glitch transition (T7) at 1.2 to 1.5 s. The other 5 use a plain cut.
- **Ending:** the last word lands in the final **0.1 to 0.3 s** (Phase 47.04 of 47.30 s; Borrow 55.16 of 55.32 s; Tag 142.0 of 142.1 s). The last shot is still moving (a push or a walk), and it can be very short (Gold's last shot starts 0.25 s before the end). No end card, no call to action, no fade, so the loop restarts straight into the whip-in. (Our sponsor edition still adds its approved ending after the story.)

## 14. Camera and film technique catalogue
Measured on Phase, Borrow and Material (stepped at 30 fps around every cut and fast moment) plus Spirit Beasts and Tag (10 fps). "Per minute" is averaged over the videos that use it. Pixel sizes are at 1080 px frame width. Blender recipes assume 30 fps, a 36 mm sensor with Auto fit on a 1080x1920 frame (horizontal field of view 32 degrees at 35 mm, so 1 px is about 0.03 degrees).

| # | Technique | What it is | Frequency | Timing (frames @30) | Size | Story trigger | Recipe |
|---|---|---|---|---|---|---|---|
| T1 | **Breathing push / pull** | Every shot slowly dollies in (or out) at constant speed and is cut mid-move | 85 to 90% of shots (about 60 to 90 a minute) | the whole shot (12 to 30 f) | 16 to 22% scale/s median; 6 to 75% over one shot | default for every shot; push on tension, pull on "everyone else" reveals | Blender: 2 keys (start/end), **Linear** interpolation. Dolly along the view axis about 0.5 m/s at 3 m (35 mm). ffmpeg fallback: `zoompan=z='1+0.0067*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30` |
| T2 | **Lateral drift / slide** | Camera slides sideways past the subject | about 15% of shots | whole shot | 170 to 205 px/s median (0.3 m/s at 3 m, 35 mm) | walking, crowd rows, two-face pans | Linear X translation, 0.2 to 0.4 m/s. Keep the subject in the centre third |
| T3 | **Whip-in on frame 0** | The video starts mid-whip with heavy motion blur, decelerating into frame 1's composition | 7 of 7 openings (once each) | blur on f0 to f3, settled by f3 to f7 | f0 blur about 60 to 100 px, horizontal or vertical | hook | Blender: `whip_in(cam, 0)`: yaw 30 degrees (25 to 35) over f0 to f5, Exponential ease-out, motion blur shutter 1.0 on f0 to f3. ffmpeg (`post_bright_cut.py` "whip_in"): `dblur=angle=0:radius=60:enable='lte(n,1)',dblur=angle=0:radius=25:enable='between(n,2,3)'` plus a whoosh starting at -2 f |
| T4 | **Crash push-in to extreme close-up plus face swap** | Continuous fast push from medium to eye-filling extreme close-up. The face decal swaps to a shocked or angry comic face on the last third | 1 to 2 per video | 20 to 26 f (0.7 to 0.85 s) | about 2.5x scale; speeds up into the end | the punchline or shock beat ("he was the cause") | `crash_push(cam, f0, f1, factor=2.5)`: dolly with Quadratic **ease-in** (speeding up). Swap the face texture at the returned `swap_frame` (65% of the move). Add `shake()` for the last 6 f |
| T5 | **Axis punch-in cut** | A cut from wide to close (or close to extreme close) on the same line of sight, for example tower, then clock face | 1 to 3 per video | 0.3 to 0.6 s per step | each step 2 to 4x | naming an object or a time | `axis_punch(cam, factor=2.5)` makes the second camera on the same axis. Same drift direction. Cut on the stressed syllable |
| T6 | **Micro-shake (impact)** | A few frames of small position jitter | 1 to 2 per video (about 2 a minute); no constant handheld shake | 4 to 8 f, then off | 4 to 10 px, 4 to 6 Hz | shock face, landing, explosion | `shake(cam, f0, f1, px_at_1080=8, freq=5)`: Noise F-modifiers on rotation X and Z, Scale = 30/freq = 6, Strength = 2 x amplitude (8 px at 35 mm = 0.0042 rad, so strength 0.0084), Restrict Frame Range with 2 f blend. ffmpeg (`post_bright_cut.py` "shake"): crop with sine offsets inside `between(n,a,b)` plus a constant 2.2% crop |
| T7 | **RGB-glitch transition** | Colour channels split apart (magenta/green and yellow/blue fringes), growing until the cut | 2 of 7 videos (both power stories), once, at the end of the first line (1.2 to 1.5 s) | 6 to 8 f before the cut, 1 to 2 f after | offsets 0 to 25 px | power activates, "he could…" reveal | Do it in post: `post_bright_cut.py` "rgb_glitch" {cut, pre 7, post 2} chains `rgbashift` 6, then 12, then 24 px in three frame windows. Add a glitch SFX on the cut |
| T8 | **Power tint fade** | The whole character turns translucent glowing (one power colour) and fades back | 6 to 14 per power video (Phase about 12) | in 3 to 5 f, out 10 to 15 f | full body | using the power | Material Mix to an Emission (power colour, strength 2) plus Alpha 0.6, keyed. Roblox: Highlight FillColor, FillTransparency 0.3 |
| T9 | **Solid-colour hit flash** | The subject goes flat solid red (or the power colour) for a few frames. In a transformation, the new material is revealed right after | Tag 1 to 2; Material about 12 (about 15 a minute) | 1 to 3 f for a hit; 3 to 5 f before a material reveal | subject silhouette | a touch, hit, transformation | Override the subject's material with Emission `#E0262A` strength 1 for 2 to 4 f, then cut the new material in |
| T10 | **Through-surface wipe** | The camera passes through a wall or floor. The surface fills the frame for 2 to 3 f, then the camera is in the new space (sometimes upside down) | 2 in Phase | 2 to 3 f fill | full frame | going through or under something, entering a room | Animate the camera through a plane. Set the cut at the full-frame surface frame. A thud or whoosh SFX |
| T11 | **Follow roll** | The camera rolls with a falling or flipping subject, 90 to 180 degrees, landing in an upside-down view | 2 to 3 per video (when motivated) | 6 to 12 f | 90 to 180 degrees | falls, flips, phasing down | Rotate the camera Y-axis keyed linearly. Hold the upside-down for up to 0.5 s |
| T12 | **Small roll / dutch** | A short roll during a shot | 5 to 7 per video | 3 to 5 f | 4 to 7.5 degrees | unease, action | 1.5 degrees a frame on Y rotation, then hold |
| T13 | **White flash transition** | A camera-flash or explosion whites out the frame, then fades into the next shot | about 1 per video (Borrow, Material) | 1 f at 85 to 95% white, 3 f fade | full frame | camera flash, explosion, magic burst | ffmpeg: `fade=t=in:st=T:d=0.1:color=white` on the incoming shot. Flash SFX |
| T14 | **Impact burst frames** | An explosion or light burst fills the frame with yellow-white | 2 to 4 per action video | 3 to 6 f | over 60% of frame | explosions, power hits | 3D explosion sprite or particle burst near the lens. Bloom up for those frames |
| T15 | **Snap-start** | The shot begins with a 1 to 3 f lurch, then drifts | 34 to 43% of fast frames sit 0 to 3 f after a cut | 1 to 3 f | 60 to 105 px/frame | most action cuts | Start the camera move 2 f before the cut-in point and drop those frames |
| T16 | **Cut on the word** | Picture cut lands on word onsets | 55 to 72% of cuts within 3 f of a word onset; 95% of phrases start on a cut | +0.6 to +1.6 f after the onset | n/a | always | Cut list from ElevenLabs word timings: every phrase start plus stressed nouns |
| T17 | **Flash inserts** | Very short object shots (a mark, a clock hand, a sign) | 8 to 20% of shots | 4 to 12 f | close or extreme close | naming an object | 0.15 to 0.35 s inserts. Push 10 to 20% inside |
| T18 | **Object to lens** | A ball, a creature or debris flies at the camera and fills 40 to 60% of frame | 1 to 3 per video | 6 to 15 f | 40 to 60% of frame | action beats | Animate the prop toward a 24 mm camera |
| T19 | **Low angle on creature** | Camera at creature height (0.3 to 0.6 m), tilted up 10 to 25 degrees, slight push | every creature intro | whole shot | creature fills 50 to 80% of height | creature reveals | 24 to 26 mm, camera Z 0.4 m |
| T20 | **Over-the-shoulder** | Back of a head or hair fills 30 to 50% of frame in the foreground | about 2 to 4 per video | whole shot | 30 to 50% | conversations, "watching" beats | Foreground head 0.5 m from a 35 mm lens |
| T21 | **Through-glass foreground** | Shot through a windshield, window or door frame with reflections and haze | a few per video | whole shot | foreground frame plus reflections | inside vehicles, peeking | Glass plane with 0.1 to 0.2 reflection. The window frame is out of focus |
| T22 | **Shadowed eyes** | The top of the face is lost in a dark band under the hair, mouth flat | about 1 per video | 1 to 2 shots | upper 40% of the face | ominous reveal | Face decal variant with a black gradient over the eyes, or a spot light blocked by a hair card |
| T23 | **Highlight outline** | A thin light outline (cyan-white) on the chosen character or pair | Spirit Beasts | whole shot | 2 to 3 px | "this one is special" | Roblox Highlight OutlineColor `#BFF3FF`, FillTransparency 1. Blender: Freestyle on that collection only |
| T24 | **Character exits, camera stays** | The subject walks out of frame and the shot holds on the empty set for 3 to 6 f before the cut | seen in Phase and Gold, about 1 per video | 3 to 6 f | n/a | someone leaves or disappears | Keep the camera drifting. Cut after the exit |
| T25 | **Caption spring pop** | See section 11 | every caption (about 30 to 40 per video) | in: 45 to 118% (f3), 90% (f6), 100% (f9); out: swell to 115% over 3 to 5 f, then 40% over 2 to 3 f; leads the picture cut by 1 to 2 f | caption | every phrase | ASS: `{\fscx45\fscy45\t(0,100,\fscx118\fscy118)\t(100,200,\fscx90\fscy90)\t(200,300,\fscx100\fscy100)}`; out: `\t(D-230,D-90,\fscx115\fscy115)\t(D-90,D,\fscx40\fscy40)` (D = caption duration in ms) |
| T26 | **Keyword colour** | One word coloured red or the power colour | about 1 in 4 captions | with the caption | one word | danger or power words | ASS `{\c&H2A26E0&}` (red, BGR order) |
| T27 | **In-world info insert** | A TV screen, clock, poster or warning sign carries story info | 1 to 3 per video | 0.3 to 1 s | full or medium | time passing, news | For us: a town crier's board, a bell tower clock, a wanted poster |
| T28 | **Snap zoom on transformation** | A very fast push, 1.8 to 2x in 3 to 5 frames, landing on the moment the subject changes | 1 to 3 per power video | 3 to 5 f | 1.8 to 2x | transformation, power-up | Dolly or focal length 35 to 70 mm over 4 f, linear. Pair with T9 and an impact SFX |

**Looked for and NOT used:** freeze frames (0 found in 5 videos), speed ramps or slow motion (none), reverse or stutter repeats (none), black or inverted impact frames (none), vignette pulses, letterbox, film grain, light leaks, lens flares, chromatic aberration outside T7, meme inserts, emoji, arrows and circles, title cards, end cards, fades to black.

### Pack mapping and how sure we are
"Seen in" counts the 7 videos checked: the 5 studied in full, plus the openings and endings of One Word (16M) and Gold (9.8M) checked in pass 2. **Low** means fewer than 3 examples: use it, but don't treat the frequency as a rule.

| # | Pack (`pack/`) | Seen in | Confidence |
|---|---|---|---|
| T1 push/pull | `push`, `pull` | all 7, every shot | high (30 fps motion fit, 2 videos; visual on all) |
| T2 drift | `drift` | all 7 | high |
| T3 whip-in | `whip_in` + post `whip_in` | 7 of 7 openings | high |
| T4 crash push + face swap | `crash_push` (+ `shake`) | Phase (30 fps); similar push in Material | **low** (2 examples) |
| T5 axis punch | `axis_punch` | Tag, Material | medium |
| T6 micro-shake | `shake`, post `shake` | 1 of 3 flagged shots was real shake | medium (size measured on 1 clip) |
| T7 RGB glitch | post `rgb_glitch` | Phase, Material | **low** (2 of 7) |
| T8 power tint | `power_tint` | Phase (about 12), Material (material swaps) | medium |
| T9 hit flash | `hit_flash` | Tag, Material (about 12) | medium |
| T10 through-surface | `fly_through` | Phase only (twice) | **low** |
| T11 follow roll | `follow_roll` | Phase, Material | **low** |
| T12 small roll | `roll` | Phase, Borrow (30 fps fit: 5 to 7 each) | medium |
| T13 white flash | post `white_flash` | Borrow (camera flash), Material (explosion) | **low** |
| T14 impact burst | staging (particles) | Material (3) | **low** |
| T15 snap-start | `push(..., lead=2)` | Phase, Borrow (30 fps fit) | medium |
| T16 cut on the word | `cut_plan` | Phase, Borrow, Tag (word timings) | high |
| T17 flash inserts | `cut_plan` shots of 0.25 to 0.4 s | all | high |
| T18 object to lens | staging | Borrow, Material | **low** |
| T19 low-angle creature | `low_angle` | Spirit Beasts, Tag | medium |
| T20 over-the-shoulder | staging | Spirit Beasts, Material, One Word | medium |
| T21 through glass | staging | Phase, Tag | **low** |
| T22 shadowed eyes | face decal | Phase only | **low** |
| T23 highlight outline | Freestyle / Roblox Highlight | Spirit Beasts only | **low** |
| T24 exit, camera stays | staging + `drift` | Phase, Gold | **low** |
| T25 caption spring | `captions_bright_cut.json` | Phase, Material (30 fps) | high |
| T26 keyword colour | `caption_plan` | all 7 | high |
| T27 in-world insert | staging | Phase, Tag, Borrow, Material | medium |
| T28 snap zoom | `snap_zoom` (+ `hit_flash`) | Material | **low** |

## 15. Blender recipe (our builders)
- **Output:** 1080x1920, 30 fps, H.264 CRF 18, then the house loudness pass (-14 LUFS).
- **Render:** EEVEE (`BLENDER_EEVEE` in Blender 5.x). Raytracing on (screen trace), Fast GI, shadows: resolution 2048, soft (light radius on). Film filter 1.5 px. Motion blur on, shutter 0.5 (1.0 on T3 frames).
- **Colour management:** View Transform **Standard** (not AgX or Filmic), Look None, Exposure **0.0** (calibrated; +0.4 was too bright on our scene), Gamma 1.0. Check: shot mean luma 135 to 155, frame 95th percentile about 229, HSV saturation 0.30 to 0.42.
- **World (calibrated):** split with Light Path "Is Camera Ray". The camera sees a sky gradient from horizon `#D6EEFA` to zenith `#8BD0F4` at strength 2^-exposure. The set is lit by a separate fill of strength 0.4. Add white cloud cards if the shot shows a lot of sky.
- **Key light:** Sun, strength 4.5, colour `#FFF3E2`, angle 3 degrees, elevation 55 degrees (50 to 60). Azimuth 30 to 45 degrees off the camera axis, so faces are lit from the front-side.
- **Fill:** world light only. No rim lights. No coloured lights except power effects.
- **Bloom and trim:** compositor Glare node (Blender 5 node group `BC_comp`), Fog Glow, threshold 1.0, size 0.5, strength 0.12, then Hue/Sat saturation 1.05. Raise glare strength to 0.35 only on T13 and T14 frames.
- **Fog/mist/volumetrics:** off.
- **Materials:** skin Principled base `#E8BC8A`, roughness 0.45, Specular IOR Level 0.35. Clothing printed texture, roughness 0.8. Keep the Cast v2 `fabric()` weave, but lower its bump strength from 0.18 to 0.05 to 0.08. Hair roughness 0.35 with one stronger highlight. Walls plastic roughness 0.5. Wood and brick with real image textures.
- **Outline:** none on 3D. Faces carry their own drawn outlines. Freestyle only for T23.
- **Cameras:** 26 mm wide, 35 mm medium, 50 mm close, 70 to 85 mm extreme close. Depth of field only on close and extreme close (f/2.8, focus on the eyes). One camera per shot, two keyframes, **Linear** interpolation (`push`, `pull`, `drift`). Most shots 0.5 to 1.2 s, inserts down to 0.25 s, never over 2.6 s.
- **Cut list:** `cut_plan(word_timings)`. A cut at every phrase start (split our `lines` on , . ! ? ; :). In any phrase longer than 0.8 s, extra cuts on stressed words (content words of 4+ letters) about 0.7 s apart. No shot under 0.25 s or over 2.6 s. Cuts sit +1 frame after the word onset. On our bell, egg-army and dungeon timings this gives average 0.75 to 0.84 s and median 0.73 to 0.80 s.
- **Captions:** ASS subtitles burned in with libass. Montserrat ExtraBold 52 px, PlayResX 1080, PlayResY 1920, Outline 5, Shadow 1, Alignment 2, MarginV 500 (baseline about 73% height). T25 and T26 tags as above. Each caption starts 2 frames before its picture cut (`caption_plan`). Full spec: `pack/captions_bright_cut.json`. Burn captions last, after the post effects, so the whip blur and shake never touch them (frame 0 captions are sharp in the reference).

### Calibrated on our scene (pass 3)
Main's town-square look test (Cast v2 kids and guard, our `a1_*` town, Cycles) with the pack defaults gives **mean luma 147.0, HSV saturation 0.349, vivid pixels 5.5%, sky `#83CEF3`** at 540x960. Targets are 135 to 155 and 0.30 to 0.42. The render is `/tmp/claude-0/kits/look/final_bright-cut.png`.

Before calibration it gave 186 / 0.26 at +0.4 exposure, and 166 / 0.29 at 0.0: washed out, with the sky clipped to `#ABFEFF`. The fixes, in order of effect:
1. Exposure +0.4 to 0.0.
2. The camera sees the sky at its true colour, while a separate, weaker fill (0.4) lights the set.
3. A pale horizon gradient.
4. A Hue/Sat trim of 1.05.

Scene scale: our units are 3.3 per metre. Every distance in this spec is in **metres**, and the pack converts with `UNITS_PER_M = 3.3`. So a 3 m camera distance is 10 units, the creature camera height of 0.4 m is 1.3 units, and depth of field is f/0.85 (equal to f/2.8 at real scale). Point lights need energy x 3.3^2.

### Roblox Studio recipe (if a scene is staged in Studio)
Lighting: Technology **Future**, ClockTime 13.5, Brightness 3, Ambient (110,110,120), OutdoorAmbient (140,140,150), EnvironmentDiffuseScale 1, EnvironmentSpecularScale 0.5, ExposureCompensation 0.25, ShadowSoftness 0.2. Atmosphere: Density 0.2, Haze 0, Glare 0, Color (199,210,227). ColorCorrection: Brightness 0.02, Contrast 0.08, Saturation -0.05, TintColor (255,252,247). Bloom: Intensity 0.35, Size 24, Threshold 1.8. SunRays 0.02. Default cloudy-blue sky. Camera FieldOfView 70 (wide), 45 (medium), 30 (close). Power tints use a `Highlight` (FillColor = power colour, FillTransparency 0.3, OutlineTransparency 1).

## 16. What changes vs our current house style
| Our current rule (Studio Bible) | Bright Snap Cut |
|---|---|
| Look: deep saturated colour, HSV 0.55 to 0.65; dusk or golden hour welcome | **Overridden.** HSV 0.30 to 0.42, brightness 135 to 155, midday |
| Banned: flat daylight, washed-out colour | **Overridden** for bright midday daylight (shadows stay; haze stays banned) |
| Frame 0 is one memorable picture with the title on it | **Overridden.** Frame 0 is a whip-in blur plus the first caption, no title |
| Camera: steady cut shots for 20 to 25 s, then one smooth glide | **Overridden.** Cuts for the whole video, about 0.7 s shots |
| Never: fast whips, swings, snaps or shake | **Overridden** for T3, T4, T6, T7, T11 and T15 only, at the sizes above. Still no constant handheld shake, no strobing |
| Opening shots last 1.2 to 3 s; eased moves | **Overridden.** 0.4 to 1.2 s; linear moves cut mid-motion |
| Gliding part: no close-to-wide move in under 3 s | **Not applicable** (size changes happen on cuts) |
| Something in the foreground in most shots | **Relaxed.** Clean frontal mediums are the default; foreground only in T20 and T21 |
| No looping music bed | **Kept by default.** The bed is an option Jake must switch on |
| Captions in the house font | **Overridden** by section 11 (small, white, outlined, pop with overshoot, one coloured keyword) |
| People only from the locked cast, rounded heads | **Kept.** Cast v2 with the classic rounded block head (`head='classic'`). New people follow `CHARACTERS.md` and only Claude creates them |
| Clothing texture rule | **Kept**, but the weave is subtle (printed-shirt look) |
| Quality checklist, handle top left, 1080x1920 30 fps, -14 LUFS, sponsor ending | **Kept.** Note T7, T13 and T14 frames in `notes.json` so `glitchscan.py` hits are expected, not errors |

## 17. Style test (build this first, about 12 s)
Before a full film, build the first 12 seconds of any Jake-approved script in this style, so he can judge it side by side with the reference. No new characters: use Cast v2 people and an existing town set.

**Make it:**
1. Run `cut_plan` on the script's word timings and keep the shots that start before 12.0 s. That's usually 14 to 17 shots. Check `plan_stats`: average 0.6 to 0.85 s.
2. `apply_look(scene)` and `light_rig("noon", cam=...)` in the noon market square or castle courtyard.
3. Stage the shots so these techniques appear at least once:

| Shot | Content | Techniques |
|---|---|---|
| 1 | Hero medium, facing camera, first caption springs in | T3 `whip_in` + T1 `push`; whoosh at -2 f |
| 2 | The rule's object (bell, crown, egg) in close-up | T5 `axis_punch` from a wide of it, T17 insert |
| 3 | Wide of the square or crowd | T1 `pull` |
| 4 | A townsperson reacting, medium | T2 `drift`; red keyword on the danger word |
| 5 | Close insert on the action (knees, hands, the mark) | T1 `push` with `lead=2` (T15 snap-start) |
| 6 | Creature or king from below | T19 `low_angle` + push |
| 7 | Hero comic face, reaction | T4 `crash_push` + face swap + T6 `shake` on the last 6 f |
| 8 | The power moment (if the story has one) | T8 `power_tint` or T9 `hit_flash` + T28 `snap_zoom`; optional T7 glitch into the next cut |
| rest | Remaining planned shots | push/pull/drift as `cut_plan` suggests |

4. Post: `post_bright_cut.py` with `whip_in`, one `shake`, the effects (whoosh on about 1 cut in 4), then the captions from `captions_bright_cut.json` burned last.

**Check it with numbers:** run `python3 pack/check_bright_cut.py test.mp4`. It should read:
- mean luma 135 to 155
- HSV saturation 0.30 to 0.42
- vivid pixels at or under 10%
- average shot 0.6 to 0.8 s, none over 2.6 s
- static shots at or under 16%

Also check by eye that every shot is moving at the cut, and that captions sit at 66 to 74% height with cap height 30 to 40 px.

**Show Jake three clips side by side, all 12 s, captions on:**
- the test
- our current opening of the same script (or the Stag Part 1 opening)
- the reference's first 12 s, linked, not downloaded: https://www.youtube.com/shorts/8WEm8GKMT4w

Ask him two things: does the faster cutting read as clear or as chaotic at phone size? And is the lighter, less saturated noon look OK against his deep-colour rule?

## 18. Do / Don't
**Do**
- Cut on every phrase start and on the stressed word. Aim for a 0.7 s average and no shot over 2.6 s.
- Keep the camera moving at constant speed in every shot, and cut while it moves.
- Light at noon: Standard view transform, exposure +0.4, sky `#8BD0F4`, soft sun shadows.
- Keep colour light. One red keyword and one power colour are the only loud things.
- Swap faces on cuts, and use the comic close-up face for reactions.
- Open on a 3 to 7 frame whip-in, and end on a moving shot with the last word in the final 0.3 s.
- Use small white outlined captions at 66 to 74% height that spring-pop (45 to 118 to 90 to 100%) and lead the cut by 2 frames.

**Don't**
- Don't hold a shot over 2.6 s or let the camera stop dead.
- Don't use dusk, fog, haze, vignette, grain, letterbox or heavy grading.
- Don't lip sync or animate the faces inside a shot.
- Don't put more than one coloured word in a caption, or emoji or stickers anywhere.
- Don't use constant handheld shake. Shake only on impact beats.
- Don't strobe (A-B-A cuts under 4 frames).
- Don't use a title card or an end card.
- Don't copy their stories, characters, names, hair designs, titles or any footage.

## 19. Evidence
**Videos studied** (YouTube @cannonanimates; view counts from the channel's Shorts tab on 11-26):

| # | Title | URL | Views | Published | Length | Shots | Avg / median shot | Longest | Brightness | HSV sat | Words/s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | The Kid Who Could Phase Through Anything | https://www.youtube.com/shorts/8WEm8GKMT4w | 21M | 2026-08-02 | 47.3 s | 70 (30 fps) | 0.68 / 0.67 s | 1.6 s | 142 | 0.41 | 4.2 |
| 2 | The Boy Who Could Borrow People's Talent | https://www.youtube.com/shorts/BFR-sN4jwJQ | 15M | 2026-08-14 | 55.3 s | 59 (30 fps, about 3% frames lost) | 0.94 / 0.80 s | 2.6 s | 148 | 0.35 | 3.6 |
| 3 | The Boy Who Could Become Any Material (newer hit) | https://www.youtube.com/shorts/d0WnD1qUNBk | 7.9M | 2026-09-15 | 45.7 s | about 82 (10 fps) | 0.56 s | n/a | 131 | 0.41 | 3.9 |
| 4 | The World Where Spirit Beasts Determine Power (Part 1) | https://www.youtube.com/shorts/bgZX1mZZVZA | 6.5M | 2026-08-05 | 46.6 s | about 65 to 75 (10 fps, 14% frames lost) | about 0.62 s | n/a | 154 | 0.29 | 3.5 |
| 5 | In This Town, A Game Of Tag Is Deadly (newest hit, our exact format) | https://www.youtube.com/shorts/Miqjydp1ulM | 5.4M | recent | 142.1 s | 176 (10 fps) | 0.81 / 0.80 s | 2.2 s | 110 (night) | 0.38 | 3.8 |

Also checked in pass 2 (openings at 30 fps, one ending): "He Could See One Word Above Everyone's Head", 16M, https://www.youtube.com/shorts/K8vEef5_yVU (whip-in settles in 3 f; first cut 1.32 s; no glitch). "Everything He Touched Turned to Gold", 9.8M, https://www.youtube.com/shorts/muQQI05Ns10 (whip-in over 4 f; push to 1.32 s; character exits frame at 1.35 to 1.6 s; last shot starts 0.25 s before the end, still pushing).

Other hits on the channel: "He Could See One Word Above Everyone's Head" 16M, "Everything He Touched Turned to Gold" 9.8M, "The Kid Who Could Take Away Pain" 9.7M, "Mirrors Showed People's Happiest Moment" 9.5M.

**Key measured numbers:**

| Measure | Value |
|---|---|
| Average shot | 0.56 to 0.94 s (pooled median about 0.7 s) |
| Cuts per minute | 64 to 108 |
| Phrases starting on a cut | 95 to 97% |
| Brightness | 131 to 154 (day) |
| HSV saturation | 0.29 to 0.41 |
| Vivid pixels | 8% |
| Shots with camera motion | 85 to 90% |
| Zoom speed | 16 to 22% /s |
| Drift | 170 to 205 px/s |
| Rolls per video | 5 to 7 |
| Real shake moments per video | 1 to 2 |
| Freeze frames | 0 |
| Caption cap height | 30 to 40 px |
| Caption height | 66 to 74% |
| Caption pop | 45 to 118 to 90 to 100% in 9 f; leads the cut by 1 to 2 f |
| Words per second | 3.5 to 4.2 |
| Music bed | about 4 dB under the voice, bass constant |
| Final word | in the last 0.1 to 0.3 s |

**Method:** I ran an in-browser frame stepper in my own tab on Jake's PC (anonymous YouTube). It stepped through every frame at 30 fps for Phase and Borrow and at 10 fps for the others. It measured, per frame: luma, saturation, contrast, a 64-bin colour histogram difference, and a global motion fit (shift ±8 px at 108x192 with sub-pixel refinement, scale 0.97 to 1.03, roll ±1.5 degrees). Cuts were found from the histogram and the structural residual and checked by eye on contact sheets: the 10 fps thumbnail count on Phase (72) matched the 30 fps count (70). Word timings came from the auto-captions, and audio band energies came from a silent Web Audio tap. Palettes are Lab k-means. Contact sheets and full-res stills were studied by eye for faces, textures and transitions.

**Caveats:**
- About 3% of frames (Borrow) and 14% (Spirit Beasts) were lost while sampling, so those shot counts are estimates.
- The jitter metric over-counts shake when characters move, so shake frequency comes from visual checks of flagged shots: 1 of 3 flagged shots had real shake.
- Spirit Beasts audio did not capture. Material audio covers its first 27 s only.
- The project docs `COMPETITOR-RESEARCH*.md` were not reachable from this session (no Projects tool). The 11-24 teardown and the Studio Bible were read from local copies.
- All competitor frames and audio were deleted after measuring.
