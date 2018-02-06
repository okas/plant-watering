import Vue from 'vue'
import Router from 'vue-router'

const routerOptions = [
    {
        path: '/irrigation/',
        component: 'Irrigation/Layout',
        children: [
            {
                path: '',
                name: 'irrigation',
                component: 'Irrigation/PlantWatcher'
            },
            {
                path: ':name/calibrate',
                name: 'plantcalibrate',
                component: 'Irrigation/PlantCalibration',
                props: true
            },
            {
                path: ':name/statistics',
                name: 'plantstats',
                component: 'Irrigation/PlantStats',
                props: true
            },
            {
                path: 'service-manager',
                name: 'irrigationservice',
                component: 'Irrigation/Service'
            }
        ]
    },
    {
        path: '/windowblind',
        component: 'Windowblind/Layout',
        children: [
            {
                path: '',
                name: 'blindscontrol',
                component: 'Windowblind/Control'
            }
        ]
    },
    {
        path: '/about',
        component: 'About'
    },
    {
        path: '/',
        alias: '/index',
        component: 'Home'
    },
    {
        path: '/*',
        component: 'NotFound'
    }
]

const componentizer = function (options) {
    return options.map(opt => {
        return {
            ...opt,
            component: () => import(`@/components/${opt.component}.vue`),
            ...opt.hasOwnProperty('children') && {
                children: componentizer(opt.children)
            }
        }
    })
}

Vue.use(Router)

export default new Router({
    routes: componentizer(routerOptions),
    mode: 'history'
})
