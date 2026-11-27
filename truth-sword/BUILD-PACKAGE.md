# BUILD PACKAGE: MY SWORD GROWS EVERY TIME I TELL THE TRUTH (truth-sword)

**Claude's own idea, picked after a session in the studio app's Idea lab. Jake pre-approved it (Fri 11-27, 12:01 AM: "I will automatically approve it").** It is our Black Knight hit (118K views, 71 s average watch, our best watch time) remade line for line with a new world rule. **Builders: Claude only, no Astra.** Props come from Claude's model builder (see "Props"); the film comes from the Claude Code builder on Jake's PC, right after tiny-seed.

**Editions (Jake's last settings):** CLEAN for Facebook, TikTok and YouTube, plus the **Flashloop sponsor edition for Instagram** (`sponsor-ending/SPONSOR-ENDING-V2.md`, fixed voice file `sponsor-ending/sponsor-ending-voice.mp3`, do not re-voice). Phone prompt line for this film: **"A stable boy's sword grows with every truth."** No music bed from you (Claude adds music to the clean edition in finishing).

## Files in this folder
- `truth-sword-voice-final.mp3`: final narration, Adam, at final speed. **100.5 s**, -14.0 LUFS, md5 `21761345c9af2af3a63a7dee8ec730f6`. Never re-voice or re-time it.
- `truth-sword-lines.srt`, `truth-sword-word-timings.json`: caption and word timings for that mp3.
- `truth-sword-script.txt`: the script, one caption line per line.
- `models/` (arriving from Claude's model builder): `truth-sword-props.blend`, `MODELS.md`, previews.

## Build style: Jake's last mix (his yes to the overrides, this film only)
Same as tiny-seed: **Toybox Fable base** (`styles/craftee-style/`: bright neutral courtyard daylight, locked framing, cuts on the captions, big line-art faces that change almost every shot, prop gags), **camera moves and captions from Torchlit Blocktale** (`styles/gneef-style/`: slow push-in on most shots with a light handheld wobble; one white word at a time, keyword in the accent colour), **transitions and effects from Bright Snap Cut** (`styles/bright-cut/`: a whoosh or hit on about one cut in four, punch-ins, flash frames, sparingly). Daylight all the way through: this is a bright courtyard story.

## Cast (Cast v2) and face styles (Jake's six face styles, one per person)
| Who | Cast v2 | Face style |
|---|---|---|
| **Narrator, the stable boy** | Hero kid, in a plain brown tunic, straw on his boots, a wooden shovel | **Storybook** (`ready/faces/storybook/` on main) |
| **The Prince** | Rich kid (purple and gold, small circlet) | **Bold Comic Ink** (`ready/faces/bold-comic-ink/`) |
| **The King** | The King the Snow Globe builder added with `cast_v2.py` (red velvet, gold crown), wearing the empty scabbard prop | **Classic Block** (`ready/faces/classic-block/`) |
| **The Sword Master** (rings the bell, whispers line 24) | Wizard (long white beard, blue robe) | **Inkface** (`styles/gneef-style/faces/`) |
| A girl in the line of kids (cheers for him at line 21) | Girl hero (no sword on her back; her own small Sword-Day sword) | **Anime Shine** (`ready/faces/anime-shine/`) |
| The stable boy's little sister, in the crowd | Little sister | **Anime Shine** |
| **The guard captain** (line 35) and the guards | Knight (Cast v2) and armoured guards | **Toybox** (`styles/craftee-style/faces/`) |
| Crowd: townsfolk and royal kids | other Cast v2 people | **Toybox** |

## Scale and the swords (keep it true; Claude's props have a length parameter)
- Every kid holds a sword about 3-5 BU (kid ~5 BU). **The stable boy's sword starts at ~1 BU: a rusty sword the size of a spoon** (line 7).
- **Line 21:** it grows past his knees, then past his head (~6-8 BU).
- **Line 23:** it shoots over the rooftops, over the castle bridge and through a cloud (~700 BU). He still holds it easily with one hand; the blade turns clean bright steel with a faint glow as it grows.
- **The Prince's Golden Sword:** ~5 BU, gleaming; on line 16 it shrinks into a toothpick in his fist.
- **Guards' swords:** ~4.5 BU; the captain's grows "a foot" (+1 BU) on line 35, then all of them grow on line 36.
- **The King:** an empty jeweled scabbard on his belt the whole film. Nobody notices it until line 31.

## Frame 0 and the cover
- **Frame 0 = the cover:** low angle, the stable boy standing on the glowing Truth Stone, holding his sword up with one hand; the blade runs up over the courtyard rooftops and the castle bridge and disappears into a cloud. The Prince beside the stone gaping at a toothpick in his fist; the King on his balcony behind, hand over his empty scabbard. Title **MY SWORD GROWS EVERY TIME I TELL THE TRUTH** (white caps, black outline, "THE TRUTH" in the accent colour, 9-20% height band), handle top left. Toybox opening: a whip-blur that lands in 3 frames.
- Hold frame 0 about 1.6 s under the title while line 1 starts.

## Shot list with final times
| # | Time (s) | Line | On screen |
|---|---|---|---|
| 1 | 0.00-2.93 | In this town, your sword grows every time you tell the truth. | Frame 0 (cover), then a kid in the square saying something and her sword grows a hand's width with a "ting" and a sparkle. |
| 2 | 3.12-6.00 | I'm the stable boy, and my sword is longer than the castle bridge. | The stable boy in the stable with his shovel (Storybook grin). Cut: a quick flash-forward of the huge blade lying across the castle bridge. |
| 3 | 6.21-8.49 | Every Sword Day, I stand at the back with my shovel. | Courtyard full of bunting and royal kids in front; he stands at the very back by the horse troughs. |
| 4 | 8.72-12.25 | The Prince pulled the Golden Sword. It shone so bright the crowd squinted. | The Prince lifts the gleaming Golden Sword (glint flash, a Bright Snap Cut flash frame). Crowd squinting, hands over eyes (staggered). |
| 5 | 12.45-15.76 | He pointed it at me. "Careful, stable boy. Don't trip over your spoon." | Low angle: the Prince points the sword across the courtyard. Bold Comic Ink sneer. |
| 6 | 16.00-18.16 | The whole courtyard laughed, even the King. | Laughing faces, staggered. The King laughing on his balcony (his empty scabbard visible but unnoticed). |
| 7 | 18.37-21.11 | That morning, my sword was a spoon. Rusty, too. | Close: the tiny rusty sword in his palm next to a real spoon for scale. A flake of rust falls. |
| 8 | 21.34-23.61 | Then the Sword Master rang the bell for the Truth Test. | The Sword Master rings the bronze bell (the bell swings, rope pulls). Everyone turns. |
| 9 | 23.79-26.88 | Every kid stands on the stone and says one true thing out loud. | The Truth Stone in the middle of the courtyard: a girl steps up, speaks, the stone glows soft blue and her sword grows a little. |
| 10 | 27.06-29.53 | Lie on it, and your sword shrinks in front of everyone. | Quick gag: a chubby kid on the stone says something, the stone cracks red-orange and his sword shrinks; he hides it behind his back. |
| 11 | 29.76-31.87 | Nobody has passed it clean in a hundred years. | An old carved list on the castle wall: years and names, every one with a little crack mark. |
| 12 | 32.08-35.37 | The old story says the longest sword belongs to whoever should wear the crown. | Gold caption line. A stained-glass window: a figure holding a sword that reaches the sky, a crown above it. |
| 13 | 35.59-39.41 | The stone was cold as a frozen pond, and every lie cracked like a plate. | Close: frost breath over the stone; insert of a plate cracking (picture comparison). |
| 14 | 39.64-42.28 | The Prince went first. "I have never cheated at anything." | The Prince on the stone, chin up, Golden Sword raised. |
| 15 | 42.49-42.88 | Crack. | Hard cut: the stone cracks red under his feet (big crack sound, Bright Snap Cut hit). |
| 16 | 43.09-45.64 | His sword shrank. And shrank. Into a toothpick. | **ANIM 1:** the Golden Sword shrinks in two steps to a toothpick in his fist. His face drops. |
| 17 | 45.84-46.91 | Nobody laughed this time. | Wide: the silent crowd. The King's smile is gone. |
| 18 | 47.13-47.91 | Then it was my turn. | The crowd parts; the stable boy walks forward with his spoon sword. |
| 19 | 48.11-49.93 | I stepped on, and my knees were shaking. | Close on his knees knocking on the stone. Storybook nervous face. |
| 20 | 50.14-52.43 | So I said the truest thing I had. "I'm scared." | Close on his face, small voice. The stone glows blue. |
| 21 | 52.65-55.40 | My spoon grew. Past my knees. Past my head. | **ANIM 2:** the sword grows in two jumps, past his knees, past his head, with a "ting" each time. The girl in the line cheers. |
| 22 | 55.60-58.06 | Then I said, "I have never told a lie in my life." | Determined face; he lifts the sword with both hands. |
| 23 | 58.32-61.46 | My sword shot over the rooftops, over the bridge, through a cloud. | **ANIM 3, the big reveal move:** the blade shoots up and out over the rooftops and the castle bridge, the camera racing along it, and pierces a cloud. |
| 24 | 61.64-63.97 | The Sword Master whispered, "That's a king's sword." | Close on the Sword Master's wide eyes (Inkface), whispering. |
| 25 | 64.19-66.27 | The whole town gasped. The King didn't. | Gasping faces (staggered); cut to the King, calm, not gasping. |
| 26 | 66.46-67.49 | He wasn't surprised at all. | Slow push-in on the King's still face. |
| 27 | 67.69-69.34 | "I knew this day would come," he said. | The King stands up on his balcony. |
| 28 | 69.56-71.79 | Because ten years ago, the King stood on it too. | Flashback (warm sepia tint): a younger King on the Truth Stone, crowd watching. |
| 29 | 71.93-74.41 | He said one sentence. "I will be a good king." | Flashback: the young King says it, hand on heart. |
| 30 | 74.64-75.83 | His sword shrank to nothing. | **ANIM 4:** the stone cracks; his sword shrinks to nothing in his hand. He quickly closes his cloak. |
| 31 | 76.03-77.69 | He's worn an empty scabbard ever since. | Back to now: close on the King's jeweled scabbard: empty, no hilt. |
| 32 | 77.87-79.84 | "Guards!" he shouted. "Take that sword!" | The King points and shouts (Classic Block angry face). |
| 33 | 80.04-82.58 | A hundred guards drew, and the gates slammed shut. | Wide: guards drawing in a ring around the stone (no swinging, no fighting). The courtyard gates slam (Bright Snap Cut hit). |
| 34 | 82.78-85.70 | I didn't swing. I just told the truth. "His scabbard is empty." | The stable boy points calmly at the King's belt. Every head turns to the scabbard. |
| 35 | 85.85-88.53 | The captain looked. "It's true." His sword grew a foot. | The guard captain looks, nods; his sword grows a foot with a "ting". |
| 36 | 88.71-92.49 | Then every guard told the truth, and every sword grew. Except the King's. | Ripple of "ting"s as every guard's sword grows; the King left gripping his empty scabbard. |
| 37 | 92.68-96.09 | He hid his lie for ten years. My sword found it in one sentence. | Gold caption line. The stable boy on the stone with the giant sword, the King small on the balcony. |
| 38 | 96.34-100.42 | Do I take the crown? A, yes. B, no, I'm a stable boy. | The King's crown on its velvet cushion between them. Then the end screen. |

## End screen
Printed question: **DO I TAKE THE CROWN?** Chips: **A: TAKE IT** / **B: STAY A STABLE BOY**. Follow line: **FOLLOW FOR MORE "IN THIS TOWN"** (no Part 2 promise). The sponsor edition adds the Flashloop ending (V2) after it.

## Animation moments
1. The Golden Sword shrinks into a toothpick (line 16).
2. The spoon grows past his knees and his head (line 21).
3. The blade shoots over the rooftops and through a cloud (line 23).
4. The young King's sword shrinks to nothing in the flashback (line 30).
5. Optional: the ripple of guards' swords growing (line 36).

## Props (Claude's model builder, NOT Astra)
Claude's model builder is making the Truth Stone (glow state + red crack state), the stable boy's sword with a `blade_length` parameter (1 to 700 BU, rust turning to clean steel), the Golden Sword (shrinks to a toothpick), a guard sword (grows a foot), the King's empty jeweled scabbard, the Sword Master's bell on its frame, stylised clouds, and the shovel. They land in `truth-sword/models/` with `MODELS.md`. Use stand-ins until then. Everything else (courtyard, castle, bridge, people) comes from what you already have.

## Kid-safety picture rules
Swords are never swung at anyone. The guards draw and stand in a ring; nobody fights. The lies are small and funny. No one gets hurt.

## Deliver
`ready/truth-sword/truth-sword.mp4` (sponsor edition, Instagram), `truth-sword-clean.mp4`, `truth-sword-cover.png` (frame 0), `truth-sword-thumbnail.jpg`, `notes.json` to main. Proofs to `proofs/truth-sword/`, then keep building. Every-frame check before delivering.
