import flask_socketio
from flask import request
from . _globals import socketio


class DefaultNamespace(flask_socketio.Namespace):
    def __init__(self):
        super().__init__('/');

    @socketio.on_error(namespace='/')
    def error_handler(e):
        print('~~!!~~!!~~!!~~  in default namespace error handler.')
        print(request.event['message']) # "my error event"
        print(request.event['args'])    # (data,)
        print(e)


# handles all namespaces without an explicit error handler
@socketio.on_error_default
def on_error_default(e):
    print('~~!!~~!!~~!!~~  in [defaul] error handler.')
    print(request.event['message']) # "my error event"
    print(request.event['args'])    # (data,)
    print(e)
