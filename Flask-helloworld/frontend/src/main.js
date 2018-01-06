// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import VueSocketio from 'vue-socketio'
import VueHead from 'vue-head'
import store from './store'
import router from './router'
import AppLayout from './AppLayout'

Vue.config.productionTip = false

Vue.use(VueHead, {
    complement: 'SaarTK'
})

Vue.use(VueSocketio,
    '/irrigation',
    { forceNew: false }/* must have at least empty object! */,
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
