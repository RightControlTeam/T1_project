# Система резервирования ресурсов

##О проекте
MVP веб-сервиса для бронирования общих ресурсов (переговорки, проекторы, ноутбуки).

## Технологии
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT
- **Frontend**: Vue 3, Vite, Pinia, Axios
- **Infrastructure**: Docker, Docker Compose
##Схема бд 
<img width="1168" height="522" alt="image" src="https://github.com/user-attachments/assets/64fab55f-182d-40ef-afc0-6ff549c06c47" />


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
