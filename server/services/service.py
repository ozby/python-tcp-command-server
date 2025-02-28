from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar("T")


def singleton(cls: Type[T]) -> Callable[..., T]:
    _instances: Dict[Type[T], T] = {}

    def get_instance(*args: Any, **kwargs: Any) -> T:
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance
