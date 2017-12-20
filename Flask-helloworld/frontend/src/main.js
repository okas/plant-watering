// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import router from './router'
import VueHead from 'vue-head'
import AppLayout from './AppLayout'

Vue.config.productionTip = false

Vue.use(VueHead, {
    complement: 'SaarTK'
})

/* eslint-disable no-new */
new Vue({
    // name: 'App' // for future use
    el: '#app-placeholder',
    router,
    template: '<app-layout/>',
    components: { AppLayout }
})
