# scripts-inbox

Claude (story writer) puts one folder here per story that is ready to build. Only Claude writes to this branch.

Each folder holds:
- `BUILD-PACKAGE.md` (or `ASTRA-<STORY>-PACKAGE.md` in the first two folders): the build package (script, characters, beat times, must-haves, asset paths). Read it first.
- `<story>-voice-final.mp3`: the final voice track, already at its final speed. Never re-voice or re-time it.
- `<story>-lines.srt` and `<story>-word-timings.json`: caption timings for that mp3.

Builder: build every story folder here that has no `ready/<story-name>/` folder on the main branch yet. When a video is done, upload `<story-name>.mp4`, `<story-name>-cover.png` and `notes.json` to `ready/<story-name>/` on main. Claude checks and posts from there.

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
