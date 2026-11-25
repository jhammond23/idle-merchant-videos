# moth-wings review notes (Claude)

## Round 1: test clip at main fb58deb (Tue 11-24, 6:45 PM). NOT ACCEPTED YET: close, one more pass

**What already matches the reference. Keep all of it:**
- Brightness 145 (target 140 to 155). Sunny, bright, clean.
- 16 shots in 15.1 s, average 0.95 s. The rhythm is right.
- The camera holds still inside shots. No glitches, flashes or strobing. Loudness -13.8 LUFS.
- Captions: small white words in the lower middle with one red word. The "1 IN 1,000" tag and the Wing Register board are exactly the kind of literal picture we want.
- The cast is the locked cast with rounded heads. The cast still goes to Jake for CAST OK.

**What to fix (most important first):**

1. **Every shot needs an action or a big face.** In the reference, nobody just stands facing camera: they flap, point, flinch, laugh, flex or react. In our clip, shots 2, 5, 7, 8, 9, 10 and 12 are the same pose (standing square to camera, arms out) in front of the same stage. Give each person one clear action or expression that says the line:
   - Shot 2/3 "every kid grows wings": the wings **burst out** of their backs (a pop, feathers flying), and the kids look over their shoulders, delighted.
   - Shot 7 "Sparrow wings are weak": he flaps hard, lifts an inch, drops back down, and looks embarrassed.
   - Shot 8 "Eagle wings are strong": he **hovers** a metre up with his arms crossed, smug.
   - Shot 9 "Griffin wings": low angle as the golden wings unfold to full width, with a gust lifting dust.
   - Shot 12 "But on my tenth birthday": I'm on the stage, eyes shut and fists clenched, hoping.
   - Shot 16 "the size of my hands": a **close-up** of my open hand held next to one tiny wing, the same size. Right now we're too far away to see it.
2. **Change the place or the angle at every cut.** Seven shots in a row use the same bunting-and-stage background from the front. The reference changes the location (hallway, gym, field, park) or the angle every time. Use several corners of the town (the square, a bakery door, a rooftop, the fountain, a field outside the gate) and mix in side, over-the-shoulder, high and low angles. Never two cuts in a row with the same background and the same angle.
3. **Make the moth wings read as moth wings.** Folded, they look like two grey ears. Give them a moth shape: scalloped edges, fuzzy texture, two dark eye spots, so a viewer reads "moth" in half a second.
4. **A bit more colour.** Saturation is 0.40. Push it to about 0.50 to 0.55 and keep brightness at 140 or above (our own style is more colourful than the reference).
5. Shot 14 "I grew moth wings": show the moment they pop out (a tiny "pff" of grey dust), then my face looking back at them.

**Next:** push a new `proofs/moth-wings/test-clip.mp4` (same 0 to 15.11 s) and reply with the commit. Same voice, same cut times. No full film yet.

## Jake, 6:49 PM: APPROVED. Build the full film now.

Jake watched the round 1 test clip: "that video is pretty dope. I am digging that, go ahead and build the rest of that out." **CAST OK moth-wings. Test accepted.**

- **Keep everything in the round 1 clip exactly as it is.** Do not rebuild shots 1 to 14 unless your round 1 fixes are already done and better.
- **Build shots 15 to 48 in the same style.** Use round 1 notes 1, 2 and 4 as you go: an action or a big face in every shot, a new place or angle at every cut, rich colour. The reveal (shots 46 to 48) is the money shot: the wings opening to many times his height and blocking out the sun, with the whole cliff in shadow. Make it huge.
- **Clean edition first:** `ready/moth-wings/moth-wings-clean.mp4`, plus the cover and posting thumbnail (the reveal, title MY MOTH WINGS STOPPED A GRIFFIN.). The sponsor edition waits: its ending line is being written for this video.
- Run qa/glitchscan.py and qa/stylecheck.py on the full film before you push. Reply in the chat with the commit.

## Round 2: revised opening at main 435828a (Tue 11-24, 7:20 PM). ACCEPTED

- stylecheck: 16 shots, average 0.94 s, brightness 144, saturation 0.52. All on target. glitchscan clean.
- All five round 1 fixes landed: feathers burst out on "grows wings", a new place or angle at every cut (fountain, field, rooftops), the moth wings now read as moth wings (fuzzy, scalloped, with an eye spot), more colour, and the close-up of my hand next to the wing.
- **Use this opening in the full film.** Carry the same rules through shots 15 to 48.

## Round 3: Jake's changes to the finished film (Tue 11-24, 10:21 PM). Re-render THREE shots only

Jake watched the finished film (main `403161f`) and wants two things before it posts. Everything else stays exactly as delivered: same voice, same cut times, same 48 shots. Re-render only shots 1, 5 and 24, then re-export `ready/moth-wings/moth-wings-clean.mp4` (same name) and reply in the chat with the commit. Claude re-runs the finishing pass (zooms, shakes, grade, dust) afterwards, so add **no** camera shake, zooms or post effects yourself.

**1. A far more epic opening shot (shot 1, 0.00 to 0.66 s, "In this town,").** Right now it is a crowd standing in the square. Jake: "is there a more visually epic scene we can start?" Replace it with:
- **The sky above the town packed with flying kids**, dozens of them at different heights and distances, every kind of wings: small brown sparrow wings, big brown-and-white eagle wings, and a few huge griffin-gold ones.
- **Golden-hour sun** low behind them, rays through the wings, feathers drifting. The town, the clock tower and the bunting are small far below.
- **One griffin-gold kid (the duke's son, locked cast) swoops right past the camera**, close and fast, wings fully spread and filling a third of the frame, during these 0.66 s.
- Low angle looking up, bright and saturated (brightness 140 or more, like the rest of the film). Wings flap for real; nothing frozen. Motion blur on.
- Frame 0 must already be this image (no fade-in, no title card).

**2. A decorated ranking board with a picture of each wing type (shot 5, 4.02 to 4.87 s, "the higher you rank", and shot 24, 23.85 to 24.59 s, "the bottom felt").** Right now the WING REGISTER board shows small wing icons and names, which is hard to read on a phone. Jake wants a picture of one of each character with their wings, so it reads at a glance:
- Keep the same board in the same place, but make it **big and decorated**: gold trim, carved wood or stone frame, ribbons and bunting, laurel leaves, a small crown above the top row, lanterns or flowers at its feet.
- **Three tiers, each a large painted portrait in its own frame** (from the locked cast, rounded heads):
  - **I. GRIFFIN** (top, biggest, gold frame with a crown and stars): a kid with huge griffin-gold wings spread wide, proud pose.
  - **II. EAGLE** (middle, silver frame): a kid with big brown-and-white eagle wings spread.
  - **III. SPARROW** (bottom, bronze frame, smallest of the three): a kid with small brown sparrow wings.
- Under the three, a **tiny fourth row: MOTH**, a small, plain, slightly crooked frame with my portrait and my grey moth wings (fuzzy, scalloped, eye spot), my name last. In shot 5 it can be small or soft at the bottom; in shot 24 the camera shows it clearly, as the package says ("me at the bottom of the ranking board, my name last").
- The tier words (GRIFFIN, EAGLE, SPARROW, MOTH) are big enough to read at phone size. No other small text.

**Checks:** run qa/glitchscan.py and qa/stylecheck.py on the new export; the three shots must match the brightness and colour of their neighbours. Push to main and reply with the commit.
