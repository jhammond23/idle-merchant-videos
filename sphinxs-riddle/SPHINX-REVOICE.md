# sphinxs-riddle: Sphinx re-voice (Jake, Wed 11-25, 10:10 PM)

Jake asked for the Sphinx's lines to be re-voiced, and for its mouth to track its lines at the end.

- `sphinxs-riddle-voice-final.mp3` is REPLACED. Only the Sphinx's lines changed: a new deep, ancient voice with a slight echo of size. The narrator is untouched and the timeline is the same (49.68 s), so your cuts still line up.
- `sphinxs-riddle-word-timings.json` and `sphinxs-riddle-lines.srt` are updated for the Sphinx's words.

| Line | Old time (s) | New time (s) |
|---|---|---|
| "What gets bigger, the more you take away from it?" (1st) | 16.20-19.94 | 16.20-19.71 |
| "What gets bigger, the more you take away from it?" (2nd) | 29.06-32.79 | 29.06-32.57 |
| "Then answer this." | 43.91-44.82 | 43.76-44.90 |
| "What can you keep, even after you give it away?" | 45.05-48.43 | 45.05-48.66 |

## What to change
1. Swap in the new voice track and keep your foley.
2. **Lip-sync the Sphinx.** Wherever its face is on screen while it speaks, the mouth opens on each word's syllables (use the word times in the json) and closes in the gaps, with no flapping. **Most important: the end.** Show the Sphinx's face on "Then answer this." and on at least the start of the final riddle, with the mouth matching every word. Cut to the King's sweating face only after that.
3. Re-deliver `ready/sphinxs-riddle/sphinxs-riddle-clean.mp4` (plus the cover, thumbnail and notes). Claude adds the swipe-in opening in the finishing pass, so don't add it yourself. Delete temp frames afterwards.
