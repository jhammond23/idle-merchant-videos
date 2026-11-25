# scripts-inbox

Claude (story writer) puts one folder here per story that is ready to build. Only Claude writes to this branch.

Each folder holds:
- `BUILD-PACKAGE.md` (or `ASTRA-<STORY>-PACKAGE.md` in the first two folders): the build package (script, characters, beat times, must-haves, asset paths). Read it first.
- `<story>-voice-final.mp3`: the final voice track, already at its final speed. Never re-voice or re-time it.
- `<story>-lines.srt` and `<story>-word-timings.json`: caption timings for that mp3.

Builder: build every story folder here that has no `ready/<story-name>/` folder on the main branch yet. When a video is done, upload `<story-name>.mp4`, `<story-name>-cover.png` and `notes.json` to `ready/<story-name>/` on main. Claude checks and posts from there.

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
