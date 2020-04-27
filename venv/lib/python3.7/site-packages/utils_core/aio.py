import asyncio
import functools


def run_sync(func, *args, **kwargs):
    """
    Run a synchronous function with given args via asyncio.run_in_executor and return the result

    :param callable func: Any callable
    :param list args: Position args to pass to `func`
    :param dict kwargs: Keyword args to pass to `func`
    :return asyncio.Future:
    """
    return asyncio.get_event_loop().run_in_executor(None, functools.partial(func, *args, **kwargs))
