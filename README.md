# URL Shortener API

A FastAPI-based URL shortener with JWT auth, Redis caching, Redis-backed rate limiting, and click analytics.

## Features

- User registration and login with JWT tokens
- URL shortening using Base62 short codes
- Redirect endpoint with expiry/active/click-limit checks
- Click tracking (IP, user-agent, referer) via background tasks
- Analytics endpoint (total clicks, daily clicks, top referers, top user agents)
- Redis caching for short-code lookups
- API-key-identity rate limiting per endpoint scope
- Periodic cleanup worker for old expired links

## Tech Stack

- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Redis
- JWT (PyJWT)

## Project Structure

```text
.
|-- app.py
|-- main.py
|-- db.py
|-- configure.py
|-- Auth/
|   |-- routes.py
|   |-- logic.py
|   |-- schemas.py
|   `-- service.py
`-- project/
    |-- routes.py
    |-- logic.py
    |-- service.py
    |-- schema.py
    |-- models.py
    |-- cache.py
    |-- rate_limiter.py
    `-- cleanup.py
```

## Prerequisites

- Python 3.11+
- PostgreSQL running locally (or reachable via connection string)
- Redis running locally (or reachable via connection string)

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install asyncpg bcrypt
```

## Environment Variables

Create a `.env` file in project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/url_shortener_db
SECRET_KEY=replace_with_a_strong_secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

Notes:
- `ALGORITHM` may exist in `.env`, but current code uses `HS256` directly.
- Tables are created automatically on startup.

## Run the API

```bash
python main.py
```

App runs on `http://0.0.0.0:8000`.

Open docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication and Headers

- Auth endpoints and API endpoints are rate-limited using `X-API-Key`.
- Protected URL creation endpoint also requires JWT Bearer token.

Required headers by use case:

- Rate-limited endpoints:
  - `X-API-Key: <your-client-key>`
- Protected endpoint (`POST /api/url_shortner`) additionally:
  - `Authorization: Bearer <jwt_token>`

## Rate Limits (Current Defaults)

- `POST /api/auth/register`: 5 requests/minute per API key
- `POST /api/auth/login`: 10 requests/minute per API key
- `POST /api/url_shortner`: 30 requests/minute per API key
- `GET /api/analytics/{short_code}`: 30 requests/minute per API key
- `GET /api/{short_code}`: 120 requests/minute per API key


## Common Error Responses

- `400`: Missing API key / validation errors / duplicate registration
- `401`: Invalid credentials or invalid/expired JWT
- `404`: Short URL not found
- `410`: Link inactive, expired, or max-click limit reached
- `429`: Rate limit exceeded

