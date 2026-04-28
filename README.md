# FoodGram

[![Main Foodgram workflow](https://github.com/Maximylis/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Maximylis/foodgram/actions/workflows/main.yml)

## Описание проекта

**Foodgram** — это веб-приложение для публикации рецептов, поиска блюд и формирования списка покупок.

Пользователи могут создавать собственные рецепты, просматривать рецепты других авторов, добавлять понравившиеся рецепты в избранное, подписываться на авторов и формировать список покупок на основе выбранных рецептов.

Проект состоит из backend-приложения на Django REST Framework, frontend-приложения и инфраструктуры для запуска в Docker-контейнерах с использованием PostgreSQL, Gunicorn и nginx.

## Сайт проекта

Проект доступен по адресу:

https://foodgrammax.ddns.net

## Основные возможности
### Для неавторизованных пользователей

- просмотр главной страницы с рецептами;
- просмотр отдельных рецептов;
- просмотр страниц авторов;
- фильтрация рецептов по тегам;
- регистрация;
- авторизация.

### Для авторизованных пользователей
- создание рецептов;
- редактирование и удаление собственных рецептов;
- добавление рецептов в избранное;
- удаление рецептов из избранного;
- подписка на авторов;
- отписка от авторов;
- просмотр страницы подписок;
- добавление рецептов в список покупок;
- удаление рецептов из списка покупок;
- скачивание списка покупок;
- изменение пароля;
- выход из аккаунта.

### Для администратора
- управление пользователями;
- управление рецептами;
- управление ингредиентами;
- управление тегами;
- доступ к административной панели Django.

## Стек технологий
### Backend
- Python
- Django
- Django REST Framework
- Djoser
- PostgreSQL
- Gunicorn

### Frontend
- JavaScript
- React
- CSS
- HTML

### Инфраструктура
- Docker
- Docker Compose
- nginx
- GitHub Actions
- DockerHub

## Структура проекта
```
foodgram/
├── backend/                 # Backend-приложение Django
├── frontend/                # Frontend-приложение React
├── infra/                   # Docker Compose, nginx, Dockerfile
├── data/                    # Исходные данные, например ингредиенты
├── docs/                    # Документация API
├── .github/workflows/       # Workflow GitHub Actions
├── README.md
└── setup.cfg
```

## Переменные окружения
Для запуска проекта необходимо создать файл `.env`.
```
POSTGRES_USER=db_user                                   |   имя пользователя PostgreSQL
POSTGRES_PASSWORD=db_password                           |   пароль пользователя PostgreSQL
POSTGRES_DB=db_name                                     |   название базы данных
DB_HOST=db                                              |   хост базы данных внутри Docker-сети
DB_PORT=5432                                            |   порт PostgreSQL
SECRET_KEY=your_secret_key                              |   секретный ключ Django
DEBUG=False                                             |   режим отладки Django
ALLOWED_HOSTS=127.0.0.1,localhost,your-domain.example   |   список разрешённых хостов
```

## Быстрое развертывание Foodgram

### Требования на сервере
```
Установите Docker на сервере (одна команда)
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
```
### Настройка сервера
Подключитесь к серверу один раз через SSH и создайте папку:
```
ssh root@ваш-сервер
mkdir -p ~/foodgram/infra/
exit
```
### Создайте файл .env на сервере

### Настройка секретов в GitHub
Добавьте эти секреты:
```
DOCKERHUB_USERNAME: логин от Docker Hub
DOCKERHUB_PASSWORD: пароль от Docker Hub
HOST: IP или домен сервера
USER: имя пользователя
SSH_KEY: приватный SSH ключ
TELEGRAM_ID: ваш Telegram ID
TELEGRAM_TOKEN: токен бота
POSTGRES_PASSWORD: пароль для БД
```

### Всё! Деплой автоматический
При каждом пуше в ветку main workflow самостоятельно:

Запускает тесты
Собирает Docker образы
Пушит их на Docker Hub
Подключается к серверу по SSH
Обновляет и запускает контейнеры
Применяет миграции
Собирает статику
Присылает уведомление в Telegram

## Работа с API
### Документация API доступна после запуска проекта:
```
http://foodgrammax.ddns.net/api/docs/
```
### Основные эндпоинты:
```
/api/users/                          пользователи
/api/auth/token/login/               получение токена
/api/auth/token/logout/              удаление токена
/api/recipes/                        рецепты
/api/recipes/{id}/                   отдельный рецепт
/api/recipes/{id}/favorite/          добавление/удаление из избранного
/api/recipes/{id}/shopping_cart/     добавление/удаление из списка покупок
/api/recipes/download_shopping_cart/ скачивание списка покупок
/api/tags/                           теги
/api/ingredients/                    ингредиенты
/api/users/subscriptions/            подписки
/api/users/{id}/subscribe/           подписка/отписка
```

## Автор 

### Maximylis
    GitHub: @Maximylis
