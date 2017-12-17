<template>
<article>
    <header>
        <h3>Service state</h3>
        <ul class="list-inline">
            <li v-if="status" v-text="status"></li>
        </ul>
        <p>
            You can start or stop irrigation service. Restarting service
            means two things:<br/>
            configuration is loaded again <i>and</i> measurements start
            right away. It doesn't consider any state from previous session.
        </p>
    </header>
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
            @click.prevent="apiToggleState"
            class="state"/>
        &nbsp;|&nbsp;
        <a href="#refresh" @click.prevent="apiGetState">refresh</a>
    </p>
</article>
</template>

<script>
import axios from 'axios'

export default {
    data () {
        return {
            status: '..loading from database..',
            defaultState: '..loading..',
            state: '..loading..',
            configDocumentObject: ''
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
        }
    },
    beforeMount () {
        this.apiGetState()
    }
}
</script>

<style scoped>
.activity {
    font-weight: 600;
}
.state {
    text-transform: uppercase;
}
</style>
