import Vue from 'vue'
import Router from 'vue-router'

const routerOptions = [
    {
        path: '/irrigation/:name/statistics',
        name: 'plantstats',
        component: 'IrrigationPlantStats',
        props: true
    },
    {
        path: '/irrigation/:name/calibrate',
        name: 'plantcalibrate',
        component: 'IrrigationPlantCalibration',
        props: true
    },
    {
        path: '/irrigation/main',
        name: 'plantwatcher',
        component: 'IrrigationMain'
    },
    {
        path: '/irrigation/manager',
        name: 'plantmanager',
        component: 'IrrigationManager'
    },
    { path: '/about', component: 'About' },
    { path: '/', component: 'HelloWorld' },
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
