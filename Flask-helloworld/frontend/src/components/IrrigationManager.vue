<template>
<layout>
<section>
    <header>
        <h2>Manage irrigation service</h2>
        <ul class="list-inline">
            <li v-if="status" v-text="status"></li>
        </ul>
    </header>
    <article>
        <h3>Service state</h3>
        <p>
            You can start or stop irrigation service. Restarting service
            means two things:<br/>
            configuration is loaded again <i>and</i> measurements start
            right away. It doesn't consider any state from previous session.
        </p>
        <p v-if="state != defaultState" class="activity">
            Service state:
            <span
                v-text="state"
                :class="stateClass"
                class="state"/>
            &nbsp;|&nbsp; toggle to
            <a
                href="#toggle"
                v-text="newState"
                @click="apiToggleState"
                class="state"/>
            &nbsp;|&nbsp;
            <a href="#refresh" @click="apiGetState">refresh</a>
        </p>
    </article>
    <article>
        <h3>Service configuration</h3>
        <p>
            Change configuration service configuration. <br/>
            This includes plant's configuration.
        </p>
        <p>
            <a href="#retreiveConfig" @click="apiGetServiceConfig">
                Retrieve config from server
            </a>
        </p>
        <p>
            <irrigation-configuration :dataObj="configDocumentObject"/>
        </p>
    </article>
</section>
</layout>
</template>

<script>
import Layout from './IrrigationLayout'
import IrrigationConfiguration from './IrrigationConfiguration'
import axios from 'axios'

export default {
    name: 'IrrigationManager',
    components: { Layout, IrrigationConfiguration },
    data () {
        return {
            status: '..loading from database..',
            defaultState: '..loading..',
            state: '..loading..',
            configDocumentObject: {}
        }
    },
    computed: {
        stateClass: function () {
            if (this.state === 'on') {
                return 'highlight'
            } else if (this.state === 'off') {
                return 'highlight-neg'
            } else {
                return 'error'
            }
        },
        newState: function () {
            if (this.state === 'on') {
                return 'off'
            } else if (this.state === 'off') {
                return 'on'
            } else {
                return 'error'
            }
        }
    },
    methods: {
        apiGetState () {
            axios.get('/api/irrigation/service-state')
                .then(resp => {
                    if (['on', 'off'].indexOf(resp.data.state) !== -1) {
                        this.state = resp.data.state
                        this.status = ''
                    } else {
                        this.status = resp.data.state
                        console.log(resp.data)
                    }
                })
                .catch(console.log)
        },
        apiToggleState () {
            var act
            if (this.newState === 'on') {
                act = 'start'
            } else if (this.newState === 'off') {
                act = 'stop'
            } else {
                console.log(`Bad value of ${this.newState} in this.state!
                             Cannot toggle service state with this, aborting!`)
                return
            }
            axios.get(`/api/irrigation/service-${act}`)
                .then(resp => {
                    if (['on', 'off'].indexOf(resp.data.state) !== -1) {
                        this.state = resp.data.state
                    } else if (['already_on', 'already_off']
                                .indexOf(resp.data.state) !== -1) {
                    } else {
                        this.status = resp.data.state
                        console.log(resp.data)
                    }
                })
                .catch(console.log)
        },
        apiGetServiceConfig () {
            axios.get('/api/irrigation/service-config')
                .then(resp => { this.configDocumentObject = resp.data })
                .catch(console.log)
        }
    },
    beforeMount () {
        this.apiGetState()
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
.activity {
    font-weight: 600;
}
.state {
    text-transform: uppercase;
}
</style>
