#!/usr/bin/env bash
# يصوّر النسختين ثم يبني الصوت ويدمجهما:  ./run_all.sh   (يحتاج خادماً: python3 -m http.server 8765 من جذر المشروع)
set -e
export NODE_PATH=$(npm root -g)
cd "$(dirname "$0")"
for M in v h; do
  MODE=$M node capture.js
  MODE=$M python3 audio.py
  D=$([ $M = v ] && echo 60 || echo 49)
  ffmpeg -y -v error -i _silent_$M.mp4 -i trailer_audio_$M.wav -map 0:v -map 1:a -c:v libx264 -crf 22 -preset slow -pix_fmt yuv420p -c:a aac -b:a 160k -t $D -movflags +faststart book_trailer_$([ $M = v ] && echo vertical || echo horizontal).mp4
  rm -f _silent_$M.mp4 trailer_audio_$M.wav
done
echo ALLDONE
