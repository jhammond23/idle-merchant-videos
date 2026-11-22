# scripts-inbox

Claude (story writer) puts one folder here per story that is ready to build. Only Claude writes to this branch.

Each folder holds:
- `ASTRA-<STORY>-PACKAGE.md`: the build package (script, characters, beat times, must-haves, asset paths). Read it first.
- `<story>-voice-final.mp3`: the final voice track, already at 1.2x. Never re-voice or re-time it.
- `<story>-lines.srt` and `<story>-word-timings.json`: caption timings for that mp3.

Builder: build every story folder here that has no `ready/<story-name>/` folder on the main branch yet. When a video is done, upload `<story-name>.mp4`, `<story-name>-cover.png` and `notes.json` to `ready/<story-name>/` on main. Claude checks and posts from there.
