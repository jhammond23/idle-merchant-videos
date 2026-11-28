#!/bin/sh
L=/tmp/claude-0/backlot/tmp/final.log
R="nice -n 19 python3 -I /tmp/claude-0/backlot/source/render.py"
$R bridge_river DAY WIDE_ESTABLISH,LOW_HERO 100 16 1 >> $L 2>&1
$R bridge_river NIGHT WIDE_ESTABLISH,LOW_HERO 100 16 1 >> $L 2>&1
$R bridge_river DAY INSERT_WATER,INSERT_MILL,UNDER_ARCH 50 16 1 >> $L 2>&1
$R bridge_river GOLDEN WIDE_ESTABLISH 50 16 1 >> $L 2>&1
echo QUEUE2_DONE >> $L
