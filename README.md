 ## Linux
 - [lvm](https://github.com/suharevA/my/blob/main/lvm)
 - [graylog](https://github.com/suharevA/my/blob/main/graylog)
 - [curl](https://github.com/suharevA/my/blob/main/curl)
 - [ssh](https://github.com/suharevA/my/blob/main/ssh) 
 - [docker](https://github.com/suharevA/my/blob/main/Dockerfile)
 - [reset root](https://github.com/suharevA/my/blob/main/resetroot)
 - [find](https://github.com/suharevA/my/blob/main/find)



## Linux
1. **vg_resize.py** -- автоматическое расширение файловой системы
1. **lvm** работа с дисками 
[resizeVG_v2.py](automation/resizeVG_v2.py)
2. **resizeroot.py** -- автоматическое расширение корневого раздела
## Scripts
1. **[generatePass.go](generatePass.go)** -- генератор паролей

1. **moni_disk_space.sh** -- мониторинг диска, запуск команды очистки например (docker image rm)  (Читай комментарии в файле)
crontab -e 
*/10 * * * * /opt/moni_disk_space.sh каждые 10 минут
1. **moni_disk_space.py** -- мониторинг диска, запуск команды очистки например (docker image rm)  (Читай комментарии в файле)
crontab -e 
*/10 * * * * /opt/moni_disk_space.py каждые 10 минут
1. **back_postgres.sh** -- резервное копирования баз данных Postgres

1. **backup_folder.sh** -- Резервная копия и архивирование папки запуск crontab @midnight bash /home/you folder/backup_folder.sh /home/dev/что бекапим/ /home/куда/backup
1. **autowebproxy.py** -- Веб-прокси позволяет вам просматривать веб-страницы анонимно и разблокировать ваши любимые веб-сайты без установки какого-либо программного обеспечения, такого как VPN
1. **mypass_genpass.py** -- Как использовать API Google Диска в Python. Генерирует пароль, сохраняет в файл, отправляет на Google диск
1. **check-ssl.py** -- Обалденный скрипт для проверки сертификата
1. **searching_yml.py** -- рекурсивный поиск файла по имени, во всех папках
