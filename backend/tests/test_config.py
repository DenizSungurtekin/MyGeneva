from app.config import _normalize_pg_scheme


def test_normalize_railway_postgres():
    """Railway injects `postgres://` URLs — must be rewritten for SQLAlchemy 2."""
    railway_url = "postgres://user:pw@monorail.proxy.rlwy.net:5432/railway"
    normalized = _normalize_pg_scheme(railway_url)
    assert normalized == "postgresql+psycopg://user:pw@monorail.proxy.rlwy.net:5432/railway"


def test_normalize_bare_postgresql():
    url = "postgresql://user:pw@host:5432/db"
    assert _normalize_pg_scheme(url) == "postgresql+psycopg://user:pw@host:5432/db"


def test_preserve_explicit_psycopg_driver():
    url = "postgresql+psycopg://user:pw@host:5432/db"
    assert _normalize_pg_scheme(url) == url


def test_preserve_psycopg2_driver():
    """Airflow / docker-compose sometimes ships psycopg2 — leave that alone."""
    url = "postgresql+psycopg2://user:pw@host:5432/db"
    assert _normalize_pg_scheme(url) == url


def test_preserve_sqlite():
    url = "sqlite:///path/to/db.sqlite"
    assert _normalize_pg_scheme(url) == url
