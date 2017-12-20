import flask


bp = flask.Blueprint('index', __name__)


@bp.route('/', defaults={ 'path': '' })
@bp.route('/<path:path>')
def catch_all(path):
    return flask.render_template('index.html')
