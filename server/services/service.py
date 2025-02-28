from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


def singleton(cls: type[T]) -> Callable[..., T]:
    _instances: dict[type[T], T] = {}

    def get_instance(*args: Any, **kwargs: Any) -> T:
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance
