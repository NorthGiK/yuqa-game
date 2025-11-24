import logging
from typing import Any, Callable


def log_func_call(logger: logging.Logger, /):
    def wrap(func: Callable[..., Any]):
        def inner(*args, **kwargs):
            message: str = "call `{func}`, args `{args}, {kwargs}`".format(
                func=func.__name__,
                args=args,
                kwargs=kwargs,
            )
            logger.info(message)
            print(message)

            return func(*args, **kwargs)

        return inner

    return wrap
