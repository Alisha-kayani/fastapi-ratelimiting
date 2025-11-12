# FastAPI Rate Limiting

A collection of rate limiting implementations for FastAPI applications, demonstrating different approaches to control API request rates.

## Features

This project includes three different rate limiting implementations:

1. **IP-based Rate Limiting** (`rate_limiter_ip.py`) - Rate limits based on client IP addresses
2. **API Key-based Rate Limiting** (`ratelimit.py`) - Rate limits based on API keys with different limits per key
3. **SlowAPI Integration** (`main.py`) - Using the `slowapi` library for rate limiting

## Requirements

- Python >= 3.12
- FastAPI >= 0.121.1
- Uvicorn >= 0.38.0

## Installation

### Using uv (Recommended)

```bash
# Install dependencies
uv sync

# Activate virtual environment
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Using pip

```bash
pip install fastapi uvicorn slowapi httpx
```

## Usage

### 1. IP-based Rate Limiting

This implementation limits requests based on the client's IP address. Each IP is allowed a maximum number of requests within a specified time period.

**File:** `rate_limiter_ip.py`

**Run the server:**
```bash
uvicorn rate_limiter_ip:app --reload
```

Or with uv:
```bash
uv run uvicorn rate_limiter_ip:app --reload
```

**Example:**
```python
@app.get("/")
@rate_limit(max_calls=5, period=60)  # 5 requests per 60 seconds
async def read_root(request: Request):
    return {"message": "Hello, World!"}
```

**Features:**
- Tracks requests per IP address using SHA256 hashing
- Automatically cleans up old timestamps
- Returns HTTP 429 with retry-after information when limit is exceeded

### 2. API Key-based Rate Limiting

This implementation uses API keys to identify clients and applies different rate limits based on the key.

**File:** `ratelimit.py`

**Run the server:**
```bash
uvicorn ratelimit:app --reload
```

**Example Request:**
```bash
curl -H "X-API-KEY: api_key_1" http://localhost:8000/
```

**Features:**
- Requires `X-API-KEY` header
- Different rate limits per API key
- Combines API key and IP address for unique identification
- Returns HTTP 400 for missing API key
- Returns HTTP 403 for invalid API key

**Pre-configured API Keys:**
- `api_key_1`: 5 requests per 60 seconds
- `api_key_2`: 10 requests per 60 seconds

### 3. SlowAPI Integration

This implementation uses the `slowapi` library, which provides a more feature-rich rate limiting solution.

**File:** `main.py`

**Run the server:**
```bash
uvicorn main:app --reload
```

**Endpoints:**
- `/limited` - Rate limited route (2 requests per second)
- `/unlimited` - No rate limiting

**Features:**
- Uses `slowapi` library for rate limiting
- Fixed-window strategy
- In-memory storage
- Can be enabled/disabled via `RATE_LIMITING_ENABLED` flag

## Rate Limit Decorator Usage

### IP-based Rate Limiting

```python
from rate_limiter_ip import rate_limit, app
from fastapi import Request

@app.get("/api/endpoint")
@rate_limit(max_calls=10, period=60)  # 10 requests per minute
async def my_endpoint(request: Request):
    return {"data": "your response"}
```

### API Key-based Rate Limiting

```python
from ratelimit import rate_limit, app
from fastapi import Request

@app.get("/api/endpoint")
@rate_limit()  # Uses limits from api_key_limits dictionary
async def my_endpoint(request: Request):
    return {"data": "your response"}
```

## Error Responses

### Rate Limit Exceeded (429)
```json
{
  "detail": "Rate limit exceeded. Retry after 45.23 seconds"
}
```

### Missing API Key (400)
```json
{
  "detail": "API key missing"
}
```

### Invalid API Key (403)
```json
{
  "detail": "Invalid API key"
}
```

## Testing

### Test IP-based Rate Limiting

```bash
# Make 5 requests (should succeed)
for i in {1..5}; do curl http://localhost:8000/; done

# 6th request should fail with 429
curl http://localhost:8000/
```

### Test API Key-based Rate Limiting

```bash
# Valid request
curl -H "X-API-KEY: api_key_1" http://localhost:8000/

# Missing API key (should fail with 400)
curl http://localhost:8000/

# Invalid API key (should fail with 403)
curl -H "X-API-KEY: invalid_key" http://localhost:8000/
```

## Project Structure

```
fasstapi-ratelimiting/
├── rate_limiter_ip.py  # IP-based rate limiting
├── ratelimit.py        # API key-based rate limiting
├── main.py             # SlowAPI integration
├── pyproject.toml      # Project dependencies
├── uv.lock             # Lock file for uv
└── README.md           # This file
```

## Notes

- **In-memory storage**: All implementations use in-memory storage, so rate limit data is lost on server restart
- **Thread safety**: The current implementations are not thread-safe for production use with multiple workers
- **Production considerations**: For production, consider using:
  - Redis for distributed rate limiting
  - Database-backed storage
  - Proper thread/process synchronization
  - More sophisticated rate limiting libraries like `slowapi` or `fastapi-limiter`

## License

This project is provided as-is for educational purposes.

