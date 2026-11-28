# BUILD PACKAGE: I TRADED MY ARMS FOR LIGHTNING (lightning-arms)

**Jake approved the script in the app (Sat 11-28, 8:25 AM), and the voice is final.** He wrote it in the Idea lab over our hit "Reflection taller than the clock tower" (949K). Claude fixed the flow first: 0 jumps, and every power has a reason before it and a result after it.

**Who builds it (Jake's picks in the app):** a Claude video builder (you, in the cloud) and Claude's model builder for the big models. The models land in `models/`.

**Edition: Flashloop sponsor.** You deliver the **clean** film. Claude makes the Instagram sponsor edition (v3 ending) and adds the music, so don't add either. **Keep your master picture and your voice+SFX mix** (`work/picture.mp4`, `work/mix.wav`): Claude builds the sponsor edition from them.

## Format: the house look (Town Storybook), still frames
- **Pick: house style.** That is the Studio Bible look: `/home/claude/STUDIO-BIBLE.md` (read it). It is the still-frame storybook style of our viral hits.
- **Every shot is a still render with a slow 2D post-move.** Use push-ins, a pull-out for scale, small drift, and a snap push on shock words. Render the stills a little oversized so the moves never show an edge.
- **Hard cuts on word onsets**, about 1.0-1.3 s a shot, one picture per phrase. That's about 80-90 shots for 101 s.
- **Faces change expression on the stressed word.** Mouths move on every spoken quote.
- **Captions:** one or two words at a time on the spoken onset, house caption style (Studio Bible).

**The pipeline is already built.** Reuse the Fake Power still-frame pipeline in `/tmp/claude-0/tv/fakepower/build/src/`:
- `fp_lib.py`, `shots_*.py`, `assemble.py`, `sfx.py`, `qa.py` and `finish.sh`.
- Its notes are in `/tmp/claude-0/tv/fakepower/build/LOG.md`. That film passed review on Fri 11-27, so copy its approach and its every-frame QA.
- Work in `/tmp/claude-0/tv/lightning/build/`.

## Files in this folder
- `lightning-voice-final.mp3`: the final narration (Adam), already at final speed. **101.1 s**, -13.7 LUFS, md5 starts `febaef85`. Never re-voice or re-time it.
- `lightning-lines.srt` and `lightning-word-timings.json`: caption and word timings for that mp3.
- `lightning-script.txt`: the script, one caption line per line.
- `models/` (from Claude's model builder): `lightning-models.blend`, `glb/`, `MODELS.md`, previews. Start with the shots that don't need the models; swap them in as they land.

## Places (Jake's picks): Claude's backlot, NIGHT for the climax
The six sets are in `/tmp/claude-0/backlot/` (BACKLOT.md; `source/backlot_api.py`). Append the collection and pick the DAY, GOLDEN or NIGHT preset scene. Use the named cameras and marks.
- **Town Square:** the Gate of Oaths stands in the square, as a model from the model builder placed at the fountain end.
  - Lines 1-9 (rules and exposition): DAY.
  - Line 10 ("That morning..."): DAY, at a house door.
  - Lines 12 and 15-30: NIGHT, torches (the whole town).
- **Bridge and River at NIGHT:** line 13, the Warlord riding in over the bridge with the beast and the chained sister.
- Call `backlot_api.use_texture_proxies()` after appending (memory).
- Dim the Cast v2 Wizard and Villain staff orbs (BACKLOT.md has the line).

## Cast
Jake's picks: Hero kid, Little sister, Villain, Boss Giant, Herald, Crowd gasper. Use house faces for everyone.

| Who | Cast | Notes |
|---|---|---|
| **Narrator ("I")**, a kid with lightning arms | Cast v2 Hero kid | Lightning arms from the model pack replace his arms after line 4. |
| **His little sister** | Cast v2 Little sister | Chained by one wrist to the beast's harness. She's scared but fine and never hurt. |
| **The Warlord** (rules the town, iron crown, iron arms) | Cast v2 Villain, with the iron crown and iron arms from the model pack | He shouts lines 18 and 22; mouth moves. |
| **The Herald** | Cast v3 `Cast v3 \| The Herald` (scripts-inbox `cast-v3/cast-v3.blend`, CAST-V3.md) | Reads the Warlord's law from his scroll on line 5. Picture only, no voice. |
| **The crowd** | Cast v3 Crowd Six (Gasper and the others, fixed poses gasp/laugh/point/cheer) + Cast v2 people | Every kid in the crowd wears visible arms: mostly stone arms, a few others. |
| **The war beast** and **the Gate of Oaths / the gate giant** | Model pack | The standing gate giant may be built on the Cast v3 Boss Giant rig, scaled up. |

- **Cast v3 is in `/tmp/claude-0/cast3/`** (or scripts-inbox `cast-v3/`). Append the collection and set faces via the rig's `face` / `mouth` / `blink` properties.
- Don't invent other people.

## Scale (keep it true; 1 m = 3.3 BU)
- **People:** Hero kid 4.16 BU, sister 3.37.
- **War beast:** about 18-22 BU at the shoulder, so the kid reaches its knee. Kneeling, its head is level with the kid.
- **The Gate of Oaths:** about 25 BU tall as a gate.
- **Standing up, the gate giant towers over the castle:** at least 120 BU, the town roofs reaching its shins.
- **The number over its head:** big and glowing, readable from the square.

## Frame 0 and the cover
- **The picture: night in the torchlit square.** The small kid stands with both arms crackling with blue-white lightning, raised. The huge horned war beast kneels in front of him, chains slack. The Gate of Oaths is behind, and the crowd holds torches. Low angle.
- **Title:** **I TRADED MY ARMS FOR LIGHTNING**. White caps, black outline, "LIGHTNING" in the accent colour, in the 9-20% band. Handle `@idlemerchantrng` top left.
- **Timing:** hold frame 0 under the title about 1.5 s while line 1 starts, then cut into the story.

## Shot list with final times (split each line into shots; these are the pictures to cover)
| # | Time (s) | Line | On screen |
|---|---|---|---|
| 1 | 0.00-3.91 | In this town, every kid trades their arms once at the Gate of Oaths, forever. | Frame 0. Then: the Gate of Oaths by day in the square, a huge carved stone arch with chains and burned numbers. A kid steps up to it. |
| 2 | 4.18-9.17 | The gate keeps your old arms in its stone and burns a number on your wrists: how rare your new ones are. | Close: rows of stone arms set into the gate's walls. Insert: a glowing number burning onto a kid's wrist band. |
| 3 | 9.43-11.51 | Half the kids get stone arms. One in two. | Kids comparing grey stone arms. Wrist band: **1 IN 2**. |
| 4 | 11.74-14.33 | I traded mine for lightning. One in ten million. | The kid's new arms crackling with lightning. Wrist band: **1 IN 10,000,000**. Proud face. |
| 5 | 14.54-19.19 | But the Warlord who rules our town has a law: the rarest arms in town wear the iron crown. | The Herald reading the law from a scroll. The Warlord on a balcony in the iron crown, smug. |
| 6 | 19.42-23.05 | His iron arms were one in a million. So my lightning would take his crown. | The Warlord's dark iron arms with wrist band **1 IN 1,000,000**. The crown, then the kid's lightning; the Warlord's eyes narrow. |
| 7 | 23.25-27.80 | He couldn't steal my arms. The gate's chains grab anyone who tries and turn their arms to stone. | The gate's chains with glowing runes. A picture of the rule: chains snapping round a thief's wrists and stone spreading up his arms, shown as a painting on the gate, not a real person. |
| 8 | 28.00-30.68 | And if anyone tries, they say the gate itself wakes up. | Slow push on the gate's carved stone face. Its eyes are closed; a faint glow inside. |
| 9 | 30.89-36.26 | So he chained my little sister to his war beast, a horned giant that kneels only to the rarest arms in sight. | The huge horned war beast in the Warlord's yard. The sister's wrist chained to its harness; she's scared, not hurt. The beast kneeling to the Warlord (a quick memory picture). |
| 10 | 36.48-40.44 | That morning, he rode to my door. "Leave by midnight, or she gets dragged away." | DAY: the Warlord on horseback at the kid's door. **Mouth moves** on the quote. Sneer. |
| 11 | 40.67-44.55 | "Your beast kneels to me," I said, and my sparks shoved him back a step. | The kid, **mouth moving**, fierce. Sparks burst off his arms; the Warlord's horse steps back. |
| 12 | 44.81-48.51 | At midnight, I stood at the Gate of Oaths, and the whole town came with torches. | NIGHT square, wide: the kid alone in front of the gate, the crowd with torches all round. |
| 13 | 48.73-51.69 | The Warlord rode up with his beast, my sister chained behind it. | NIGHT bridge: the Warlord rides over the bridge, the war beast pulling at its chains, the sister behind. |
| 14 | 51.91-54.56 | "Then it drags you both," he said, and let it charge. | The Warlord, **mouth moving**. He drops the chain. The beast lowers its horns. |
| 15 | 54.78-57.77 | So I raised my arms, and lightning split the ground in front of it. | The kid's arms up, a lightning strike (3-frame whiteout), a glowing crack across the square in front of the beast. |
| 16 | 57.95-61.39 | The beast skidded. Then it knelt to me, and the whole town went quiet. | Hooves skidding, ground cracking. Then the beast kneels, head level with the kid. The crowd silent, torches still. **Goosebumps shot.** |
| 17 | 61.60-64.11 | Its chains went slack, and my sister ran free. | Chains drop. The sister runs to the kid, who catches her. |
| 18 | 64.29-66.72 | The Warlord jumped down. "Those arms are mine!" | The Warlord jumps from his horse, **mouth moving**, furious. |
| 19 | 66.97-68.99 | He grabbed my wrists to tear the lightning off. | The Warlord's iron hands grabbing the kid's lightning wrists. |
| 20 | 69.20-73.26 | So the gate's chains snapped around his wrists, and his iron arms turned to stone. | The gate's chains lash out and snap round the Warlord's wrists. Stone creeps up his iron arms. He's stuck, never hurt. |
| 21 | 73.47-76.72 | The whole town laughed. Stone arms. One in two. | The crowd laughing (Cast v3 crowd laugh and point poses). Insert: his wrist band now **1 IN 2**. |
| 22 | 76.94-78.92 | "Kneel to me!" he roared at his beast. | The Warlord, **mouth moving**, pulling at the chains. |
| 23 | 79.10-82.66 | But it stayed kneeling to me. Mine were still the rarest arms in sight. | The beast stays bowed toward the kid. The kid's wrist **1 IN 10,000,000** glowing. |
| 24 | 82.85-86.81 | So by his own law, the town pulled off his iron crown and laid it at my feet. | Townsfolk lift the iron crown off the Warlord's head. The crown placed at the kid's feet. |
| 25 | 87.02-90.39 | Then the Gate of Oaths shook, because someone had tried to break its oath. | The gate shaking, dust falling, its eyes opening (glow). |
| 26 | 90.58-93.68 | It stood up on legs and arms made of every arm it ever kept. | The gate rising up: legs and arms built from hundreds of stone arms. Huge pull-out for scale. |
| 27 | 93.87-95.12 | It towered over the castle. | Wide from far away: the gate giant taller than the castle keep. |
| 28 | 95.28-97.07 | The war beast turned and bowed to it. | The beast turns and bows low to the gate giant. |
| 29 | 97.25-99.02 | And a number began to burn over its head. | A huge glowing number starting to appear over the giant's head, digits climbing, too long to read. |
| 30 | 99.26-101.08 | What's the number over the gate? Guess. | Close on the kid looking up, the number's glow on his face. Then the end screen. |

## End screen (signature, over the final shot)
- **Printed question:** WHAT'S THE NUMBER OVER THE GATE?
- **Line under it:** GUESS IN THE COMMENTS
- **Follow line:** FOLLOW FOR MORE "IN THIS TOWN"
- No Part 2 promise.

## Models (Claude's model builder, NOT you)
Brief: `models/MODELS-BRIEF.md`. They land in `/tmp/claude-0/tv/lightning/models/` with `MODELS.md`:
- the Gate of Oaths (gate form + standing giant form)
- the horned war beast (rigged, poses)
- lightning arms
- iron crown
- the gate's chains + stone arms + iron arms
- wrist number bands + the big number over the giant's head

Build the people, sets and effects yourself; don't build the models.

## Kid-safety picture rules
- Nobody is hurt. The sister is chained by one wrist, scared but fine, and runs free.
- The Warlord's arms turning to stone is a stuck, funny comeuppance, not painful.
- The beast is big and fierce but never horror: no fangs, no red eyes, no blood. The gate giant is awe, not terror.
- Lightning never hits a person; it splits the ground.

## Deliver
- **Files:** `/tmp/claude-0/tv/lightning/build/out/lightning-clean.mp4` (1080 x 1920, 30 fps, about -14 LUFS, under 25 MB), `lightning-cover.png` (frame 0), `lightning-thumbnail.jpg`, `notes.json`. Keep `work/picture.mp4` and `work/mix.wav`.
- **Cast check first:** a cast check to `proofs/cast-check.png`, then keep building.
- **Every-frame check before delivering:**
  - no pops
  - no edges showing from the post-moves
  - no frozen stretches longer than one shot
  - captions never empty while the voice runs
  - mouths closed when nobody talks
