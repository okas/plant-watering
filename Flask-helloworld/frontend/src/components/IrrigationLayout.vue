<template>
<main class="clearfix">
    <header>
        <h1 class="toptitle">
            <router-link :to="{name: 'plantwatcher'}">
                Plant Irrigation Module
            </router-link>
        </h1>
    </header>
    <irrigation-aside/>
    <slot/>
</main>
</template>

<script>
import IrrigationAside from './IrrigationAside'

export default {
    name: 'irrigation-layout',
    components: { IrrigationAside }
}
</script>
