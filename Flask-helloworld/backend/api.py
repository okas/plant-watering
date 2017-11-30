from flask import (
    Blueprint,
    jsonify,
    current_app as app
    )


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/plant-watcher')
def index_page():
    for plant in app.plant_waterer.plants:
        measurement = plant.measure(True)
        resp = {
            'message': 'Plant: {0.name} | state: {0.state} | '\
              'needed moisture: {0.moist_level} | '\
              'current moisture: {1:.2f}'
              .format(plant, measurement[1])
        }
    return jsonify(resp)
