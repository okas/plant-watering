from flask import Blueprint, render_template


bp = Blueprint('index', __name__)


@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')
