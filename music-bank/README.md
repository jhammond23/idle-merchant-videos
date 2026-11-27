# Music bank (from Thu 11-26)

Jake (11-26, 6:03 PM): build a bank of background music and reuse it going forward. Only create a new track in ElevenLabs when nothing in the bank fits the video.

This replaces the old "no music bed" rule. Every viral account we studied keeps quiet music or ambience under the narrator the whole time; we were the only one with silence between lines.

## How it works
1. Claude picks a bank track whose mood fits the story (`bank.json`: moods, energy, goodFor / notFor).
2. If none fits, Claude makes one: ElevenLabs Music v2.5, instrumental, 47 s, steady energy, no intro or ending (so it loops), sparse, no lead melody in the vocal range. One take. About 700 credits. Add it to `bank.json` with the prompt, generation id and credits.
3. Claude adds it in finishing: `python3 -I addbed.py FILM.mp4 VOICE.mp3 TRACK_ID OUT.mp4`. The track loops with a 1.5 s crossfade, fades out over the last 1.4 s, ducks under the narrator, and sits about 13 dB under speech; the whole mix is -14 LUFS. The video stream is copied untouched.

**Builders:** keep delivering voice + sound effects only (no music). Claude adds the bed.

## Sponsor editions
ElevenLabs' music terms may not cover paid or sponsored content on our plan, so Flashloop sponsor editions stay music-free until that is checked.

## Tracks
| id | title | moods | used in |
|---|---|---|---|
| storybook-whimsy | Storybook Whimsy (pizzicato, celesta, 100 BPM) | whimsical, playful, wonder, light mystery | My Bunny Ate the King's Chains |
