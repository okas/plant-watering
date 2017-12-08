<template>
<main class="clearfix">
    <header><h1>Plant Irrigation Module</h1></header>
    <plant-aside/>
    <slot/>
</main>
</template>

<script>
import PlantAside from './PlantAside'

export default {
    name: 'plant-layout',
    components: { PlantAside }
}
</script>
