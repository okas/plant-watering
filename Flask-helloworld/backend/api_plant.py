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

@bp.route('/plant/watcher')
def index_page():
    #TODO Do it async
    resp = [make_viewmodel(p, p.measure(True)[1]) for p in app.plant_waterer.plants]
    return jsonify(resp)


@bp.route('/plant/<name>/status')
def get_plant_status(name):
    plant = next((p for p in app.plant_waterer.plants if p.name == name), None)
    resp = make_viewmodel(plant, plant.measure(True)[1])
    return jsonify(resp)


@bp.route('/plant/<name>/statistics')
def get_plant_statistics(name):
    gc = app.plant_waterer.db.collection('gardener_instances')
    mc = app.plant_waterer.db.collection('plant_moistures')
    plants = []
    def extraxt_plants(g, k, v):
        plants.extend(list(p for p in g['plants'] if p[k] == v))
    gc.filter(lambda g: extraxt_plants(g, 'name', name))
    result = mc.filter(lambda m: m['plant_uuid1'] in (p['uuid1'] for p in plants))
    project = {}
    return jsonify(result)

