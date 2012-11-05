#!/bin/bash
set -u
set -e

rm -f *jpg

cp full/*jpg .

for file in $(ls *jpg);
do
    mogrify -resize 640x480^ "$file"
    mogrify -crop 640x480 "$file"
done

rm *1.jpg
rename 's/-0.jpg/.jpg/' *0.jpg
