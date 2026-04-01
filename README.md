# TaskBee — информационная система быстрого поиска и заказа профессиональных услуг

Платформа для взаимодействия заказчиков и самозанятых специалистов: быстрый подбор исполнителей и снижение издержек поиска услуг.

**Стек:** Python 3.11 (Flask, SQLAlchemy, Alembic), PostgreSQL, Redis, Docker Compose, статический фронтенд (Nginx).

---

## Лабораторная работа 1. Docker и Docker Compose

**Цель:** контейнеризация компонентов: БД, бэкенд (Flask), фронтенд, сервис адаптации под тематику (Redis).

### Сервисы

| Сервис | Описание |
|--------|----------|
| **db** | PostgreSQL 18. Данные в volume `pgdata`. Монтирование в `/var/lib/postgresql` (совместимо с образом 18+). При первом запуске выполняется `db/init.sql` (расширение `uuid-ossp`). |
| **redis** | Redis 7 — кэш, очереди, сессии (адаптация под «быстрый поиск и заказ услуг»). Volume `redisdata`. Проверка: `GET /redis-check` на backend. |
| **backend** | Flask + Gunicorn, порт **5000**. SQLAlchemy + Alembic, REST API `/api/v1`. После старта выполняется `alembic upgrade head`. |
| **frontend** | Nginx со статической страницей, порт **3000** (внутри контейнера 80). |

### Архитектура

```
frontend :3000 ──► backend :5000 ──┬──► db (PostgreSQL)
                                   ├──► redis
                                   └──► app-network (bridge)
```

### Первый запуск

1. Скопируйте `.env.example` в `.env` и задайте `DB_PASSWORD` и при необходимости остальные переменные.

2. Запуск:
   ```bash
   docker compose up --build -d
   ```

3. Проверка:
   ```bash
   docker compose ps
   docker compose logs db
   docker compose logs backend
   ```

4. В браузере: фронтенд <http://localhost:3000>, API <http://localhost:5000/health>, БД <http://localhost:5000/db-check>.

5. Подключение к PostgreSQL из контейнера backend:
   ```bash
   docker compose exec backend bash
   apt-get update && apt-get install -y postgresql-client
   psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB"
   ```

### Локальная разработка backend (без Docker)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
set POSTGRES_HOST=localhost
set POSTGRES_USER=...
set POSTGRES_PASSWORD=...
set POSTGRES_DB=taskbee
alembic upgrade head
flask --app app run --debug --port 5000
```

---

## Лабораторная работа 2. PostgreSQL и ORM

**Цель:** схема БД, SQLAlchemy (ORM), миграции Alembic, REST CRUD.

- **ORM:** Flask-SQLAlchemy (`models.py`).
- **Миграции:** Alembic (`backend/alembic/`, первая ревизия `20260201_0001_initial_taskbee.py`).
- **Команды:** из каталога `backend`:
  ```bash
  alembic upgrade head
  alembic downgrade -1
  alembic history
  ```

### Сущности

`users`, `service_categories`, `services`, `specialists`, `orders`, `reviews` — см. ER-диаграмму [docs/db_schema.png](docs/db_schema.png).

### API и документация

- OpenAPI 3.0: [docs/openapi.yaml](docs/openapi.yaml) (базовый URL `http://localhost:5000/api/v1`).
- Просмотр в Scalar: `npx @scalar/cli document serve docs/openapi.yaml`

### Примеры curl

```bash
curl http://localhost:5000/api/v1/categories
curl -X POST http://localhost:5000/api/v1/categories -H "Content-Type: application/json" -d "{\"name\":\"Ремонт\",\"slug\":\"remont\"}"
```

---

## Структура репозитория

```
TaskBee/
├── backend/           # Flask, SQLAlchemy, Alembic, Dockerfile
├── frontend/          # Nginx + статическая страница, Dockerfile
├── db/init.sql        # Инициализация PostgreSQL
├── docs/              # openapi.yaml, db_schema.png
├── docker-compose.yml
├── .env.example
└── README.md
```
