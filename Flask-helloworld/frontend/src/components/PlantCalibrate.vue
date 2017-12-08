<template>
<plant-layout>
<section>
    <h2>Calibrate <span v-text="name"></span></h2>
    <article>
        <div>You should calibrate plants moisture sensor when...</div>
        <div>[insctructions]</div>
    </article>
</section>
<section>
    <article>
        <div>
            Calibrate dry sensor
        </div>
        <div>
            Calibrate wet sensor
        </div>
    </article>
</section>
</plant-layout>
</template>

<script>
import PlantLayout from './PlantLayout'

// import axios from 'axios'

export default {
    name: 'PlantCalibrate',
    components: { PlantLayout },
    props: {
        name: {
            type: String,
            required: true
        }
    },
    data () {
        return {
            status: '...'
        }
    }
}
</script>

<style scoped>
h1 > span {
  box-shadow: -1px -1px 1px 1px #52e4b585;
}
</style>
