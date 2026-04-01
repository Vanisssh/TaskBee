# TaskBee — информационная система быстрого поиска и заказа профессиональных услуг

Платформа для взаимодействия заказчиков и самозанятых специалистов: быстрый подбор исполнителей и снижение издержек поиска услуг.

**Стек:** Python 3.11 (Flask, Flask-RESTx, Marshmallow, SQLAlchemy, Alembic), PostgreSQL, Redis, Docker Compose, Nginx (фронт).

---

## Лабораторная работа 1. Docker и Docker Compose

**Цель:** контейнеризация компонентов: БД, бэкенд (Flask), фронтенд, сервис адаптации под тематику (Redis).

### Сервисы

| Сервис | Описание |
|--------|----------|
| **db** | PostgreSQL 18. Данные в volume `pgdata`. Монтирование в `/var/lib/postgresql` (совместимо с образом 18+). При первом запуске выполняется `db/init.sql` (расширение `uuid-ossp`). |
| **redis** | Redis 7 — кэш, очереди, сессии (адаптация под «быстрый поиск и заказ услуг»). Volume `redisdata`. Проверка: `GET /redis-check` на backend. |
| **backend** | Flask + Gunicorn, порт **5000**. SQLAlchemy, Alembic, REST API `/api/v1`, Swagger UI `/api/docs/`. После старта — `alembic upgrade head`. |
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

4. В браузере: фронтенд <http://localhost:3000>, Swagger <http://localhost:5000/api/docs/>, проверки <http://localhost:5000/health> и <http://localhost:5000/db-check>.

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

- **Интерактивно (ЛР3):** после запуска backend откройте <http://localhost:5000/api/docs/> (Swagger UI, Flask-RESTx).
- Статичный OpenAPI: [docs/openapi.yaml](docs/openapi.yaml) — Scalar: `npx @scalar/cli document serve docs/openapi.yaml`

### Примеры curl

```bash
curl http://localhost:5000/api/v1/categories
curl -X POST http://localhost:5000/api/v1/categories -H "Content-Type: application/json" -d "{\"name\":\"Ремонт\",\"slug\":\"remont\"}"
```

---

## Лабораторная работа 3. Разработка REST API

**Цель:** RESTful API с валидацией (Marshmallow), CORS, ограничением частоты запросов, Swagger UI, единым форматом ошибок и логированием запросов; адаптация под тему TaskBee.

### Реализовано

| Требование | Реализация |
|------------|------------|
| Модульная структура | `api/` — Blueprint с префиксом `/api`; `api/v1/*.py` — Flask-RESTx **Namespace** по ресурсам |
| Валидация | **Marshmallow** — `schemas.py`, все тела POST/PUT проходят `validate_load` |
| Документация | **Flask-RESTx** — Swagger UI по адресу **`http://localhost:5000/api/docs/`** |
| CORS | **flask-cors**, список origin из переменной **`CORS_ALLOWED_ORIGINS`** (через запятую) |
| Rate limiting | **flask-limiter** — **100 запросов/мин** на IP; хранилище **Redis** (`RATELIMIT_STORAGE_URL`, по умолчанию `redis://redis:6379/1`). Исключены `/health`, `/db-check`, `/redis-check`, `/api/docs` |
| Ошибки | Ответы вида `{"error": "...", "message" или "details": ...}`, коды 4xx/5xx |
| Логирование | `after_request`: метод, путь, статус, время ответа (мс) |
| Адаптация под ИС | **`GET /api/v1/specialists/search`** — быстрый подбор исполнителей (`min_rating`, `category_id`, `limit`); **`GET /api/v1/stats/summary`** — агрегаты (заказы по статусам, средние рейтинги, счётчики). CRUD **users** и **specialists** для сценариев «клиент → заказ → исполнитель» |

### Переменные окружения (ЛР3)

См. `.env.example`: `CORS_ALLOWED_ORIGINS`, `RATELIMIT_STORAGE_URL`.

---

## Структура репозитория

```
TaskBee/
├── backend/           # Flask, api/, schemas.py, Alembic, Dockerfile
├── frontend/          # Nginx + статическая страница, Dockerfile
├── db/init.sql        # Инициализация PostgreSQL
├── docs/              # openapi.yaml, db_schema.png
├── docker-compose.yml
├── .env.example
└── README.md
```
