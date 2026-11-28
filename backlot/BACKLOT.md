# Backlot: Town Square, Bridge & River, Throne Hall, Castle Courtyard, Forest Edge, Harbor

Six ready-to-shoot, pre-lit sets for In This Town films (v1: the first three; Nov 27 evening: CC0 photo-scan
textures on all of them + three new places). Realistic weathered materials, bright saturated
daylight, moonlit nights with warm practicals. Scale 1 m = 3.3 BU (Cast v2 Hero kid = 4.16 BU).

| Set | File | Collection to append | Code |
|---|---|---|---|
| Town Square | `town_square/town_square.blend` | `Backlot | Town Square` | `TS` |
| Bridge & River | `bridge_river/bridge_river.blend` | `Backlot | Bridge and River` | `BR` |
| Throne Hall | `throne_hall/throne_hall.blend` | `Backlot | Throne Hall` | `TH` |
| Castle Courtyard | `castle_courtyard/castle_courtyard.blend` | `Backlot | Castle Courtyard` | `CC` |
| Forest Edge | `forest_edge/forest_edge.blend` | `Backlot | Forest Edge` | `FE` |
| Harbor | `harbor/harbor.blend` | `Backlot | Harbor` | `HB` |

Previews: `previews/<set>_<CAMERA>_<PRESET>.jpg` (WIDE_ESTABLISH and LOW_HERO at 1080x1920 for DAY and NIGHT;
the other bookmarks and the GOLDEN wides at 540x960) and `previews/<set>_contact.jpg` (tiles marked `(v1)` were
rendered before the CC0 textures). Material sheet: `previews/material_catalogue.jpg` (scanned swatches marked
`*`). Before / after of the texture pass: `previews/before_after_town.jpg` (town_square LOW_HERO DAY).
Previews show Cast v2 people standing on the marks for scale; the people are NOT in the set files.

## How to use a set

**By hand:** File > Append > `<set>.blend` > Collection > `Backlot | <Set>`. Then pick the light preset (below).
Each .blend also opens as three ready scenes, `<Set> DAY`, `<Set> GOLDEN`, `<Set> NIGHT`, which share every
object and differ only in lights, sky and exposure; open one, pick a camera, render.

**By script (recommended for builders):**
```python
import sys; sys.path.insert(0, '/tmp/claude-0/backlot/source')   # or wherever the backlot folder lives
import backlot_api as bl
bl.append_set('town_square', scene, preset='DAY')       # appends the collection + its 3 skies
bl.use_preset(scene, 'town_square', 'NIGHT')            # switch any time (lights, sky, exposure)
scene.camera = bl.camera('town_square', 'LOW_HERO')
bl.drop_on_mark(hero_root, 'town_square', 'MARK_HERO')  # Cast v2 root -> mark (location + facing)
bl.render_settings(scene, 'final')                      # the settings below
```
Inside the collection: `<CODE> Set` (geometry), `<CODE> Marks`, `<CODE> Cameras`, and `<CODE> Light DAY|GOLDEN|NIGHT`.
A preset = include exactly one Light collection (the others excluded in the View Layer) + set the world
`<CODE> Sky <PRESET>` + exposure. The skies travel with the collection (they are referenced from custom
properties on the collection: `world_DAY`, `world_GOLDEN`, `world_NIGHT`, `exposure_*`).
Night-only meshes (lit window panes, candle and torch flames, lantern flames) live in the NIGHT collection, so
lanterns are dark by day and lit at night with no drivers. In the Throne Hall the stained glass and the light
shafts are per preset too (bright by day, warm at golden hour, faint blue at night); braziers burn in all presets.

Every object has scale 1 and real dimensions. Origins: houses and big props sit under named empties
(`TS House W2`, `TS Town Hall`, `BR Gatehouse Cinderpass`, ...): move the empty to move the whole building.

## Light presets

| Preset | Sun / moon | Sky | Exposure | Practicals |
|---|---|---|---|---|
| DAY | warm white sun, 4.2 (hall 6.0), 52 deg up | saturated blue gradient + painted clouds | -0.55 (hall -0.1) | none (hall: braziers, candles) |
| GOLDEN | orange sun 4.0, 13 deg up, long shadows | blue to orange horizon, peach clouds | -0.35 (hall 0) | none (hall: braziers, candles) |
| NIGHT | blue moon 0.55-1.2 + soft moon fill | deep blue, stars, moonlit clouds | +0.6 (bridge +1.0, hall +0.35) | lanterns, lamp posts, lit windows, torches |

Colour management: View transform **Standard**, look **Medium High Contrast** (punchy, not pastel), gamma 1.
The sky shader shows its colours at full saturation to the camera and lights the set separately
(`SKYLIGHT` background node), so the sky stays blue whatever the exposure.

## Camera bookmarks (all 9:16, 1080x1920, sensor 36 mm fit AUTO = vertical)

Names are `<CODE>_<BOOKMARK>`; lens and a one-line note are stored on each camera (`lens_mm`, `note`).

**Town Square** — WIDE_ESTABLISH 18 mm (from the south street mouth: town hall, clock tower, fountain, stalls) ·
LOW_HERO 20 mm (knee height up at the hero, town hall and balcony behind) · CROWD_MED 35 mm · TWO_SHOT 35 mm ·
CLOSE_A 50 mm (hero) · CLOSE_B 50 mm (rival) · INSERT_RANKING 35 mm (ranking board) · INSERT_SIGN 45 mm (the
sunlit locksmith 'key' sign on the north row) · INSERT_FOUNTAIN 30 mm · WIDE_REVERSE 20 mm (from the balcony over
the square to the south street).

**Bridge & River** — WIDE_ESTABLISH 20 mm (west bank downstream: river, three-arch bridge, gatehouse, town) ·
LOW_HERO 20 mm (low on the deck, sky and parapet) · CROWD_MED 26 mm (along the deck to the gate) · TWO_SHOT
35 mm (raised, from over the downstream water: the stand-off on the bridge with the river behind) · CLOSE_A /
CLOSE_B 50 mm · INSERT_WATER 35 mm (foam at a cutwater) · INSERT_MILL 35 mm (mill wheel) ·
UNDER_ARCH 22 mm (low over the water through the central arch).

**Throne Hall** — WIDE_ESTABLISH 18 mm (from the doors down the carpet to the throne) · LOW_HERO 20 mm (hero in
front of the dais, throne + canopy + rose window behind) · CROWD_MED 28 mm (down the carpet from the west) ·
TWO_SHOT 30 mm · CLOSE_A / CLOSE_B 50 mm · INSERT_THRONE 35 mm · INSERT_WINDOW 24 mm (lancets and light shafts) · RULER_POV 24 mm.

**Castle Courtyard** — WIDE_ESTABLISH 18 mm (from inside the gate: well, stair up to the keep, banners, turrets) ·
LOW_HERO 20 mm (knee height up at the hero, stair and keep behind) · CROWD_MED 28 mm (from the training-yard side) ·
TWO_SHOT 35 mm · CLOSE_A / CLOSE_B 50 mm · INSERT_WELL 30 mm · INSERT_GATE 24 mm (open gates, raised
portcullis) · WIDE_REVERSE 20 mm (from the keep landing over the courtyard to the gate: the ruler's view).

**Forest Edge** — WIDE_ESTABLISH 18 mm (from the last houses up the dirt road to the dark forest wall) ·
LOW_HERO 20 mm (hero on the road, the road vanishing into the trees behind) · CROWD_MED 35 mm · TWO_SHOT 35 mm ·
CLOSE_A / CLOSE_B 50 mm · INSERT_SIGNPOST 35 mm (word boards FOREST / TOWN / CASTLE) · INSERT_FOREST 24 mm (into
the trees along the road: toadstools, bushes, trunks) · WIDE_REVERSE 20 mm (from the tree line back to the town).

**Harbor** — WIDE_ESTABLISH 18 mm (from the harbor houses over the quay: jetties, boats, breakwater, lighthouse) ·
LOW_HERO 20 mm (hero on the quay, jetty and red sail behind) · CROWD_MED 28 mm (from the east, crowd framing the edges) · TWO_SHOT 35 mm · CLOSE_A /
CLOSE_B 50 mm · INSERT_BOAT 30 mm (the red-sail boat at the jetty) · INSERT_DOCK 24 mm (low along the jetty
planks) · WIDE_REVERSE 20 mm (from the jetty head back to the quay and houses).

## Character marks

Empties (ARROWS) named `<CODE>_MARK_*`. Copy location + Z rotation onto a Cast v2 root (`bl.drop_on_mark`).
The mark's rotation is the character's facing: Cast v2 faces -Y, so a mark at 0 deg faces -Y.

| Mark | Town Square | Bridge & River | Throne Hall |
|---|---|---|---|
| MARK_HERO | south of the hall steps, 3/4 to camera | on the deck west of the crown | on the carpet before the dais |
| MARK_RIVAL | facing the hero | facing the hero | facing the hero |
| MARK_SIBLING | beside the hero | behind the hero | beside the hero |
| MARK_RULER | town hall balcony (z 4.9 m) | gatehouse battlement (z 8.7 m) | standing on the dais in front of the throne (`TH_MARK_RULER_SEATED` = on the seat, for a sitting pose) |
| MARK_CROWD_1..8 | arc around hero/rival, facing them | east and west bridge ends | both sides of the carpet |
| MARK_GIANT | NE of the square (25 m creature fits, roofs ~14 m) | standing in the river below the bridge (bed) | mid-hall: vault apex is 17.5 m, so a 25 m creature must crouch or kneel |
| extras | MARK_GUARD_1..2 at the hall doors | MARK_BOAT (on the water) | MARK_GUARD_1..6 (dais, throne, doors), MARK_RULER_SEATED |

Preview cast note: the Wizard (CROWD_6) and the Villain (CROWD_8) of Cast v2 carry staffs with glowing orbs
(materials `orbm` blue, `glowp` purple, emission 5-6). By day they clip to white and read as floating lamp globes,
so the previews dim them (DAY 0.25, GOLDEN 1.0, NIGHT as built; `render.py`). Films using Cast v2 by day should do
the same: `bpy.data.materials['orbm'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0.25`
(and `glowp`). No lamp, lantern or lighthouse in the sets is lit by day: their flames, lit panes and glows live in the
NIGHT collections (only the throne hall's indoor braziers and candles burn in every preset).

| Mark | Castle Courtyard | Forest Edge | Harbor |
|---|---|---|---|
| MARK_HERO | courtyard centre, in front of the keep stair | on the dirt road past the signpost | on the quay by the main jetty |
| MARK_RIVAL / SIBLING | facing the hero / beside the hero | facing the hero / beside the hero | facing the hero / beside the hero |
| MARK_RULER | keep landing at the top of the 12-step stair (z 3.0 m) | roadside verge by the signpost | head of the main jetty (z 0) |
| MARK_CROWD_1..8 | both sides of the stair foot and the training yard | on the road between the fences (6-8 further up the road) | along the quay and the jetty root |
| MARK_GIANT | NE corner of the courtyard (walls 7 m, keep 17 m) | among the trees west of the road | standing in the harbor water (on the bed, z -3.6 m) |
| extras | MARK_GUARD_1..2 inside the gate, MARK_GUARD_3..4 on the keep landing | MARK_GUARD_1..2 at the town lamps, MARK_FOREST (where the road enters the trees) | MARK_GUARD_1..2 on the quay, MARK_BOAT (on the red-sail boat) |

## What is in each set

**Town Square** (32 x 28 m square, cobbles everywhere): 19 half-timbered town houses round the square plus 7
backdrop houses, all from a generator (2-3 storeys,
jettied upper floors with joist ends and brackets, timber framing in four styles, plaster in six colours with
cracks, stains and patches of exposed brick, stone ground floors with quoins, leaded casements with painted
shutters, flower boxes, planked doors with strap hinges, clay / slate / shingle roofs with sagging ridges,
dormers, chimneys with pots, slight lean on every house) · Town hall with a 4-arch arcade, balcony, heraldic
banners, slate roof with dormers and iron cresting, notices on the end pier · clock tower with two working-looking
clock faces, belfry and bell, slate spire and weathervane · two-tier fountain with overflow streams, pool and
moss · 4 market stalls with striped canvas awnings and goods (apples, bread, cloth, pots) · ranking board with
10 blank name plaques + a gold header plaque (separate objects `TS_RANK_PLAQUE_01..10`, `TS_RANK_PLAQUE_HEADER`,
each with a text anchor empty `TS_RANK_TEXT_xx` whose local Z faces out of the plaque; `text_height_bu` and
`text_width_bu` custom properties give a safe text size) · hanging shop signs (mug, loaf, boot, key, potion,
horseshoe, sword) · wall lanterns and 5 lamp posts (lit at night) · carts (hay, barrels), hay bales, barrels,
crates, pumpkins · laundry lines across two alleys · pigeons · backdrop houses and the Swanveil castle on a hill.

**Bridge & River**: hump-backed three-arch stone bridge (40 m, 4.2 m road for a cart, cobbled deck, parapets
with coping stones, voussoirs, string course, pointed cutwaters, end pillars, a lantern at the crown), river
21 m wide flowing towards the WIDE camera (water at -1.8 m, bed at -2.9 m, same numbers as the Fake Power
FP_Bridge, so the two can stand in for each other) with real depth colour, animated ripples and painted foam
at piers, rocks, banks and the mill wheel · terrain blending pebbles, wet mud and grass by height · reeds and
cattails along both banks, grass tufts, boulders, 18 oaks and willows (9000 leaf cards each) · dirt road west, cobbled road east · the
Cinderpass gatehouse (re-skinned) as the town gate with torches, town wall with round towers, 10 town houses
behind it · a mill with an undershot wheel in the river.

**Throne Hall** (18 x 34 m, vault apex 17.5 m): polished marble floor (cream and black, per-tile tilt, worn
paths) · 12 clustered pillars with gold bands and leaf capitals · pointed arcades, pointed barrel vaults with
stone ribs and gold bosses · 10 stained-glass lancets and two rose windows (glass colours the sunlight on the
floor) · subtle fake light shafts per preset · 5-step marble dais with gold nosings · carved throne (gold, dark wood,
red velvet, crown emblem) under a velvet-valanced canopy · velvet drapes and a giant crown banner · long red
carpet with gold border running up the steps · 12 heraldic banners on the pillars · 6 braziers with fire, 4
candelabras, 2 ring chandeliers · benches in the aisles · great double doors with studs and ring pulls.

**Castle Courtyard** (bailey 30 x 25 m): crenellated curtain walls 7 m high with wall walk and a stair up to
it, four round corner towers with slate cones and gold finials · twin-tower gatehouse with a round-arched passage,
raised iron portcullis, open studded oak gates, torches, gold-lion and silver-tower banners · the keep (14 x 8 m,
17 m to the battlements) with arched leaded windows (lit at night), string courses, crenellated top, four
corbelled corner turrets with tall slate cones and red pennants, two tall banners (gold lion, black dragon) ·
12-step stone stair with low side walls, newel posts with stone balls, up to a landing at 3 m before the red
door (MARK_RULER) · cobbled courtyard with a flagstone path and a paved ring round the well (shingle roof) ·
stable lean-to with stalls, hay and a water trough · two-storey kitchen house (timber-framed, lit windows,
lantern) · training yard: two straw dummies with bucket helmets, two archery targets · braziers at the stair
foot (burning at night), barrels, crates, apple crate, two carts, hay, pigeons · outside: grass, rolling hills,
oaks, the dirt road leaving the gate.

**Forest Edge**: the last six town houses (generator) on a short cobbled street with three lamp posts · a dirt
road (scan, displaced) curving north between split-rail pasture fences, rising gently into the forest ·
signpost with three painted word boards (FOREST / TOWN / CASTLE, big capitals a 3rd grader can read) · hay
bales, a hay cart, two pasture oaks · the forest: 34 big oaks 14-20 m tall (dark leaf cards) on a leaf-litter
floor (forest_floor scan), extra trunks and dark canopy masses behind so no sky shows through, bushes along the
road, red-and-white toadstools, rocks, a fallen log and a stump, grass tufts along the fences · night: lit
windows, lamp posts and 70 fireflies glowing at the forest edge · distant hills. The forest is instanced: 64 oaks,
130 canopy masses and 150 bushes are linked copies of 6 + 4 + 3 prototypes (`FE Oak 1..6`, `FE Canopy Mass 1..4`,
`FE Bush 1..3`; editing a prototype's mesh changes all its copies). DAY and GOLDEN carry extra canopy light
(`FE canopy bounce`, `FE canopy edge fill`, 8 `FE dapple` spots) so the trees read dark green, not black;
NIGHT has none of it.

**Harbor**: nine harbor houses (generator; mug, potion and horseshoe signs, a shop) on a cobbled quay ·
quay wall with coping stones and a water stair · main timber jetty (20 m) with a T-head, a second jetty, posts
with weed bands at the waterline, mooring posts with rope, five lanterns on posts (lit at night) · four boats:
red-sail boat at the main jetty (lantern at night, MARK_BOAT), fishing boat, green rowing boat with oars,
yellow boat with a blue sail out in the harbor · water (still-water shader with depth colour) over a rocky bed
· breakwater of big rocks and a red-and-white lighthouse with a lamp (glows and lights the water at night) ·
fish stall with a FISH board, crates, barrels, rope coils, bollards, a cart, nets drying on poles, lamp posts,
seagulls on the quay and bollards · two headlands with open sea and horizon between them behind the lighthouse.
Sun: DAY from the east-south-east and GOLDEN low from the west, so the house row does not shade the quay.

## Material library (`materials/mats.py`)

Every material is `BL <Name>`: a procedural surface group `BLS <Name>` (Color, Roughness, Metallic, Normal,
Height in metres, Cavity) + the shared wear group `BLW Wear` (edge wear from AO-inside, grime in crevices,
moss on up- and north-facing (+Y) faces and in joints, damp band near each material's ground level, rain
streaks) + Principled BSDF. Ground, roofs, flagstones and thatch use real displacement (adaptive subdivision
on the `... D` objects); everything else uses bump. Textures are sized in metres through the `UVm` UV map
that every backlot mesh carries.

Families: cobbles (wet with puddles / dry), flagstones, mud, pebbles, grass, moss, dirt, rock, riverbank blend ·
ashlar (warm, grey, hall, bridge with a waterline stain), stone drums, rubble, brick, limestone · plaster
(cream, ochre, rose, white, sage, blue, hall) · timber (dark, oak), planks (brown, pale, grey), painted wood
(green, red, blue, yellow) with chips · roof clay (new, old), slate, shingle, thatch · iron (rusty, black),
brass, gold, steel, copper verdigris · canvas stripes (red, blue, green, yellow, plain), cloth (6 colours),
velvet (red, blue, purple), royal carpet, rope, parchment · marble floor, marble white / dark · water
(river, river along Y, still, thin, falling), leaded glass, lit window glass, clear glass, stained glass
(day / golden / night), flames, embers, glows, light-shaft cards · hay, produce (apples, pumpkin, orange,
cabbage, bread), leaves, reeds, bark, wax, terracotta, feathers, leather, charcoal, foam.

Global switches: node group `BL Global` (Value nodes `Wet` 0..1, `AO` 1/0, `Moss`, and `Time` = frame/24 via a
simple-expression driver that drives water ripples and flames; no Python auto-run needed).

## CC0 photo-scan textures (Nov 27 pass)

The sets now use the CC0 photo-scan pack staged at `/mnt/user-data/uploads/3d-models/cc0-textures/`
(Poly Haven / ambientCG, CC0 1.0, see its `SOURCES.md`; 2K JPG maps, normal = OpenGL +Y). Each pick was chosen
from 540x960 test renders with Cast v2 on the marks, judged at phone size against the procedural material.

**How the textures are linked (not packed):** the scan images are *linked* with paths relative to each .blend
(`//../../../../mnt/user-data/uploads/3d-models/cc0-textures/<folder>/<map>.jpg`), so none of the 348 MB pack is
copied and the .blend files stayed small (Town Square 19.4 MB, Bridge 21.2 MB, Throne Hall 4.4 MB, Castle
Courtyard 9.7 MB, Forest Edge 18.2 MB, Harbor 7.1 MB). The banner / sign art (small JPG/PNG made from the pack's
`custom/` art and the v1 paintings) stays packed. **Moving a set to another machine:** copy the pack to the same
relative place, or run `python3 -I source/apply_cc0.py <pack> --packed` to also write `<set>_packed.blend`
with every image packed (+15 MB for the hall up to +115 MB for the bridge / forest, ~500 MB for all six;
not written here because disk is tight).
If the pack is missing, Blender shows those surfaces pink; `mats.use_procedural(name)` (or re-running
`build_<set>.py`) brings back the procedural version.

**Render proxies (memory):** Cycles holds textures uncompressed (2K RGB = 16 MB, 2K grey = 4 MB), so the full
2K scans add ~0.4-0.6 GB per set. `textures_1k/` (20 MB, built by `source/tex_proxy.py`) holds 1K copies of
the used maps; `render.py` swaps to them in memory (`backlot_api.use_texture_proxies(keep=['cobblestone_02'])`
keeps the hero cobbles at 2K). Nothing is saved with the proxy paths. On a desktop with RAM to spare, render
with the full 2K maps (`render.py ... full`). Also for memory: no AO maps are loaded (the wear stack's AO does
crevice grime; the displacement map feeds the cavity), and displaced surfaces get no normal map (a tangent
normal map would make Cycles store UV tangents on every micropolygon).

**How a scan is applied** (`mats.CC0_PICKS`, `mats.apply_picks`, `python3 -I source/apply_cc0.py [pack]`):
the material keeps its name, wear stack (edge wear, grime, moss, damp, streaks), and its displacement on the
ground and roofs. Only the `SURF` group is swapped (`BLI <name>` = scan, `BLS <name>` = procedural;
`mats.use_procedural(name)` / `mats.use_scan(name)` switch back and forth). Per pick: real tile size in metres
on the `UVm` map (or object space for flat ground), grain along the beams (`rot90`, per-island offsets), tint
to a target colour (so one ashlar scan gives warm ashlar, grey ashlar and pale limestone), desaturation,
anti-tiling (a second rotated sample blended by noise, only on direction-free scans like plaster, dirt and
mud), slow world-space brightness variation, and puddles in the low spots of the scanned cobbles (night
glints). Plaster uses *detail* mode: the procedural colours, cracks and damaged patches stay, and the scan adds
its grain and normal. `apply_cc0.py` is idempotent (`mats.reset_scans` first) and covers all six sets.

| Material | Scan (pack folder) | Notes |
|---|---|---|
| Cobbles, Cobbles Dry | cobblestone_02 | 1.15 / 1.3 m tile, 4 / 3.5 cm displacement; puddles on the wet one. cobblestone_01 lost: setts too big and dark next to the blocky kids |
| Flagstones | worn_flagstone | 2.6 m tile, desaturated toward the old grey-brown |
| Dirt (roads) | dirt_path | 3 m tile, anti-tiling, brightened |
| Forest Floor (new) | forest_floor | leaf litter under the forest-edge trees |
| Ashlar, Ashlar Grey, Ashlar Bridge, Limestone | ashlar_blocks | tinted warm / grey / pale; 2 m tile (1.6 m limestone) |
| Brick | old_brick | 2.6 m tile |
| Rubble | mossy_stone | 2.2 m tile, brightened |
| Plaster (6 colours) | aged_white_plaster | detail mode over the procedural plaster |
| Timber Dark, Timber Oak, Planks Grey | half_timber_beams | grain along the beams, tinted dark / oak |
| Planks, Planks Pale | weathered_planks | |
| Roof Clay, Roof Clay Old, Roof Slate, Roof Shingle | clay_roof_tiles, slate_roof_shingles | tinted; 3 m tile; displaced |
| Bark | tree_bark | grain up the trunk |
| Riverbank | river_pebbles + wet_mud | scanned pebbles at the waterline, mud on the slopes, procedural grass on top |

**Kept procedural (the scan looked worse or did not fit):** Gold (worn_gold reads as dull, spotty brass),
Velvet (red_velvet is a flat pink-red), Marble Floor (marble_tiles are small grey tiles; the hall needs its big
black/cream checker), Carpet Royal (dirty_carpet is a dark rug with no gold border), Iron (rusty_iron is pale
painted sheet with rust blooms), Grass (no grass scan), Rock, Stone Drums. In the **Throne Hall** the masonry
(Ashlar Hall, Plaster Hall, Limestone) stays procedural: there the ashlar scan went dark and blotchy and lost the
clean royal look. Thatch, rope and burlap are not seen by any camera, so they were not switched.

**Banners / signs from `custom/`** (Jake's own art, not CC0; laid out for the banner meshes by
`source/cc0_art.py`: cloth quilted from the art's own plain field, emblem centred, frame extended): Town Square
town-hall banners crown -> **gold lion**, sun -> **silver tower**, tavern sign -> **tavern mug**; Throne Hall
pillar banners sun -> **gold lion**, tower -> **black dragon**; the Castle Courtyard uses all four. The
embroidered art is lifted in the material (`mats.ART_LIFT`: saturation x1.2, value x1.5, less cloth
translucency) so the emblems read at phone size like the old flat ones. `castle_tapestry` and `knight_and_sun`
are not used (square pictures; no tapestry or window surface of that shape in the sets yet).

**HDRIs:** not used. The pack's skies are cloudless (sunny_midday) or overcast (cloudy_day), at 2K they are
soft behind an 18 mm lens at 1080x1920, and `moonlit_night` is a daytime sky with the moon in it. The
procedural skies (saturated blue + painted clouds, starry night) read better for these films.
`apply_cc0.py --hdri` still puts them behind the presets if wanted.

## Render settings and cost

`backlot_api.render_settings(scene)`: Cycles, adaptive sampling (threshold 0.01), OpenImageDenoise with
albedo + normal, bounces 8 / diffuse 3 / glossy 3 / transmission 8, indirect clamp 8, no caustics, dicing
rate 1.5 px (offscreen x6), persistent data on for animation. Scene sizes: Town Square 377k faces before
displacement, Bridge 355k, Throne Hall 51k; files see the CC0 section (scans linked, art packed, compressed).

**Previews / finals as rendered here (Nov 27 CC0 pass):** `source/render.py <set> <PRESET> <CAM> 100 16 1
<outdir> 1k:cobblestone_02 split 2` then `source/denoise_exr.py <outdir>/exr/*.json` (queues:
`final_queue_cc0.sh`, `final_queue_cc0b.sh`, `final_queue_new.sh`). 16 spp adaptive (0.015), dicing 3 px
(4 px for the wides), offscreen dicing x16, 512 tiles, 1K texture proxies except the hero cobbles, one camera
per process. **Why split:** Cycles' own denoiser holds the whole 1080x1920 frame plus its passes, about 1 GB
on top of the scene (a town final denoised inside the render peaked at ~3 GB). In `split` mode the render
writes the noisy image + denoising passes (albedo, normal, vector) as two overlapping horizontal bands to
EXR, and a separate small process denoises each band with OIDN, colour-manages it exactly like the render
(Standard / Medium High Contrast / the preset's exposure) and cross-fades the bands into the JPG. Same look as
the in-render denoise; peaks: render 1.1-1.8 GB, denoise 1.40-1.48 GB. On a desktop with RAM, plain
`render.py ... cycles` (in-render OIDN) is simpler.

Measured on this container (2 CPU cores, shared with other jobs part of the time), 1080x1920, 16 spp + OIDN:

| Set | WIDE_ESTABLISH DAY / NIGHT | LOW_HERO DAY / NIGHT | Peak RAM (render / denoise) |
|---|---|---|---|
| Town Square | 188-327 s / 204-405 s | 193-514 s / 214-352 s | 1.63-1.85 GB / 1.48 GB |
| Bridge & River | 201 s / 202 s | 90 s / 115 s | 1.73-1.77 GB / 1.48 GB |
| Throne Hall | 388 s / 544 s | 357 s / 638 s | 1.11 GB / 1.48 GB |
| Castle Courtyard | 331 s / 311 s | 395 s / 250 s | 1.37-1.52 GB / 1.40 GB |
| Forest Edge | 269 s / 289 s | 304 s / 312 s | 1.43-1.57 GB / 1.40 GB |
| Harbor | 153 s / 153 s | 99 s / 108 s | 1.31-1.42 GB / 1.40 GB |
Plus ~20-50 s per shot for the denoise step. The longer town times are the re-render that ran beside a film
encode and a cast render; the lower ones had both cores.

Older v1 numbers (procedural, in-render denoise, a film render sharing the CPU): town 209-633 s, bridge
250-697 s, hall 684-824 s per 1080x1920 frame.

Relative cost: Throne Hall (glossy marble, glass, many lights) > Town Square (displaced cobbles over a big area,
30 houses) > Bridge. NIGHT costs about the same as DAY. 540x960 tests take about a quarter of the time.

What looks good, and what it costs:
- **Stills / held shots:** the preview settings above (16 spp adaptive + OIDN) are clean at phone size.
- **Animation:** use 32-64 spp (adaptive threshold 0.01) so the denoiser does not shimmer on cobbles, reeds
  and leaves; roughly 2-4x the times above per frame. Persistent Data on saves the scene sync per frame.
- **Displacement:** dicing 1 px is the sharpest cobble/roof relief but doubles memory; 2 px is nearly
  identical at 1080x1920; 3 px is fine for wides. `Scene > Render > Subdivision > Dicing Rate`.
- **AO wear switch:** `BL Global > AO = 0` drops edge wear and crevice grime: about 17% faster, slightly
  flatter. Keep it on for hero shots.
- **Faster look-dev:** Workbench (Material colours) or 25% resolution with 8 spp.
These timings scale roughly with CPU cores; on a desktop GPU (OptiX/CUDA) expect a large speed-up, but
measure one frame on the target PC before planning a whole film.

## Source (rebuildable)

`source/build_town_square.py`, `build_bridge_river.py`, `build_throne_hall.py` (each rebuilds its .blend in
2-20 s: `python3 -I source/build_<set>.py`), `geo.py` (metre mesh builder, UVm rules), `kit.py` (houses,
town parts, props, trees, water wheel), `look.py` (skies, suns, cameras, marks, preset scenes), `setbase.py`
(collections, saving, re-skinning the older Marches models), `art.py` (sign and banner paintings), `castref.py`
+ `render.py` + `contact.py` (previews), `wb_all.py` (Workbench framing sheet of every camera, cast on marks),
`final_queue.sh` / `final_queue2.sh` (the v1 preview render queues), `catalogue.py` (material sheet; `--cc0` shows the
scan swatches), `apply_cc0.py` (switch all six sets to the CC0 photo-scans), `backlot_api.py` (film use).
Added in the Nov 27 pass: `build_castle_courtyard.py`, `build_forest_edge.py`, `build_harbor.py` (3-8 s each;
run `apply_cc0.py --sets=<set>` after a rebuild, the build itself is procedural), `kit2.py` (fortification,
courtyard props, fences, signposts, jetties, boats, gulls, prototype instancing), `art2.py` (signpost word
boards), `cc0_art.py` (banner / sign layouts from the pack's custom/ art), `tex_proxy.py` (1K render proxies),
`denoise_exr.py` (band denoiser for `render.py ... split`), `final_queue_cc0.sh`, `final_queue_cc0b.sh`,
`final_queue_new.sh`, `job_queue.sh` (the queues of this pass; `job_queue.sh` reads `tmp/jobs.txt` and records
finished jobs in `tmp/jobs.done`, so after a crash or restart it carries on where it stopped).

Re-used from the studio library: Swanveil (castle on the hill behind the square) and Cinderpass (the bridge's
town gate), appended from `towers-of-the-marches/v001` with their flat colours replaced by backlot materials.
The Marketford houses were the reference for the generator's proportions (gable/eaves roofs, jetties,
shutters, flower boxes, signs) but are rebuilt at higher detail rather than re-skinned.

## Blender version notes

Built with bpy 5.3, using only features present in 5.1: adaptive subdivision on the Subdivision Surface
modifier (5.0+), Principled BSDF v2 sockets, `Material.displacement_method`. No geometry nodes, no Python
drivers (one simple-expression driver: `frame/24`). If an older Blender complains, turn off "Adaptive
Subdivision" on the `... D` objects and give them 3 levels of plain subdivision.

## Known limits / next steps

- The CC0 scans are linked from `/mnt/user-data/uploads/3d-models/cc0-textures/`: keep the pack there (or
  write packed copies with `apply_cc0.py --packed`) or those surfaces render pink.
- Most 540x960 extras of the first three sets (TWO_SHOT, CLOSE_B, INSERT_*, the bridge and hall CROWD_MED /
  CLOSE_*) are still v1 procedural renders (marked `(v1)` on the contact sheets). With the scans: the 12 finals,
  the GOLDEN wides, and town CROWD_MED / CLOSE_A.
- Forest Edge: looking up into the canopy (LOW_HERO, closes) the top of the frame stays dark green by design
  ("big dark trees"); the DAY/GOLDEN canopy fill lights (`FE canopy ...`, `FE dapple ...`) can be raised in
  `FILL_E` in `build_forest_edge.py` (or their power in the file) if a film wants it lighter.
- The new places' CROWD_MED frames use 28 mm: the 8 crowd marks spread wider than a 9:16 frame holds at mid
  distance, so each crowd shot shows hero, rival and 3-6 of the crowd; `tmp/cc0/scripts/frame_check.py` lists
  which marks a candidate camera sees (and whether anything blocks the hero / rival).
- Water foam is a painted vertex attribute + noise; it reads well in wides but looks speckly in the tight
  INSERT_WATER close-up. Flames are emissive meshes (no smoke or volumetrics); the hall light shafts are subtle.
- Trees, reeds and grass are procedural cards: fine at mid distance, not for macro close-ups.
- The river is straight (one reach); the mill and trees break it up, but there is no bend.
- Only Swanveil and Cinderpass were re-used directly; the Marketford buildings were rebuilt by the generator at
  higher detail instead of re-skinning their flat box shapes.
- Marks point the way a character should face for the bookmark cameras; turn the cast root after
  `drop_on_mark` if a shot needs a different facing.
