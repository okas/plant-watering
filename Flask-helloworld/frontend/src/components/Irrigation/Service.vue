<template>
<section>
    <header>
        <h2>Manage irrigation service</h2>
    </header>
    <service-status/>
    <service-configuration/>
</section>
</template>

<script>
import ServiceStatus from './ServiceStatus'
import ServiceConfiguration from './ServiceConfiguration'

export default {
    name: 'service',
    components: {
        ServiceStatus, ServiceConfiguration
    },
    head: {
        title: { inner: 'Manage Irrigation' }
    }
}
</script>
