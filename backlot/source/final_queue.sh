#!/bin/sh
# Single sequential render queue (one render at a time, nice 19). Required 1080x1920 finals first, extras after.
L=/tmp/claude-0/backlot/tmp/final.log
R="nice -n 19 python3 -I /tmp/claude-0/backlot/source/render.py"
$R town_square DAY WIDE_ESTABLISH,LOW_HERO 100 16 1 >> $L 2>&1
$R town_square NIGHT WIDE_ESTABLISH,LOW_HERO 100 16 1 >> $L 2>&1
$R bridge_river DAY WIDE_ESTABLISH,LOW_HERO 100 16 1 >> $L 2>&1
$R bridge_river NIGHT WIDE_ESTABLISH,LOW_HERO 100 16 1 >> $L 2>&1
echo REQUIRED_DONE >> $L
(cd /tmp && nice -n 19 python3 -I /tmp/claude-0/backlot/source/catalogue.py render 1300 16 >> $L 2>&1)
echo CATALOGUE_DONE >> $L
$R town_square DAY CROWD_MED,TWO_SHOT,CLOSE_A,CLOSE_B,INSERT_RANKING,INSERT_SIGN,INSERT_FOUNTAIN 50 16 1 >> $L 2>&1
$R bridge_river DAY CROWD_MED,TWO_SHOT,CLOSE_A,CLOSE_B,INSERT_WATER,INSERT_MILL,UNDER_ARCH 50 16 1 >> $L 2>&1
$R throne_hall DAY CROWD_MED,TWO_SHOT,CLOSE_A,CLOSE_B,INSERT_THRONE,INSERT_WINDOW 50 16 1 >> $L 2>&1
$R town_square GOLDEN WIDE_ESTABLISH 50 16 1 >> $L 2>&1
$R bridge_river GOLDEN WIDE_ESTABLISH 50 16 1 >> $L 2>&1
$R throne_hall GOLDEN WIDE_ESTABLISH 50 16 1 >> $L 2>&1
echo EXTRAS_DONE >> $L
