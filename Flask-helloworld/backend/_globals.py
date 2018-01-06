import flask_socketio


# It allows to ommit dealing of flask context management, where it's mode comfortable.
io = flask_socketio.SocketIO()


del flask_socketio
