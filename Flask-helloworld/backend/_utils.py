import logging
from contextlib import suppress
from functools import wraps
from . _globals import io


log = logging.getLogger(__name__)
#TODO: There should be better way to 'inject' socketio instance for resuability


def room_has_clients(namespace, room):
    _room = None
    with suppress(KeyError):
        _room = io.server.manager.rooms[namespace][room]
    return _room is not None and len(_room) > 0


def suppress_on_empty_room(namespace, room):
    def decorator(func):
        @wraps(func)
        def func_wrapper(*arg, **kwarg):
            if room_has_clients(namespace, room):
                return func(*arg, **kwarg)
            log.debug('- suppress emit, room is empty: [{}]'.format(room))
        return func_wrapper
    return decorator
