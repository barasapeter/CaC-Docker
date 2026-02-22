# CaC-Docker

A minimal Dockerized Python API backed by PostgreSQL.

This repository contains a small Flask application that accepts an email address, stores it in Postgres if it does not exist, and returns whether the record was newly created or already present.

## Tech stack

- Python 3.11
- Flask
- PostgreSQL
- Gunicorn
- Docker / Docker Compose

## Project structure

- `main.py` – Flask app and database initialization logic.
- `docker-compose.yaml` – Multi-service setup for API + PostgreSQL.
- `Dockerfile` – Container image build for the API service.
- `requirements.txt` – Python dependencies.
- `web.http` – Sample HTTP request for local testing.

## Prerequisites

- Docker
- Docker Compose

## Environment variables

Create a `.env` file in the project root (same directory as `docker-compose.yaml`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=docker-learn
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

> `POSTGRES_HOST=db` is recommended when running inside Docker Compose so the app can reach the database container.

## Run with Docker Compose

```bash
docker compose up --build
```

This starts:

- `db` (PostgreSQL) on host port `5433`
- API container (service name is `fastapi`, but it runs Flask) on host port `5000`

## API usage

### Endpoint

- `POST /`

### Request body

```json
{
  "email": "user@example.com"
}
```

### Example cURL

```bash
curl -X POST http://localhost:5000 \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

### Responses

- `201 Created` when a new user is inserted.
- `200 OK` when the email already exists.
- `400 Bad Request` when `email` is missing.
- `500 Internal Server Error` for database errors.

## Notes

- On startup, the app attempts to:
  - create the target database if it does not exist,
  - create the `users` table if it does not exist.
- Data is persisted via Docker volume: `psql-volume`.

## Stop services

```bash
docker compose down
```

To also remove the named volume:

```bash
docker compose down -v
```
