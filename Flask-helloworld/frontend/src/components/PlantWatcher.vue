<template>
<div>
    <h2 v-text="heading"></h2>
    <ul>
        <dl class="plant-block" v-for="p in plants">
            <dt class="h1">
                <a href="#" @click="refresh(p)" v-text="p.name"></a>
            </dt>
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
            </div>
        </dl>
    </ul>
</div>
</template>

<script>
import axios from 'axios'

const apiBase = 'http://saarmas-rp3-1.saared.eu:4999/api'

export default {
    name: 'PlantWatcher',
    data () {
        return {
            heading: 'Welcome to Plant Watcher page',
            plants: []
        }
    },
    methods: {
        getPlantWatcherStatus () {
            axios.get(apiBase + '/plant-watcher')
                .then(resp => {
                    this.plants = resp.data
                })
                .catch(err => { console.log(err) })
        },
        refresh (p) {
            axios.get(`${apiBase}/plant-status/${p.name}`)
                .then(resp => { Object.assign(p, resp.data) })
                .catch(err => { console.log(err) })
        }
    },
    beforeMount () { this.getPlantWatcherStatus() }
}
</script>

<style scoped>
.plant-block {
    width: 150px;
    float: left;
    box-shadow: 0px -1px 1px #9fcbe4;
}
.h1 {
    font-size: 1.5em;
}
.h2 {
    font-size: 1.25em;
}
.h1, .h2 {
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
