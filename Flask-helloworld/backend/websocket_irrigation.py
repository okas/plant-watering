import os
import logging
import flask_socketio
import flask
from . _globals import socketio
from . import service_irrigation


ns = '/irrigation'
log = logging.getLogger(__name__)


@service_irrigation.state_changed_event.connect_via('svc_start')
@service_irrigation.state_changed_event.connect_via('svc_stop')
def broadcast_service_status(sender, **kw):
    print('---------- sender: % s ; data: %s' % (sender, kw))
    socketio.emit('service_status', kw, namespace=ns)


@socketio.on_error(ns)
def on_error(e):
    print('~~!!~~!!~~!!~~ in irrigation error handler')
    print(e)


class IrrigationNamespaceHandlers(flask_socketio.Namespace):
    def __init__(self):
        super().__init__(ns);

    def on_connect(self):
        print('~~#~~#~~#~~ client connected')
        self.emit('service_status', service_irrigation.get_state())
        return 'you\'re connected'

    def on_disconnect(self):
        print('~~#~~#~~#~~ client disconnected')
        return 'ok'

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

    def _make_viewmodel(self, plant):
        measure = (plant.measure(True)[1] *100 ) / 100
        return {
            'name': plant.name,
            'state': plant.state.name,
            'moist_level': plant.moist_level,
            'moist_measured': measure
            }

    def on_get_watcher_state(self):
        return [self._make_viewmodel(p) for p in service_irrigation.get_worker().plants]

    def on_get_plant_status(self, name):
        generator = (p for p in service_irrigation.get_worker().plants
            if p.name == name)
        plant = next(generator, None)
        return self._make_viewmodel(plant)

    def _extract_statistics_for(self, name, stat_collection_name):
        db = service_irrigation.get_worker().db
        gardenenrs = db.collection('gardener_instances')
        stats_data = db.collection(stat_collection_name)
        plants = []
        gardenenrs.filter(
            lambda g: plants.extend([p for p in g['plants'] if p['name'] == name])
            )
        filtered_plants = stats_data.filter(
            lambda m: m['plant_uuid1'] in (p['uuid1'] for p in plants)
            )
        shaped_plants = [ { k: v
            for k,v in p.items() if k not in ('gardener__id', 'plant_uuid1')}
            for p in filtered_plants]
        shaped_plants.reverse()
        return shaped_plants

    def on_get_plant_stats_waterings(self, name):
        return self._extract_statistics_for(name, 'plant_waterings')

    def on_get_plant_stats_measurings(self, name):
        return self._extract_statistics_for(name, 'plant_moistures')
