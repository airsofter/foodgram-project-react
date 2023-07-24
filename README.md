# Сайт Foodgram "Продуктовый помощник"


## _Онлайн-сервис для публикации рецептов_

### Описание проекта Foodgram

Foodgram - Продуктовый помощник. Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


### Стек технологий

Python 3.9, Django 3.2, Django REST Framework, Djoser, React, 
PostgreSQL, Docker, nginx, gunicorn, Github-Actions, Yandex Cloud


### Локальный запуск приложения в Docker

Склонировать репозиторий на свой компьютер и перейти в корневую папку:
```
git clone git@github.com:airsofter/foodgram-project-react.git
cd foodgram-project-react
```

Создать в корневой папке файл .env с переменными окружения, необходимыми 
для работы приложения.

Пример содержимого файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=key
```

Перейти в папку /infra/ и запустить сборку контейнеров с помощью 
docker-compose: 
```
cd infra
docker-compose up -d
```
После этого будут созданы и запущены в фоновом режиме контейнеры 
(db, web, nginx).

Внутри контейнера web выполнить миграции, создать суперпользователя (для входа 
в админку), собрать статику и загрузить ингредиенты из recipes_ingredients.csv 
в базу данных:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py load_ingredients
```
После этого проект должен стать доступен по адресу http://localhost/.

Для подготовки сайта к работе нужно зайти в админ-зону по адресу 
http://localhost/admin/ и создать теги для рецептов, указав для каждого тега 
его название и выбрав цвет в палитре

### Остановка контейнеров

Для остановки работы приложения можно набрать в терминале команду Ctrl+C 
либо открыть второй терминал и воспользоваться командой
```
docker-compose stop 
```
Снова запустить контейнеры без их пересборки можно командой
```
docker-compose start 
```

### Спецификация API в формате Redoc:

Чтобы посмотреть спецификацию API в формате Redoc, нужно локально запустить 
проект и перейти на страницу http://localhost/api/docs/



### Автор

[Набатов Денис](https://github.com/airsofter)
