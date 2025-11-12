
import hashlib
import time
from functools import wraps
from typing import Any, Callable

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


def rate_limit(max_calls: int, period: int):
    def decorator(func: Callable[[Request], Any]) -> Callable[[Request], Any]:
        usage: dict[str, list[float]] = {}

        @wraps(func)
        async def wrapper(request: Request) -> Any:
            # get the client's IP address
            if not request.client:
                raise HTTPException(
                    status_code=400,
                    detail="Request has no client information"
                )
            ip_address: str = request.client.host

            # create a unique identifier for the client
            unique_id: str = hashlib.sha256((ip_address).encode()).hexdigest()

            # update the timestamps
            now = time.time()
            if unique_id not in usage:
                usage[unique_id] = []
            timestamps = usage[unique_id]
            timestamps[:] = [t for t in timestamps if now - t < period]

            if len(timestamps) < max_calls:
                timestamps.append(now)
                return await func(request)

            # calculate the time to wait before the next request
            wait = period - (now - timestamps[0])
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Retry after {wait:.2f} seconds",
            )

        return wrapper

    return decorator


@app.get("/")
@rate_limit(max_calls=5, period=60)
async def read_root(request: Request):
    return {"message": "Hello, World!"}


# Run the server using: uvicorn rate_limiter_ip:app --reload
# Or with uv: uv run uvicorn rate_limiter_ip:app --reload
