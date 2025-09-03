
from __future__ import annotations

from collections.abc import Callable
from functools import wraps



def randam_sleep(func: Callable):
    from random import uniform
    from time import sleep

    def _wrapper(*args, **keywords):
        sleep(uniform(0.1, 0.5))
        v = func(*args, **keywords)
        return v

    return _wrapper


def ensure_driver_exists(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.driver:
            raise RuntimeError("Browser driver is not initialized. Call new() first.")
        return func(self, *args, **kwargs)

    return wrapper
