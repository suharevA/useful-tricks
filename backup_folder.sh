#!/usr/bin/env bash

SRC=$1
DEST=$2

if [[ -z $SRC ]]
then
  echo "----> no source provided"
  exit
fi

if [[ -z $DEST ]]
then
  echo "----> no destination provided"
  exit
fi

if [[ ! -d $SRC ]]
then
  echo "----> source must be a directory"
  exit
fi

if [[ ! -d $DEST ]]
then
  echo "----> destination must be a directory"
  exit
fi

DATE=$(date +%Y-%m-%d-%H%M%S)

echo "----> starting backup"
cd "$SRC" && tar -jcvf "$DEST/$DATE.tar.bz" . &>/dev/null

if [ $? -eq 0 ]; then
    echo "----> backup completed"
else
    echo "----> backup failed"
    exit
fi

FILES=$(ls -1q "$DEST"/* | wc -l)
if (( $FILES > 5 ))
then
  echo "----> cleaning up backups"
  rm -f "$DEST/$(ls -t $DEST | tail -1)"
fi

echo "----> all done"
