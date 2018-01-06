import logging
import flask_socketio
from flask import request
from . _globals import io


log = logging.getLogger(__name__)


# handles all namespaces without an explicit error handler
@io.on_error_default
def on_error_default(e):
    print('~~!!~~!!~~!!~~  in [default] error handler.')
    print(request.event['message']) # "my error event"
    print(request.event['args'])    # (data,)
    print(e)


@io.on_error(namespace='/')
def error_handler(e):
    print('~~!!~~!!~~!!~~  in ["/" namespace] error handler.')
    print(request.event['message']) # "my error event"
    print(request.event['args'])    # (data,)
    print(e)


class DefaultNamespaceHandlers(flask_socketio.Namespace):
    def __init__(self):
        super().__init__('/');


io.on_namespace(DefaultNamespaceHandlers())
