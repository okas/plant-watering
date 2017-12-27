<template>
<article>
    <header>
        <h3>Service state</h3>
        <p>
            You can start or stop irrigation service. Restarting service
            means two things:<br/>
            configuration is loaded again <i>and</i> measurements start
            right away. It doesn't consider any state from previous session.
        </p>
        <ul class="list-inline">
            <li v-if="status" v-text="status" :class="statusClass"></li>
        </ul>
    </header>
    <p v-if="state" class="activity">
        <span>
            Service state:</span>
        <span v-text="state" :class="stateClass" class="state"/>
        <span>
            &nbsp;|&nbsp; toggle to</span>
        <a href="" v-text="newState" @click.prevent="apiToggleState" class="state"/>
        <span>
            &nbsp;|&nbsp;</span>
        <a href="" @click.prevent="wsRefreshState">
            refresh</a>
    </p>
</article>
</template>

<script>
import axios from 'axios'

export default {
    name: 'IrrigationServiceState',
    props: ['statusObj'],
    data () {
        return {
            status: '..loading from database..',
            configDocumentObject: ''
        }
    },
    computed: {
        state () {
            return this.statusObj.state || ''
        },
        statusClass () {
            return this.status ? 'highlight-neg' : ''
        },
        stateClass () {
            if (this.state === 'on') {
                return 'highlight'
            } else if (this.state === 'off') {
                return 'highlight-neg'
            } else {
                return 'error'
            }
        },
        newState () {
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
        _handleReject (err, forEmptyResponse) {
            let newStatus = err.response ? err.response.data : forEmptyResponse
            this.status = `${newStatus} (${err.message})`
            console.log(err)
        },
        wsRefreshState () {
            this.$emit('refresh-status')
            // this.$socket.emit('refresh_status')
            // axios.get('/api/irrigation/service-state')
                // .then(resp => {
                    // if (['on', 'off'].indexOf(resp.data.state) !== -1) {
                        // this.state = resp.data.state
                        // this.status = ''
                    // } else {
                        // this.status = resp.data.state
                    // }
                // })
                // .catch(err => this._handleReject(
                    // err, 'Error occured during service state retreival.'
                // ))
        },
        apiToggleState () {
            var act
            if (this.newState === 'on') {
                act = 'start'
            } else if (this.newState === 'off') {
                act = 'stop'
            } else {
                console.log(`Bad value of ${this.newState} in [this.state]!
                             Cannot toggle service state with this, aborting!`)
                return
            }
            axios.get(`/api/irrigation/service-${act}`)
                .then(resp => {
                    if (['on', 'off'].indexOf(resp.data.state) !== -1) {
                        // this.state = resp.data.state
                    } else if (['already_on', 'already_off']
                                .indexOf(resp.data.state) !== -1) {
                    } else {
                        // this.status = resp.data.state
                        console.log(resp.data)
                    }
                })
                .catch(err => this._handleReject(
                    err, `Error occured during service ${act}.`
                ))
        }
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
