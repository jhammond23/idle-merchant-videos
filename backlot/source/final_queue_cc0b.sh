#!/bin/sh
# After final_queue_cc0.sh: re-render the town finals with the brighter banner art.
L=/tmp/claude-0/backlot/tmp/final_cc0.log
P=/tmp/claude-0/backlot/previews
R="nice -n 19 python3 -I /tmp/claude-0/backlot/source/render.py"
D="nice -n 19 python3 -I /tmp/claude-0/backlot/source/denoise_exr.py"
while kill -0 "$1" 2>/dev/null; do sleep 15; done
cd /tmp
for PR in DAY NIGHT; do
  echo "== town_square $PR (banner lift) $(date +%H:%M:%S)" >> $L
  $R town_square $PR WIDE_ESTABLISH,LOW_HERO 100 16 1 $P 1k:cobblestone_02 split 2 >> $L 2>&1
  $D $P/exr/*.json >> $L 2>&1
done
rmdir $P/exr 2>/dev/null
echo "TOWN_REDONE $(date +%H:%M:%S)" >> $L
