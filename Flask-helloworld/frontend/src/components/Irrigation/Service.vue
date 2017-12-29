<template>
<layout>
<section>
    <header>
        <h2>Manage irrigation service</h2>
    </header>
    <service-state :status-obj="serviceStatusObj" @refresh-status="refreshStatus"/>
    <service-configuration :status-obj="serviceStatusObj"/>
</section>
</layout>
</template>

<script>
import Layout from './Layout'
import ServiceState from './ServiceState'
import ServiceConfiguration from './ServiceConfiguration'

export default {
    name: 'IrrigationManager',
    components: {
        Layout, ServiceState, ServiceConfiguration
    },
    head: {
        title: { inner: 'Manage Irrigation' }
    },
    data () {
        return {
            serviceStatusObj: { state: '' }
        }
    },
    sockets: {
        connect (msg) {
            console.log(`~ ~ [irrigation] socket said: ${msg}`)
        },
        disconnect (reason) {
            console.log(`~ ! ~ [irrigation] socket disconnected, reson: ${reason}`)
        },
        service_status (data) {
            // TODO: how to handle errors, like ones API handles now?
            // TODO api/../update-restart can output message prop as well!
            this.serviceStatusObj = data
        }
    },
    methods: {
        refreshStatus () {
            this.$socket.emit('get_status', (data) => {
                this.serviceStatusObj = data
            })
        }
    },
    created () {
        this.refreshStatus()
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
