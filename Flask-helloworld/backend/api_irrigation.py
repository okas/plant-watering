import os
import logging
from contextlib import suppress
from flask import Blueprint, current_app, jsonify, request
from . import service_irrigation as service


log = logging.getLogger(__name__)
bp = Blueprint('api', __name__, url_prefix='/api/irrigation')

#TODO: All service usages should check it's availability beforehand!


def _make_viewmodel(plant):
    measure = (plant.measure(True)[1] *100 ) / 100
    return {
        'name': plant.name,
        'state': plant.state.name,
        'moist_level': plant.moist_level,
        'moist_measured': measure
        }


@bp.route('/watcher')
def get_watcher_state():
    #TODO Do it async
    log.debug(service.get_worker().plants)
    resp = [_make_viewmodel(p) for p in service.get_worker().plants]
    return jsonify(resp)


@bp.route('/<name>/status')
def get_plant_status(name):
    generator = (p for p in service.get_worker().plants if p.name == name)
    plant = next(generator, None)
    resp = _make_viewmodel(plant)
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
    return jsonify(service.get_state())


@bp.route('/service-start')
def get_service_start():
    info = service.get_state()
    if info['state'] == 'on':
        info['state'] = 'already_on'
        resp = (info, 200)
    elif info['state'] == 'off':
        try:
            service.start()
        except BaseException as err:
            info['state'] = 'service-start-error'
            resp = (info, 500)
        else:
            info['state'] = 'on'
            resp = (info, 200)
    else:
        resp = (info, 200)
    return jsonify(resp[0]), resp[1]


@bp.route('/service-stop')
def get_service_stop():
    resp = service.get_state()
    if resp['state'] == 'off':
        resp['state'] = 'already_off'
    elif resp['state'] == 'on':
        service.stop()
        resp['state'] = 'off'
    return jsonify(resp)


@bp.route('/service-config')
def get_service_config():
    return jsonify(service.get_config())


def _restart_service_if_possible():
    info = service.get_state()
    if info['state'] == 'on':
        service.stop()
        try:
            service.start()
        except BaseException as err:
            info['state'] = 'service-start-error'
            resp = (info, 500)
        else:
            resp = (None, 204)
    elif resp['state'] == 'off':
        resp = ({
            'state': info['state'],
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
        info_ = service.get_state().update({
            'message': 'Filename mismatch, didn\'t expect "{}". '
                'Either, config filename is already changed on '
                'server or you\'ve created request with bad filename.'
                .format(filename)
            })
        resp = (info_, 422)
    return jsonify(resp[0]), resp[1]
