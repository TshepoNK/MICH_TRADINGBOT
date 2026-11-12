import time
from functools import wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def retry(retries: int = 3, base_delay: float = 0.5, backoff_factor: float = 2.0, retry_exceptions: tuple[type[Exception], ...] = (Exception,)):
    """Retry a function with exponential backoff for transient failures."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions:
                    if attempt >= retries:
                        raise
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper  # type: ignore[return-value]

    return decorator
