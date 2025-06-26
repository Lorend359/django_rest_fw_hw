# Django REST Framework: Платформа онлайн-обучения

## Содержание

- [О проекте](#о-проекте)
- [Домашние задания](#реализованные-модули-и-домашние-задания)
- [Стек технологий](#используемый-стек)
- [Запуск через Docker](#как-запустить-с-помощью-docker)
- [Ручной запуск без Docker](#как-запустить-вручную-без-docker)
- [CI/CD и деплой](#cicd-и-деплой-на-удалённый-сервер)
- [Ручной деплой на сервер](#ручной-деплой-на-сервер)

## О проекте

Это учебный проект, выполненный в рамках курса по Django REST Framework (DRF). В процессе разработки реализуется backend-часть платформы онлайн-обучения — RESTful API, предназначенный для SPA-клиента.

API предоставляет:

* управление курсами и уроками,
* регистрацию и аутентификацию пользователей (JWT),
* разграничение прав доступа по ролям,
* фильтрацию и сортировку данных,
* обработку платежей через Stripe,
* отображение профиля пользователя (с ограничениями),
* асинхронные уведомления и периодические задачи через Celery и Redis.

## Реализованные модули и домашние задания

[Домашки оставлены как в оригинале, без изменений]

## Используемый стек

* Python 3.12
* Django 4+
* Django REST Framework
* PostgreSQL
* Redis
* Celery
* JWT (`djangorestframework-simplejwt`)
* Stripe
* Swagger / drf-yasg
* Postman (для тестирования)
* Docker + Docker Compose
* GitHub Actions

## Как запустить с помощью Docker

1. Убедитесь, что установлен Docker и Docker Compose.
2. Создайте `.env` файл в корне проекта (если ещё нет) по шаблону `.env.example` и заполните нужные переменные.
3. Соберите и запустите проект командой:

```bash
docker-compose up --build
```

4. Проверка работоспособности сервисов:

* Backend (Django): http://localhost:8000/
* Swagger UI (локально): http://localhost:8000/swagger/
* Swagger UI (сервер): http://158.160.181.224/swagger/
* ReDoc (локально): http://localhost:8000/redoc/
* ReDoc (сервер): http://158.160.181.224/redoc/
* PostgreSQL: порт 5432
* Redis: порт 6379

## Как запустить вручную без Docker

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Дополнительно:

```bash
poetry run celery -A config worker -l info -P eventlet
poetry run celery -A config beat -l info
```

## CI/CD и деплой на удалённый сервер

* При пуше в ветку `develope`, `feature/hw_1` или `feature/hw_2` запускается GitHub Actions workflow.
* Прогоняются тесты, устанавливаются зависимости и запускается сборка проекта в контейнере.
* При успехе выполняется деплой на сервер через SSH:
  * `git pull`
  * `docker-compose up -d --build`

Секреты (`SECRET_KEY`, `DATABASE_URL`, `STRIPE_KEYS`, `SSH_PRIVATE_KEY`) хранятся в GitHub Secrets.

## Ручной деплой на сервер

Если GitHub Actions временно не срабатывает, можно задеплоить вручную:

```bash
ssh user@158.160.181.224
cd ~/project
git pull origin your-branch
docker-compose up -d --build
```

### Подготовка сервера

```bash
sudo apt update && sudo apt install docker.io docker-compose git -y
```

* Установите SSH-ключи для доступа GitHub Actions.
* Клонируйте проект и создайте `.env` по `.env.example`.
* Сервер доступен по адресу: http://158.160.181.224/