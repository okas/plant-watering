<template>
<layout>
<section>
    <header>
        <h2>Manage irrigation service</h2>
    </header>
    <service-status @refresh-status="refreshServiceStatus"/>
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
    },
    methods: {
        refreshServiceStatus () {
            this.$socket.emit('get_status', (data) => {
                this.$store.commit('irrigation/SOCKET_SERVICE_STATUS', [data])
            })
        }
    },
    created () {
        this.refreshServiceStatus()
    }
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
