import Vue from 'vue'
import Router from 'vue-router'

const routerOptions = [
    {
        path: '/plant-statistics/:name',
        name: 'plantstats',
        component: 'PlantStats',
        props: true
    },
    {
        path: '/plant-calibrate/:name',
        name: 'plantcalibrate',
        component: 'PlantCalibrate',
        props: true
    },
    {
        path: '/plant-watcher',
        name: 'plantwatcher',
        component: 'PlantWatcher'
    },
    {
        path: '/plant-manager',
        name: 'plantmanager',
        component: 'PlantManager'
    },
    { path: '/', component: 'HelloWorld' },
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
