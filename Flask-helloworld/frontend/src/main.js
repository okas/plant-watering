// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import store from './store'
import router from './router'
import VueSocketio from 'vue-socketio'
import VueHead from 'vue-head'
import Buefy from 'buefy'
import 'buefy/lib/buefy.css'
import AppLayout from './AppLayout'

Vue.config.productionTip = false

Vue.use(VueHead, {
    complement: 'SaarTK'
})

Vue.use(VueSocketio,
    '/irrigation',
    { forceNew: false }/* must have at least empty object! */,
    store)

Vue.use(Buefy)

window.Vue = new Vue({
    el: '#app-placeholder',
    store,
    router,
    template: '<app-layout/>',
    components: { AppLayout }
})
