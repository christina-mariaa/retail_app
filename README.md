# Работа с docker-compose
## Сборка контейнеров:
### docker-compose build
Это надо делать если внесли изменения в Dockerfile, requirements.txt надо пересобрать контейнеры командой docker-compose build
## Запустить контейнеры:
### docker-compose up
Если надо с пересборкой, то docker-compose up --build
## Остановить и удалить контейнеры:
### docker-compose down
Это надо делать если изменился docker-compose.yml, settings.py или .env, или если обычные изменения кода не применяются
## Перезапустить контейнеры:
### docker-compose restart
## Работа с миграциями:
### Создать миграции
docker-compose exec web python manage.py makemigrations
### Применить миграции
docker-compose exec web python manage.py migrate
