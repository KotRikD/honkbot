import asyncio
from typing import Coroutine

def schedule_coroutine(target: Coroutine):
    '''
    Tool schedules target in Asyncio

    :param Coroutine: Routine for schedule
    :return: True or False
    '''
    if asyncio.iscoroutine(target):
        return asyncio.ensure_future(target, loop=asyncio.get_event_loop())
    else:
        raise TypeError("target must be a coroutine, "
                        "not {!r}".format(type(target)))

