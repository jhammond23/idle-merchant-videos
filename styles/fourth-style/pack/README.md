# Comic Sticker Saga: style pack (`fourth-style`)

This pack is code that puts the measured style (see `../STYLE.md`) into a build. Builders use `style_fourth_style.py` in Blender. The finishing pass (Claude, in the cloud) uses `post_fourth_style.py` and `captions_fourth-style.json`. `preview/` holds stills of every sticker, the question card and each effect, so Jake can judge the look without a render.

| File | What it is |
|---|---|
| `style_fourth_style.py` | Blender 5.3 helpers: look, lights, cameras, the camera moves, face swaps, and `cut_plan()` |
| `post_fourth_style.py` | Frame effects and the comic sticker layer (name stickers, speech bubbles, time tags, icon gags, question card), all drawn with PIL; frames go through ffmpeg |
| `captions_fourth-style.json` | The caption spec: font, size, position, colours, grouping, pop, keyword rules, plus the sticker text specs |
| `preview/` | Our own test stills (no competitor pixels) |

## Fonts (do this once)
The two free OFL fonts could not be downloaded from the cloud sandbox, because GitHub and Google Fonts are blocked there. On Jake's PC:
1. Download **Poppins** (ExtraBold) and **Lilita One** from fonts.google.com.
2. Put `Poppins-ExtraBold.ttf`, `Poppins-Bold.ttf` and `LilitaOne-Regular.ttf` in `pack/fonts/`.

Until then the code falls back to Poppins Bold for captions and to the house Fredoka One for stickers. The previews were drawn with those fallbacks.

## Calibrated on our scene (pass 3)
- **Scale:** `UNITS_PER_M = 3.3`, because Cast v2 people are about 6 units tall. Every distance default is in metres x 3.3. Point and area light energies are multiplied by 3.3², and the over-the-shoulder f-stop is divided by 3.3.
- **Day look** (`CAL['day']`):
  - AgX, look **High Contrast**, exposure **-1.3**;
  - Multiple Scattering sky with the sun disc off: strength 0.12 to the camera, 0.04 as fill;
  - Sun **6.0** at elevation 48°, azimuth 35° for +Y cameras (or `sun_rot_for(cam)`);
  - Bloom threshold 0.9, contrast +10, saturation trim 0.95.
- **Result** on main's town-square test (Cycles, 270x480): luma **107.9**, p5 0, p95 184, saturation **0.418**. Before calibration it was 214 / 0.10.
- **Not calibrated:**
  - Sunset, interior, night and insert are extrapolated starting points. Check one still of each with `check`.
  - EEVEE was not test-rendered.
- Details are in `../STYLE.md` section 15, "Calibrated on our scene".

## Builder, in order (Blender)
1. **Plan the cuts first.** From the cloud shell, run `python3 -I style_fourth_style.py <story>-word-timings.json`. It prints every shot (start, end, frames, a framing hint, the captions it covers) and the stats. The targets are an average shot of 1.3-1.6 s and nothing over 3.1 s.
   - Every cut lands on a caption start: the new shot and the new caption arrive on the same frame.
   - The film ends with 3 background shots under the question card (6 s).
   - The framing hint follows the measured mix (wide 19%, medium 35%, medium close-up 24%, close-up 18%). Change it per beat. After every reveal line, give the lead a reaction close-up with a new face.
2. In each shot's script:
   ```python
   import sys; sys.path.insert(0, r'<...>/styles/fourth-style/pack')
   import bpy, style_fourth_style as S
   cam = S.camera('s07', 'closeup', loc=(0, -7.3, 5.3), look_at=(0, 0, 5.1))   # scene units (3.3 a metre)
   r = S.sun_rot_for(cam)                   # sun behind the camera's shoulder
   S.apply_look(bpy.context.scene, 'day', sun_rot=r)   # or 'sunset' | 'interior' | 'night'; engine='CYCLES' optional
   S.light_rig('day', sun_rot=r)            # or 'sunset' | 'interior' | 'night' | 'insert' (top-down notes)
   ```
3. **Keep the camera locked.** About 90% of shots have no move at all, or only `S.creep(cam, f0, f1)` (0.3 px a frame).
4. Use **at most 2 moves per film**, each on the biggest beat:

   | Function | When to use it | Default |
   |---|---|---|
   | `S.snap_zoom(cam, f)` | the one shouted "NO!" | +5, +5, +5, +2% over 5 frames |
   | `S.pull_out(cam, f0)` | a transformation reveal | 85 to 42 mm; 6 frames hold, 42 frames move, ease-out over the last 12 |
   | `S.orbit(cam, prop_location, f0)` | the voice lists a prop's features | 30° in 48 frames, ease in and out |
   | `S.crane_down(cam, f0)` | sneaking or hiding, into an over-the-shoulder | -0.65 m and -8.5° in 42 frames, ease-in over 9 |
   | `S.jump_cuts(cam, f0)` | a repeated line ("waited... and waited") | 3 segments of 33 frames at 100/110/121% |
   | `S.ff_jitter(cam, f0, f1)` | a fast-forward repeat only | ±27 px, ±0.9° roll; retime the action 3-4x yourself |

5. Shot types:
   - `S.ots(cam, far_subject)`: over-the-shoulder, f/2.8.
   - `S.low_angle(cam, head)`: low angle from chest height, 20° up.
   - `S.top_down(cam, spot)`: straight down.
   - `S.eye_ecu(cam, eyes)`: extreme close-up on the eyes, 85 mm.
   - `S.light_dim(light, f0)`: the light dims for "hours later".
6. **Faces:** call `S.set_face(head, '<char>_<expression>.png')` before each close-up, so the face changes between shots. For a 1-frame swap on a reaction inside a shot, use `S.face_swaps(head, [(frame, png), ...])`.
7. **Don't add** shakes, whips, swish pans, dutch angles, motion blur, grain, light leaks, letterbox or impact flashes. All of these were measured at zero. The module has no `shake()` on purpose.
8. Render true 30 fps, 1080x1920. Check two stills with `python3 -I post_fourth_style.py check a.png b.png`. The targets are luma 95-110, p5 under 15, p95 220-232, saturation 0.40-0.48.

## Finishing pass, in order (cloud)
1. Captions: group them with `style_fourth_style.caption_groups()` and draw them to `captions_fourth-style.json`. That means 1-3 words, white with a 7 px ink outline, baseline at y 1290 (y 1515 on face close-ups), a 1-frame pop at 108%, and keywords marked `{gold}`, `[red]` or `<magic>`, with quoted dialogue in gold. Use the house caption tool if it supports this spec. If it doesn't, add `caption` events to the post plan.
2. Write a post plan JSON. The event list is at the top of `post_fourth_style.py`; frames are at 30 fps, `f0` inclusive and `f1` exclusive:
   - `name` at each featured character's first appearance (2-3 per film, in their own permanent colour);
   - 2-4 `bubble` events for quoted lines from other characters;
   - `time_tag` events on time skips;
   - 1-3 `gag` events (stars, question, exclaim, sweat, anger);
   - `card` at the end;
   - optional `flash`, `bw`, `sepia`, `dim`, `snap_zoom` (only if it wasn't keyed in Blender) and `dip_black` (1-3 frames before the sponsor).
3. Run one of these:
   - `python3 -I post_fourth_style.py run plan.json in.mp4 out.mp4` for a video;
   - `python3 -I post_fourth_style.py frames plan.json renders/ out/` for a PNG sequence.

   For plain ffmpeg, `post_fourth_style.py ffmpeg plan.json` prints a `-vf` chain for the simple effects only. It has no stickers, no card and no sepia border.
4. Sound: `post_fourth_style.py cues plan.json` lists a pop for every sticker landing and a thump on the card or wherever `"sfx": "thump"` is set. Also add soft thumps on the 3-4 biggest cuts. House rule: no music bed unless Jake says yes.

## What a builder will find hard
- **New faces every close-up.** Each featured person needs 8-10 expression decals in the two line-art families (`../CHARACTERS.md`). Claude makes them; builders only swap them.
- **Oversized anime hair** (1.3-1.8x the head width) is not in the Cast v2 library yet. Until hair meshes exist, the look falls back to normal Cast v2 hair. That is the weakest part of the match.
- **Bloom on whites:** Blender 5.x Glare sizes are relative, so `Size 0.25` is a translation of the old "size 7". Check on a still that whites glow a little and p95 stays at 222-232.
- **The crane distance** is tuned for a subject 4 m away at 35 mm. Closer subjects move more on screen: halve `dz` at 2 m.
