from app.config import Settings, _normalize_pg_scheme


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


def test_cors_origins_from_csv_env(monkeypatch):
    """Railway delivers CORS_ORIGINS as a comma-separated string, not JSON —
    pydantic-settings must not try to JSON-decode it."""
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example,https://b.example")
    s = Settings(_env_file=None)
    assert s.cors_origins == ["https://a.example", "https://b.example"]


def test_cors_origins_empty_env_falls_back_to_default(monkeypatch):
    """Empty CORS_ORIGINS must not crash (this is the exact failure we hit
    on the first Railway deploy)."""
    monkeypatch.setenv("CORS_ORIGINS", "")
    s = Settings(_env_file=None)
    assert len(s.cors_origins) > 0
