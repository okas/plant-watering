<template>
<layout>
<section>
    <header>
        <h2>'Real-time' plant overview</h2>
        <ul class="list-inline">
            <li v-if="status" v-text="status"></li>
        </ul>
    </header>
    <article>
        <ul class="plant-list clearfix">
            <dl class="plant-block" v-for="p in plants">
                <dt class="h1" v-text="p.name"></dt>
                <div class="horizontal status">
                    <dt>state:</dt>
                    <dd v-text="p.state"></dd>
                </div>
                <div class="horizontal">
                    <dt class="h2">Moisture</dt>
                    <dd class="h2">%</dd>
                </div>
                <div>
                    <div class="horizontal status">
                        <dt>required:</dt>
                        <dd v-text="p.moist_level"></dd>
                    </div>
                    <div class="horizontal status">
                        <dt>measured:</dt>
                        <dd v-text="p.moist_measured"></dd>
                    </div>
                    <div class="horizontal">
                        <a href="" @click.prevent="wsRefreshPlant(p)">refresh</a>
                        <span>&nbsp;|&nbsp;</span>
                        <router-link :to="{name: 'plantstats', params: {name: p.name}}">
                            stats
                        </router-link>
                        <span>&nbsp;|&nbsp;</span>
                        <router-link :to="{name: 'plantcalibrate', params: {name: p.name}}">
                            calibrate
                        </router-link>
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
            status: 'loading plants from server...',
            plants: []
        }
    },
    sockets: {
        update_plant_status (data) {
            const fraction = 'server initiated plant status update'
            if (!data) {
                this.status = `${fraction}, but no data was sent.`
                return
            }
            var plant = this.plants.find(p => p.name === data.name)
            if (!plant) {
                this.status = `${fraction}, didn't found plant with name "${data.name}"'`
                return
            }
            Object.assign(plant, data)
            this.status = ''
        }
    },
    methods: {
        wsRefreshPlant (plant) {
            this.$socket.emit('get_plant_status', plant.name, (data) => {
                if (!data) {
                    this.status = `didn't get refresh for "${plant.name}", check what's wrong.`
                    return
                }
                Object.assign(plant, data)
                this.status = ''
            })
        }
    },
    beforeMount () {
        this.$socket.emit('get_watcher_state', (data) => {
            if (!Array.isArray(data) || data.length === 0) {
                this.status = "didn't get any plants, check what's wrong'"
                return
            }
            this.plants = data
            this.status = ''
        })
    }
}
</script>

<style scoped>
.plant-list {
    padding: 0;
}
.plant-block {
    width: 195px;
    box-shadow: -1px -1px 4px 2px #52e4b585;
    display: inline-block;
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
    float: left;
    width: auto;
    padding: 0;
    margin: 0;
}
.horizontal > dd {
    float: right;
    width: auto;
    padding: 0;
    margin: 0;
    text-align: right;
}
.status {
    margin-top:0.1em;
    box-shadow: 1px 1px 2px 0px lightgrey;
}
</style>
