# Build styles and character kits (Thu 11-26)

Jake asked for 3-5 selectable **build styles**, reverse-engineered from viral accounts (animation, colour, shapes, textures, camera shake, film and camera techniques: everything), plus a separate set of **character styles** for making new characters. Jake picks a style per story in the studio app (New story, step 6 "Build style"); the idea's `buildStyle` field names it, and the build package says which folder to follow. Default is `house` (the Studio Bible look).

**Picking a style is Jake's yes to the house rules that style lists under "overrides" (style.json) / "What changes vs our house style" (STYLE.md), for that film only.** Everything else in the Studio Bible still applies (Cast v2 only, cast check, quality checklist, no music bed unless the style's own sound section and Jake say otherwise, sponsor rules).

Method only: these were measured from other creators' videos (frame by frame, 5-7 top videos each); never copy their stories, lines, characters, names, titles or footage. All their frames were deleted after measuring.

| Folder | Build style | Learned from | Character kit | Look in one line |
|---|---|---|---|---|
| `bright-cut/` | Bright Snap Cut | cannonanimates (YouTube) | Sunny Block Folk | noon toy-town light, a cut every ~0.7 s, every shot drifting, small white captions with one red word |
| `gneef-style/` | Torchlit Blocktale | Gneef (YouTube) | Inkface Blockfolk | lantern and moonlight, deep colour over crushed blacks, push-in on every shot, light handheld wobble, one white word at a time |
| `craftee-style/` | Toybox Fable | Craftee Films (Instagram) | Toybox Blockfolk | bright neutral game-map towns, locked shots cut on every caption, big thick line-art faces |
| `fourth-style/` | Comic Sticker Saga | Stickman Deadzone (Instagram) | Sticker Saga Cast | locked shots every ~1.45 s, natural colour with true blacks, a comic sticker layer (name stickers, speech bubbles, time tags, question card) |

## In each folder
- `STYLE.md`: the full spec (palette, light, camera with numbers, cutting, characters, textures, animation, captions, sound, frame 0 and ending, Blender recipe, a catalogue of 26-32 camera/film techniques with timing, size, trigger and recipe, a 10-15 s **style test** to build first, and "Calibrated on our scene").
- `style.json`: the same in data form (the app reads it).
- `CHARACTERS.md` + `characters.json`: the character kit (head, face construction, expressions, measured proportions, body types, skin tones, hair, clothing, materials, motion, recipe on Cast v2).
- `swatch.png`, `charsheet.png`: style card and character sheet (drawn by us).
- `pack/`: **code**. `style_<id>.py` (Blender 5.3 module: `apply_look`, `light_rig`, one function per camera technique, `cut_plan` from our `*-word-timings.json`), a post-processing script (ffmpeg / PIL effects, captions), the caption spec JSON, and a README with the steps in order. Every pack uses `UNITS_PER_M = 3.3` because Cast v2 people are about 6 Blender units tall.
- `faces/`: a first face set drawn by Claude for the kit (1024x1024 transparent PNGs; use with `head_mat2(..., fs=...)`; fs values below).
- `samples/`: new characters of our own built in the kit (`*-sample.jpg`) and the same town-square shot in the style (`*-test.jpg`).

## Face scale (`fs` in `person()` / `head_mat2`) for the drawn face sets
Sunny 1.3, Inkface 1.1, Toybox 1.1, Sticker 1.08 (bigger fs = bigger features on the head).

## Calibration (same town-square shot, Cycles, our cast and a1_* town models)
| Style | Mean luma | HSV saturation | Target |
|---|---|---|---|
| Town Storybook (house) | 126 | 0.40 | Studio Bible |
| Bright Snap Cut | 147 | 0.35 | 135-155 / 0.30-0.42 |
| Torchlit Blocktale | 77 | 0.67 | ~82 / 0.60-0.72 |
| Toybox Fable | 117 | 0.43 | 106-125 / 0.38-0.46 |
| Comic Sticker Saga | 108 | 0.42 | 95-110 / 0.40-0.48 |
Only the daytime (and gneef's four moods) rigs are calibrated; check one still before a full render in any other rig, and in EEVEE.

## Tools (`tools/`)
- `faces.py`: draws the kit face sets. `render_kit.py`: kit sample renders (KIT=sunny|toybox|ink|sticker SHOT=lineup|faces). `look_test.py`: the same town-square shot in any style (STYLE=<id>). `overlay.py`: each style's caption treatment on its test frame. They import `/tmp/claude-0/cast2/cast_v2.py` (copy on scripts-inbox `cast-v2/`).

## Fonts to install on the PC
Montserrat ExtraBold (bright-cut), Poppins Bold / ExtraBold (gneef, craftee, fourth), Lilita One (fourth stickers): all free on Google Fonts.
