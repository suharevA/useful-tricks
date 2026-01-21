#!/bin/bash
# Скрипт ограничения количества VIP на одной ноде
# Размещается: /etc/keepalived/check_vip_count.sh
# chmod +x /etc/keepalived/check_vip_count.sh

IFACE="ens192"
# VIP только из диапазона 241–245
VIP_REGEX="10\.6\.56\.24[1-5]"

# Максимум VIP на одной ноде (при 5 нодах = 1, при 2 нодах = 3)
MAX_VIP=3

cnt=$(ip -4 addr show dev "$IFACE" | grep -E -c "$VIP_REGEX")

if [ "$cnt" -gt "$MAX_VIP" ]; then
    exit 1
fi

exit 0
