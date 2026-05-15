import os
from urllib.parse import quote_plus


def database_uri() -> str:
    """Строка подключения к PostgreSQL. Логин и пароль кодируются для URL (спецсимволы в пароле)."""
    test_uri = os.environ.get("TEST_DATABASE_URL")
    if test_uri:
        return test_uri

    user = os.environ.get("POSTGRES_USER", "taskbee_user")
    password = os.environ.get("POSTGRES_PASSWORD", "taskbee_secret")
    host = os.environ.get("POSTGRES_HOST", "db")
    port = os.environ.get("POSTGRES_PORT", "5432")
    name = os.environ.get("POSTGRES_DB", "taskbee")
    u = quote_plus(user)
    p = quote_plus(password)
    n = quote_plus(name) if name else name
    return f"postgresql+psycopg2://{u}:{p}@{host}:{port}/{n}"
