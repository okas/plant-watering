<template>
<article>
    <header>
        <h3>Service status</h3>
        <p>
            You can start or stop irrigation service. Restarting service
            means two things:<br/>
            configuration is loaded again <i>and</i> measurements start
            right away. It doesn't consider any state from previous session.
        </p>
        <ul class="list-style-none" :class="status ? 'highlight-crit' : ''">
            <li v-if="status" v-text="status"/>
            <li v-if="specStatus" v-text="specStatus"/>
        </ul>
    </header>
    <p v-if="serverOnline" class="activity">
        <span>
            Current state:</span>
        <span v-text="state" :class="stateClass" class="state"/>
        <span>
            &nbsp;|&nbsp; toggle to</span>
        <a href="" v-text="newState" @click.prevent="wsToggleState" class="state"/>
        <span>
            &nbsp;|&nbsp;</span>
        <a href="" @click.prevent="$store.dispatch('irrigation/refreshServiceStatus')">
            refresh</a>
    </p>
</article>
</template>

<script>
import { mapState } from 'vuex'

export default {
    name: 'IrrigationServiceStatus',
    data () {
        return {
            specStatus: ''
        }
    },
    computed: {
        ...mapState('irrigation', {
            state: s => s.statusObj.state,
            status: s => {
                if (s.api.state !== 'online') {
                    return 'No server communication.'
                }
                return ['on', 'off'].includes(s.statusObj.state)
                    ? ''
                    : `Service is not good right now: '${s.statusObj.state}'.`
            },
            newState: s => {
                switch (s.statusObj.state) {
                case 'on': return 'off'
                case 'off': return 'on'
                default: return 'error'
                }
            },
            serverOnline: s => s.api.state === 'online',
            stateClass: s => {
                switch (s.statusObj.state) {
                case 'on': return 'highlight'
                case 'off': return 'highlight-warn'
                default: return 'highlight-crit'
                }
            }
        })
    },
    methods: {
        wsToggleState () {
            var act
            if (this.newState === 'on') {
                act = 'start'
            } else if (this.newState === 'off') {
                act = 'stop'
            } else {
                console.log(`Bad value of ${this.newState} in [this.state]!
                             Cannot toggle service state with this, aborting!`)
                this.specStatus = 'Frontend app error, see console!'
                return
            }
            this.$socket.emit(`service_${act}`, (resp) => {
                this.specStatus = resp && resp !== 'ok'
                    ? `Error occured during service ${act}: '${resp}'.`
                    : ''
            })
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
