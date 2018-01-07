import os
import logging
import flask_socketio
from flask import current_app, request
from .. _globals import io
from . ws_broadcasts import _make_viewmodel
from . import service


#TODO: See dependency handling possibilities near disconnect()
# See: https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/flask_socketio/__init__.py

ns = '/irrigation'
log = logging.getLogger(__name__)


class IrrigationNamespaceHandlers(flask_socketio.Namespace):
    def __init__(self):
        super().__init__(ns);

    def on_connect(self):
        log.info('~~#~~#~~#~~ connected; ns: [%s], client: [%s]'
            % (ns, request.sid))
        self.emit('service_status', service.get_state())

    def on_disconnect(self):
        log.info('~~#~~#~~#~~ disconnected; ns: [%s], client: [%s]'
            % (ns, request.sid))

    @io.on_error(ns)
    def on_error(e):
        log.info('~~!!~~!!~~!!~~ in irrigation error handler')
        log.info('flask.request.sid: %s' % request.sid)
        log.exception(e)
        return { 'error': 'Internal server error! ToDo: add details.' }

    def on_get_status(self):
        return service.get_state()

    def on_service_stop(self):
        info = service.get_state()
        if info['state'] == 'on':
            service.stop()
        elif info['state'] == 'off':
            return 'ok'
        else:
            return info['state']

    def on_service_start(self):
        info = service.get_state()
        if info['state'] == 'off':
            try:
                service.start()
            except BaseException as err:
                return 'service-start-error'
        elif info['state'] == 'on':
            return 'ok'
        else:
            return info['state']

    def on_get_service_config(self):
        return service.get_config()

    def _restart_service_if_possible(self):
        info = service.get_state()
        if info['state'] == 'on':
            service.stop()
            try:
                service.start()
            except BaseException as err:
                return ('error', 'service-start-error')
        elif info['state'] == 'off':
            return ( 'info',
                'Configuration was updated, but service was not restarted '
                'as restart pre-condition is running service.')

    def _is_correct_filename(self, filename):
        return filename == os.path.basename(
            current_app.config['IRRIGATION_CFG'])

    def on_store_service_config_and_restart(self, data):
        if data['content'] is None or len(data['content']) < 1:
            return ('error', 'JSON content is missing.')
        elif self._is_correct_filename(data['filename']):
            service.save_config(data['content'])
            return self._restart_service_if_possible()
        else:
            return ( 'error',
                'Filename mismatch, didn\'t expect "{filename}". Either, '
                'filename is already changed on server or you\'ve '
                'created request with bad filename.'.format(**data))

    def on_push_all_plants(self):
        for plant in service.get_worker().plants:
            self.emit(
                'update_plant_status',
                data=_make_viewmodel(plant),
                room=request.sid
                )

    def on_initiate_plant_measuring(self, name):
        gen = (p for p in service.get_worker().plants if p.name == name)
        plant = next(gen, None)
        plant.measure(True)

    def _extract_statistics_for(self, name, stat_collection_name):
        db = service.get_worker().db
        gardenenrs = db.collection('gardener_instances')
        stats_data = db.collection(stat_collection_name)
        plants = []
        gardenenrs.filter(
            lambda g: plants.extend(
                list(p for p in g['plants'] if p['name'] == name))
            )
        filtered_plants = stats_data.filter(
            lambda m: m['plant_uuid1'] in (p['uuid1'] for p in plants))
        shaped_plants = [ { k: v
            for k,v in p.items() if k not in ('gardener__id', 'plant_uuid1')}
            for p in filtered_plants]
        shaped_plants.reverse()
        return shaped_plants

    def on_get_plant_stats_waterings(self, name):
        return self._extract_statistics_for(name, 'plant_waterings')

    def on_get_plant_stats_measurings(self, name):
        return self._extract_statistics_for(name, 'plant_moistures')


io.on_namespace(IrrigationNamespaceHandlers())
