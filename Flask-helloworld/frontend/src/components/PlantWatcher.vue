<template>
<div>
    <h1>Irrigation Module</h1>
    <span v-if="status" v-text="status"></span>
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
                    <a href="#refresh" @click="refresh(p)">refresh</a>
                    <span>&nbsp;|&nbsp;</span>
                    <router-link :to="{name: 'plantstats', params: {name: p.name}}">
                        stats
                    </router-link>
                </div>
            </div>
        </dl>
    </ul>
</div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'PlantWatcher',
    data () {
        return {
            status: 'loading plants from server...',
            plants: []
        }
    },
    methods: {
        _handleListResp (resp) {
            if (Array.isArray(resp.data) && resp.data.length > 0) {
                this.plants = resp.data
                this.status = ''
            } else {
                this.status = "didn't get any plants, check what's wrong'"
            }
        },
        _handleSingleResp (resp, plant) {
            if (resp.data) {
                Object.assign(plant, resp.data)
                this.status = ''
            } else {
                this.status = `didn't get refresh for "${plant.name}", check what's wrong'`
            }
        },
        getPlantWatcherStatus () {
            axios.get('/api/plant/watcher')
                .then(this._handleListResp)
                .catch(console.log)
        },
        refresh (p) {
            axios.get(`/api/plant/${p.name}/status`)
                .then(resp => this._handleSingleResp(resp, p))
                .catch(console.log)
        }
    },
    beforeMount () { this.getPlantWatcherStatus() }
}
</script>

<style scoped>
.plant-list {
    padding: 0;
}
.plant-block {
    width: 150px;
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
