# 📂 Мои материалы по Linux, скриптам и технологиям

---

## 📌 Linux: Руководства и инструкции

| Тема       | Описание                     | Ссылка                                                                 |
|------------|------------------------------|------------------------------------------------------------------------|
| LVM        | Управление логическими томами | [lvm](https://github.com/suharevA/my/blob/main/lvm)                  |
| Graylog    | Логирование                  | [graylog](https://github.com/suharevA/my/blob/main/graylog)          |
| cURL       | Работа с HTTP                | [curl](https://github.com/suharevA/my/blob/main/curl)                |
| SSH        | Удалённое подключение         | [ssh](https://github.com/suharevA/my/blob/main/ssh)                  |
| Docker     | Контейнеризация              | [Dockerfile](https://github.com/suharevA/my/blob/main/Dockerfile)     |
| Сброс root | Восстановление доступа       | [reset root](https://github.com/suharevA/my/blob/main/resetroot)      |
| Поиск файлов | Утилита `find`             | [find](https://github.com/suharevA/my/blob/main/find)                |

---

## 📌 Linux: Автоматизация

| Скрипт               | Описание                              | Файл/Ссылка                          |
|----------------------|---------------------------------------|---------------------------------------|
| **vg_resize.py**     | Автоматическое расширение файловой системы | [resizeVG_v2.py](automation/resizeVG_v2.py) |
| **resizeroot.py**    | Автоматическое расширение корневого раздела |                                       |

---

## 📌 Полезные скрипты

| Скрипт                     | Описание                                                                 | Пример использования/Запуск         |
|----------------------------|--------------------------------------------------------------------------|--------------------------------------|
| **[generatePass.go](generatePass.go)** | Генератор паролей                                                        |                                      |
| **moni_disk_space.sh**     | Мониторинг дискового пространства, очистка (например, `docker image rm`) | `crontab -e` → `*/10 * * * * /opt/moni_disk_space.sh` |
| **moni_disk_space.py**     | Аналог на Python                                                         | `crontab -e` → `*/10 * * * * /opt/moni_disk_space.py` |
| **back_postgres.sh**       | Резервное копирование баз данных PostgreSQL                              |                                      |
| **backup_folder.sh**       | Архивирование папки                                                     | `@midnight bash /home/you/folder/backup_folder.sh /home/dev/что_бекапим/ /home/куда/backup` |
| **autowebproxy.py**        | Веб-прокси для анонимного просмотра веб-страниц                          |                                      |
| **mypass_genpass.py**      | Генерация пароля, сохранение в файл и отправка на Google Диск через API |                                      |
| **check-ssl.py**           | Проверка SSL-сертификатов                                                |                                      |
| **searching_yml.py**       | Рекурсивный поиск файлов по имени                                        |                                      |

---

## 🐍 Python

| Проект/Скрипт          | Описание                                                                 | Файл/Ссылка                          |
|------------------------|--------------------------------------------------------------------------|---------------------------------------|
| **mypass_genpass.py**  | Генерация пароля, сохранение в файл и отправка на Google Диск через API |                                       |
| **check-ssl.py**       | Проверка SSL-сертификатов                                                |                                       |
| **searching_yml.py**   | Рекурсивный поиск файлов по имени                                        |                                       |
| **autowebproxy.py**    | Веб-прокси для анонимного просмотра веб-страниц                          |                                       |

---

## 📜 Bash

| Скрипт                     | Описание                                                                 | Пример использования/Запуск         |
|----------------------------|--------------------------------------------------------------------------|--------------------------------------|
| **moni_disk_space.sh**     | Мониторинг дискового пространства, очистка (например, `docker image rm`) | `crontab -e` → `*/10 * * * * /opt/moni_disk_space.sh` |
| **back_postgres.sh**       | Резервное копирование баз данных PostgreSQL                              |                                      |
| **backup_folder.sh**       | Архивирование папки                                                     | `@midnight bash /home/you/folder/backup_folder.sh /home/dev/что_бекапим/ /home/куда/backup` |

---

## 🦊 Go

| Проект/Скрипт          | Описание                     | Файл/Ссылка                          |
|------------------------|------------------------------|---------------------------------------|
| **[generatePass.go](generatePass.go)** | Генератор паролей |                                       |

---

## 🌙 Lua

| Проект/Скрипт                           | Описание                     | Файл/Ссылка             |
|-----------------------------------------|------------------------------|-------------------------|
| Health Check (HTTP/HTTPS) для openresty | *(Описание)* | [healthcheck_init.lua](lua/healthcheck_init.lua)|
| Health Check (TCP) для openresty        | *(Описание)* | [tcp-nginx.lua](lua/tcp-nginx.lua) |
---
