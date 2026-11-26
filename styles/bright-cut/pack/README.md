# Bright Snap Cut style pack (`bright-cut`)

This pack has the code a builder needs for the Bright Snap Cut style. Read `../STYLE.md` for the look and the numbers, and `../CHARACTERS.md` for people. Everything here copies the method only. Use our own stories, Cast v2 characters and medieval sets.

## Files
| File | What it is |
|---|---|
| `style_bright_cut.py` | Blender 5.3 helper module: look, lights, every camera technique, subject flashes and tints, cut plan and caption plan |
| `post_bright_cut.py` | ffmpeg finishing pass: whip blur, RGB glitch, white flash, impact shake, optional halo, whooshes, -14 LUFS |
| `captions_bright_cut.json` | Caption spec: font, size, position, colours, keyword rules, spring animation, timing, ASS style line |
| `check_bright_cut.py` | Reads a finished mp4 and checks it against the measured targets: luma, saturation, vivid share, shot lengths, static shots |

## Order of work
1. **Plan the cuts from the voice.** In Blender's Python console (or a script):
   ```python
   import sys; sys.path.insert(0, r"C:\...\styles\bright-cut\pack")
   import style_bright_cut as bc
   shots = bc.cut_plan(r"...\story-word-timings.json")
   print(bc.plan_stats(shots))
   ```
   Every shot gets a start and end frame, the words it covers, a suggested size (`medium`, `close`, `wide`, `ecu`) and a suggested move (`push`, `pull`, `drift`). The size changes at every cut. Target: average 0.7 s, median 0.67 to 0.80 s, nothing over 2.6 s. On our bell, egg-army and dungeon timings the plan gives average 0.75 to 0.84 s and median 0.73 to 0.80 s. Merge a pair of shots only if the story needs a longer hold.
2. **Set the look once per scene:** `bc.apply_look(scene)`, then `bc.light_rig("noon", cam=main_cam)`. For night stories use `apply_look(scene, night=True)` and `light_rig("night")`.
3. **One camera per shot.** Use `bc.make_camera(name, size)`, which sets the lens: wide 26 mm, medium 35 mm, close 50 mm, extreme close 80 mm. Then key exactly one move for that shot:
   - `bc.push(cam, f0, f1)` or `bc.pull(cam, f0, f1)`. The defaults are 18% scale per second, linear, and the cut comes mid-move. Use `lead=2` for a snap-start.
   - `bc.drift(cam, f0, f1)`: 190 px/s sideways.
   - Shot 1 only: `bc.whip_in(cam, 0)` before its push.
4. **Big beats** (see the STYLE.md catalogue for when):
   - `crash_push` plus a face swap at the returned `swap_frame`, plus `shake` on the last 6 frames (shock, punchline).
   - `snap_zoom` plus `hit_flash` (transformation).
   - `power_tint` (using the power).
   - `axis_punch` (naming an object or time).
   - `roll` and `follow_roll` (falls and flips).
   - `fly_through` (through a wall or floor).
   - `low_angle` (creature reveal).
   Every function returns the numbers it used.
5. **Faces:** swap the face image on cuts only (see CHARACTERS.md). No lip sync.
6. **Render** at 1080x1920, 30 fps (the look sets this).
7. **Captions:** `caps = bc.caption_plan(timings, power_words=("phase",))` gives one caption per phrase with its frames and coloured keyword. Build an `.ass` file from `captions_bright_cut.json`: style line plus spring-pop tags, keyword colour tags, start 2 frames before the cut. Install **Montserrat ExtraBold** (free, Google Fonts) first, otherwise libass falls back to another font.
8. **Finish:** write an effects plan (`python3 post_bright_cut.py --example` prints one), then
   `python3 post_bright_cut.py render.mp4 final.mp4 --plan fx.json`.
   It adds:
   - the whip blur on frames 0 to 3
   - RGB glitch into chosen cuts
   - white flashes
   - impact shakes, which apply a constant 2.2% crop
   - whoosh and impact effects at given times (aim for 20 to 24 a minute, mostly on cuts)
   - loudness at -14 LUFS
   Add `"ass": "captions.ass"` to the plan to burn the captions last in the same pass, so the blur and shake never touch them. Then the house steps: handle, sponsor edition, glitchscan.
9. **Check it:** `python3 check_bright_cut.py final.mp4`. Every line should say OK.
10. **Note the deliberate effect frames** (whip, glitch, flashes) in `notes.json`, so `glitchscan.py` hits on them are expected.

## Calibrated on our scene (Thu 11-26, pass 3)
Main's town-square look test (`/tmp/claude-0/kits/look_test.py`: Cast v2 kids and guard, `a1_*` town models, Cycles, camera 30 mm at 15 units) with the pack defaults:

| Render | Mean luma | HSV saturation | Vivid pixels | Sky |
|---|---|---|---|---|
| Pass 2 defaults (exposure +0.4, one bright world) | 186 | 0.26 | 0.2% | clipped `#ABFEFF` |
| Main's run (exposure 0.0, same world) | 166 | 0.29 | n/a | n/a |
| **Calibrated defaults, 270x480 SAMP 8** | **147.4** | **0.344** | 5.2% | `#83CEF3` |
| **Final, 540x960 SAMP 16** (`/tmp/claude-0/kits/look/final_bright-cut.png`) | **147.0** | **0.349** | 5.5% | `#83CEF3` |

Targets: luma 135 to 155, saturation 0.30 to 0.42. The exact settings are now the defaults of `apply_look()` and `light_rig("noon")`:
- View Transform Standard, Look None, **Exposure 0.0**, Gamma 1.0.
- World split with Light Path "Is Camera Ray":
  - What the camera sees: a sky gradient from horizon `#D6EEFA` to zenith `#8BD0F4` (zenith from about 25 degrees up), strength 2^-exposure.
  - What lights the set: a **fill of 0.4** in `#8BD0F4`.
- Sun 4.5, `#FFF3E2`, angle 3 degrees, elevation 55, azimuth 35 degrees off the camera.
- Compositor: Glare Fog Glow (threshold 1.0, size 0.5, strength 0.12), then Hue/Sat saturation **1.05**. At 1.12 saturation overshoots to 0.39.

**Scene scale:** `UNITS_PER_M = 3.3`. Cast v2 adults are about 6.3 units tall, kids about 5, cottages 12 to 16. The pack converts everything to that scale:
- Every `dist`, `height`, `back` and `distance_m` argument is in **metres** and converted to units inside. Return values are in units (`travel_units`).
- Shake is an angle, so it doesn't depend on scale.
- The night window light is 60 W x 3.3^2 (about 650 W).
- Depth of field uses f/0.85, which equals f/2.8 at real scale.

Tested in Cycles. EEVEE should match closely (the Light Path trick works in both), but check one frame with `check_bright_cut.py` before a full EEVEE film.

## Checked
- The module imports in bpy 5.3. Every camera function keys a dummy camera without errors, and the shutter, lens and shake values evaluate correctly. `power_tint` and `hit_flash` key a test material. Nothing was rendered.
- `post_bright_cut.py` runs on a 2-second 270x480 test clip. The ASS tags parse in libass.

## Things that will trip you up
- **Every shot must move and be cut mid-move.** No easing to a stop. This is the opposite of our old glide rule.
- Keep shake to impact beats: 4 to 10 px for 4 to 8 frames. Constant handheld shake is wrong for this style.
- Colour should stay light (HSV saturation 0.30 to 0.42). Don't push saturation to our old 0.55 to 0.65.
- `power_tint` and `hit_flash` make single-user copies of the character's materials (`*_bcfx`) so other characters don't flash too.
