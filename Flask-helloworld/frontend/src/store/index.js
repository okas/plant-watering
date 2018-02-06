import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

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
        setApiOnConnect: (s, ioId) => {
            s.apiState = 'online'
            s.ioId = ioId
        },
        setApiOnDisconnect: (s, ioId) => {
            s.apiState = 'offline'
            s.state = 'server-off'
            s.ioId_prev = ioId
        },
        setServiceStatus: (s, data) => {
            Object.assign(s, data)
        }
    },
    actions: {
        refreshServiceStatus ({commit}) {
            this._vm.$socket.emit('get_status', data =>
                commit('setServiceStatus', data)
            )
        }
    },
    strict: debug
}

export default new Vuex.Store({
    modules: { irrigation }
})
