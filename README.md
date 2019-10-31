# Script_python 

untitled1.py -- Python Script to monitor disk space (Читай комментарии в файле)
crontab -e 
*/10 * * * * /opt/untitled1.py каждые 10 минут

untitled12_bucardo.py -- Скрипт решает проблему (Bucardo не может автоматически синхронизировать потерянные узлы) скрипт для отслеживания состояния сервера. Как только соединение возобновляется, скрипт выполняет команду перезагрузки bucardo. Синхронизация восстановлена.
Bucardo Multimaster и Master / Slave Postgres репликации https://bucardo.org/
start command: python2.7 /opt/bucardo_watch2.py host.bucardo2 /bucardo_replication_log.txt

