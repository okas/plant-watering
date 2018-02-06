<template>
<section>
    <header class="has-text-centered">
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
    head: { title: { inner: 'Manage Irrigation' } },
    components: {
        ServiceStatus, ServiceConfiguration
    }
}
</script>
