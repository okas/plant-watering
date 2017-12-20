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
import Layout from './Layout'
import ServiceState from './ServiceState'
import ServiceConfiguration from './ServiceConfiguration'

export default {
    name: 'IrrigationManager',
    components: { Layout, ServiceState, ServiceConfiguration },
    head: { title: { inner: 'Manage Irrigation' } }
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
