from flask_socketio import Namespace


class DefaultNamespace(Namespace):
    def __init__(self):
        super().__init__('/');

    # handles all namespaces without an explicit error handler
    def on_error_default(e):
        print('~~!!~~!!~~!!~~  in default error handler')
        print(request.event['message']) # "my error event"
        print(request.event['args'])    # (data,)
        print(e)
