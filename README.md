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

# Совместная работа над проектом
Все участники работают в отдельных ветках feature/... — это важно, чтобы не мешать работе друг друга и упростить объединение кода.
## Как работать с ветками:
### 1. Перейти в ветку dev и обновить её
git checkout dev  
git pull origin dev
### 2. Создать свою ветку от dev
git checkout -b feature/название-задачи
### 3. После завершения задачи
git add .  
git commit -m "описание изменений"  
git push origin feature/название-задачи
### 4. Зайти на GitHub → открыть Pull Request из своей ветки в dev
### 5. Второй человек делает ревью и подтверждает слияние (merge)
После слияния изменений нужно подтянуть обновлённый dev, чтобы быть в курсе всех изменений:  
git checkout dev  
git pull origin dev  
Если ты продолжаешь работу в своей ветке — влей туда изменения из dev:  
git checkout feature/твоя-ветка  
git merge dev  
