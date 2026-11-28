#!/bin/sh
# New places (castle courtyard, forest edge, harbor): 4 finals each at 1080x1920 (WIDE_ESTABLISH + LOW_HERO,
# DAY + NIGHT), then the other bookmarks + the GOLDEN wide at 540x960; then the two town wides again (stray
# lantern caps removed) and the material catalogue.  One process per camera (lower peak memory), nice 19,
# banded split render + separate denoise.
L=/tmp/claude-0/backlot/tmp/final_new.log
P=/tmp/claude-0/backlot/previews
R="nice -n 19 python3 -I /tmp/claude-0/backlot/source/render.py"
D="nice -n 19 python3 -I /tmp/claude-0/backlot/source/denoise_exr.py"
cd /tmp
shot() {  # set preset cam pct
  $R $1 $2 $3 $4 16 1 $P 1k:cobblestone_02 split 2 >> $L 2>&1
  $D $P/exr/*.json >> $L 2>&1
}
for S in castle_courtyard forest_edge harbor; do
  echo "== $S finals $(date +%H:%M:%S)" >> $L
  for PR in DAY NIGHT; do for C in WIDE_ESTABLISH LOW_HERO; do shot $S $PR $C 100; done; done
  echo "== $S extras $(date +%H:%M:%S)" >> $L
  case $S in
    castle_courtyard) EX="CROWD_MED TWO_SHOT CLOSE_A CLOSE_B INSERT_WELL INSERT_GATE WIDE_REVERSE";;
    forest_edge) EX="CROWD_MED TWO_SHOT CLOSE_A CLOSE_B INSERT_SIGNPOST INSERT_FOREST WIDE_REVERSE";;
    harbor) EX="CROWD_MED TWO_SHOT CLOSE_A CLOSE_B INSERT_BOAT INSERT_DOCK WIDE_REVERSE";;
  esac
  for C in $EX; do shot $S DAY $C 50; done
  shot $S GOLDEN WIDE_ESTABLISH 50
  python3 -I /tmp/claude-0/backlot/source/contact.py $S >> $L 2>&1
  echo "PLACE_DONE $S $(date +%H:%M:%S)" >> $L
done
echo "== town wides (stray caps fixed) $(date +%H:%M:%S)" >> $L
shot town_square DAY WIDE_ESTABLISH 100
shot town_square NIGHT WIDE_ESTABLISH 100
python3 -I /tmp/claude-0/backlot/source/contact.py town_square >> $L 2>&1
echo "== catalogue $(date +%H:%M:%S)" >> $L
nice -n 19 python3 -I /tmp/claude-0/backlot/source/catalogue.py render 1300 16 --cc0 >> $L 2>&1
rmdir $P/exr 2>/dev/null
echo "ALL_DONE $(date +%H:%M:%S)" >> $L
