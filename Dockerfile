# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Обновим переменные среды (чтобы poetry был в PATH)
ENV PATH="/root/.local/bin:$PATH"

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости и README
COPY pyproject.toml poetry.lock* /app/

# Устанавливаем зависимости без виртуального окружения
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi --only main

# Копируем оставшийся код проекта
COPY . /app/

# Открываем порт для доступа к приложению
EXPOSE 8000

# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
