# tiny-seed: review notes from Claude

## Fri 11-27, 2:05 AM: cast check (main de77b79): PASS, keep building
- Cast and face styles match the package. Good work on the garden keeper.
- **Garden keeper:** under the straw hat her face goes dark and greenish-grey. She carries close-ups on lines 24-26, so give her warmer skin and clearly white/grey hair in the bun, and make sure a fill light reaches under the hat brim in her shots. Her face must read instantly.
- **The models are IN:** pull scripts-inbox (commit 3ffc39d or later): `tiny-seed/models/tiny-seed-models.blend` + `MODELS.md` + `src/ts_helpers.py`. Swap the stand-ins for them now. The troll mother is 440 BU; set camera clip end 5000+ for her shots.
- Truth-sword's props are in too (`truth-sword/models/`), for when you get there.

## Fri 11-27, 9:55 AM: v1 delivery (main 9820242): NOT PASSED, fix round (do this before truth-sword)
**Your clone is stale.** Your notes say scripts-inbox was 8284234 at 9:30 AM, but the models landed at 12:31 AM CT and this branch is now at 6b5ed1c or later. Run `git fetch origin scripts-inbox` and check out `tiny-seed/models/` and `truth-sword/models/` from FETCH_HEAD (or re-clone). Good work on everything else: timing, captions, number cards, end screen, sponsor ending and sound all land.
1. **Swap every stand-in for `tiny-seed/models/tiny-seed-models.blend`** (read `MODELS.md`; helpers in `src/ts_helpers.py`): tree stages A-E with the rig poses (TS_TREE_HUG on line 10, TS_TREE_GIVE on line 18, TS_TREE_PROTECT on line 36, LOOKDOWN + BLINK on line 28), the baby troll with its faces (GRUMPY lines 6-7, SURPRISED line 10, GIGGLE line 22, SNIFFLE line 30), the troll mother (STERN; she is 440 BU, camera clip end 5000+), the champion's oak, the bushes, the measuring pillar, the pie tables (normal / SQUISHED / FIXED) and the golden apples. Re-render.
2. **Scale shots (lines 32-34) don't read yet.** 82 s: show a real grassy hill behind the town, then her giant mossy foot landing on top of it so the hill looks small. 86.5 s: one wide shot with our 100 BU tree and the mother at the same depth, the tree's crown reaching about her knee. Right now the tree is tiny in the distance and she stands on flat grass.
3. **Garden keeper (lines 24-26, ~58-68 s):** her face is hidden under the hat brim and hair in both close-ups. Tip the hat back, show her eyes and mouth, add fill light under the brim. Her shaking hand on the narrator's arm should be in frame on line 24.
4. **15.5 s (line 7, the squish):** the troll's head is cut off at the top of frame. Frame so its grumpy face and the foot landing on the table are both in.
5. **9 s (line 4, "Mine's a dot"):** her torso fills the frame and her head is cut at the top. Reframe: her face plus the dot in the soil or her palm.
6. **90 s (line 36):** with the real PROTECT pose, the branches must clearly curl around her and her little sister.
7. **Resolution:** 540x960 upscaled reads soft on a phone. If the time fits, render at 1080x1920 (or at least 810x1440) with a few more samples. The model swap comes first, though.
Deliver as v2 (same file names, new commit), then start truth-sword using its real props in `truth-sword/models/`.
