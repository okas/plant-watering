/**
 * Credit: https://github.com/icebob/vue-websocket
 * This is modified version and works with custom socketio client multiplexNamespace option.
 */

import io from './socket.io-client-multiplex-namespace.js'


export default {
    install (Vue, connection, ioOpts) {
        if (connection != null && typeof connection === 'object') {
            Vue.prototype.$socket = connection
        } else {
            Vue.prototype.$socket = io(connection || '', ioOpts)
        }
        let addListeners = function () {
            if (this.$options['socket']) {
                let conf = this.$options.socket
                if (conf.namespace) {
                    this.$socket = io(conf.namespace, conf.options)
                }
                if (this.$socket.io.readyState === 'closed'
                    && !this.$socket.connected
                    && this.$socket.disconnected
                ) {
                    this.$socket.open()
                }
                if (conf.events) {
                    let prefix = conf.prefix || ''
                    Object.keys(conf.events).forEach((key) => {
                        let func = conf.events[key].bind(this)
                        this.$socket.on(prefix + key, func)
                        conf.events[key].__binded = func
                    })
                }
            }
        }
        let removeListeners = function () {
            if (this.$options['socket']) {
                let conf = this.$options.socket
                if (conf.namespace) {
                    if (--io.managerIndex[io.url(conf.namespace).source] < 1) {
                        this.$socket.close()
                    }
                }
                if (conf.events) {
                    let prefix = conf.prefix || ''
                    Object.keys(conf.events).forEach((key) => {
                        this.$socket.off(prefix + key, conf.events[key].__binded)
                    })
                }
            }
        }
        Vue.mixin({
            [Vue.version.indexOf('2') === 0 ? 'beforeCreate' : 'beforeCompile']: addListeners,
            beforeDestroy: removeListeners
        })
    }
}
