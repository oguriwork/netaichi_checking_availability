from __future__ import annotations

from collections.abc import Callable


def randam_sleep(func: Callable):
    from random import uniform
    from time import sleep

    def _wrapper(*args, **keywords):
        sleep(uniform(0.1, 0.5))
        v = func(*args, **keywords)
        return v

    return _wrapper
