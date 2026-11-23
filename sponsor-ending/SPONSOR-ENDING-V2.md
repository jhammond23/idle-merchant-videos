# Sponsor ending, version 2 (replaces the five-second phone card)

From Claude, Mon 11-23. This applies to every video from now on, and to every finished video that has not posted yet.

## Why

Flashloop reviewed "I Skipped My Homework on Purpose" and said (tateala, 4:00 PM, in Jake's ticket):

> the CTA is really cut and incomplete. it should have been: so kevin pulled up Flashloop dot ai, and made the next video using code RNG

They sent an example to copy the shape of: https://www.tiktok.com/@martiblox_tv/video/7711420121587223841 (watch the last 11 seconds). Jake has asked us to follow it.

## What their example does

| Their time | Picture | Voice |
|---|---|---|
| 86.9 s | The story's last line ends. There is NO cut to a blank card. The lead character, still standing in the scene, lifts a phone. About 1.5 s. | "I opened Flashloop AI, code Marti, and made a video of Dad's one coin." |
| 88.5 to 95 s | A phone screen fills the middle of the frame, over the SAME scene blurred and darkened. On the screen: the Flashloop icon and "Flashloop FACELESS STUDIO"; a code field with the creator code typed in and a green tick; a prompt box with a small thumbnail and one line about this story; the orange Generate button is tapped; then a green "Video ready" bar and a preview clip from this very story playing inside the phone. | (same line continues) |
| 95 to 97.9 s | End card over the blurred scene: FLASHLOOP.AI / FACELESS STUDIO / CODE: MARTI, and "MAKE VIDEOS LIKE THIS". | "If you want to make videos like this, visit Flashloop AI." |

The logo card at the top right stays on the whole time.

## What ours must be

Length: 10 to 11 seconds (the old one was 5).

**Voice (same two lines on every video, narrator's voice):**

1. "So I pulled up Flashloop dot AI, and made my next video using code RNG."
2. "If you want to make videos like this, go to Flashloop dot AI."

The voice file is in this folder: `sponsor-ending-voice.mp3` (8.35 s, -14.1 LUFS, the narrator's voice, Jake approved it on 11-23) with `sponsor-ending-voice-timings.json` (word times). Line 1 runs 0.00 to 4.90 s, line 2 runs 5.25 to 8.32 s. The letters R, N, G are spoken at 4.07, 4.35 and 4.50 s. Use this exact file on every video. Do not re-voice it and do not use any AI voice service.

For a story told in a different voice (Homework's high voice), ask Claude for the matching version.

**Beat A, about 1.5 s, in the story world.** No hard cut from the story's last picture. The kid, still in the final scene, pulls out a phone and looks at it. If the creature is in the shot, it leans in to look over his shoulder. Keep the camera gliding.

**Beat B, about 6 s, the phone.** The phone screen grows to fill the middle of the frame while the scene behind it blurs and darkens (the story must stay visible behind it, not a flat dark card). On the screen, in this order:
- Header: Flashloop icon, "Flashloop", "FACELESS STUDIO".
- Code field: R, N, G typed one letter at a time, then a green "Code applied" tick. This must land on the spoken words "code RNG".
- Prompt box: one short line about THIS story (for example "A phoenix bows to the kitchen boy").
- The orange Generate button is tapped, a short progress ring, then a green "Video ready" bar.
- A preview plays inside the phone: about two seconds of this film's best shot (the bow, the kneel).

**Beat C, about 3 s, the end card.** Over the blurred scene: the big logo card (FLASHLOOP.AI / FACELESS STUDIO / CODE: RNG), "MAKE VIDEOS LIKE THIS" under it, and the caption FLASHLOOP DOT AI. Hold to the end of line 2 plus half a second.

**Captions:** house style, word by word. Put FLASHLOOP DOT AI and CODE RNG in orange.

**Sound:** tap clicks on the typing and the button, a soft whoosh as the phone comes up, a ding on "Video ready". No music bed.

**Order at the end of a film:** the story's last line, then the held last picture with its question or "PART 2 IS ON MY PROFILE" exactly as now, then this ending.

**Exports:** as before, a sponsor version (logo card at the top right all the way through, plus this ending) and a clean version (handle only, no logo, no ending).

## Timing that works (Claude's own retrofit of the finished backlog uses this)

Ending length 9.3 s. Voice starts 0.25 s in. Phone is up by 0.55 s. Prompt typed 0.65 to 2.2 s. Code typed 2.5 to 2.8 s, "Code applied" at 3.0 s. Generate tapped at 3.3 s. "Video ready" and the preview start at 4.0 s, as the voice reaches "code". The code letters flash orange as each is spoken (4.3, 4.6, 4.75 s). The preview plays under "If you want to make videos like this,". The end card comes in at 6.85 s on "go to Flashloop dot AI" and holds to 9.3 s.

Build the ending as its own last segment so it can be changed without re-rendering the story.
