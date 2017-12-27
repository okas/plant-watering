<template>
<layout>
<section>
    <header>
        <h2>Manage irrigation service</h2>
    </header>
    <service-state
        :status-obj="serviceStatusObj"
        @refresh-status="$socket.emit('get_status')"/>
    <service-configuration :status-obj="serviceStatusObj"/>
</section>
</layout>
</template>

<script>
import Layout from './Layout'
import ServiceState from './ServiceState'
import ServiceConfiguration from './ServiceConfiguration'
import Vue from 'vue'
import VueSocketio from 'vue-socketio'
Vue.use(VueSocketio, '/irrigation')

export default {
    name: 'IrrigationManager',
    components: {
        Layout, ServiceState, ServiceConfiguration
    },
    head: {
        title: { inner: 'Manage Irrigation' }
    },
    data () {
        return { serviceStatusObj: {} }
    },
    sockets: {
        connect () {
            console.log('~ ~ [irrigation] socket connected')
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
    beforeDestroy () {
        this.$socket.disconnect()
        console.log('~ ~ [irrigation] socket disconnected (beforeDestroy)')
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
