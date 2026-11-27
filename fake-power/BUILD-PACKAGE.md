# BUILD PACKAGE: MY FAKE POWER BEAT THE STONE GIANT (fake-power)

**Jake approved the script (Fri 11-27, 12:30 PM) and the voice is final.** He wrote it in the Idea lab over our hit "The stronger you are, the more chains" (344K), line for line. **Who builds it (Jake's pick): a NEW Claude video builder** (the PC builder is busy with Tiny Seed and Truth Sword), plus Claude's model builder for the big models.

**Edition: CLEAN only** (Facebook, TikTok, YouTube and Instagram). No music bed from you: Claude adds music in the finishing pass.

## THE FORMAT: STILL-FRAME FILM (Jake, 12:30 PM; read this first)
Jake wants this one in the older **non-animated** style that all our viral hits used (Reflection, Guardian, Chains): every shot is a **still render**. Characters hold a pose for the whole shot: no walking, swinging or jumping animation. That is the only change. **Everything else he picked in the app stays exactly as chosen:**
- **Camera moves (Torchlit Blocktale):** a continuous slow push-in on most shots, pull-outs to show scale, a small handheld wobble on every shot (bigger in action), a roll drift on about every other shot, a snap push on shock words, and motion-continuous hard cuts. Do these as **2D post-moves on oversized stills** with `styles/gneef-style/pack/post_gneef.py` (`push`, `snap`, `wobble`, `roll`). Render every still at **1296 x 2304** (1.2x) so the moves never show an edge, then crop and scale to 1080 x 1920.
- **Faces change expression** every beat, like in a moving film: about 70% of the shots where a face is visible show a new expression, and the expression swaps on the stressed word (Toybox "face-swap punch"; same framing, new face = a second render of that shot, or a re-composite of the face region).
- **Mouths move when someone talks.** On every spoken quote (lines 9, 10 and 24) the speaker's mouth flaps on the syllables: alternate closed / half-open / open mouth faces at about 8 to 10 swaps a second, following the word timings, and closed in the gaps. Make an open-mouth and half-open-mouth version of each speaker's face style if the set doesn't have one, drawn in that face style's line art. When the narrator kid faces camera on a narration line, his mouth may move the same way.
- **Look:** Toybox Fable base. **Captions and effects:** Torchlit Blocktale (below). **Six face styles**, one per person (below).
- Cheap trick for the face and mouth variants: render the full still once, then render only the face region again with Cycles border render (`render.use_border`, `use_crop_to_border` off) for each extra expression and composite it over the base still. That keeps the variants fast.

## Files in this folder
- `fake-power-voice-final.mp3`: final narration (Adam), already at final speed. **86.6 s**, -14.1 LUFS, md5 starts `68043ca7`. Never re-voice or re-time it.
- `fake-power-lines.srt` and `fake-power-word-timings.json`: caption and word timings for that mp3.
- `fake-power-script.txt`: the script, one caption line per line.
- `models/` (arriving from Claude's model builder after 1 PM): `fake-power-models.blend` + `glb/` + `MODELS.md` + previews. Start with the shots that don't need them; use simple stand-ins only for layout and swap the real models in when they land.

## Build style: Jake's mix (picking it is his yes to the overrides, this film only)
- **Base look: Toybox Fable** (`styles/craftee-style/`): bright neutral game-map town in plain daylight, moderate saturation, crisp soft-edged shadows, no grade. Use its pack (`apply_look`, `light_rig('noon')`, `cut_plan`).
- **Cut rhythm: Toybox Fable** `cut_plan(word_timings, 'standard')`: hard cuts on word onsets, about 1.2 s a shot (about 1.0 s in the first 30 s), one shot per phrase. That's about 65 to 75 shots.
- **Camera moves: Torchlit Blocktale** (`styles/gneef-style/` STYLE.md §4 and §14), as 2D post-moves (above).
- **Captions: Torchlit Blocktale** (`captions_gneef.json`): one white word at a time, Poppins Bold 72 px, thin black outline and soft shadow, baseline y = 1330, 2-frame pop-in, on the spoken onset.
- **Effects: Torchlit Blocktale** (§14): effects land on actions, not cuts; sound-ring rings on the crowd gasp and the badge hitting the ground; a whiteout glow (3 frames) into the moment the lantern fists light up (line 8); one stepped jump-cut burst (3 cuts, each a little tighter) on line 16 "It cracked". No flash frames, no shake bursts.
- **Light:** Toybox daytime for the town, bridge and river. The nightly boulder punching (lines 4, 26, 27) is moonlight, a hard cut each way.

## Cast (Cast v2) and face styles (one face style per person for the whole film)
| Who | Cast v2 | Face style |
|---|---|---|
| **Narrator ("I")**, 12, the "lantern boy" | Hero kid | **Storybook** (`ready/faces/storybook/` on main) |
| **His little sister**, 5, hums everywhere | Little sister | **Anime Shine** (`ready/faces/anime-shine/`) |
| **The guard captain**, thunder fists, 20 years, top rank | Knight | **Inkface** (`styles/gneef-style/faces/` on scripts-inbox) |
| **The duke**, ranks every kid, never got a power, squeaks "Arrest him!" | King (in duke's clothes: no crown, a velvet cap and a chain of office) | **Classic Block** (`ready/faces/classic-block/`) |
| **The baker's kid**, hot hands, brags | Rich kid (flour-dusted apron over his clothes) | **Bold Comic Ink** (`ready/faces/bold-comic-ink/`) |
| Guards and the crowd | Goofy guard + the other Cast v2 people | **Toybox** (`styles/craftee-style/faces/` on scripts-inbox) |
Don't invent new people. The stone giant has its own face from the model pack.

## Scale (keep it true)
Hero kid 4.16 BU, sister 3.37, captain 5.67 (1 m = 3.3 BU). **Stone giant about 70 to 80 BU**: the bridge reaches about his knees. **The giant's boulder is bigger than the kid** (about 6 to 7 BU), and he holds it up with one glowing fist. The kid standing on the giant's forearm is a small figure on a huge stone arm.

## Frame 0 and the cover
- **Frame 0 = the cover:** on the stone bridge, the small kid holds the giant's boulder over his head with ONE glowing lantern fist, the stone giant looming behind and above, his sister tiny behind the kid's legs, the crowd on the riverbank. Low angle, bright daylight. Title **MY FAKE POWER BEAT THE STONE GIANT** (white caps, black outline, key words "FAKE POWER" in the accent colour, in the 9-20% band), handle `@idlemerchantrng` top left.
- Frame 0 is already moving (a push-in). Hold it under the title about 1.5 s while line 1 starts, then cut into the story.

## Shot list with final times (split each line into shots with `cut_plan`; these are the pictures to cover)
| # | Time (s) | Line | On screen |
|---|---|---|---|
| 1 | 0.00-4.08 | In this town, every kid gets a fighting power at twelve, and the duke ranks us all. | Frame 0. Cut: a twelfth-birthday kid on a festival stage, sparks around her hands. Cut: the duke in front of a huge wooden **ranking board** (kids' names, power icons, gold numbers), pointing at it with a smug face. |
| 2 | 4.27-7.77 | The baker's kid got hot hands and brags. The captain got thunder fists. | The baker's kid with red heat shimmering round his hands, smug, a loaf toasting in his grip. Cut: the captain, low angle, blue-white lightning crackling round his fists. |
| 3 | 7.98-10.61 | Mine's a fake. My fists just glow like lanterns. | The ranking board's bottom row: the kid's name with **FAKE** stamped across it. Cut: the kid holds up his fists; they glow a soft warm gold, like two lanterns. Embarrassed face. |
| 4 | 10.89-12.58 | Every night, I punched boulders anyway. | **Moonlight.** The kid alone in a rocky yard, fist into a boulder with a dent in it; more dented boulders around him. Determined face. |
| 5 | 12.78-15.56 | Today a stone giant stomped onto my little sister's bridge. | **Day.** Low angle: the stone giant (STOMP-ANGRY) planting a foot beside the stone bridge, water splashing. Cut: the sister on the bridge, small, looking up. |
| 6 | 15.75-17.71 | She's five. She hums everywhere. | Close on the sister, humming (music-note stickers drifting up), happy face, then a scared face as the giant's shadow falls on her. |
| 7 | 17.93-19.80 | So I ran past the guards. All of them. | The kid mid-stride (held pose) past a line of guards with spears; guards' faces shocked, one dropping his spear. |
| 8 | 20.00-22.42 | My fists lit up. The whole crowd gasped. | 3-frame whiteout, then close on the fists blazing gold. Cut: the crowd on the riverbank, mouths open (sound rings from the crowd). |
| 9 | 22.63-24.67 | "Go home, lantern boy," the captain said. | The captain blocks the way, **mouth moving** on "Go home, lantern boy", sneer. |
| 10 | 24.87-25.43 | "Make me." | Close on the kid, **mouth moving**, fierce face. Snap push. |
| 11 | 25.63-29.03 | He has the strongest power alive. He shoved me with thunder fists. | Low angle on the captain, lightning fists raised. Cut: both lightning hands pressed on the kid's chest, sparks everywhere. |
| 12 | 29.20-31.14 | His boots slid backward. I didn't move. | Insert: the captain's boots with skid marks behind them in the dust. Cut: the kid standing firm, calm face; the captain's shocked face. |
| 13 | 31.35-33.96 | The giant swung a boulder. I caught it with one fist. | The giant (SWING_WINDUP) with the boulder overhead. Cut: the **cover moment**: the boulder stopped on one glowing fist, dust burst. |
| 14 | 34.12-35.96 | Yes. It felt as good as you think. | Close on the kid's grin under the boulder (proud, cheeky). |
| 15 | 36.15-38.07 | One jump, and I was on the giant's arm. | The kid standing on the giant's level forearm (ARM_OUT), tiny on the huge stone arm, the giant's surprised face behind. |
| 16 | 38.25-41.10 | I hit his rocky arm. It cracked, and he fell in the river. | The punch (glow flare at the fist). **Stepped jump-cut burst** on "cracked": the CRACK state, three tighter cuts. Cut: the giant falling back into the river, a huge splash (FALL_BACK), then sitting dazed in the water (SITTING_IN_RIVER). Nobody hurt. |
| 17 | 41.33-44.15 | A beam had fallen on my sister. I lifted it like a twig. | The fallen bridge beam over the sister (she's fine, just stuck, scared face). Cut: the kid lifting the beam one-handed, easily. |
| 18 | 44.37-46.57 | Then I did the one thing I was never allowed to do. | Close on the kid looking at his glowing hands, hesitant face. |
| 19 | 46.76-47.64 | I hugged her tight. | The hug: the kid lifts his sister into a hug, eyes shut, warm face. |
| 20 | 47.87-51.09 | The duke always said glowing fists burn things. I believed him. | Flashback-style insert: a sign in the square, "GLOWING FISTS: DO NOT TOUCH" with the duke's seal. Cut: the kid's worried face. |
| 21 | 51.28-52.78 | She didn't burn. She laughed. | The sister laughing in the glow, happy. |
| 22 | 53.01-53.83 | I looked up at the duke. | The kid looking up (low angle past his shoulder) at the duke on the riverbank. |
| 23 | 54.00-56.16 | He never got a power at all. So what does that make him? | The duke's empty hands, nervous face. Insert: the ranking board's top: the duke's name with no power icon. |
| 24 | 56.51-58.70 | "Arrest him!" he squeaked. Nobody moved. | The duke, **mouth moving** on "Arrest him!", squeaky panicked face. Cut: the guards not moving, arms folded. |
| 25 | 58.92-59.91 | Here's what the duke missed. | Push in on the kid, knowing face. |
| 26 | 60.08-62.27 | More boulders every night. Never enough. | **Moonlight** montage stills: more and more dented boulders, the kid older-looking stance, fists glowing. |
| 27 | 62.45-64.88 | What happens to a kid who punches a mountain of rock every night? | Wide, moonlight: a whole hill of cracked boulders behind the small kid. |
| 28 | 65.10-66.79 | My fake power never made me strong. | **Day.** Close on the glowing fists (soft lantern glow). |
| 29 | 66.94-67.74 | The boulders did. | Hard cut back to the night yard: a boulder split clean in half. Snap push. |
| 30 | 67.92-70.61 | The duke laughed so hard at weak kids that he made a strong one. | The ranking board: the kid's FAKE stamp. Cut: the duke shrinking back, the kid standing tall. |
| 31 | 70.82-72.58 | And he called half this town's kids fake. | The bottom half of the ranking board: lots of names stamped FAKE. |
| 32 | 72.82-74.53 | The crowd looked down at their own fists. | Close on several crowd kids looking at their own hands, staggered faces (thinking, surprised). |
| 33 | 74.71-76.25 | Then a badge hit the ground behind me. | Insert: the gold top-rank badge landing in the dust (sound rings). |
| 34 | 76.44-77.83 | The captain was throwing his away. | The captain, his hand still open, serious face, no badge on his chest. |
| 35 | 78.00-79.56 | Twenty years. Top rank. | Insert: the badge's three stars, close. |
| 36 | 79.73-81.47 | Almost twice as long as I've been alive. | The captain and the small kid side by side (scale of age). |
| 37 | 81.71-83.74 | He wasn't looking at me. He was looking at my sister. | The captain's softened face, looking down. Cut: the sister smiling up at him from the kid's arms. |
| 38 | 83.91-84.95 | And I was still holding her. | The kid holding his sister, the giant sitting in the river far behind. |
| 39 | 85.17-86.58 | What would they call your power? | Close on the kid's face, then the end screen. |

## End screen (signature, over the final shot)
Printed question: **WHAT WOULD THEY CALL YOUR POWER?** Chips: **A: REAL** / **B: FAKE**. Follow line: **FOLLOW FOR MORE "IN THIS TOWN"** (no Part 2 promise).

## Models (Claude's model builder, NOT you)
Being built in the cloud (brief: `models/MODELS-BRIEF.md`): the stone giant (rigged, poses, crackable right forearm, face states), the stone bridge + river + loose beam, the giant's boulder + training boulders, lantern fists (glow 0-1), thunder fists + hot hands, the top-rank badge. They land in `fake-power/models/` with `MODELS.md`. Don't build these yourself. Build the town sets, the ranking board, the sign and the people.

## Kid-safety picture rules
The giant is big and grumpy but never horror: no fangs, no red eyes. Nobody is hurt: the giant just sits dazed in the river; the sister is stuck under the beam, not crushed, and fine. The lantern fists glow, never burn.

## Deliver
`ready/fake-power/fake-power-clean.mp4` (1080 x 1920, 30 fps, about -14 LUFS, under 25 MB), `fake-power-cover.png` (frame 0), `fake-power-thumbnail.jpg`, `notes.json`. Cast check to `proofs/fake-power/cast-check.png` first, then keep building. Every-frame check before delivering (no pops, no edges showing from the post-moves, no frozen stretches longer than one shot, captions never empty while the voice runs, mouths closed when nobody talks).
