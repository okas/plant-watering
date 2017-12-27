from flask_socketio import Namespace, send, emit
from . import service_irrigation


#TODO: print statements to log
#TODO: cleanup prints

__io = None

NSP = '/irrigation'

def init(socketio):
    global __io
    __io = socketio


@service_irrigation.state_changed_event.connect_via('svc_start')
@service_irrigation.state_changed_event.connect_via('svc_stop')
def handle_get_status(sender, **kw):
    __io.emit('service_status', kw, namespace=NSP)


# handles all namespaces without an explicit error handler
@__io.on_error_default
def on_error_default(e):
    print('~~!!~~!!~~!!~~  in default error handler')
    print(request.event['message']) # "my error event"
    print(request.event['args'])    # (data,)
    print(e)


class IrrigationNamespace(Namespace):
    def __init__(self):
        super().__init__(NSP);

    def on_connect(self):
        print('~~#~~#~~#~~ client connected')
        emit('service_status', service_irrigation.get_state())
        return 'ok'

    def handle_disconnect():
        print('~~#~~#~~#~~ client disconnected')
        return 'ok'

    def on_error(e):
        print('~~!!~~!!~~!!~~ in irrigation error handler')
        print(e)

    def on_get_status():
        emit('service_status', service_irrigation.get_state())
