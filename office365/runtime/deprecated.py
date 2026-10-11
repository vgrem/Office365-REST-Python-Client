from __future__ import annotations

import warnings
from functools import wraps


def deprecated(reason: str, version: str = "next"):
    """Mark functions/methods as deprecated with a warning.

    Args:
        reason: Explanation why this is deprecated
        version: Version when this will be removed
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated and will be removed in v{version}. {reason}",
                category=FutureWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
