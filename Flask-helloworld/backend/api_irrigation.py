import os
import logging
from contextlib import suppress
from flask import Blueprint, current_app, jsonify, request
from . import svc_irrigation as service


log = logging.getLogger(__name__)
bp = Blueprint('api', __name__, url_prefix='/api/irrigation')

#TODO: All service usages should check it's availability beforehand!

def _make_viewmodel(plant, measure):
    return {
        'name': plant.name,
        'state': plant.state.name,
        'moist_level': plant.moist_level,
        'moist_measured': (measure * 100) / 100,
        }


@bp.route('/watcher')
def get_watcher_state():
    #TODO Do it async
    log.debug(service.get_worker().plants)
    resp = [
        _make_viewmodel(p, p.measure(True)[1])
            for p in service.get_worker().plants
        ]
    return jsonify(resp)


@bp.route('/<name>/status')
def get_plant_status(name):
    plant = next(
        (p for p in service.get_worker().plants if p.name == name),
        None
        )
    resp = _make_viewmodel(plant, plant.measure(True)[1])
    return jsonify(resp)


def _extract_statistics_for(name, stat_collection_name, db):
    gc = db.collection('gardener_instances')
    sc = db.collection(stat_collection_name)
    plants = []
    gc.filter(
        lambda g: plants.extend([p for p in g['plants'] if p['name'] == name])
        )
    filtered_plants = sc.filter(
        lambda m: m['plant_uuid1'] in (p['uuid1'] for p in plants)
        )
    shaped_plants = [ { k: v
        for k,v in p.items() if k not in ('gardener__id', 'plant_uuid1')}
        for p in filtered_plants]
    shaped_plants.reverse()
    return shaped_plants


@bp.route('/<name>/statistics/watering')
def get_plant_stats_measurings(name):
    plants_statistics = _extract_statistics_for(
        name, 'plant_waterings', service.get_worker().db)
    return jsonify(plants_statistics)


@bp.route('/<name>/statistics/measuring')
def get_plant_stats_waterings(name):
    plants_statistics = _extract_statistics_for(
        name, 'plant_moistures', service.get_worker().db)
    return jsonify(plants_statistics)


@bp.route('/service-state')
def get_service_state():
    return jsonify({ 'state': service.get_state() })


@bp.route('/service-start')
def get_service_start():
    state = service.get_state()
    if state == 'on':
        resp = ({ 'state': 'already_on' }, 200)
    elif state == 'off':
        try:
            service.start()
        except BaseException as err:
            resp[0]['state'] = 'service-start-error'
            resp[1] = 500
        else:
            resp = ({ 'state': 'on' }, 200)
    else:
        resp = ({ 'state': state }, 200)
    return jsonify(resp[0]), resp[1]


@bp.route('/service-stop')
def get_service_stop():
    state = service.get_state()
    resp = { 'state': None }
    if state == 'off':
        resp['state'] = 'already_off'
    elif state == 'on':
        service.stop()
        resp['state'] = 'off'
    else:
        resp['state'] = state
    return jsonify(resp)


@bp.route('/service-config')
def get_service_config():
    return jsonify(service.get_config())


def _restart_service_if_possible():
    state = service.get_state()
    if state == 'on':
        service.stop()
        try:
            service.start()
        except BaseException as err:
            resp = ({ 'state': 'service-start-error'}, 500)
        else:
            resp = (None, 204)
    else:
        resp = ({
            'state': state,
            'message': 'Configuration is updated, but service must '\
                'be running beforehand to be restarted.'
            }, 202)
    return resp


@bp.route('/service-config/<string:filename>/update-restart', methods=['PUT'])
def put_service_config_file_update_restart(filename):
    jsonData = request.get_json(silent=True, cache=False)
    if jsonData is None or len(jsonData) < 1:
        resp = ({'message': 'JSON content is missing or empty.' }, 400)
    elif filename == os.path.basename(current_app.config['IRRIGATION_CFG']):
        service.save_config(jsonData)
        resp = _restart_service_if_possible()
    else:
        resp = ({
            'state': service.get_state(),
            'message': 'Filename mismatch, didn\'t expect "{}". Either, '\
                'config filename is already changed on server or you\'ve '\
                'created request with bad filename.'.format(filename)
            }, 422)
    return jsonify(resp[0]), resp[1]
