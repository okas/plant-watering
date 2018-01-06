import os
import logging
import flask_socketio
import flask
from . _globals import socketio
from . apiws_brc_irrigation import _make_viewmodel
from . import service_irrigation


#TODO: See dependency handling possibilities near disconnect()
# See: https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/flask_socketio/__init__.py

ns = '/irrigation'
log = logging.getLogger(__name__)


class IrrigationNamespaceHandlers(flask_socketio.Namespace):
    def __init__(self):
        super().__init__(ns);

    def on_connect(self):
        print('~~#~~#~~#~~ connected; ns: [%s], client: [%s]'
            % (ns, flask.request.sid))
        self.emit('service_status', service_irrigation.get_state())

    def on_disconnect(self):
        print('~~#~~#~~#~~ disconnected; ns: [%s], client: [%s]'
            % (ns, flask.request.sid))

    @socketio.on_error(ns)
    def on_error(e):
        print('~~!!~~!!~~!!~~ in irrigation error handler')
        print('flask.request.sid: %s' % flask.request.sid)
        return { 'error': 'Internal server error! ToDo: add details.' }

    def on_get_status(self):
        return service_irrigation.get_state()

    def on_service_stop(self):
        info = service_irrigation.get_state()
        if info['state'] == 'on':
            service_irrigation.stop()
        elif info['state'] == 'off':
            return 'ok'
        else:
            return info['state']

    def on_service_start(self):
        info = service_irrigation.get_state()
        if info['state'] == 'off':
            try:
                service_irrigation.start()
            except BaseException as err:
                return 'service-start-error'
        elif info['state'] == 'on':
            return 'ok'
        else:
            return info['state']

    def on_get_service_config(self):
        return service_irrigation.get_config()

    def _restart_service_if_possible(self):
        info = service_irrigation.get_state()
        if info['state'] == 'on':
            service_irrigation.stop()
            try:
                service_irrigation.start()
            except BaseException as err:
                return ('error', 'service-start-error')
        elif info['state'] == 'off':
            return ( 'info',
                'Configuration was updated, but service was not restarted '
                'as restart pre-condition is running service.')

    def _is_correct_filename(self, filename):
        return filename == os.path.basename(
            flask.current_app.config['IRRIGATION_CFG'])

    def on_store_service_config_and_restart(self, data):
        if data['content'] is None or len(data['content']) < 1:
            return ('error', 'JSON content is missing.')
        elif self._is_correct_filename(data['filename']):
            service_irrigation.save_config(data['content'])
            return self._restart_service_if_possible()
        else:
            return ( 'error',
                'Filename mismatch, didn\'t expect "{filename}". Either, '
                'filename is already changed on server or you\'ve '
                'created request with bad filename.'.format(**data))

    def on_get_watcher_state(self):
        return list(_make_viewmodel(p, True)
            for p in service_irrigation.get_worker().plants)

    def on_get_plant_status(self, name):
        generator = (p for p in service_irrigation.get_worker().plants
            if p.name == name)
        plant = next(generator, None)
        # TODO: should handle 'no plant found' case
        return _make_viewmodel(plant, True)

    def _extract_statistics_for(self, name, stat_collection_name):
        db = service_irrigation.get_worker().db
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


socketio.on_namespace(IrrigationNamespaceHandlers())
