import logging
from flask import current_app, request
from flask_socketio import Namespace
from .. _globals import io, io_connect_message_fmt
from . __init__ import ns


log = logging.getLogger(__name__)


class WindowblindNamespaceHandlers(Namespace):
    def __init__(self):
        super().__init__(ns);

    def on_connect(self):
        log.info(io_connect_message_fmt.format('connected', ns, request.sid))

    def on_disconnect(self):
        log.info(io_connect_message_fmt.format('disconnected', ns, request.sid))

    @io.on_error(ns)
    def on_error(e):
        log.info('~~!!~~!!~~!!~~ in {} error handler'.format(ns))
        log.info('flask.request.sid: %s' % request.sid)
        log.exception(e)
        return { 'error': 'Internal server error! ToDo: add details.' }

    def on_up(self):
        ...

    def on_stop(self):
        ...

    def on_down(self):
        ...


io.on_namespace(WindowblindNamespaceHandlers())
