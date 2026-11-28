#!/bin/bash
# make_v3.sh CLEAN.mp4 SPONSOR_V2.mp4 OUT.mp4
# Sponsor edition v3 (Jake 11-27, per Flashloop): the clean film untouched (no corner logo) + the last 3.9 s of the
# v2 sponsor ending (line 2 "If you want to make videos like this, go to Flashloop dot AI." + end card), with the
# corner logo removed (delogo). The ending is encoded to match the clean file and joined with the concat demuxer (-c copy).
set -e
C=$(realpath "$1"); S=$(realpath "$2"); O="$3"; W=$(mktemp -d)
ds=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$S")
st=$(python3 -c "print(round($ds-9.3+5.4,3))")
ffmpeg -v error -y -ss "$st" -i "$S" -vf "fps=30,delogo=${DL:-x=612:y=36:w=448:h=192},format=yuv420p,setsar=1" -c:v libx264 -profile:v high -level 4.0 -preset veryfast -crf 18 -pix_fmt yuv420p -video_track_timescale 15360 -c:a aac -b:a 160k -ar 48000 -ac 2 "$W/end.mp4"
printf "file '%s'\nfile '%s'\n" "$C" "$W/end.mp4" > "$W/list.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$W/list.txt" -c copy -movflags +faststart "${O%.mp4}.tmp.mp4"
mv "${O%.mp4}.tmp.mp4" "$O"; rm -rf "$W"
echo "ending from $st of $ds"; ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$O"
