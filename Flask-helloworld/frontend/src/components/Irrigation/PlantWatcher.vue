<template>
<layout>
<section>
    <header>
        <h2>Real-time plant overview</h2>
    </header>
    <article>
        <header>
            <ul class="list-style-none">
                <li class="status-small">
                    Updates: <span v-text="ticker"/>
                    </li>
                <li v-if="status" v-text="status" :class="statusClass"/>
            </ul>
        </header>
        <ul class="plant-list clearfix">
            <dl v-for="p in plants" :class="stateOutterClass" class="plant-block">
                <div :class="stateInnerClass">
                    <dt class="h1" v-text="p.name"></dt>
                    <div class="horizontal status">
                        <dt class="float-left">state:</dt>
                        <dd v-text="p.state" class="float-align-right"></dd>
                    </div>
                    <div class="horizontal">
                        <dt class="h2 float-left">Moisture</dt>
                        <dd class="h2 float-align-right">%</dd>
                    </div>
                    <div>
                        <div class="horizontal status">
                            <dt class="float-left">required:</dt>
                            <dd v-text="p.moist_level" class="float-align-right"></dd>
                        </div>
                        <div class="horizontal status">
                            <dt class="float-left">measured:</dt>
                            <dd v-text="p.moist_measured" class="float-align-right"></dd>
                        </div>
                        <div class="horizontal">
                            <a href=""
                                v-if="serviceIsOn"
                                v-text="linkRef"
                                @click.prevent="wsRefreshPlant(p)"/>
                            <span v-text="linkRef" v-else/>
                            <span>&nbsp;|&nbsp;</span>
                            <router-link
                                v-if="serviceIsOn"
                                v-text="linkSta"
                                :to="{name: 'plantstats', params: {name: p.name}}"/>
                            <span v-text="linkSta" v-else/>
                            <span>&nbsp;|&nbsp;</span>
                            <router-link
                                v-if="serviceIsOn"
                                v-text="linkCal"
                                :to="{name: 'plantcalibrate', params: {name: p.name}}"/>
                            <span v-text="linkCal" v-else/>
                        </div>
                    </div>
                </div>
            </dl>
        </ul>
    </article>
</section>
</layout>
</template>

<script>
import Layout from './Layout'

export default {
    name: 'IrrigationPlantWatcher',
    components: { Layout },
    head: { title: { inner: 'Plant watcher' } },
    data () {
        return {
            status: '...loading plants from server...',
            plants: [],
            watcherIsRendering: false,
            statusClass: 'highlight-disa',
            stateOutterClass: '',
            stateInnerClass: '',
            ticker: 0,
            linkRef: 'refresh',
            linkSta: 'stats',
            linkCal: 'calibrate'
        }
    },
    sockets: {
        update_plant_status (data) {
            if (!data) {
                this.status = 'server initiated plant status update, but no data was sent.'
                this.statusClass = 'highlight-crit'
                return
            }
            if (this.plants.length === 0) {
                this.plants.push(data)
                this.stateOutterClass = 'high'
                this.stateInnerClass = 'default-text-color'
            } else {
                this.addOrUpdatePlant(data)
            }
            this.status = ''
            this.ticker++
        }
    },
    computed: {
        serviceIsOn () {
            return this.$store.getters['irrigation/generalStatus'] === 'on'
        }
    },
    watch: {
        serviceIsOn (s) {
            if (s) {
                this.activatePlantsClasses()
                this.status = ''
                this.renderPlants()
            } else {
                this.deActivatePlantsClasses()
                this.status = 'Service is not running, cannot update.'
            }
        }
    },
    methods: {
        wsRefreshPlant (plant) {
            this.$socket.emit('get_plant_status', plant.name, (data) => {
                if (!data) {
                    if (!this.watcherIsRendering) {
                        this.status = `didn't get refresh for "${plant.name}", check what's wrong.`
                    }
                    return
                }
                Object.assign(plant, data)
                this.status = ''
            })
        },
        renderPlants () {
            this.watcherIsRendering = true
            this.$socket.emit('get_watcher_state', (data) => {
                if (data && 'error' in data) {
                    this.status = data.error
                    this.deActivatePlantsClasses()
                    return
                }
                // TODO: plants on loading situation
                // ## load 1x1 -- server must notify at first(or additional argument) how much plants will come.
                if (!Array.isArray(data) || data.length === 0) {
                    this.status = "didn't get any plants, check what's wrong'"
                    return
                }
                data.forEach(this.addOrUpdatePlant)
                this.status = ''
                this.activatePlantsClasses()
                this.watcherIsRendering = false
            })
        },
        addOrUpdatePlant (plant) {
            var existing = this.plants.find(p => p.name === plant.name)
            if (existing) {
                Object.assign(existing, plant)
            } else {
                this.plants.push(plant)
            }
        },
        activatePlantsClasses () {
            this.stateOutterClass = 'high'
            this.stateInnerClass = 'default-text-color'
            this.statusClass = ''
        },
        deActivatePlantsClasses () {
            this.stateInnerClass = 'disa'
            this.stateOutterClass = 'disa'
            this.statusClass = 'highlight-warn'
        }
    },
    created () {
        if (this.$store.state.irrigation.statusObj.state !== 'on') {
            this.deActivatePlantsClasses()
            this.status = 'Service is not running, can\'t render the overview for you.'
            return
        }
        this.renderPlants()
    }
}
</script>

<style scoped>
.plant-list {
    padding: 0;
    margin: 0;
}
.plant-block {
    width: 195px;
    box-shadow: -1px -1px 4px 2px;
    display: inline-block;
    margin: 0 25px 50px;
}
.h1 {
    font-size: 1.5em;
    text-align: center;
}
.h2 {
    font-size: 1.25em;
    text-align: left;
}
.horizontal {
    width: 100%;
    overflow: hidden;
    padding: 0;
    margin: 0;
}
.horizontal > dt {
    width: auto;
    padding: 0;
    margin: 0;
}
.horizontal > dd {
    width: auto;
    padding: 0;
    margin: 0;
}
.status {
    margin-top:0.1em;
    box-shadow: 1px 1px 2px 0px lightgrey;
}
</style>
