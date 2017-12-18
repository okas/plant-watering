<template>
<layout>
<section>
    <header>
        <h2>Manage irrigation service</h2>
    </header>
    <service-state/>
    <service-configuration/>
</section>
</layout>
</template>

<script>
import Layout from './IrrigationLayout'
import ServiceState from './IrrigationServiceState'
import ServiceConfiguration from './IrrigationServiceConfiguration'

export default {
    name: 'IrrigationManager',
    components: { Layout, ServiceState, ServiceConfiguration }
}
</script>

<style scoped>
article {
    margin-bottom: 1px;
}
article:first-of-type {
    border-top: 1px solid lightgrey;
}
article:not(:last-of-type) {
    border-bottom: 1px solid lightgrey;
}
</style>
