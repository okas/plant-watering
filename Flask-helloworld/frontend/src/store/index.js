import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const mutateServiceStatus = (state, args) => {
    if (args[0]) {
        Object.assign(state, args[0])
    }
}

const socketMutations = {
    'SOCKET_SERVICE_STATUS': mutateServiceStatus,
    'SOCKET_WATER_SUPPLY_STATE': mutateServiceStatus,
    'SOCKET_WATER_CONSUMED_CHANGED': mutateServiceStatus,
    'SOCKET_CONNECT' (s, msg) {
        console.log('~ ~ [irrigation] socket connected')
        s.apiState = 'online'
        s.ioId = this._vm.$socket.id
    },
    'SOCKET_DISCONNECT' (s, reason) {
        console.log(`~ ! ~ [irrigation] socket disconnected, reson: ${reason}.`)
        s.apiState = 'offline'
        s.state = 'server-off'
        s.ioId_prev = s.ioId
    }
}

// If there are more modules in future then refactor them into separate files
const irrigation = {
    namespaced: true,
    state () {
        return {
            apiState: '',
            state: 'server-off',
            waterLevel: '',
            waterConsum: 0,
            ioId: '',
            ioId_prev: ''
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
