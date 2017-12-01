<template>
  <div>
    <p v-for="p in plants">
        {{ p.status }} > <a href="#" @click="refresh(p)">refresh</a>
    </p>
  </div>
</template>

<script>
import axios from 'axios'

const apiBase = 'http://saarmas-rp3-1.saared.eu:4999/api'

export default {
    name: 'PlantWatcher',
    data () {
        return {
            msg: 'Welcome to Plant Watcher page.',
            plants: []
        }
    },
    methods: {
        getPlantWatcherStatus () {
            axios.get(apiBase + '/plant-watcher')
                .then(resp => {
                    this.plants = resp.data.plants
                })
                .catch(err => { console.log(err) })
        },
        refresh (p) {
            axios.get(`${apiBase}/plant-status/${p.name}`)
                .then(resp => { p.status = resp.data })
                .catch(err => { console.log(err) })
        }
    },
    beforeMount () { this.getPlantWatcherStatus() }
}
</script>

<style scoped>
    a {
        color: blue;
    }
</style>
