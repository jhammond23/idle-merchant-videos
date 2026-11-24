# Locked Reflection cast: source and per-role manifest (Claude, 11-24)

Builder 1 asked for `nx/set_refl.py` and the character definitions it imports. They were found in Claude's build folder, not in `/mnt/project-files/...` (that path no longer exists). Everything the Reflection square build loaded is in this folder, at the same relative paths it ran from:

- `lib.py`: the shared R6 rig (`r6()`), the hair and face library loaders.
- `oc/base.py`: `person(name, shirt, pants, hair, face, skin, beard)` plus the shared SHIRTS, PANTS, SKINS, HAIRS and FACES lists.
- `sky/set_sky.py`, `sky/look3.py`, `town.py`: the town square, light and sky that `gk/set_gk.py` builds on.
- `gk/set_gk.py`: **the cast** (the hero kid, the 26-person crowd, the captain, six guards).
- `nx/set_common.py`, `nx/set_refl.py`, `nx/set_land_nx.py`: the Reflection additions (water twin, water captain, water crowd, king).
- `nx/scenes_r.py`, `gk/scenes_gk.py`: the shots. Use them to check who stands where.

**Load order on the Reflection server:** `gk/set_gk.py` (which execs `oc/base.py`, `sky/look3.py` and blocks of `sky/set_sky.py`), then `gk/cmd_src/gk_props.py`, `poster_fix.py`, `palm_mat.py`, then `nx/set_common.py`, `nx/set_wheel.py`, `nx/set_refl.py`. The three `gk/cmd_src` patch files are props and materials only (no people), and they are lost, so they are not here.

The paths inside the files point at Claude's old folder (`/tmp/claude-0/tv/...`). Re-point them at your copy. The hair and face assets are the October 31 libraries already on the PC.

**The hero for Egg Army, Dungeon Master and every new story is `kid` (first row):** burnt-orange shirt (206,76,48), dark blue-grey pants (52,58,82), `hero_crop` hair, `face_bright` face, skin (238,196,156), scale 0.8 next to adults at 1.0.

## Every person in the Reflection build

| Role | Defined at | Shirt RGB | Pants RGB | Hair | Face | Skin RGB | Beard | Scale |
|---|---|---|---|---|---|---|---|---|
| kid (THE HERO, `KID`) | gk/set_gk.py:252 | (206,76,48) burnt orange | (52,58,82) | hero_crop | face_bright | (238,196,156) | - | 0.8 |
| twin (water reflection, `TWIN`) | nx/set_refl.py:62 | water blues | water blues | hero_crop | face_bright | water (150,214,255) | - | RS |
| captain (`CAPT`) | gk/set_gk.py:257 | (190,196,206) + steel plate | (70,74,86) | hero_slick_back | face_bold | (206,150,112) | face_full_beard | 1.0 |
| water captain (`WCAP`) | nx/set_refl.py:92 | water blues | water blues | hero_slick_back | face_bold | water | face_full_beard | 1.0 |
| king (`KING`, land set) | nx/set_land_nx.py:13 | (150,22,34) | (96,16,28) | hero_slick_back | face_bold | (214,160,122) | face_full_beard | 1.0 |
| guard gd0 | gk/set_gk.py:262 | (190,196,206) + steel plate + helmet | (70,74,86) | hero_crop | face_bold | (200,150,112) | - | 1.0 |
| guard gd1 | gk/set_gk.py:262 | (190,196,206) + steel plate + helmet | (70,74,86) | hero_crop | face_calm | (190,140,100) | - | 1.0 |
| guard gd2 | gk/set_gk.py:262 | (190,196,206) + steel plate + helmet | (70,74,86) | hero_crop | face_cool | (226,176,140) | - | 1.0 |
| guard gd3 | gk/set_gk.py:262 | (190,196,206) + steel plate + helmet | (70,74,86) | hero_crop | face_bold | (236,190,150) | - | 1.0 |
| guard gd4 | gk/set_gk.py:262 | (190,196,206) + steel plate + helmet | (70,74,86) | hero_crop | face_calm | (240,200,170) | - | 1.0 |
| guard gd5 | gk/set_gk.py:262 | (190,196,206) + steel plate + helmet | (70,74,86) | hero_crop | face_cool | (170,118,84) | - | 1.0 |
| crowd cw0 | gk/set_gk.py:255 | (200,90,70) | (60,60,90) | hero_crop | face_bright | (236,190,150) | - | 1.0 |
| crowd cw1 | gk/set_gk.py:255 | (90,150,200) | (80,60,50) | hero_long_tie | face_starry | (226,176,140) | - | 1.0 |
| crowd cw2 | gk/set_gk.py:255 | (230,190,80) | (70,70,80) | hero_side_wave | face_bold | (190,140,100) | - | 1.0 |
| crowd cw3 | gk/set_gk.py:255 | (150,80,160) | (50,50,60) | hero_twin_tails | face_cheeky | (200,150,112) | - | 1.0 |
| crowd cw4 | gk/set_gk.py:255 | (90,170,110) | (60,60,90) | hero_half_knot | face_calm | (120,84,60) | - | 1.0 |
| crowd cw5 | gk/set_gk.py:255 | (220,130,160) | (80,60,50) | hero_low_bun | face_grin | (150,104,74) | - | 1.0 |
| crowd cw6 | gk/set_gk.py:255 | (240,150,60) | (70,70,80) | hero_long_straight | face_shy | (170,118,84) | - | 1.0 |
| crowd cw7 | gk/set_gk.py:255 | (120,120,200) | (50,50,60) | hero_slick_back | face_sweet | (240,200,170) | - | 1.0 |
| crowd cw8 | gk/set_gk.py:255 | (200,90,70) | (60,60,90) | hero_pixie | face_wink | (236,190,150) | - | 1.0 |
| crowd cw9 | gk/set_gk.py:255 | (90,150,200) | (80,60,50) | hero_crop | face_bright | (226,176,140) | - | 1.0 |
| crowd cw10 | gk/set_gk.py:255 | (230,190,80) | (70,70,80) | hero_long_tie | face_starry | (190,140,100) | - | 1.0 |
| crowd cw11 | gk/set_gk.py:255 | (150,80,160) | (50,50,60) | hero_side_wave | face_bold | (200,150,112) | - | 1.0 |
| crowd cw12 | gk/set_gk.py:255 | (90,170,110) | (60,60,90) | hero_twin_tails | face_cheeky | (120,84,60) | - | 1.0 |
| crowd cw13 | gk/set_gk.py:255 | (220,130,160) | (80,60,50) | hero_half_knot | face_calm | (150,104,74) | - | 1.0 |
| crowd cw14 | gk/set_gk.py:255 | (240,150,60) | (70,70,80) | hero_low_bun | face_grin | (170,118,84) | - | 1.0 |
| crowd cw15 | gk/set_gk.py:255 | (120,120,200) | (50,50,60) | hero_long_straight | face_shy | (240,200,170) | - | 1.0 |
| crowd cw16 | gk/set_gk.py:255 | (200,90,70) | (60,60,90) | hero_slick_back | face_sweet | (236,190,150) | - | 1.0 |
| crowd cw17 | gk/set_gk.py:255 | (90,150,200) | (80,60,50) | hero_pixie | face_wink | (226,176,140) | - | 1.0 |
| crowd cw18 | gk/set_gk.py:255 | (230,190,80) | (70,70,80) | hero_crop | face_bright | (190,140,100) | - | 1.0 |
| crowd cw19 | gk/set_gk.py:255 | (150,80,160) | (50,50,60) | hero_long_tie | face_starry | (200,150,112) | - | 1.0 |
| crowd cw20 | gk/set_gk.py:255 | (90,170,110) | (60,60,90) | hero_side_wave | face_bold | (120,84,60) | - | 1.0 |
| crowd cw21 | gk/set_gk.py:255 | (220,130,160) | (80,60,50) | hero_twin_tails | face_cheeky | (150,104,74) | - | 1.0 |
| crowd cw22 | gk/set_gk.py:255 | (240,150,60) | (70,70,80) | hero_half_knot | face_calm | (170,118,84) | - | 1.0 |
| crowd cw23 | gk/set_gk.py:255 | (120,120,200) | (50,50,60) | hero_low_bun | face_grin | (240,200,170) | - | 1.0 |
| crowd cw24 | gk/set_gk.py:255 | (200,90,70) | (60,60,90) | hero_long_straight | face_shy | (236,190,150) | - | 1.0 |
| crowd cw25 | gk/set_gk.py:255 | (90,150,200) | (80,60,50) | hero_slick_back | face_sweet | (226,176,140) | - | 1.0 |
| water crowd wtw0 | nx/set_refl.py:91 | water blues | water blues | hero_crop | face_bright | water | - | 1.0 |
| water crowd wtw1 | nx/set_refl.py:91 | water blues | water blues | hero_long_tie | face_starry | water | - | 1.0 |
| water crowd wtw2 | nx/set_refl.py:91 | water blues | water blues | hero_side_wave | face_bold | water | - | 1.0 |
| water crowd wtw3 | nx/set_refl.py:91 | water blues | water blues | hero_twin_tails | face_cheeky | water | - | 1.0 |
| water crowd wtw4 | nx/set_refl.py:91 | water blues | water blues | hero_half_knot | face_calm | water | - | 1.0 |
| water crowd wtw5 | nx/set_refl.py:91 | water blues | water blues | hero_low_bun | face_grin | water | - | 1.0 |
| water crowd wtw6 | nx/set_refl.py:91 | water blues | water blues | hero_long_straight | face_shy | water | - | 1.0 |
| water crowd wtw7 | nx/set_refl.py:91 | water blues | water blues | hero_slick_back | face_sweet | water | - | 1.0 |
| water crowd wtw8 | nx/set_refl.py:91 | water blues | water blues | hero_pixie | face_wink | water | - | 1.0 |
| water crowd wtw9 | nx/set_refl.py:91 | water blues | water blues | hero_crop | face_bright | water | - | 1.0 |
| water crowd wtw10 | nx/set_refl.py:91 | water blues | water blues | hero_long_tie | face_starry | water | - | 1.0 |
| water crowd wtw11 | nx/set_refl.py:91 | water blues | water blues | hero_side_wave | face_bold | water | - | 1.0 |

## Faces and hair

- `lib.py` reads hair from `.../last-caravan-build-r001/assets-src/hair/player-20261031-r001/models/` and faces from `.../last-caravan-hero-faces/20261031-r001/catalog/png/`. Both are the October 31 libraries on the PC.
- Shocked, scared and angry faces (with talking-mouth and blink frames) were drawn by `faces_new/mkfaces.py`, included here. Run it to regenerate the PNGs.
- Crowd rows are worked out from the formulas in `gk/set_gk.py` (`SHIRTS[i % 8]`, `PANTS[i % 4]`, `HAIRS[(i*5) % 9]`, `FACES[(i*4) % 9]`, `SKINS[(i*3) % 8]`), so the table matches the code exactly.
