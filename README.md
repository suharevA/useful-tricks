 ## Linux
 - [lvm](https://github.com/suharevA/my/blob/main/lvm)
 - [graylog](https://github.com/suharevA/my/blob/main/graylog)
 - [curl](https://github.com/suharevA/my/blob/main/curl)
 - [ssh](https://github.com/suharevA/my/blob/main/ssh) 
 - [docker](https://github.com/suharevA/my/blob/main/Dockerfile)

## Scripts
1. **moni_disk_space.sh** -- мониторинг диска, запуск команды очистки например (docker image rm)  (Читай комментарии в файле)
crontab -e 
*/10 * * * * /opt/moni_disk_space.sh каждые 10 минут

1. **moni_disk_space.py** -- мониторинг диска, запуск команды очистки например (docker image rm)  (Читай комментарии в файле)
crontab -e 
*/10 * * * * /opt/moni_disk_space.py каждые 10 минут

1. **untitled12_bucardo.py** -- Скрипт решает проблему (Bucardo не может автоматически синхронизировать потерянные узлы) скрипт для отслеживания состояния сервера. Как только соединение возобновляется, скрипт выполняет команду перезагрузки bucardo восстанавливая синхронизацию.
start script: python2.7 untitled12_bucardo.py host.bucardo2 /bucardo_replication_log.txt
добавляем в автозагрузку

1. **back_postgres.sh** -- резервное копирования баз данных Postgres 

1. **tool_ping.py** -- Скрипт решает проблему (Bucardo не может автоматически синхронизировать потерянные узлы) скрипт для отслеживания состояния сервера. Как только соединение возобновляется, скрипт выполняет команду перезагрузки сервера bucardo.Скрипт добавляем в автозагрузку
1. **enum.py** -- сканирует папку, пишет сожержиое и размер найденого в файл enum.txt 

1. **pars.py** -- читает файлы в папке и собирает все данные в один файл txt 
  запуск ./pars.py путь к папке
  
1. **backup_folder.sh** -- Резервная копия и архивирование папки запуск crontab @midnight bash /home/you folder/backup_folder.sh /home/dev/что бекапим/ /home/куда/backup

1. **autowebproxy.py** -- Веб-прокси позволяет вам просматривать веб-страницы анонимно и разблокировать ваши любимые веб-сайты без установки какого-либо программного обеспечения, такого как VPN

1. **mypass_genpass.py** -- Как использовать API Google Диска в Python. Генерирует пароль, сохраняет в файл, отправляет на Google диск
1. **check-ssl.py** -- Обалденный скрипт для проверки сертификата
1. **searching_yml.py** -- рекурсивный поиск файла по имени, во всех папках
1. **ping_hosts.py** -- пинг по списку хостов.
