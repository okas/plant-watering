from flask import (
    Blueprint,
    jsonify,
    current_app as app
    )


bp = Blueprint('api', __name__, url_prefix='/api')

status_format = 'Plant: {0.name} | state: {0.state} | '\
                'needed moisture: {0.moist_level} | '\
                'current moisture: {1:.2f}'

@bp.route('/plant-watcher')
def index_page():
    resp = {'plants': []}
    #TODO Do it async
    for p in app.plant_waterer.plants:
        measurement = p.measure(True)
        resp['plants'].append({
            'name': p.name,
            'status': status_format.format(p, measurement[1])
        })
    return jsonify(resp)


@bp.route('/plant-status/<name>')
def get_plant_status(name):
    plant = next((p for p in app.plant_waterer.plants if p.name == name), None)
    measurement = plant.measure(True)
    resp = status_format.format(plant, measurement[1])
    return jsonify(resp)
