import Vue from 'vue'
import Router from 'vue-router'

const routerOptions = [
    {
        path: '/irrigation/:name/statistics',
        name: 'plantstats',
        component: 'Irrigation/PlantStats',
        props: true
    },
    {
        path: '/irrigation/:name/calibrate',
        name: 'plantcalibrate',
        component: 'Irrigation/PlantCalibration',
        props: true
    },
    {
        path: '/irrigation/',
        name: 'irrigation',
        component: 'Irrigation/PlantWatcher'
    },
    {
        path: '/irrigation/service-manager',
        name: 'irrigationservice',
        component: 'Irrigation/Service'
    },
    {
        path: '/',
        alias: '/index',
        component: 'Home'
    },
    { path: '/about', component: 'About' },
    { path: '/*', component: 'NotFound' }
]

const routes = routerOptions.map(route => {
    return {
        ...route,
        component: () => import(`@/components/${route.component}.vue`)
    }
})

Vue.use(Router)

export default new Router({
    routes: routes,
    mode: 'history'
})
