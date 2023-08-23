#!/bin/bash

MON_DIR=/opt
inotifywait -mqr --format %f -e create $MON_DIR |\
while read files; do
   rsync -avz /opt /tmp/opt
   #echo "$(date +'%F %T') create $files" | mail -s "dir monitor" xxx@163.com
done
