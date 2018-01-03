import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const mutateServiceStatus = (state, args) => {
    if (args[0]) {
        Object.assign(state.statusObj, args[0])
    }
}

const socketMutations = {
    'SOCKET_SERVICE_STATUS': mutateServiceStatus,
    'SOCKET_WATER_SUPPLY_STATE': mutateServiceStatus,
    'SOCKET_WATER_CONSUMED_CHANGED': mutateServiceStatus,
    'SOCKET_CONNECT' (state, msg) {
        console.log('~ ~ [irrigation] socket connected')
        state.api.state = 'online'
    },
    'SOCKET_DISCONNECT' (state, reason) {
        console.log(`~ ! ~ [irrigation] socket disconnected, reson: ${reason}.`)
        state.api.state = 'offline'
    }
}

// If there are more modules in future then refactor them into separate files
const irrigation = {
    namespaced: true,
    state () {
        return {
            api: { state: '' },
            statusObj: {
                state: '',
                waterLevel: '',
                waterConsum: 0
            }
        }
    },
    getters: {
        generalStatus (s) {
            if (s.api.state !== 'online') {
                return 'server-off'
            }
            return ['on', 'off'].includes(s.statusObj.state)
                ? s.statusObj.state
                : 'error'
        }
    },
    mutations: {
        mutateServiceStatus,
        ...socketMutations
    },
    actions: {
        refreshServiceStatus ({commit}) {
            this._vm.$socket.emit('get_status', data =>
                commit('mutateServiceStatus', [data])
            )
        }
    },
    strict: debug
}

export default new Vuex.Store({
    modules: { irrigation }
})
