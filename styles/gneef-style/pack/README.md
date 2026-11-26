# Torchlit Blocktale style pack (`gneef-style`)

Everything a builder needs to make a film in this style. Read `../STYLE.md` once first (sections 5, 13, 14 and 18 matter most). People come from Cast v2 built the `../CHARACTERS.md` way, and still go through the Studio Bible cast check.

| File | What it is |
|---|---|
| `style_gneef.py` | Blender 5.3 module: look, lights, every camera technique, cut plan |
| `example_shot.py` | A 20-line example that sets up a scene with the module (no render) |
| `post_gneef.py` | ffmpeg post pass: tints, whiteout, vignette, post-moves, bed and effects mix |
| `post_plan_example.json` | Example input for the post pass |
| `captions_gneef.json` | Caption spec: font, size, position, outline, 2-frame pop, timing |
| `measure_gneef.py` | Reads a finished test or film and prints brightness, saturation, near-black share, vignette, shot lengths and push share next to the targets (no rendering) |

## Scene scale (important)
Our scene is in Cast v2 units: people are about 6 units tall, so 1 m = 3.3 units. The module has `UNITS_PER_M = 3.3`. Every default distance (push distance, low-angle height, top-down height, extreme close-up distance, tilt rise, pre-roll offset) is written in metres and converted with `S.U(m)`. Point-light energies are multiplied by 3.3². Pass distances you measure yourself (`dist=`, `target=`, `spread=`) in **scene units**. For a metre-scale scene, set `S.UNITS_PER_M = 1.0` first.

**Calibrated look** (11-26, on main's town-square test, Cycles):
- `apply_look(mood='ember')` with `light_rig('ember_interior', target=(0, 0, 4), spread=10)` gives luma 77, saturation 0.67, 37% near-black. That is a lantern-lit dusk with an indigo sky.
- moon: 69 / 0.61. golden: 94 / 0.55. day: 95 / 0.58.
- The full preset table is in STYLE.md §15, "Calibrated on our scene".

## Steps, in order
1. **Cut plan from the voice.** `plan = S.cut_plan('<story>-word-timings.json')`, then `S.plan_stats(plan)`.
   - Every cut sits on a word onset: about 1.0 s per shot for the first 30 s, then about 1.4 s, at most 4 words per shot in the opening and 6 after.
   - Check the numbers: average 1.3-1.5 s, median about 1.25 s.
   - Mark at most one long reveal with `hold_words=[word_index]` (a 3-8 s tilt-up or crane).
2. **Pick a framing for every shot** using the mix in STYLE.md §4: 26% wide, 24% full, 26% medium, 13% close, 6% extreme close, 7% insert.
   - Vary the size from cut to cut (the source sometimes repeats a size; avoid long runs of one size).
   - Each rule the narrator states gets its own insert (a sign, clock or calendar).
3. **Set the look per scene.** `S.apply_look(scene, mood='ember'|'moon'|'day'|'golden')` and `S.light_rig('ember_interior'|'moon_night'|'day'|'golden', target=...)`.
   - Put a visible lantern or window in frame for each practical light.
4. **Camera.**
   - `cam = S.new_camera('wide')` (vertical 36 mm sensor, 26 mm lens). Make one camera per set, or re-`place()` it per shot.
   - Per shot: `S.place(cam, loc, look_at, frame=shot['f0'])`, then the moves.
   - Quickest: `S.assign_moves(plan, reveal_words=[...])`, then `S.apply_moves(cam, shot, dist=...)`. That gives a push on about 3 of 4 shots, a pull-out on about 1 in 8, a snap push when a shot starts on a reveal word, roll drift on alternate shots, and a 2 px wobble everywhere.
   - Special moments: `tilt_up_reveal`, `lateral_truck`, `low_angle`, `top_down`, `ecu`, `plunge`, `follow_tumble`, `boat_rock`, `calendar_flip`, `whiteout`, `preroll_snap` (frames 1-3 of the film).
   - Pass `dist=` (camera-to-subject metres) so pushes and trucks scale right. Otherwise the module uses the DOF focus object or distance, or 5 m.
5. **Characters hold poses.** One expression per shot, swapped on the cut; no lip sync. Animate 2D stickers ("Z z z", music notes) normally, then call `S.step_animation(obj, 3)` to step them at 10 fps.
6. **Render** 1080x1920 at 30 fps (the module sets it). EEVEE, motion blur off, the compositor grade is already wired. Render the shots straight through, since the cuts are in the plan.
7. **Post.** Fill a post plan (copy `post_plan_example.json`) and run `python3 post_gneef.py plan.json`.
   - The pass adds flashback tints (`sepia`, `bw`), the `whiteout` glow, the vignette, and mixes the voice, the bed at -10 dB and effects placed on actions.
   - The `push` / `snap` / `roll` / `wobble` post-moves are only for shots rendered locked-off. 3D moves look better (parallax).
   - Leave `grade` null if Blender already graded the shots.
   - The post pass runs at about 6 fps for 1080x1920 when moves are used, so allow about 12 minutes for a 150 s film.
8. **Captions last**, from `captions_gneef.json`:
   - one lowercase white word at a time, Poppins Bold 72 px;
   - centred on x 540 with the baseline at y 1330;
   - 4 px black outline and a soft shadow;
   - a 2-frame pop from 85% to 100%;
   - each word shows from its onset until the next word starts.
   - Our handle `@idlemerchantrng` goes top left.

## Checks before delivery
Run `python3 -I measure_gneef.py film.mp4` and fix anything marked OFF. Then check by eye:
- `plan_stats`: average 1.3-1.6 s, no shot under 0.45 s, at most one over 3 s.
- At least 70% of shots have a push.
- No locked-off shot.
- Wobble 1-3 px (6-14 px only in action or boat scenes).
- Brightness 70-100 (night 60-75), saturation 0.60-0.72, 30-45% of the frame near-black.
- Captions never empty while the voice runs. No title card.
- The Studio Bible quality checklist still applies (strobing, pops, -14 LUFS, two editions).

## Needs Jake's yes before use (Studio Bible overrides)
- Cutting for the whole video.
- Wobble, roll drift, snap pushes and the one whip re-frame (`whip_reframe`).
- A sound bed under the voice. Without a yes, use an ambience bed (wind, sea, fire, crowd) and no music.
- One-word white captions instead of coloured keywords.
- No title on frame 0 (the title goes on the thumbnail).
