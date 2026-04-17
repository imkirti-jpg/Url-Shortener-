# LinkSnip: Production-Grade URL Shortener API

**Transform long URLs into shareable, trackable short links with sub-millisecond redirect latency.**

LinkSnip is a high-performance URL shortening service built on **FastAPI + PostgreSQL + Redis**. It combines intelligent caching, distributed rate limiting, and real-time click analytics to deliver a scalable, reliable alternative to bit.ly or TinyURL.


**[🚀 Live Demo](https://url-shortener-2g3f.onrender.com/docs)**

## ✨ Key Features

### Core Functionality
- **Instant URL Shortening** — Convert any URL to a compact 6-character Base62 code
- **Stateless User Auth** — JWT-based registration & login with bcrypt password hashing
- **Smart Redirects** — Expiry dates, max-click limits, and active/inactive status checks
- **Sub-millisecond Performance** — Multi-layer caching: Redis hot cache + PostgreSQL persistent storage

### Analytics & Tracking
- **Real-time Click Analytics** — Track IP, user-agent, referer, and click timestamps
- **Daily Aggregation** — View clicks by day, top referers, and user-agent breakdown
- **Background Processing** — Non-blocking analytics writes keep redirects fast (<10ms)

### Reliability & Scale
- **Redis-backed Rate Limiting** — 5-120 requests/minute per API key, per endpoint
- **Automatic Link Cleanup** — Periodic worker removes expired links, prevents storage bloat
- **Async I/O Throughout** — asyncpg + FastAPI for handling 5000+ concurrent requests
- **Container-Ready** — Dockerfile + Docker Compose for Render/Railway/Heroku deployment

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Application                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTP Request
                           │
        ┌──────────────────▼──────────────────┐
        │      FastAPI (Async Handler)        │
        │  ├─ JWT Auth Middleware             │
        │  ├─ Rate Limit Middleware           │
        │  └─ Request Router                  │
        └──────┬──────────────────┬───────────┘
               │                  │
        [Cache Hit?]      [Cache Miss]
               │                  │
        ┌──────▼──┐      ┌────────▼─────────┐
        │  Redis  │      │  PostgreSQL      │
        │ (<1ms)  │      │  (asyncpg)       │
        └─────────┘      │  ✅ Populate     │
                         │     Cache        │
                         └──────────────────┘
                                  │
                          ┌────────▼────────┐
                          │ Background Task │
                          │  • Log Click    │
                          │  • Update Count │
                          │  • Analytics    │
                          └─────────────────┘

Parallel Services:
┌──────────────────────────────────────────┐
│  Periodic Cleanup Worker (every 1 hour)  │
│  • Remove expired links                  │
│  • Archive old analytics data            │
└──────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Web Framework** | FastAPI 0.104+ | Native async/await, auto-generated OpenAPI docs, Pydantic validation |
| **Async Database** | PostgreSQL + asyncpg | ACID guarantees + async driver for sub-10ms latency |
| **ORM** | SQLAlchemy 2.0+ | Async-first, type-safe query builder |
| **Caching Layer** | Redis 7.0+ | <1ms lookups, built-in expiry, atomic rate limiter |
| **Authentication** | JWT (PyJWT) + bcrypt | Stateless, scalable, industry-standard |
| **Background Jobs** | FastAPI BackgroundTasks | Lightweight, no external worker needed |
| **Server** | Uvicorn | ASGI server, production-ready |
| **Containerization** | Docker | Reproducible deployments to Render/Railway |

## 📡 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|-----------|
| `POST` | `/api/auth/register` | Register a new user | 5/min |
| `POST` | `/api/auth/login` | Login & get JWT token | 10/min |

**Example: Register**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'
```

**Example: Login**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}'
```

### URL Shortening Endpoints

| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|-----------|
| `POST` | `/api/url_shortner` | Create short URL | JWT Bearer | 30/min |
| `GET` | `/{short_code}` | Redirect to original URL | None | 120/min |
| `GET` | `/api/analytics/{short_code}` | Get click analytics | JWT Bearer | 30/min |

**Example: Shorten URL**
```bash
curl -X POST "http://localhost:8000/api/url_shortner" \
  -H "X-API-Key: your-api-key" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://github.com/example/very-long-repository-name",
    "expires_at": "2026-12-31T23:59:59Z",
    "max_clicks": 1000
  }'
```

**Response:**
```json
{
  "short_code": "a7x9kL",
  "original_url": "https://github.com/...",
  "short_url": "https://url-shortener-2g3f.onrender.com/a7x9kL",
  "created_at": "2026-04-17T10:30:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "is_active": true,
  "clicks_count": 0
}
```

**Example: Get Analytics**
```bash
curl -X GET "http://localhost:8000/api/analytics/a7x9kL" \
  -H "X-API-Key: your-api-key" \
  -H "Authorization: Bearer <jwt_token>"
```

**Response:**
```json
{
  "short_code": "a7x9kL",
  "total_clicks": 342,
  "daily_clicks": {
    "2026-04-17": 45,
    "2026-04-16": 112,
    "2026-04-15": 185
  },
  "top_referers": [
    {"referer": "twitter.com", "count": 120},
    {"referer": "reddit.com", "count": 89}
  ],
  "top_user_agents": [
    {"user_agent": "Chrome/125.0", "count": 200},
    {"user_agent": "Safari/18.0", "count": 142}
  ]
}
```

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
DATABASE_URL=your url
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

## Docker Deployment

Build the image from the project root:

```bash
docker build -t url-shortener .
```

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL= neon database link \
  -e SECRET_KEY="replace_with_a_strong_secret" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  -e REDIS_URL= upstash link \
  url-shortener
```

For Render, use this `Dockerfile` and configure the service environment variables in the Render dashboard. The app listens on port `8000` by default.


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

