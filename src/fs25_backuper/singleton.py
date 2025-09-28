from typing import Any


class Singleton(object):
    _instance = None

    def __new__(class_, *args: tuple, **kwargs: dict[str, Any]) -> "Singleton":
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
