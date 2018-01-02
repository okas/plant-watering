<template>
<layout>
<section>
    <header>
        <h2>Manage irrigation service</h2>
    </header>
    <service-status/>
    <service-configuration/>
</section>
</layout>
</template>

<script>
import Layout from './Layout'
import ServiceStatus from './ServiceStatus'
import ServiceConfiguration from './ServiceConfiguration'

export default {
    name: 'IrrigationManager',
    components: {
        Layout, ServiceStatus, ServiceConfiguration
    },
    head: {
        title: { inner: 'Manage Irrigation' }
    }
}
</script>
