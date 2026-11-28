# Sponsor edition, version 3 (from Fri 11-27, 7:19 PM; replaces v2 for every sponsor edition from now on)

## Why
Flashloop wrote in Jake's ticket (#307) on Thu 11-27 about 2:20 PM: "i see your views dropped, might be because of the logo, you can remove it, and add made with flashloop in description" and "for cta you can keep it 3-4s no longer, should help with retention". Jake, 7:19 PM: "let's go ahead and do as they suggested for reels now, and going forward."

## What changes
1. **No Flashloop logo card in the corner. Ever.** The sponsor edition is the clean film (handle only), untouched.
2. **The ending is 3 to 4 seconds, no longer.** It is line 2 of the approved sponsor voice only: "If you want to make videos like this, go to Flashloop dot AI." (sponsor-ending-voice.mp3, 5.25 to 8.32 s), over the phone screen with the "Video ready" preview of this film, then the end card (FLASHLOOP.AI / FACELESS STUDIO / CODE: RNG, "MAKE VIDEOS LIKE THIS", caption FLASHLOOP DOT AI) from "go to" on, holding about 0.7 s past the last word. Total about 3.9 s. Line 1 ("So I pulled up Flashloop dot AI ... code RNG") is dropped; the end card still shows CODE: RNG.
3. **Caption:** every Instagram sponsor post adds the line "Made with Flashloop.ai (code RNG)" (Claude does this when booking).

## Builders
Export two files as before: `<story>-clean.mp4` (handle only, no logo, no ending) and `<story>.mp4` = the clean film + this 3.9 s ending. If you already have the v2 9.3 s ending built as its own last segment, the v3 ending is that segment from 5.4 s to the end, with the corner logo removed. Claude's retrofit script for finished films: `make_v3.sh CLEAN SPONSOR_V2 OUT` (clean film untouched, joined with -c copy).

## Already swapped (11-27, 7:25 PM)
Power Level Zero (IG trial Sat 12:00), Tiny Seed (IG trial Sun 14:00), Truth Sword (IG trial Sun 18:00): media replaced with the v3 files on claude-finished c876207 (fin1127/sponsor-v3/), captions updated. Fake Power is clean only (Jake).
