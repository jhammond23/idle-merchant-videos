#!/bin/sh
# CC0 pass: the 12 required 1080x1920 finals, one render at a time (nice 19).  Banded 'split' render
# (noisy image + denoising passes to EXR) then a separate denoise/stitch process: peak ~1.7 GB instead of ~3 GB.
L=/tmp/claude-0/backlot/tmp/final_cc0.log
P=/tmp/claude-0/backlot/previews
R="nice -n 19 python3 -I /tmp/claude-0/backlot/source/render.py"
D="nice -n 19 python3 -I /tmp/claude-0/backlot/source/denoise_exr.py"
cd /tmp
for S in town_square bridge_river throne_hall; do
  for PR in DAY NIGHT; do
    echo "== $S $PR $(date +%H:%M:%S)" >> $L
    $R $S $PR WIDE_ESTABLISH,LOW_HERO 100 16 1 $P 1k:cobblestone_02 split 2 >> $L 2>&1
    $D $P/exr/*.json >> $L 2>&1
  done
done
rmdir $P/exr 2>/dev/null
echo "FINALS_DONE $(date +%H:%M:%S)" >> $L
