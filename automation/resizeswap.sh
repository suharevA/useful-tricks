#!/bin/bash

#Минимальное свободное место на диске 1000Mb
MIN_FREE_SIZE=100000000

echo "$(lsblk -l -d -o NAME,TYPE 2>/dev/null | grep 'disk' | awk '{print $1}')" | while read GETDEV; do
#Rescan disk
echo 1 > /sys/class/block/$GETDEV/device/rescan
DEVICE="/dev/$GETDEV"
#FIX partition table GPT
echo -e "w\nY\nY\n" | gdisk $DEVICE  2>/dev/null
partprobe $DEVICE 2>/dev/null

FDISK_OUTPUT=$(fdisk -l "$DEVICE" 2>/dev/null | grep "^$DEVICE" | tail -1)
SECTOR_SIZE=$(blockdev --getss "$DEVICE" 2>/dev/null)
DISK_SIZE=$(fdisk -l "$DEVICE" 2>/dev/null | sed 's/.*, \([0-9]*\) bytes.*/\1/' | head -n1)

DISKPART_N=$(echo "$FDISK_OUTPUT" | awk '{print $1}')
PART_NUMB=${DISKPART_N//$DEVICE/}
LAST_SECTOR=$(echo "$FDISK_OUTPUT" | awk '{print $3}')

NOT_USED=$((DISK_SIZE - LAST_SECTOR * SECTOR_SIZE))
echo "FREE SPACE (bytes) $NOT_USED"

if [ $NOT_USED -le $MIN_FREE_SIZE ]; then

  echo "[BAD] Нет достаточного свободного места на диске "$DEVICE >&2
  exit 1
  
else

echo "Начало процедуры расширения раздела"

#out: parted /dev/nvme0n1 resizepart 3 100%
#fix: для корректировки инфы о gpt информации в конце диска
#echo "parted -a opt $DEVICE resizepart $PART_NUMB 100%"
#echo Fix | parted -s $DEVICE resizepart $PART_NUMB 100%

#parted $DEVICE unit B print free | grep "Free Space" | awk 'END{print $2}

echo -e "Fix\n" | parted $DEVICE print 2>/dev/null

LAST_BYTE=$(parted $DEVICE unit B print free 2>/dev/null | grep "Free Space" | awk 'END{print $2}')
#LAST_BYTE=${LAST_BYTE%?}

parted $DEVICE unit B resizepart $PART_NUMB ${LAST_BYTE%?} 2>/dev/null

#expand PV
echo "запуск команды: pvresize "$DEVICE$PART_NUMB
pvresize $DEVICE$PART_NUMB 2>/dev/null
VGNAME=$(lvs 2>/dev/null | grep "swap" | awk '{print $2}')
echo "Используем VolumeGroup: "$VGNAME

lvextend -l +100%FREE /dev/$VGNAME/swap
if [ $? -ne 0 ]; then
  echo "[BAD] Ошибка при расширении LV" >&2
  exit 1
fi

swapoff -v /dev/$VGNAME/swap 2>/dev/null
mkswap /dev/$VGNAME/swap 2>/dev/null
swapon -v /dev/$VGNAME/swap 2>/dev/null
free -h 2>/dev/null

exit 0

fi
done

#echo "[BAD] Никаких изменений не сделано."

#exit 1
