# Система резервирования ресурсов

##О проекте
MVP веб-сервиса для бронирования общих ресурсов (переговорки, проекторы, ноутбуки).

## Технологии
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT
- **Frontend**: Vue 3, Vite, Pinia, Axios
- **Infrastructure**: Docker, Docker Compose

##  Установка и запуск

### Предварительные требования
- Docker и Docker Compose
- Git
### Быстрый старт
```bash
# Клонировать репозиторий
git clone <url>
cd T1_project

# Создать .env как в примере
cp backend/.env.example backend/.env

# Запустить через Docker
docker-compose up -d

# Применить миграции
docker exec reserve_backend alembic upgrade head