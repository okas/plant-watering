import flask_socketio


# It allows to ommit dealing of flask context management, where it's mode comfortable.
io = flask_socketio.SocketIO()

io_connect_message_fmt = '~~#~~#~~#~~ {}; NS: [{}], client: [{}]'

del flask_socketio
