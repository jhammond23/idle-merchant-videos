# snow-globe: "MY WHOLE TOWN FIT IN MY HAND."

**Builder: the new Claude Code builder chat on Jake's PC.** One builder for this film, start to finish. You build it; Claude (in the cloud) reviews it.
**How to build:** follow `Studio Bible\10 How Astra Builds a Video.md` (Astra's real process: paths, tools, cast, lip-sync, render, captions, sound, print, screening, delivery). Read `09 Claude Builder Handoff.md` and the evening-of-11-25 notes in `00 Start Here.md` first.
**CLEAN edition only.** No sponsor ending (it would break the loop).
**Quality bar: Moth Wings / Crown Stag.** Claude rejects anything below it.
**The PC is busy:** Astra's 100 Doors render queue is still running. Don't touch it. Build sets, cast and dailies now; run **one heavy render at a time**, so start the full native render only when the 100 Doors workers have finished (check the processes as note 10 shows). Keep frames on D:, delete temp frames after delivery.

Jake approved the script and the voice (Thu 11-26, 12:00 AM: "Automatically approve it"). Voice final: `snow-globe-voice-final.mp3` (53.23 s, Adam, 3.8 words a second). Never re-voice or re-time it. Captions: `snow-globe-lines.srt`; word times: `snow-globe-word-timings.json`. Script: `snow-globe-script.txt`.

## THIS IS AN INFINITE LOOP REEL (the most important thing)
- The voice ends on "...the king hides under his bed, **because**" and the video restarts on "**In this town**, the sky is glass, and a giant eye is always watching." It plays as one sentence on repeat.
- **The film is exactly 1,597 frames (53.233 s at 30 fps).** The audio ends at 53.230 s on purpose. Don't add a tail, a fade, an end card or black.
- **The last shot and the first shot are the SAME shot** (same camera, set, light, eye position, title, handle). The final shot (from about 52.4 s, "...bed, because") must flow straight into frame 0, so when the video repeats you can't see the join. Render it as one continuous shot of a cycle: the end shot is the moments just *before* frame 0, the opening shot is the moments just after. The falling snow must cycle seamlessly across the join. No cut at the loop point.
- **Title:** on screen in the top band for the opening shot (0 to about 2.8 s) **and** on the final shot (52.4 s to the end), so the last frame matches frame 0 exactly. Handle top left all the time.
- **Sound:** no fade-in at the start and no fade-out at the end. The town ambience (soft wind, distant bells, snow hush) at the end must match the start in level and texture, so the loop is seamless in sound too.

## World rule (it carries the story)
The town is inside a snow globe. **The glass makes everything inside it small; anyone who steps outside it is the size of the real world.** The sky over the town is the curved inside of the glass. The "earthquakes" in town are the globe sliding on its shelf in the wind from an open window.

## Cast (Cast v2: append from `cast-v2/cast-v2.blend`)
- **The kid (lead):** `Cast v2 | Hero kid`. Small, brave, cheeky. Use his full expression set; his face changes every beat.
- **Little sister:** `Cast v2 | Little sister` (pink dress, twin tails).
- **The king (NEW, Claude authorizes you to add him):** build him with `cast-v2/cast_v2.py`'s `person()` exactly like the other 13, and save him into the cast as `Cast v2 | King`. Adult, wide round body (Big-kid build at adult height), pale pink skin, **classic Roblox head with the classic faces** (smile, angry, scared, shocked: his scream must read huge), short grey beard, a tall gold crown with red gems, a deep red velvet robe with white fur trim and a gold chain (fine weave texture like the others). Push him on the cast check.
- **Townsfolk and guards:** mix the others (Newbie, Bacon kid, Big kid, Girl hero, Wizard, Slender teen, Goofy guard, Knight as the king's guard captain). No two people in a shot share face style, skin and body.

## Places (they must read as the script says; scale must stay true)
1. **The town inside the globe:** a snowy medieval town, lantern-gold windows, warm stone, a **bell tower** (with inside stairs), the **castle** with the king's balcony and his bedroom, the family's cottage with the sister's bedroom. Golden evening light, bright and warm. Through the curved glass sky you see the blurred warm room outside. Reuse a snowy town from an earlier episode if it fits (Astra's snow sets in `episodes\` such as phoenix or footprints) and relight it gold.
2. **The glass:** a clean, slightly refractive dome with warm reflections. It is "magic-soft": when the kid pushes through, it **ripples like a soap bubble and closes behind him**. It never cracks or shatters.
3. **The room outside:** a cosy, normal-size bedroom in golden evening lamp light. A wooden **shelf by an open window** (curtains blowing, snow outside), books, a candle, a teacup for scale, and a sturdy table. The snow globe has a carved wooden base.
4. **The eye (frame 0 and the last shot):** the kid's own eye, outside the glass, full-screen-big. Build a **high-detail eye matching the Hero kid's eye design and colours** (painted at high resolution so it stays crisp at full screen; eyelid, lashes, a soft curious brow, one bright lamp glint). Warm it with lamp light. It must blink and look around. It must feel friendly and curious, never horror.

## Frame 0 (cover)
Low angle from the town square looking up: lantern-gold roofs, the bell tower pointing up, the curved glass sky, and **a huge warm eye pressed against the glass**, looking down at the town. Three or four tiny townspeople looking up. Snow drifting. **Warm, NOT blue:** keep cool tones under a quarter of the frame; bright (average brightness 85+). Title **MY WHOLE TOWN FIT IN MY HAND.** in the 9-20% height band above the eye. Handle top left. In the first second: the eye blinks once and the pupil slides down to look at the town.

## Beats (times in the final voice track; a new shot about every 1 to 1.5 s, each showing exactly what the voice says)
| Time (s) | Line | Picture |
|---|---|---|
| 0.00-4.21 | In this town, the sky is glass, and a giant eye is always watching. | FRAME 0 (the loop shot). Then the same eye from a second low angle over the castle; then townspeople glancing up nervously. |
| 4.48-8.23 | The king said a monster lived up there, so small boys like me must never look up. | The king on his balcony jabbing a finger at the sky ("monster" 4.94); a "NO LOOKING UP" sign; the kid, smallest in the crowd, made to stare at his boots ("look up" 8.0). |
| 8.51-11.68 | Whenever the town shook like a jar of marbles, he blamed the monster. | On "shook" (9.07) the whole town jolts sideways: snow flies level, a soup bowl slides off a table, people grab posts. The king points up and shouts ("monster" 11.19). |
| 11.93-13.54 | And my little sister hid under her bed. | The sister's boots sticking out from under her rattling bed, her scared eyes in the dark. |
| 13.75-15.72 | So I ran up the bell tower and looked up anyway. | The kid sprinting up the **inside** tower stairs ("ran" 13.99); bursting out at the top, tipping his head back ("looked up" 14.96). |
| 15.93-18.86 | There was no monster, only glass as thin as a soap bubble. | Empty warm sky. His fingertip touches the glass ("glass" 17.21) and it ripples like a soap bubble. |
| 19.08-21.01 | I pushed through, and I learned the secret. | He pushes through the rippling glass ("pushed" 19.16). From outside: a tiny kid popping out of the top of the globe, the glass closing behind him. |
| 21.20-23.33 | That glass makes everything inside it small. | One clear shot: the tiny lit town inside the globe, the big room around it. |
| 23.52-26.55 | Outside it, I grew until my town was smaller than my shoe. | He shoots up to full size in the room ("grew" 24.40, one of the two shots allowed a slow camera move). His boot lands beside the globe; the boot is bigger than the whole town ("shoe" 26.16). |
| 26.80-30.46 | We lived inside a snow globe, and the wind kept sliding it toward the edge of a shelf. | Wide: the globe on the shelf by the open window, curtains whipping, the globe skidding toward the edge. A half-second cut inside: the town jolts (same shake as 9.07). |
| 30.68-33.18 | One more gust tipped it over the edge, and I caught it. | The globe tips over the edge ("tipped" 31.48), falling; his hand shoots under it; **catch on "caught" (32.77)**. Clean catch, nobody inside hurt. |
| 33.40-36.41 | My whole town fit in one hand, like a snowy cupcake. | Close on his palm: the glowing globe, tiny lit windows, snow swirling. Then the kid's proud grin. |
| 36.64-40.01 | The king looked up, saw a giant eye, and screamed, "Monster!" | Inside, from the frame-0 angle: the giant eye fills the sky ("eye" 38.26). The king's face: classic scared/shocked face, crown tumbling off, scream on "Monster!" (39.33). |
| 40.27-44.03 | It was me, the boy he called small. Now he was shorter than my fingernail. | Outside: the kid's eye at the glass, calm and amused. His fingertip beside the tiny king on his balcony; the king is shorter than his fingernail ("fingernail" 43.44). |
| 44.25-47.20 | I was never small. I was just on the wrong side of the glass. | He shuts the window and sets the globe on the sturdy table, away from every edge. A hero shot of the kid, full size, the globe glowing beside him. |
| 47.45-50.01 | Now every evening, I press my eye to the glass. | Golden evening. He leans down; his eye closes in on the glass ("eye" 49.13). |
| 50.23-53.23 | My little sister waves. The king hides under his bed, because | The sister waving up from her window, smiling ("waves" 50.85); the king's crown and boots poking out from under his bed ("bed" 52.54); then the LOOP SHOT (= frame 0) from about 52.4 s to the last frame, flowing into frame 0. |

## Camera (Jake's evening notes)
Steady, **locked camera inside each shot**; the cuts carry the energy. Vary the shot size. Slow moves only for the two reveals that earn them (the grow, the catch). **Never freeze a frame:** held shots breathe, blink and have snow moving. **Realistic, eased movement with different speeds** per character, and **stagger the timing** (people never start and stop together). **Believable, varied faces** that fit each moment. **Scale stays true:** show a known object (the teacup, a book, the boot, a fingertip) next to the globe whenever size matters. No shake or whips (Claude adds finishing in post, but NOT a swipe-in on this one, because it would break the loop).

## Sound
**No music bed.** Effects only, voice untouched: soft town ambience (wind, distant bells, snow hush) that loops seamlessly; a jar-of-marbles rattle and low rumble on each town-quake; rattling bed; footsteps on stone stairs; a soft glass hum; a bubbly "bloop" ripple when he touches and pushes through; a rising whoosh as he grows; a boot thump; wind gusts and flapping curtains; a wooden scrape as the globe slides; a falling whoosh and a soft thud with a glass chime on the catch; a twinkle of swirling snow in his palm; the crown clattering; the window shutting.

## Caption (Claude posts it; for your notes.json)
Comment question: "If you climbed out and grew giant, would you A) stay out and guard the town, or B) shrink back in and go home?" Chips: "A - STAY GIANT" / "B - GO BACK HOME".

## Proofs, then keep building
Push `proofs/snow-globe/cast-check.png` (the kid, the sister, the new king, the townsfolk) and `proofs/snow-globe/frame0.png`, then keep building. Claude reviews them and only writes back if something must change.

## Deliver
- `snow-globe-clean.mp4` (1080 x 1920, 30 fps, exactly 1,597 frames, under 25,000,000 bytes, about -14 LUFS), `snow-globe-cover.png` (frame 0), `snow-globe-thumbnail.jpg`, `notes.json`, to `ready/snow-globe/` on main.
- Screen every frame (note 10, section 6). Also **play the loop**: last 3 s straight into the first 3 s, picture and sound, and confirm you can't see or hear the join.
- Add a dated entry to the Builder log at the end of note 09. Delete temp frames afterwards.
