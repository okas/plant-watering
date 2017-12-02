from flask import (
    Blueprint,
    jsonify,
    current_app as app
    )


bp = Blueprint('api', __name__, url_prefix='/api')


def make_viewmodel(plant, measure):
    return {
        'name': plant.name,
        'state': plant.state.name,
        'moist_level': plant.moist_level,
        'moist_measured': (measure * 100) / 100,
        }

@bp.route('/plant-watcher')
def index_page():
    #TODO Do it async
    resp = [make_viewmodel(p, p.measure(True)[1]) for p in app.plant_waterer.plants]
    return jsonify(resp)


@bp.route('/plant-status/<name>')
def get_plant_status(name):
    plant = next((p for p in app.plant_waterer.plants if p.name == name), None)
    resp = make_viewmodel(plant, plant.measure(True)[1])
    return jsonify(resp)

@bp.route('/plant-stats/<name>')
def get_plant_stats(name):
    db = app.plant_waterer.db
    col = db.collections('gardener_instances')
    print(col.all())
