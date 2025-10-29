# Movie App

A microservices-based movie browsing application with user authentication, favorites management, and multi-layer caching.

## Features

### Movie Service

- **TMDB Integration:** Fetch trending movies, search, and view detailed movie information
- **Two-Layer Caching:** L1 in-memory + L2 Redis cache for optimal performance
- **Batch Operations:** Retrieve multiple movies in a single request
- **Rate Limiting:** Request throttling and monitoring via Prometheus metrics

### User Service

- **JWT Authentication:** Secure token-based auth with password hashing (bcrypt)
- **User Management:** Registration, profile updates, and account deletion
- **Favorites System:** Full CRUD for user's favorite movies with persistent storage
- **Flexible Storage:** Postgres for production, in-memory/JSON for development

### Architecture

- **Service Isolation:** Independent movie and user services with clear boundaries
- **Request Tracing:** UUID-based request IDs across all services
- **Health Checks:** Dedicated endpoints for monitoring service status
- **API Versioning:** Organized routes under `/api/*` prefix

## Tech Stack

- **Backend:** Python 3.13, FastAPI
- **Databases:** PostgreSQL (users), Redis (caching)
- **Validation:** Pydantic v2 with strict type checking
- **HTTP Client:** HTTPX for async external API calls
- **Testing:** Pytest with 88% code coverage
- **Code Quality:** Ruff (linting/formatting), MyPy (type checking)
- **Containerization:** Docker Compose for orchestration

---

## Quick Start

### 1. Clone and Configure

```bash
git clone <your-repo-url>
cd movie_app
```

Create a `.env` file:

```bash
# Required for Movie Service
TMDB_API_KEY=your_tmdb_api_key_here

# Required for User Service
# Used for signing JWTs. Generate a strong key, e.g., by running:
# python -c 'import secrets; print(secrets.token_hex(32))'
JWT_SECRET_KEY=your_super_secret_key_for_jwt_here

# --- Optional: These are the defaults used by docker-compose ---
# You generally do not need to set these in your .env file
# DATABASE_URL=postgresql://user:password@postgres:5432/movie_db
# REDIS_URL=redis://redis:6379
```

### 2. Start Services (Docker Compose)

```bash
# Start all services
make up

# View logs
make logs

# Stop services
make down
```

Services will be available at:

- **Movie API:** http://localhost:8000
- **User API:** http://localhost:8001
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

### 3. Explore the APIs

Interactive Swagger documentation:

- Movie Service: http://localhost:8000/docs
- User Service: http://localhost:8001/docs

---

## Development Setup (Local)

### Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with dev tools
pip install -e .[dev]
```

### Run Services Locally

```bash
# Terminal 1 - Movie Service
uvicorn movie_service.src.movie_api.main:app --reload --port 8000

# Terminal 2 - User Service
uvicorn user_service.src.user_api.main:app --reload --port 8001
```

### Useful Make Commands

```bash
make help        # Show all available commands
make test        # Run test suite
make test-cov    # Run tests with HTML coverage report
make lint        # Run ruff linter and mypy
make format      # Auto-format code
make clean       # Remove cache files and build artifacts
```

---

## Testing

Run the full test suite with coverage:

```bash
make test-cov
# Opens htmlcov/index.html with detailed coverage report
```

**Current Coverage:** 88% (64 tests, all passing)

Tests include:

- **Unit Tests:** Cache implementations, TMDB service, security functions
- **Integration Tests:** Full API endpoint testing with mocked dependencies
- **Test Isolation:** In-memory SQLite database per test, no external API calls

---

## API Examples

### Movie Service

```bash
# Get trending movies
curl http://localhost:8000/api/movies/trending

# Search movies
curl http://localhost:8000/api/movies/search?query=inception

# Get movie details
curl http://localhost:8000/api/movies/550

# Batch fetch movies
curl -X POST http://localhost:8000/api/movies/batch \
  -H "Content-Type: application/json" \
  -d '{"movie_ids": [550, 680, 155]}'

# Health check
curl http://localhost:8000/health
```

### User Service

```bash
# Register user
curl -X POST http://localhost:8001/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secure123"}'

# Login (get JWT token)
curl -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=secure123"

# Get current user profile (requires auth)
curl http://localhost:8001/api/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Add favorite movie (e.g., movie with ID 550)
curl -X POST http://localhost:8001/api/favorites/550 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
  -d '{"movie_id": 550, "title": "Fight Club", "poster_path": "/path.jpg"}'

# Get all favorites
curl http://localhost:8001/api/favorites/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Project Structure

```bash
movie_app/
├── movie_service/          # Movie API microservice
│   ├── src/movie_api/
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic (TMDB, caching)
│   │   ├── monitoring/     # Metrics and stats
│   │   └── middleware/     # Request ID, rate limiting
├── user_service/           # User API microservice
│   ├── src/user_api/
│   │   ├── routers/        # Auth, users, favorites endpoints
│   │   ├── services/       # User/favorites implementations
│   │   ├── models.py       # SQLAlchemy ORM models
│   │   ├── schemas.py      # Pydantic request/response models
│   │   └── security.py     # JWT and password hashing
├── tests/                  # Test suite
│   ├── movie_service_tests/
│   └── user_service_tests/
├── docker-compose.yml      # Service orchestration
├── Makefile               # Development commands
└── pyproject.toml         # Python dependencies and config
```

---

## Architecture Overview

```mermaid
graph TD
    Client[Client Browser/App]
    
    subgraph "Movie Service :8000"
        MovieAPI[FastAPI App]
        L1[L1: In-Memory Cache]
        L2[L2: Redis Cache]
        TMDB[TMDB API]
    end
    
    subgraph "User Service :8001"
        UserAPI[FastAPI App]
        Postgres[(PostgreSQL)]
    end
    
    Client -->|Movie Requests| MovieAPI
    Client -->|Auth/Favorites| UserAPI
    
    MovieAPI --> L1 --> L2 --> TMDB
    UserAPI --> Postgres
    
    L2 -.->|Shared Cache| Redis[(Redis)]
```

### Key Design Decisions

**Two-Layer Caching Strategy:**

- L1 (in-memory): Ultra-fast, per-instance cache with LRU eviction
- L2 (Redis): Shared across instances, persistent across restarts
- Cache miss flow: L1 → L2 → TMDB API, then backfill both layers

**Service Separation:**

- Movie service: Read-heavy, benefits from aggressive caching
- User service: Write-heavy, requires ACID guarantees (Postgres)
- Independent scaling: Cache more movie instances, fewer user instances

**Flexible Storage Adapters:**

- Production: Postgres + Redis
- Development: In-memory or JSON file storage
- Testing: SQLite in-memory + mock Redis
- Easy to swap implementations via dependency injection

---

## Configuration

All settings are managed through environment variables with sensible defaults:

### Movie Service
```bash
TMDB_API_KEY=required          # Your TMDB API key
TMDB_IMAGE_BASE_URL=...        # Default: https://image.tmdb.org/t/p/w500
CACHE_DURATION_HOURS=1         # How long to cache responses
CACHE_IMPLEMENTATION=redis     # Options: redis, json_file, in_memory
REDIS_URL=redis://localhost:6379/0
```

### User Service

```bash
DATABASE_URL=postgresql://...  # Postgres connection string
SECRET_KEY=...                 # JWT signing key
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Token expiration time
USER_IMPLEMENTATION=postgres   # Options: postgres, in_memory
FAVORITES_IMPLEMENTATION=json_file  # Options: json_file, in_memory
```

---

## Monitoring

### Prometheus Metrics

Movie service exposes metrics at `/api/metrics`:

- Cache hit/miss rates per layer
- Request counts and latencies
- TMDB API call rates

### Health Checks

Both services provide health endpoints:

- `/health` - Service status and dependency checks
- `/` - Basic root endpoint
