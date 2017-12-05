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
    resp = [
        make_viewmodel(p, p.measure(True)[1])
        for p in app.plant_waterer.plants
        ]
    return jsonify(resp)


@bp.route('/plant/<name>/status')
def get_plant_status(name):
    plant = next(
        (p for p in app.plant_waterer.plants if p.name == name),
        None
        )
    resp = make_viewmodel(plant, plant.measure(True)[1])
    return jsonify(resp)


def _extract_statistics_for(name, stat_collection_name, db):
    gc = db.collection('gardener_instances')
    sc = db.collection(stat_collection_name)
    plants = []
    gc.filter(
        lambda g: plants.extend(
            [p for p in g['plants'] if p['name'] == name]
            )
        )
    filtered_plants = sc.filter(
        lambda m: m['plant_uuid1'] in (p['uuid1'] for p in plants)
        )
    shaped_plants = [ { k: v
        for k,v in p.items() if k not in ('gardener__id', 'plant_uuid1')}
        for p in filtered_plants]
    shaped_plants.reverse()
    return shaped_plants


@bp.route('/plant/<name>/statistics/watering')
def get_plant_stats_measurings(name):
    plants_statistics = _extract_statistics_for(
        name,
        'plant_waterings',
        app.plant_waterer.db)
    return jsonify(plants_statistics)


@bp.route('/plant/<name>/statistics/measuring')
def get_plant_stats_waterings(name):
    plants_statistics = _extract_statistics_for(
        name,
        'plant_moistures',
        app.plant_waterer.db)
    return jsonify(plants_statistics)
