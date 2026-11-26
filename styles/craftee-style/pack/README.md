# Toybox Fable style pack (`craftee-style`)

This is the code behind `../STYLE.md`. It holds no competitor material, only our own numbers and code.

| File | What it is |
|---|---|
| `style_craftee_style.py` | The Blender 5.3 helper module: look, lights, every camera technique, face swaps, VFX, cut plan, caption cards and a still checker. Python cannot import a hyphen, so the file uses `_` where the style id has `-`. |
| `post_craftee-style.py` | The ffmpeg post steps and QA checks: light pulse, music drop-out, cut SFX, caption burn-in, cinematic extras, and the luma, saturation and loop checks. |
| `captions_craftee-style.json` | The caption spec: font, sizes, positions, colours, words per card, animation and timing. |

Units, as in our scenes: **1 m = 3.3 Blender units (BU)** (`tf.UNITS_PER_M`). A Cast v2 person at `s=1.0` is **about 6 BU** tall including hair (`tf.CHAR_H`, written "H"). Town models use the same units. Light watts and DOF f-stops in the module are given for real scale and converted for you. Frames run at 30 fps. Pixel sizes are at 1080 px wide.

## Build a film, in order

1. **Plan the cuts from the voice** (plain Python, no Blender needed):
   ```python
   import sys; sys.path.insert(0, r'...\styles\craftee-style\pack')
   import style_craftee_style as tf
   plan  = tf.cut_plan('story-word-timings.json', fmt='short')   # or 'long'
   print(tf.plan_stats(plan))   # short: mean ~1.2-1.4 s, max 2.1 s, ~40-50 cuts a minute
   cards = tf.caption_cards(plan, 'short', keywords={'egg', 'dragon'})   # keywords: from the script
   tf.write_json(plan, 'plan.json'); tf.write_json(cards, 'cards.json')
   ```
   Each shot has `f0`/`f1` frames, its words, a suggested framing (W, MW, M, C, INSERT), and `face_swap_frame` (the longest content word, which is our stand-in for the stressed word). Shot 1 is the whip-in. The last shot is the punchline (short) or the loop or emotional close (long). A shot runs over the maximum only where the voice track has an inserted pause.
2. **Set the look** in the Blender scene:
   ```python
   tf.apply_look(scene, 'day')        # Standard + 'High Contrast' (neutral curve, no tint), exposure -1.0, 1080x1920 30 fps, Cycles 24 spp
   tf.light_rig('day', cam=cam)       # sun 6.0 at 50 deg, 35 deg off the camera axis; sky #5D8CD0 -> #A4AEC0, fill 0.3
   ```
   Other rigs: `'dusk'`, `'evening'`, `'night'`, `'interior'`, `'black'`. Add `tf.practical(loc, 100)` for lamps.
3. **Check the exposure once per new set.** The day look is calibrated on our town square (see below). For a different set, render ONE small daytime still (270x480, 8-16 samples) and run:
   ```python
   tf.measure('test.png', 'day')      # -> luma, sat, luma_sd, corner_ratio, clip_pct, pass{...}, exposure_change
   ```
   Add `exposure_change` to `scene.view_settings.exposure`, and repeat until luma is 106-125. If saturation is low, raise the sun or lower the sky fill. If it is over 0.46, desaturate the set and the extras' outfits. Never tint.
4. **Cameras.** `tf.setup_camera(cam, 'standard')` gives 26 mm (`'comic'` 18, `'two_shot'` 35, `'insert'` 50). Aim with `tf.look_at(cam, point)`, then key the shot's technique. Every function keys relative to the current pose:
   - most shots: `tf.lock(cam, f0, f1)` (82-90% of a short film)
   - shot 1: `tf.whip_in(cam, f0)` (blurred frame 0, lands at +3, overshoots 2 deg, settled at +8)
   - long films only: `drift`, `fly_through` (returns the frames in which to hide the cut), `crane_out`, `snap_pull`, `swish`, `follow_prop`, `track_runner`, `dutch`, `prop_insert`, `time_skip`, and `zoom_through` for the loop ending
   - cinematic variant only: `swing_settle`
   - `impact_shake` is off-style: use it only if Jake asks for it
5. **Faces.** Point each head at the Blockfolk face sequence and key instant swaps:
   ```python
   tf.face_set(head_material, r'...\blockfolk\face_001.png')
   tf.face_swaps(head_material, [(shot['f0'], 'innocent'), (shot['face_swap_frame'], 'shocked')])
   ```
   The face order is `tf.EXPRESSIONS` (17 images). Swap on ~70% of face shots and on every punchline. For an entrance, use `tf.walk_to_camera(person, cam, f0)` with a locked camera.
6. **VFX** as the story needs them: `tf.hat_pop`, `tf.puff_rings`, `tf.light_pulse` (switch `tf.bloom(scene, True)` on only for those shots).
7. **Render** each shot's `f0`..`f1` and cut them together with hard cuts in plan order. No dissolves.
8. **Post**, in this order:
   ```
   python3 post_craftee-style.py dropout music.wav music_drop.wav --ranges 915-945   # long films: once, at the scariest/saddest beat
   (mix the voice and music: music bed ~8 dB under the voice)
   python3 post_craftee-style.py sfx cut.mp4 sfx.mp4 --plan plan.json --whoosh whoosh.wav --boom boom.wav
   python3 post_craftee-style.py pulse sfx.mp4 pulse.mp4 --frames 1830          # only if a 2D pulse is used instead of tf.light_pulse
   python3 post_craftee-style.py captions pulse.mp4 final.mp4 --cards cards.json --fmt short
   python3 post_craftee-style.py check final.mp4 --mode day       # luma 106-125, sat 0.38-0.46, no vignette
   python3 post_craftee-style.py loopcheck final.mp4              # long films with a loop ending
   ```
   Then loudness to -14 LUFS, as in the house rules.

## Calibrated on our scene (pass 3)
- **Scene:** main's look test (`/tmp/claude-0/kits/look_test.py`, STYLE=craftee-style): our town square, the Cast v2 hero, sister and guard, Cycles, 1 m = 3.3 units.
- **Before:** the pass 2 defaults (look None, exposure -0.3, sun 3.0, fill 0.9) gave luma 117, saturation 0.29 and SD 37: grey and flat.
- **Final defaults:** Standard + `High Contrast`, exposure -1.0, sun 6.0, sky fill 0.3. At 270x480 with 8 samples this gives **luma 117.2, saturation 0.428, SD 49, 0% blown whites, no vignette**.
- **Not calibrated yet:** the dusk, evening, night and interior rigs. Check them with `measure()` the first time they are used.

## Checked in pass 2 (no renders)
- The module imports in bpy 5.3. Every camera function keys a dummy camera without errors, and the keys evaluate as specified. The whip measured +17° at f0, 0 at +3, -2° at +5 and 0 at +8. Drift distance matches the px/s formula. The face swaps evaluate to the right images.
- `cut_plan` on three of our timing files gives mean shots of 1.33-1.51 s at 39-44 cuts a minute.
- The caption cards keep reading order, and every cut is a card change.
- Every post filter was syntax-checked on one still or on audio only. The caption burn-in was measured: 62-64 px caps, block centred at y 503 (short) and y 1402 (long), as in the spec.

## Known limits
- The **Blockfolk face set does not exist yet.** Claude must draw it first (17 PNGs, see `../CHARACTERS.md` §13). Until then, T11 cannot be built.
- `face_swap_frame` only guesses the stressed word. Check it by ear for the punchline.
- The keyword choice is a guess unless the script marks keywords. Pass `keywords=`.
- Techniques seen in only 1-2 films are starting values: T6, T9, T12, T13, T15, T19, T20-T22, T26 (see STYLE.md §14).
