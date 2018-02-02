// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import store from './store'
import router from './router'
import VueSocketio from 'vue-socketio'
import VueHead from 'vue-head'
import VueFontAwsome from '@fortawesome/vue-fontawesome'
import fontawesome from '@fortawesome/fontawesome'
import getAppIcons from './assets/fontawesomeIcons'
import AppLayout from './AppLayout'

Vue.config.productionTip = false

Vue.use(VueHead, {
    complement: 'SaarTK'
})

Vue.use(VueSocketio,
    '/irrigation',
    { forceNew: false }/* must have at least empty object! */,
    store
)

Vue.component('f-a', VueFontAwsome)

fontawesome.library.add(
    getAppIcons()
)

window.Vue = new Vue({
    el: '#app-placeholder',
    store,
    router,
    template: '<app-layout/>',
    components: { AppLayout }
})
