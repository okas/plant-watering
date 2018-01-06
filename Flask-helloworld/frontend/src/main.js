// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import VueSocketio from 'vue-socketio'
import VueHead from 'vue-head'
// import io from 'socket.io-client'
import store from './store'
import router from './router'
import AppLayout from './AppLayout'

Vue.config.productionTip = false

Vue.use(VueHead, {
    complement: 'SaarTK'
})

Vue.use(VueSocketio,
    '/irrigation',
    { forceNew: false }/* vital for store to work! */,
    store)

/* eslint-disable no-new */
new Vue({
    // name: 'App' // for future use
    el: '#app-placeholder',
    store,
    router,
    template: '<app-layout/>',
    components: { AppLayout }
})
