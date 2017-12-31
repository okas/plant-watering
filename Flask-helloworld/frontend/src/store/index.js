import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const mutateServiceStatus = (state, args) => {
    if (args[0]) {
        state.statusObj = args[0]
    }
}

const socketMutations = {
    'SOCKET_CONNECT' (state, msg) {
        const _msg = msg ? `; server said, {msg}` : ''
        console.log(`~ ~ [irrigation] socket connected${_msg}.`)
        state.api.state = 'online'
    },
    'SOCKET_DISCONNECT' (state, reason) {
        console.log(`~ ! ~ [irrigation] socket disconnected, reson: ${reason}.`)
        state.api.state = 'offline'
    },
    'SOCKET_SERVICE_STATUS': mutateServiceStatus
}

// If there are more modules in future then refactor them into separate files
const irrigation = {
    namespaced: true,
    state () {
        return {
            api: { state: '' },
            statusObj: {
                state: '',
                waterLevel: ''
            }
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
