<template>
<plant-layout>
    <section>
        <article>
            <h2>Management</h2>
        </article>
    </section>
</plant-layout>
</template>

<script>
import PlantLayout from './PlantLayout'

export default {
    name: 'PlantManager',
    components: { PlantLayout },
    data () {
        return {
            msg: 'test'
        }
    }
}
</script>

<style scoped>
</style>
