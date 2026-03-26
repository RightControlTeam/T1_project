# Система резервирования ресурсов

## Технологии
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT
- **Frontend**: Vue 3, Vite, Pinia, Axios
- **Infrastructure**: Docker, Docker Compose

##  Установка и запуск
### Запуск проекта
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
```

##  Схема БД
<img width="1168" height="522" alt="image" src="https://github.com/user-attachments/assets/7ec36181-76ef-491b-8ea1-31557db419e8" />

## Архитектура проекта
<img width="974" height="489" alt="image" src="https://github.com/user-attachments/assets/a0ef9523-326f-4088-819a-d2fd42c3b196" />
