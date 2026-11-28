#!/bin/sh
# Job-file render queue (survives being restarted: done jobs are recorded).  One render at a time, nice 19.
# Each line of tmp/jobs.txt:   render <set> <PRESET> <CAM> <pct>   |  contact <set>  |  catalogue
# Lines may be appended while it runs; finished lines are listed in tmp/jobs.done.
J=/tmp/claude-0/backlot/tmp/jobs.txt
DONE=/tmp/claude-0/backlot/tmp/jobs.done
L=/tmp/claude-0/backlot/tmp/final_new.log
P=/tmp/claude-0/backlot/previews
S=/tmp/claude-0/backlot/source
touch $DONE
cd /tmp
while true; do
  next=$(grep -vxF -f $DONE $J | head -1)
  [ -z "$next" ] && break
  echo "== job: $next $(date +%H:%M:%S)" >> $L
  set -- $next
  case $1 in
    render) nice -n 19 python3 -I $S/render.py $2 $3 $4 $5 16 1 $P 1k:cobblestone_02 split 2 >> $L 2>&1
            nice -n 19 python3 -I $S/denoise_exr.py $P/exr/*.json >> $L 2>&1
            rm -rf $P/exr;;
    contact) python3 -I $S/contact.py $2 >> $L 2>&1;;
    catalogue) nice -n 19 python3 -I $S/catalogue.py render 1300 16 --cc0 >> $L 2>&1;;
  esac
  echo "$next" >> $DONE
done
echo "QUEUE_IDLE $(date +%H:%M:%S)" >> $L
