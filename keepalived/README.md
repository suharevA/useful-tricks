# Keepalived v3 - Шахматка + Ограничение VIP + Автовозврат

## 📦 Комплект файлов

```
check_vip_count.sh           - скрипт ограничения VIP (одинаковый на всех)
is299b-lb001t1-hc-lab.conf   - конфиг для lb001 (мастер .241)
is299b-lb002t1-hc-lab.conf   - конфиг для lb002 (мастер .242)
is299b-lb004t1-hc-lab.conf   - конфиг для lb004 (мастер .243)
is299b-lb005t1-hc-lab.conf   - конфиг для lb005 (мастер .244)
is299b-lb006t1-hc-lab.conf   - конфиг для lb006 (мастер .245)
```

---

## ✅ Что включено

| Функция | Описание |
|---------|----------|
| **Шахматные приоритеты** | Каждая нода — мастер для своего VIP |
| **chk_nginx** | VIP уезжает если nginx упал |
| **chk_vip_limit** | Не даёт собрать >3 VIP на ноде |
| **preempt_delay 30** | VIP возвращается на мастера через 30 сек после восстановления |

---

## 📊 Матрица приоритетов

```
              │  VI_1    VI_2    VI_3    VI_4    VI_5
              │  (.241)  (.242)  (.243)  (.244)  (.245)
──────────────┼──────────────────────────────────────────
lb001         │  150★    110     120     130     140
lb002         │  140     150★    110     120     130
lb004         │  130     140     150★    110     120
lb005         │  120     130     140     150★    110
lb006         │  110     120     130     140     150★
```

★ = MASTER (priority 150)

---

## 🚀 Установка

### На КАЖДОЙ ноде выполни:

```bash
# 1. Создай скрипт check_vip_count.sh (ОДИНАКОВЫЙ на всех)
cat > /etc/keepalived/check_vip_count.sh << 'EOF'
#!/bin/bash
IFACE="ens192"
VIP_REGEX="10\.6\.56\.24[1-5]"
MAX_VIP=3
cnt=$(ip -4 addr show dev "$IFACE" | grep -E -c "$VIP_REGEX")
if [ "$cnt" -gt "$MAX_VIP" ]; then
    exit 1
fi
exit 0
EOF

chmod +x /etc/keepalived/check_vip_count.sh

# 2. Бэкап старого конфига
cp /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf.bak

# 3. Скопируй СВОЙ конфиг (для каждой ноды свой файл!)
# Пример для lb001:
# cp is299b-lb001t1-hc-lab.conf /etc/keepalived/keepalived.conf

# 4. Перезапусти
systemctl restart keepalived

# 5. Проверь
ip a | grep "10.6.56.24"
systemctl status keepalived
```

---

## 🔄 Как работает

### Сценарий: lb002 падает и восстанавливается

```
00:00  lb002 падает
       → VIP .242 мгновенно переезжает на lb004 (следующий по priority)
       → Даунтайм: 1-2 сек

00:00 - 05:00
       → VIP .242 работает на lb004
       → Пользователи ничего не замечают

05:00  lb002 восстановился
       → lb002 ждёт 30 секунд (preempt_delay)
       → VIP .242 всё ещё на lb004, работает!

05:30  30 секунд прошло, lb002 стабилен
       → VIP .242 возвращается на lb002
       → Даунтайм: 1-2 сек
```

### Сценарий: Осталось 2 ноды

```
lb001: 3 VIP (максимум по chk_vip_limit)
lb002: 2 VIP

Если lb001 попытается взять 4-й VIP:
→ chk_vip_limit вернёт FAIL
→ priority упадёт на 50
→ VIP уедет на lb002
```

### Сценарий: Осталась 1 нода

```
lb001: все 5 VIP (физический предел, это норма)
```

---

## 🧪 Тестирование

### 1. Проверь что скрипты работают:

```bash
# check_nginx
/etc/keepalived/check_nginx.sh && echo "OK" || echo "FAIL"

# check_vip_count
/etc/keepalived/check_vip_count.sh && echo "OK (≤3 VIP)" || echo "FAIL (>3 VIP)"
```

### 2. Проверь распределение VIP:

```bash
# На каждой ноде:
ip a | grep "10.6.56.24"
```

Ожидаемый результат (все 5 нод работают):
- lb001: только .241
- lb002: только .242
- lb004: только .243
- lb005: только .244
- lb006: только .245

### 3. Тест failover:

```bash
# На lb002:
systemctl stop keepalived

# Подожди 5 сек, проверь на lb004:
ip a | grep "10.6.56.24"
# Должен быть .243 И .242

# Верни lb002:
systemctl start keepalived

# Подожди 35 сек (preempt_delay + время на выборы)
# Проверь что .242 вернулся на lb002
```

### 4. Смотри логи:

```bash
journalctl -u keepalived -f
```

---

## ⚠️ Важные моменты

1. **preempt_delay 30** — VIP вернётся на мастера через 30 сек после восстановления
2. **MAX_VIP=3** — можно изменить в check_vip_count.sh
3. **weight -50** — при >3 VIP priority падает, "лишние" VIP уезжают
4. **state BACKUP везде** — VRRP сам выбирает мастера по priority

---

## 🐛 Troubleshooting

### VIP не переезжает:
```bash
# Проверь логи
journalctl -u keepalived -f

# Проверь что скрипты исполняемые
ls -la /etc/keepalived/*.sh
```

### VIP не возвращается после восстановления:
```bash
# Подожди 30+ секунд (preempt_delay)
# Проверь что nginx работает на мастере
/etc/keepalived/check_nginx.sh && echo "OK" || echo "FAIL - nginx не работает!"
```

### Все VIP на одной ноде:
```bash
# Проверь что chk_vip_limit работает
/etc/keepalived/check_vip_count.sh
echo $?  # 0=OK, 1=превышен лимит

# Проверь priority в логах
journalctl -u keepalived | grep -i priority
```
