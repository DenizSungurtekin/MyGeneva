-- Executed once at first Postgres startup (docker-entrypoint-initdb.d).
-- Creates a second database used only for Airflow metadata, distinct from
-- the application DB.

CREATE DATABASE airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO mygeneva;

-- Enable PostGIS on the application DB (needed as soon as we introduce
-- geographic types; noop-safe if run again).
\connect mygeneva
CREATE EXTENSION IF NOT EXISTS postgis;
