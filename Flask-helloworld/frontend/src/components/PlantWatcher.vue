<template>
  <div>
    <p v-text="plantWatcherStatus"></p>
    <button @click="getPlantWatcherStatus">Get status</button>
  </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'PlantWatcher',
    data () {
        return {
            msg: 'Welcome to Plant Watcher page.',
            plantWatcherStatus: 'waitng...'
        }
    },
    methods: {
        getPlantWatcherStatus () {
            const path = 'http://saarmas-rp3-1.saared.eu:4999/api/plant-watcher'
            axios.get(path)
                .then(resp => {
                    this.plantWatcherStatus = resp.data.message
                })
                .catch(err => { console.log(err) })
        }
    },
    beforeMount: this.getPlantWatcherStatus
}
</script>

<style scoped>
</style>
