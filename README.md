# scripts-inbox

Claude (story writer) puts one folder here per story that is ready to build. Only Claude writes to this branch.

Each folder holds:
- `BUILD-PACKAGE.md` (or `ASTRA-<STORY>-PACKAGE.md` in the first two folders): the build package (script, characters, beat times, must-haves, asset paths). Read it first.
- `<story>-voice-final.mp3`: the final voice track, already at its final speed. Never re-voice or re-time it.
- `<story>-lines.srt` and `<story>-word-timings.json`: caption timings for that mp3.

Builder: build every story folder here that has no `ready/<story-name>/` folder on the main branch yet. When a video is done, upload `<story-name>.mp4`, `<story-name>-cover.png` and `notes.json` to `ready/<story-name>/` on main. Claude checks and posts from there.

## Fri 11-27, 9:55 AM: FETCH FIRST. Both model packs have been here since 12:31 AM (`tiny-seed/models/`, `truth-sword/models/`); your v1 used stand-ins because your clone stopped at 8284234. tiny-seed v1 did not pass: read `tiny-seed/REVIEW-NOTES.md`, deliver v2 with the real models, then build truth-sword with its real props.

## Fri 11-27, 2:05 AM: tiny-seed cast check passed. Read `tiny-seed/REVIEW-NOTES.md` (garden keeper lighting) and swap in the models (they're in).

## NEW Fri 11-27, 12:30 AM: truth-sword (the Claude Code builder on Jake's PC, right after tiny-seed) + props from Claude's model builder

`truth-sword/` = "MY SWORD GROWS EVERY TIME I TELL THE TRUTH." Claude's own idea, pre-approved by Jake; the voice is final (100.5 s). Our Black Knight hit remade line for line. **Claude builds it, not Astra.** Same settings as tiny-seed: clean (FB/TT/YT) + the Flashloop sponsor edition for Instagram; Toybox Fable base + Torchlit camera and captions + Bright Snap Cut effects; six face styles, one per person. Bright courtyard daylight all the way. **Read `truth-sword/BUILD-PACKAGE.md`.** **Props are IN (Fri 1:05 AM, Claude reviewed them): `truth-sword/models/truth-sword-props.blend` + `MODELS.md`** (Truth Stone with glow + crack states, swords with one `sword_length` property each, the King's empty scabbard, the bell, clouds, the shovel). Append, don't link.

## NEW Thu 11-26, 11:55 PM: tiny-seed (the Claude Code builder on Jake's PC, next) + models from Claude's model builder

`tiny-seed/` = "MY TINY SEED HUGGED A GIANT TROLL." Jake approved the script and the voice (94.1 s). **Jake's rule for this film: Claude builds it, not Astra.** Editions: clean (FB/TT/YT) + the Flashloop sponsor edition for Instagram (sponsor ending V2, fixed voice file). Build style: Jake's mix, Toybox Fable base + Torchlit camera and captions + Bright Snap Cut effects, and six face styles assigned per character. One new character authorized: the old garden keeper. **Read `tiny-seed/BUILD-PACKAGE.md`.** **Models are IN (Fri 1:20 AM, Claude reviewed them): `tiny-seed/models/tiny-seed-models.blend` + `MODELS.md` + `src/ts_helpers.py`** (the tree A-E with HUG/GIVE/PROTECT/LEAN/LOOKDOWN poses and blink/smile, the champion's oak, bushes, the baby troll with four faces, the troll mother (440 BU; camera clip end 5000+), the measuring pillar, pie tables). Append, don't link. Finish anything already in progress first; one heavy render at a time while Jake is on the PC.

## NEW Thu 11-26, 4:20 PM: snow-globe delivery needs a fix round (Claude Code builder)

The loop, sound and bedroom shots are good, but frame 0 still has the round-1 problems and five shots are unclear or crop the kid's head. **Read `snow-globe/REVIEW-NOTES-2.md`**, fix only those shots, re-deliver with the frame ranges.

## Thu 11-26, 4:20 PM: bunny-chains PASSED review (thanks, Video builder (2)).

## NEW Thu 11-26, 3:15 PM: bunny-chains proof notes

Cast check PASS, bunny PASS. Changes: the fog giant must look like fog (soft misty see-through body, gold pinprick eyes, not a pale gaunt figure); the horse-stage bunny must be clearly bigger than the kid; the castle-stage bunny goes beside OUR castle with the towers at its shoulder. Details in `bunny-chains/REVIEW-NOTES.md`. Keep building.

## NEW Thu 11-26, 2:30 PM: bunny-chains (Video builder (2), next; bunny model: Model Builder)

`bunny-chains/` = "MY BUNNY ATE THE KING'S CHAINS." Jake approved the script and the voice (90.6 s). CLEAN edition only, house look (no build style picked). It reuses three past-hit monsters (the Black Knight model as a chained iron knight, the Crown Stag, the Fog Giant) and needs one new creature: the bunny in three sizes (teacup, horse, castle), plus a hill-sized chained egg prop. **Read `bunny-chains/BUILD-PACKAGE.md`.** Model Builder: build the bunny pack first and push `proofs/bunny-chains/bunny.png`, then keep going. Kid-safety picture rules are in the package.

## NEW Thu 11-26, 12:15 PM: BUILD STYLES (selectable per film) + character kits

`styles/` holds four new build styles Jake can pick per film in the studio app, each reverse-engineered from a viral account (method only), with a Blender code pack calibrated on our scene, a character kit and drawn face sets: **Bright Snap Cut** (`bright-cut`), **Torchlit Blocktale** (`gneef-style`), **Toybox Fable** (`craftee-style`), **Comic Sticker Saga** (`fourth-style`). **Read `styles/README.md`.** A film's build package names its style; if it names none, build the house look (Studio Bible). Picking a style is Jake's yes to the house rules that style overrides, for that film only. Start any new-style film with the style test in its STYLE.md.

## NEW Thu 11-26, 11:20 AM: snow-globe frame 0 notes

Cast check: PASS. **Frame 0: change it before the final render** (the glass dome must read, pull the face back, no clipped people in the corners, lose the side colour smudges). Details in `snow-globe/REVIEW-NOTES.md`. Keep building.

## NEW Thu 11-26, 12:20 AM: snow-globe (the NEW Claude Code builder chat on Jake's PC)

`snow-globe/` = "MY WHOLE TOWN FIT IN MY HAND." A brand-new film and an **infinite loop reel**: the last shot and the voice flow straight back into frame 0. Jake approved the script and the voice (53.23 s). CLEAN edition only. **Read `snow-globe/BUILD-PACKAGE.md`**, and build it the way `Studio Bible\10 How Astra Builds a Video.md` describes. Cast v2 plus one new character (the king), which Claude authorizes you to add with `cast_v2.py`. The 100 Doors render queue is still running on the PC: one heavy render at a time.

## NEW Wed 11-25, 11:25 PM: CAST V2 is the cast for every new film

Jake approved `cast-v2/` (13 characters: very different bodies, classic yellow avatars and real skin tones, Pokemon-style, anime and classic Roblox faces). **Read `cast-v2/CAST-V2.md`** and append the characters from `cast-v2/cast-v2.blend`. Films already in progress keep their cast unless Claude says otherwise. Builders never invent people; ask Claude for anyone new. The 16-character Model Builder brief in `cast-v2/CAST-LIBRARY-V2-BRIEF.md` is cancelled.

## NEW Wed 11-25, 5:30 PM: handshake ("Build moth-wings style test", right after the Moth Wings Part 2 round 2 test clip)

`handshake/` = "I COPY ANY SKILL WITH ONE HANDSHAKE." It is built line for line on the structure of a 15.4M-view reel. Jake approved the script and the voice (54.9 s, fast, last word cut for the loop). CLEAN edition only. Moth Wings pace and quality. **Read `handshake/BUILD-PACKAGE.md`.** Do it while Jake reviews the Moth P2 test clip, then go back to Moth P2 when his notes arrive. Delete temp frames after each delivery.

## NEW Wed 11-25, 4:40 PM: sphinxs-riddle (Video builder (2), after the Egg Army creature swap) + the Sphinx (Model Builder)

- **Video builder (2):** `sphinxs-riddle/` = "THE SPHINX'S RIDDLE." It is NON-SPONSORED, so build the CLEAN edition only. Jake approved the script and the voice (Adam narrates; the sphinx has its own deep voice). The visuals and the on-screen riddles carry the story. **Read `sphinxs-riddle/BUILD-PACKAGE.md`.**
- **Model Builder:** `sphinxs-riddle/SPHINX-BRIEF.md`. Build the colossal stone sphinx with sun eyes and golden wings that burst out, plus a "turned to stone" material. Push one still to `proofs/sphinxs-riddle/sphinx.png`, then keep going.

## NEW Wed 11-25, 1:40 PM: power-level-zero (Video builder, right after King's Scale)

`power-level-zero/` = "MY POWER LEVEL SAID ZERO." Jake approved the script and the voice. It is the Black Knight structure with a giant glowing number counting up on screen. The bar is Moth Wings / Stag quality with ~1 s cuts. **Read `power-level-zero/BUILD-PACKAGE.md`.** Push the cast-check still and keep building (Claude reviews it). Both editions to `ready/power-level-zero/`.

## CAST OK egg-army-day1 + DRAGON OK (Jake, Wed 11-25, 11:45 AM). NEW RULE: Claude approves casts from now on

- **CAST OK egg-army-day1.** Video builder (2): build the full Day 1 film now, at Stag quality. Use stand-ins for the knight, the giant, the moon and the sparks until the Model Builder's packs are approved, then swap them in.
- **DRAGON OK.** The Model Builder's revised Dungeon Master dragon (main 87e863a, `proofs/dungeon-called-me-master-dark/dragon.png`) is approved. "Build moth-wings style test": use it for every dragon shot. Model Builder: carry on with the Egg Army packs now.
- **NEW RULE (Jake, 11:45 AM): Jake no longer approves cast checks or creature stills.** Still push the cast-check still to `proofs/<story>/` as always, then **keep building**. Do not stop and wait. Claude reviews it and only writes in this README if something must change. Claude still rejects anything below Moth Wings / Stag quality.

## NEW Wed 11-25, 10:35 AM: Dungeon Master dark look ACCEPTED

- **"Build moth-wings style test" chat:** build the FULL `dungeon-called-me-master` film in the dark look, with the 4 fixes in its REVIEW-NOTES.md. Build the dragon shots last, with the Model Builder's revised dragon. Then do the Moth Wings Part 2 round 2.
- **Model Builder chat: FIRST, before the Egg Army packs,** touch up the Dungeon Master obsidian/lava dragon (the one in the look test at main bc20c6e, about 10.7 to 11.5 s) so it reads clearly as a dragon: a clear head with horns, eyes, snout and jaw, a neck, folded wings and claws, with the lava cracks as accents only. Push one still to `proofs/dungeon-called-me-master-dark/dragon.png` (front three-quarter, plus lying at a boy's feet for scale, in torchlight), then STOP for Jake. After that, the Egg Army packs.

## NEW Wed 11-25, 10:40 AM: egg-army-day1 REWRITTEN (Video builder (2)) + creatures (Model Builder)

- **Video builder (2): `egg-army-day1/` is a brand-new film.** "I HATCHED AN ARMY TO STOP THE MOON." This is Day 1 of 4, at Crown Stag quality. It has a new voice, script, beats and frame 0 (a flash-forward that opens every day). **Read the new `egg-army-day1/BUILD-PACKAGE.md`.** The old dragon/bear/fox package and its cast check are void. Cast check first, then stop.
- **Model Builder chat: `egg-army-day1/CREATURES-BRIEF.md`.** Build the Blue Fire Knight, the Storm Giant, the burning moon and the sparks. Deliver one review still to `proofs/egg-army-day1/creatures.png`, then stop for Jake.

## Wed 11-25, 9:45 AM: Jake cut the list (quality over quantity)

- **DROPPED, do no more work on them:** footprints, i-walked-out-to-meet-it (delivered; it will not post), phoenix part 2.
- **egg-army-day1 is NOT dropped.** It has been REWRITTEN; see the 10:40 AM section above.
- **KEEP:** dungeon-called-me-master (dark look test), moth-wings-2 (round 2), and my-number-broke-the-kings-scale (Video builder: finish it).
- **New bar:** Claude rejects any delivery that is not at Moth Wings quality and sends it back with notes. Only films that pass go to Jake. Fast cuts (about 1 s), big readable subjects, no empty, clipped or see-through shots, rich scenery.

## NEW Wed 11-25, 9:20 AM: three re-dos from Jake (read the folder's REVIEW-NOTES.md; each one = test clip first, then STOP)

- **"Build moth-wings style test" chat, in this order:**
  1. **`dungeon-called-me-master/`: NEW ART STYLE.** "Ultra dark, grimy, and poor." The bright gold look is out. Deliver a frame 0 and a 10 to 12 s look test only, then stop.
  2. **`moth-wings-2/`: Round 2.** Jake finds the test clip "a bit sloppy." Take more time and re-do the 0 to 36.3 s test clip cleaner and more epic (no empty, clipped or see-through shots; richer scenery; a bigger fly-past). Then stop.
- ~~**Video builder, next after the current job:** **`footprints/`: NEW OPENING.** Re-do 0 to 6.2 s only, as a strong, fast, moonlit first scene (glowing prints racing to the black river). Deliver a 0 to 8 s test clip, then stop.~~ **CANCELLED by Jake 9:44 AM: Footprints is dropped. Do not work on it.**

## NEW Wed 11-25, 12:15 AM: moth-wings-2 (for the "Build moth-wings style test" chat, right after the Dungeon Master test clip)

`moth-wings-2/` = "MY MOTH WINGS LED THE GRIFFINS HOME." Moth Wings Part 2 (Part 1 posts Wed 6 AM). Jake approved the script and the voice: "exact same art style, and have a very similar attention grabbing intro." Frame 0 is a fly-past: the hero diving out of bright white fog at the lens with his eye spots blazing. Big cartoon faces, strong joke pictures, the first-year's "You're glowing" close-up. **Read `moth-wings-2/BUILD-PACKAGE.md`.** Test clip of lines 1 to 8 first, then stop for notes. Clean edition only. No shake or zooms (Claude adds them).

## CAST OK dungeon-called-me-master (Jake, Tue 11-24, 11:26 PM)

**CAST OK dungeon-called-me-master.** Jake saw the cast still at main `bb34b26` (the obsidian dragon, the torch boy, prince, knight, goblins and the 10 faces) and said "Yes, let's see a small clip." Go to step 2: the **test clip of lines 1 to 9 (0 to 41.30 s)** with the real voice, captions and sound, to `proofs/dungeon-called-me-master/test-clip.mp4`. Use the faces exactly as on the sheet (they're great). Frame 0 is the dragon bursting out of the gate into the sunny square. Run glitchscan and stylecheck, push, reply with the commit, then STOP for notes.

## NEW Tue 11-24, 11:05 PM: dungeon-called-me-master (for the "Build moth-wings style test" chat, right after Moth Wings)

`dungeon-called-me-master/` = "THE DUNGEON CALLED ME MASTER." Jake approved the script and wants it built "with as cool visuals as you can in the same art style as the wings". It **replaces** dungeon-master (Jake dropped that story; do not reuse its shots). Built exactly like Moth Wings: a new shot every 3 to 4 words, literal pictures, bright and saturated, still camera, captions with one red word. **New for this film: a set of big, exaggerated cartoon faces** on our rounded heads (Jake asked to copy that from the reference). **Read `dungeon-called-me-master/BUILD-PACKAGE.md` first.** Steps: cast still (with the dragon and the 10 faces), STOP for Jake's CAST OK; then a test clip of lines 1 to 9; then the full film, clean edition only. No shake or zooms: Claude adds them in the finishing pass.

## Moth Wings ROUND 3 (Jake, Tue 11-24, 10:21 PM): re-render shots 1, 5 and 24 only

Jake changed his mind about "Moth Wings is not being re-rendered" (section below). He wants a far more epic opening shot and a decorated ranking board with a picture of each wing type. **Read the "Round 3" section at the end of `moth-wings/REVIEW-NOTES.md`.** Same voice and cut times; re-export `ready/moth-wings/moth-wings-clean.mp4`; no shakes or zooms (Claude adds those in the finishing pass). Do this before the other builds: the post is on hold until it lands.

## CAST OK footprints, i-walked-out-to-meet-it, my-number-broke-the-kings-scale (Jake, Tue 11-24, 10:09 PM)

Jake approved all three cast stills, each with the changes below. Make the changes in the full render; no new cast still is needed. Then deliver to `ready/<story>/` as usual. The "make every film feel ALIVE" section above applies to all three.

**CAST OK footprints** (main `cb9b385`).
- Light it like the approved Phoenix moonlit look: bright blue moonlight on the snow and the street, faces clearly lit. Frame 0 measured brightness 65; aim for 100 or more.
- The moon is a flat grey disc. Make it glow, with a soft halo and light on the clouds around it, in every shot it appears in.
- The glowing footprints are the hook. Make them glow much brighter (strong cyan-white emission, light spilling onto the snow around each print), bright enough to stop a scroll at phone size.
- Frame 0: frame the boy bigger. The bottom third of the frame is empty dark ground; bring the camera lower and closer so he and the first prints fill it.

**CAST OK i-walked-out-to-meet-it** (main `86f7b42`).
- The creature: keep what the voice says (long thin arms, a black body, a white mask with no face), but it must NOT read as Slender Man. Grow frost-covered antlers or bare branches up out of the mask, and give it a ragged cloak of snow and frost over the shoulders and back. It should read as a winter forest spirit. Softer hands (long thin fingers) instead of claws.
- The same moon fix as Footprints: a glowing moon with a halo, not a flat grey disc.
- Frame 0: Tomas is small with empty snow under him. Bring the camera lower and closer so Tomas and his lantern are bigger and the spirit towers over him from the frame edges.
- Mom and Dad have almost the same face and hair. Give them different hair (and a scarf or hat on one) so they read as two people.

**CAST OK my-number-broke-the-kings-scale** (main `c0ac6b7`).
- The twins must read as twins: give the twin sister the same skin tone and the same hair colour as Shorty (her hair can be longer). Same eye height, as now.
- Everything else as shown: bright daytime square, brass scale, the Reflection King and Prince.

## NEW Tue 11-24, 10:15 PM: make every film feel ALIVE (Jake, both builders, from the next render on)

Jake asked for the films to be far more cinematic and "feel more alive". Claude now runs a finishing pass after delivery (slow camera drift, punch-ins, light, dust in the air, grade, sound effects and ambience; `finish.py` on branch `claude-polish-moth-wings`). **Do not add those yourselves** (they would double up). What only Blender can do is below, and it applies to every new film and every visual rebuild. Please also copy this section into the Studio Bible notes `01 Look and Characters` and `05 Quality Checklist` with today's date.

- **Nothing on screen is frozen.** Wings, capes, hair, banners, bunting and kites move. Wings at rest breathe or twitch; flying wings really flap; a reveal is a real unfold over several frames, never a pop-in.
- **Crowds are alive.** Every person breathes, shifts weight and looks around, with staggered timing. Reactions (laughing, gasping, kneeling, cheering) are full-body and staggered across the crowd, never in sync.
- **Light that shapes people.** One strong warm key light plus a rim or back light on every character so they separate from the background; cool sky fill. Faces lit.
- **No flat low-poly rock.** Cliffs, rocks and ground in close and medium shots are smooth-shaded and textured, with grass lips, moss and detail. (Moth Wings' cliff at 28 s, 40 s and the final shot is the example of what not to do.)
- **Big moments happen in the scene's light.** If the story says the wings blocked out the sun, the scene goes into real shadow, with light rays around the edges.
- **Render motion blur on.** Shallow depth of field on close-ups. Something in the foreground in most shots.
- Everything else in the bible still applies: house look, locked cast, camera rules, no music bed, every-frame check.
- Moth Wings itself is NOT being re-rendered (Jake's call: it's a style test; Claude finished it in post).

## CAST OK moth-wings, TEST ACCEPTED (Jake, Tue 11-24, 6:49 PM)

**CAST OK moth-wings.** Jake approved the test clip at main `fb58deb`: "pretty dope... go ahead and build the rest." Build the full film now. Clean edition first; the sponsor edition waits for its own ending line. Details are at the end of `moth-wings/REVIEW-NOTES.md`.

## NEW Tue 11-24, 6:15 PM: moth-wings (for the NEW builder chat that Jake's PC opens for it)

`moth-wings/` = "MY MOTH WINGS STOPPED A GRIFFIN." A **style test**: our cast and world, with the editing of a 6.5M-view reel (a new shot about every 0.9 s, bright daylight, small captions with one red word). **Read `moth-wings/BUILD-PACKAGE.md` first.** It overrides the bible's camera rule for this film only. Steps: cast still, then a **15-second test clip** (shots 1 to 14), then STOP and wait for Claude's notes in `moth-wings/REVIEW-NOTES.md`. The full film comes only after the test clip is accepted and CAST OK moth-wings appears here.

## CAST OK dungeon-master (Jake, Tue 11-24, 5:43 PM)

**CAST OK dungeon-master.** Jake approved the cast still at main `c1eed58`. Go ahead with the full render.
- Jake's rule from now on: **head shape stays rounded,** like the Reflection head. **Face art is flexible**: any face drawing used in our earlier reels is fine on that rounded head. This is in `Studio Bible/01 Look and Characters.md`.
- Claude's note: the courtyard in the still is dim and blue. Light the full render as bright daytime with strong colour, so the faces read at phone size.
- Egg Army is **not** approved yet. Wait for "CAST OK egg-army-day1".

## NEW Tue 11-24, 4:55 PM: locked Reflection cast source (asked for by Video builder)

`locked-cast/reflection-source/` holds `nx/set_refl.py` and every file it builds on: the R6 rig, `person()`, the cast in `gk/set_gk.py` and the Reflection additions. **Read `CAST-MANIFEST.md` first**: one row per person, with exact shirt, pants, hair, face, skin, beard and scale. The hero for every new story is `kid`: burnt-orange shirt, `hero_crop` hair, `face_bright` face, scale 0.8. Use this for the Dungeon Master cast still and for the shared `locked-cast` folder. Jake's rule still applies: cast-check still first, then wait for CAST OK.

## Build order (updated Mon 11-23, 1:50 PM)
**First Video builder:**
1. **phoenix**: "The Phoenix Bowed to Me." A new story on the pattern of the Black Knight, with a new main character. Read `phoenix/BUILD-PACKAGE.md`. The Phoenix itself comes from the Model Builder (`Lunchbox\material\story-video\phoenix-v001\`); block with a stand-in until it lands. Upload a frame-0 still and a five-second clip of the bow to `proofs/phoenix/` on main before the full render.

**Video builder (2):**
1. **crown-stag-part1**: "The Enemy's Beast Knelt to Me." In progress. Creature packs are ready: `crown-stag-v001` and `mountain-stag-v001`.
2. **crown-stag-part2**: "The Mountain Knelt to Me." Same valley, cast and creatures. Part 1 cannot be posted until Part 2 is finished.

For crown-stag and phoenix, deliver **two exports each**: the sponsor version and a clean version with no Flashloop logo and no phone ending (`<story>-clean.mp4`). Details are in the packages.

**Jake's camera rule (11-23):** no fast camera swings, whips or snap moves, especially in the first seconds: he says they look like the camera is jerking around and make people leave. Open with steady shots joined by clean hard cuts, then one smooth gliding move. Where a package says "whip", use a hard cut instead.

Everything else in this inbox is delivered (black-knight-onetake and catch-the-crown included).

Already delivered, nothing more to do: dungeon-party, cloud (the original 74-shot cut is Jake's final choice), swordrain, string, river, whole-stone, monster-punch, dungeon-master, homework, final-boss, zombie-cure, count, footprints.

**Every package has a section called "The vibe".** Read it before the beats.

**Sponsor rules for every new build (Flashloop, 11-22):** the logo card FLASHLOOP.AI / FACELESS STUDIO / CODE: RNG in the top right, one third of the video width; and the new 4 to 5 second ending (phone-shaped Flashloop app screen, caption FLASHLOOP DOT AI, voice line "If you want to make videos like these, go to Flashloop dot AI", then the logo card). Sponsor examples: https://drive.google.com/drive/folders/116zrwIr87VPjsrKmR02Q1MPHmk_cdZFH

One continuous moving camera on every new video (Jake, 11-22; a package may name a few deliberate hard cuts), the corner handle, and a posting thumbnail taken from the actual scene.
The memory folder was removed on 11-22: Jake shelved that story. Do not build it.

## Added Mon 11-23, 7:30 PM: slime-world (for the first Video builder)

`slime-world/` = "I Hatched a Level 1 Slime. It Almost Ended the World." Jake's own idea, script approved by him, voice final. **Build it next, after the Phoenix, once the PC has disk space free.** Read `slime-world/BUILD-PACKAGE.md` first: Jake asked for scene-by-scene creative guidance and for the size idea to be a fun watch. It uses the new sponsor ending in `sponsor-ending/`. Push a frame-0 still and a five-second proof of the first doubling to `proofs/slime-world/` before the full render.

## Added Mon 11-23, 11:15 PM: look fix for five finished films (both builders, tonight)

Jake does not like the pale, flat look of five finished films. `look-fix/LOOK-FIX-BRIEF.md` has the new house look and a section for each film.
- **Video builder (2):** `dungeon-master`, then `final-boss`, after the Crown Stag pair.
- **Video builder:** `zombie-cure`, then `footprints`, then `i-walked-out-to-meet-it`, after the Phoenix changes and Slime World.
- Homework stays as it is. Scripts and voices do not change. Each film gets the new sponsor ending. Claude approves or rejects each delivery.

## Added Tue 11-24, 3:15 AM: Slime World needs ONE fix before anything else (Video builder)

Claude reviewed `ready/slime-world/` at 7663dce. It passes everything except one thing: the boy is standing outside the slime in the three far-away shots at hits 15, 19 and 23, although by then he is inside it. Details in `slime-world/REVIEW-NOTES.md`. Please fix those three shots first, re-export both versions, then go on to Zombies, Footprints and I Walked Out.

## Added Tue 11-24, 6:10 AM: status and next steps

- **Slime World (de9d613): approved.** Thank you. **Phoenix (6af9f20): approved. Crown Stag pair (7ac5b60): approved** and booked for today.
- **Zombies look proof: the look is approved; frame 0 needs one change.** See `zombie-cure/PROOF-NOTES.md`: the zombies must be running away from the kid, and his hand is up for a high five. Do not wait for another proof round.
- **Video builder (2):** the Crown Stag pair is done, so please start the look fix now: `dungeon-master`, then `final-boss` (`look-fix/LOOK-FIX-BRIEF.md`). I could not reach your chat overnight.
- **Video builder:** if `dungeon-master` has no proof on main by the time you finish Zombies, take it next and say so in your handoff (the brief's "finishes early" rule).
- Please put one line in this chat or a commit on main when you deliver. Two deliveries last night arrived with no message.

## Added Tue 11-24, 7:40 AM: Zombies needs ONE fix (Video builder)

Claude reviewed `ready/zombie-cure/` at 7aa55c9. The new look, frame 0, sound and sponsor ending all pass. One fix: three fast camera swings at 43.4-45.5 s, 53.8-55.5 s and 56.6-58.3 s break Jake's camera rule. Details in `zombie-cure/REVIEW-NOTES.md`. Please fix those, re-export both versions, then carry on with Dungeon Master (yes, it is yours now; thank you for taking it).

**For every look-fix film:** after the opening cuts, no camera move should cross from a close-up to a wide shot, or from eye level to overhead, in under three seconds. Use a clean hard cut instead when the story needs to jump.

## Added Tue 11-24, 8:00 AM: CHARACTER STYLE CHANGE from Jake. Read `character-style/CHARACTER-STYLE.md` before building any people.

Jake rejected Slime World's people ("Coraline style"). He wants people in the style of "My Reflection Knelt to Me": classic Roblox block people. Everything else keeps today's quality. Picture of the three styles: `character-style/character-styles-A-B-C.jpg`.
- Zombies: finish the camera fix as it is.
- Dungeon Master: build with the Reflection-style people.
- Slime World: wait for `slime-world/REDO-PACKAGE.md` (new opening plus the new people). It is not going out as it is.

## Added Tue 11-24, 8:20 AM: TOP PRIORITY from Jake, before anything else

Read `camera-openings/CAMERA-OPENINGS.md` now. New camera work for the slow cut openings of three finished films, in this order: **Stag Part 1, then Stag Part 2, then Phoenix.** Pause the Zombies fix, Dungeon Master and everything else until all three are delivered. Only the opening section is re-rendered; voice, timing, frame 0, the people and the ending stay the same. No proof round. The Stag parts are held off today's schedule until these land.

## Added Tue 11-24, 8:55 AM: Zombies camera fix CANCELLED

Jake watched the 7aa55c9 cut, said it is "MUCH better", and it posts today as it is. Do NOT do the three camera fixes in `zombie-cure/REVIEW-NOTES.md`. Order now: Stag Part 1, Stag Part 2, Phoenix (camera openings), then Dungeon Master in the Reflection-style people.

## Added Tue 11-24, 10:30 AM: Jake added a walk fix for BOTH Stag parts

Read `camera-openings/STAG-WALK.md`. The stags glide with their feet planted; Jake wants real walking steps. New order: **Stag Part 2 opening (add the walk in the same pass if you can), then the Stag Part 1 walk, then the Phoenix opening, then Dungeon Master.** Stag Part 1's opening (c1d8364) passed review; thank you.

## Added Tue 11-24, 11:45 AM: work split between the two builders

- **Video builder (2):** take the **Phoenix camera opening** (`camera-openings/CAMERA-OPENINGS.md`, Phoenix section), then **Final Boss** with the Reflection-style people (`character-style/CHARACTER-STYLE.md` and `look-fix/LOOK-FIX-BRIEF.md`). When you start the Phoenix, commit `proofs/phoenix/CLAIMED-BY-BUILDER-2.txt` to main so nobody doubles up.
- **Video builder:** Stag Part 2 opening, then the stag walk fix (`camera-openings/STAG-WALK.md`), then Dungeon Master in the Reflection-style people. Skip the Phoenix if `proofs/phoenix/CLAIMED-BY-BUILDER-2.txt` exists on main; if it does not exist when you finish the walk fix, take the Phoenix yourself.

## Added Tue 11-24, 3:00 PM: READ FIRST — new quality rules from Jake

Read `quality/QUALITY-RULES.md` before any work. Then:
- **Video builder:** finish the Stag Part 2 steps, then fix the Phoenix flicker (`quality/PHOENIX-FLICKER.md`), then build the locked-cast folder (rule 1). Dungeon Master waits for CAST OK.
- **Video builder (2):** Final Boss is rejected for its people (`quality/FINAL-BOSS-REJECT.md`). Help build the locked-cast folder, then push the Final Boss cast check and wait for CAST OK.

## Added Tue 11-24, 3:45 PM: NEW TOP JOB for Video builder (2): egg-army-day1

`egg-army-day1/` = "The Dragon Picked Me. I Hatched an Army." Day 1 of Jake's new daily vote series. Script approved, voice final. **Due on main by Wednesday 3:00 PM Central** (posts 6 PM). Jake: "go as close to the quality of stag as you can, but use the reflection avatar shapes (specifically the head)." Read `egg-army-day1/BUILD-PACKAGE.md`. **Cast check still first, then wait for CAST OK.** This comes before the Final Boss rebuild.

Video builder: no change (Stag Part 2 steps, Phoenix flicker, then the locked-cast folder).
