# BUILD PACKAGE: MY TINY SEED HUGGED A GIANT TROLL (tiny-seed)

**Jake approved the script (Thu 11-26, 11:48 PM) and the voice is final.** He wrote it in the Idea lab over our hit "My slime ate a dragon" (157K), line for line. **Who builds it (Jake's pick): Claude only, no Astra.** The 3D models come from Claude's model builder (see "Models" below); the film comes from the Claude Code builder on Jake's PC.

**Editions:** CLEAN for Facebook, TikTok and YouTube, plus the **Flashloop sponsor edition for Instagram** (Jake picked "Clean + Flashloop"). The sponsor ending is `sponsor-ending/SPONSOR-ENDING-V2.md` with its fixed voice file `sponsor-ending/sponsor-ending-voice.mp3` (already approved; do not re-voice). The phone prompt line for this film: **"A tiny seed hugs a giant troll."** No music bed from you: Claude adds music to the clean edition in the finishing pass.

## Files in this folder
- `tiny-seed-voice-final.mp3`: final narration, Adam, already at its final speed. **94.1 s**, about -14.6 LUFS, md5 `0d0a100ece88637fd691e7c4526bc6e7`. Never re-voice or re-time it.
- `tiny-seed-lines.srt` and `tiny-seed-word-timings.json`: caption and word timings for that mp3.
- `tiny-seed-script.txt`: the script, one caption line per line.
- `models/` (arriving from Claude's model builder): `tiny-seed-models.blend` + `MODELS.md` + previews. Start with stand-ins and swap the real models in when they land.

## Build style: Jake's mix (picking it is his yes to the overrides, this film only)
- **Base: Toybox Fable** (`styles/craftee-style/`): bright neutral game-map town, moderate saturation, locked framing, cuts on the captions, big line-art faces that change on almost every shot, prop gags. Use its `pack/` (`apply_look`, `light_rig('noon')`, `cut_plan`).
- **Camera moves from Torchlit Blocktale** (`styles/gneef-style/`): a slow push-in on almost every shot with a light handheld wobble (use its camera functions; keep the wobble small). Exception: the three big reveal moves below.
- **Captions from Torchlit Blocktale**: one white word at a time (its caption spec), keyword in the accent colour. Numbers on screen big (see the number cards).
- **Transitions and effects from Bright Snap Cut** (`styles/bright-cut/`): its whoosh or hit on about one cut in four, its punch-ins and flash frames, used sparingly.
- **Light stays Toybox daytime for lines 1-30** (bright harvest-day square). From line 31 the troll mother's shadow darkens the square (Toybox's dark beat), then hold that shadowed light to the end.

## Cast (Cast v2) and face styles
Jake picked six face styles to mix across the characters. Give each person ONE face style for the whole film:
| Who | Cast v2 | Face style |
|---|---|---|
| **Narrator ("I")**, owner of the dot seed | Girl hero (no sword on her back for this film: a small trowel in her belt instead) | **Storybook** (Astra set, `ready/faces/storybook/` on main) |
| Her best friend, beside her all story | Hero kid | **Classic Block** (`ready/faces/classic-block/`) |
| Her little sister (the one she shields at the end) | Little sister | **Anime Shine** (`ready/faces/anime-shine/`) |
| **The champion** (owner of the 9,000 oak, offers all his gold) | Rich kid | **Bold Comic Ink** (`ready/faces/bold-comic-ink/`) |
| Crowd: townsfolk with their bushes, sprouts in pots | the other Cast v2 people | **Toybox** (`styles/craftee-style/faces/`) |
| **The old garden keeper** (line 24-26, "she") | **New character, authorized by Claude:** build her with `cast_v2.py` the way the King was added: an old woman, grey hair in a bun, straw sun hat with a flower, green apron over a brown dress, garden gloves, a trowel. Push a cast check to `proofs/tiny-seed/cast-check.png` and keep building. | **Inkface** (`styles/gneef-style/faces/`) |
| Wizard (Jake added him as Mentor) | Wizard | Inkface; a cameo in the Harvest Day crowd (line 6 and 11). The garden keeper speaks, not him: the script says "she". |
The trolls and the tree have their own faces from the model pack.

## Scale ladder (keep it true)
- **The dot (stage A):** about the size of a pea next to the narrator's shoe. Broccoli for ants.
- **Bushes:** knee-to-waist high. **The champion's oak:** about 40 BU, the tallest thing in the square until line 12.
- **Baby rock troll:** about 2.5x a grown-up (~16 BU). It can squish a table; the tree can hug it like a teddy.
- **Our tree (stage C-E):** ~100 BU, taller than the castle tower. It holds the troll in its branches like a teddy bear.
- **Troll mother:** ~450 BU. When she steps onto the hill, the hill looks small. Our 100 BU tree reaches about her knee.

## Frame 0 and the cover
- **Frame 0 = the cover:** the giant blossoming tree (golden apples glowing) hugging the baby rock troll like a teddy in the sunny harvest square, its knothole face smiling; the narrator tiny in front, seen from behind; the measuring pillar beside her showing **9,001**. Title **MY TINY SEED HUGGED A GIANT TROLL** (white caps, black outline, key word "TINY SEED" in the accent colour, 9-20% band), handle top left. Toybox opening: a whip-blur that lands in 3 frames.
- Hold frame 0 about 1.6 s under the title while line 1 starts, then cut into the story.

## Number cards (on screen, big, the measuring pillar's panel glowing)
"50" on line 3 (a bush), "9,000" on line 3 (the oak), "1" on line 4 (the dot), **"9,001"** on line 12, **"900,000"** on line 33. Numbers appear on the pillar panel AND as a big card for ~0.8 s. Line 12's "9,001" is the biggest moment of the first half: the number flicks from 1 to 9,001 with a hit.

## Shot list with final times
| # | Time (s) | Line | On screen |
|---|---|---|---|
| 1 | 0.00-2.57 | In this town, every kid gets one magic seed. | Frame 0 (cover). Cut: a festival table where a kind elder hands each kid one glowing seed; the narrator takes hers. |
| 2 | 2.74-5.14 | Every sprout gets measured. That's how strong it is. | Sprouts in pots lined up at the carved measuring pillar; a kid holds a sprout to the pillar and the panel glows. |
| 3 | 5.37-8.57 | A bush is fifty. Our champion's oak is nine thousand. | A townsperson's bush, card "50". Cut: low angle up the champion's huge oak, the champion posing smugly in front, card "9,000". |
| 4 | 8.76-10.14 | Mine's a dot. A one. | Close on the narrator's palm/soil patch: the tiny dot sprout. The pillar panel: "1". The champion snorts (Bold Comic Ink grin). |
| 5 | 10.32-11.42 | It's broccoli for ants. | Gag shot: macro from ant height, two cartoon ants looking up at the dot like it's a broccoli tree. |
| 6 | 11.69-14.02 | And on Harvest Day, a rock troll came stomping. | Harvest square full of bunting, pie tables, pumpkins. Ground shakes (dust, pies hop). The baby rock troll stomps in through the gate, grumpy face. |
| 7 | 14.21-16.46 | The troll didn't stop. It just squished the pie table. | Its foot comes down on the pie table: SQUISHED version, pies splat cartoonishly. Crowd faces (staggered). |
| 8 | 16.68-19.02 | I had one idea. "Hug him first," I whispered. | Close on the narrator kneeling to the dot, whispering to it (Storybook "determined" face). Pull in on the dot. |
| 9 | 19.23-20.14 | My dot shot up. | **ANIM 1, reveal move:** the dot shoots up: stage A to B to C in under a second, soil bursting, camera tilting up fast with it. |
| 10 | 20.34-22.40 | It grabbed the troll. Gently. Like a teddy. | Tree arms wrap the troll (TREE_HUG): the troll lifted off its feet, surprised face. Cut: close, the tree's face content, the troll squished cheek-to-bark like a teddy. |
| 11 | 22.60-24.10 | Nobody cheered. Nobody moved. | Wide: the whole crowd frozen mid-gasp (they still breathe and blink). The champion's mouth open. |
| 12 | 24.32-26.98 | Then my tree got measured. Nine thousand and one. | The pillar panel flicks from "1" to **"9,001"** with a hit; big card. The champion's face drops. |
| 13 | 27.28-28.97 | A tiny seed grows when it's needed. | Gold caption line. Warm shot of the narrator looking up at her tree, sun through the leaves. |
| 14 | 29.14-32.11 | It grew branches. Then blossoms. Then golden apples. | **ANIM 2:** three quick beats on the canopy: branches stretch, blossoms pop open, golden apples swell and glow. |
| 15 | 32.33-35.56 | The champion stared at his oak. Ten years, it was the tallest. | The champion beside his oak, which now looks small under our tree's shadow. A "10 YEARS" tag on his oak. |
| 16 | 35.75-37.78 | Every bush in town leaned toward my tree. | Gag: every bush and potted sprout in the square leans toward our tree like sunflowers, one after another (staggered). |
| 17 | 37.95-40.34 | I pointed at the broken tables. My tree fixed them. | The narrator points. A branch lifts the squished table and pats it back to normal (FIXED version), the pies pop back up. |
| 18 | 40.54-42.95 | Then it handed me an apple. From across the square. | **ANIM 3:** a long branch reaches across the whole square (TREE_GIVE) and places a golden apple in her hands. |
| 19 | 43.16-46.24 | So the champion made me an offer. All his gold. For my tree. | The champion drags over a cart heaped with gold coins and holds out a bag, grinning. |
| 20 | 46.40-48.81 | A tree. Or a mountain of gold. Which would you pick? | Split frame: the tree vs a mountain of gold. A/B chips flash small: A: TREE / B: GOLD. (Jake's hit does this mid-video; keep it.) |
| 21 | 49.08-52.33 | I kept my tree. "But the troll can go," I said. "Let go." | The narrator pushes the gold bag back (stick-it-to-them smile). Then she looks up and says "Let go". |
| 22 | 52.56-56.00 | Out rolled the troll. Giggling like a baby. Not one grump left. | **ANIM 4:** the branches open and the troll rolls out across the square like a boulder, stops on its back, kicking its feet, GIGGLE face. |
| 23 | 56.19-58.07 | A tree hug squeezes out all the grumpy. | Gold caption line. A little puff of grey "grump" cloud floats away from the troll. |
| 24 | 58.27-60.74 | Then the old garden keeper grabbed my arm. She was shaking. | The garden keeper (new character) grabs the narrator's arm, hand trembling, eyes wide. |
| 25 | 60.95-65.18 | "Tiny seeds don't listen," she said. "Not to anyone. Not in a thousand years." | Close on the keeper speaking. Cut: an old carved stone in her garden showing a dot seed and "1000 YEARS". |
| 26 | 65.41-67.91 | "It hugged when you said hug. It let go when you said so." | Two quick flash inserts: the hug (line 10) and the release (line 22). Back to the keeper's face. |
| 27 | 68.16-72.00 | A tiny seed can grow into anything. It just never does. That's why it's a one. | Gold caption line. The narrator's open hand with a new dot seed glowing on it; behind it, the tree. |
| 28 | 72.24-73.51 | Mine does. For me. | The tree's face looks down at the narrator and blinks, slowly. |
| 29 | 73.72-76.30 | Nobody ever woke a tiny seed. Until today. | The crowd staring at the narrator (staggered head turns). |
| 30 | 76.52-78.88 | Then the giggling troll sniffled. One rumble. | The baby troll stops giggling, lip wobbles (SNIFFLE face). A low rumble: the pies on the tables jump once. |
| 31 | 79.02-80.27 | And a shadow covered the sun. | A shadow sweeps over the whole square; daylight drops to the dark beat. Everyone looks up. |
| 32 | 80.47-82.94 | Something stomped onto the hill. The hill looked small. | **Reveal move:** the hill behind the town; a gigantic mossy foot lands on it and the hill suddenly looks small. Dust rolls. |
| 33 | 83.11-84.97 | Its mother. Nine hundred thousand. | Slow tilt up the troll mother (STERN face) against the sky. The pillar panel bursts: **"900,000"** card. |
| 34 | 85.16-86.83 | Nine thousand and one was a pebble. | Wide: our 100 BU tree comes up to about her knee. The "9,001" card shrinks to a pebble-sized number. |
| 35 | 87.02-88.78 | Everybody ran. My tree didn't. | The crowd scatters (the champion first, dropping his gold). The tree stays planted. |
| 36 | 88.95-91.16 | It bent its branches around me. And it looked down. | TREE_PROTECT: branches curl around the narrator and her little sister. The tree's face looks down at her. |
| 37 | 91.37-94.09 | It was waiting for one word. Would you say "hug"? | Close on the narrator's face, the giant mother's eye in the sky behind the leaves. Then the end screen. |

## End screen (signature, over the final shot)
Printed question: **WOULD YOU SAY "HUG"?** Chips: **A: HUG** / **B: RUN**. Follow line: **FOLLOW FOR MORE "IN THIS TOWN"** (no Part 2 promise). In the sponsor edition the Flashloop ending (V2) follows the end screen.

## Animation moments (3-5, 2-4 s each)
1. The dot shoots up into the giant tree (line 9).
2. Branches, blossoms, golden apples (line 14).
3. The long branch hands her the apple across the square (line 18).
4. The troll rolls out giggling (line 22).
5. Optional: the mother's foot landing on the hill (line 32).

## Models (Claude's model builder, NOT Astra)
Claude's model builder is making, in Blender, at the scales above: our tree in stages (A dot, B shooting up, C giant, D blossoms, E golden apples) with a face and an armature with named poses TREE_REST / TREE_HUG / TREE_GIVE / TREE_PROTECT; the champion's oak; bushes; the baby rock troll (GRUMPY, GIGGLE, SNIFFLE, SURPRISED faces, stomp/roll rig); the troll mother (STERN, SOFT); the measuring pillar with a glowing blank panel; the pie table (normal, SQUISHED, FIXED); golden apples. They will land in `tiny-seed/models/` on this branch with `MODELS.md` (names, bones, how to append). **Do not build these yourself**: use simple stand-ins until they land, then swap. If something in the pack doesn't work for a shot, write it in the Builder log and Claude gets it fixed.

## Kid-safety picture rules
The trolls are big and a bit scary but never horror: no fangs, no red eyes, no drool. The squished table only ever has pies on it, never people. The mother never touches anyone; the film ends before anything happens. Everyone who runs is fine.

## Deliver
`ready/tiny-seed/tiny-seed.mp4` (sponsor edition, Instagram), `tiny-seed-clean.mp4`, `tiny-seed-cover.png` (frame 0), `tiny-seed-thumbnail.jpg`, `notes.json` to main. Cast check and model swaps to `proofs/tiny-seed/`, then keep building. Every-frame check before delivering (no strobing, pops, frozen stretches, clipped heads).
