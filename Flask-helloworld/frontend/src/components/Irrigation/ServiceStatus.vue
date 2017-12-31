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
        <a href="" @click.prevent="$emit('refresh-status')">
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
            status: s => s.api.state === 'online'
                ? ['on', 'off'].includes(s.statusObj.state)
                    ? ''
                    : `Service is not good right now: '${s.statusObj.state}'.`
                : 'No server communication.',
            newState: s => s.statusObj.state === 'on'
                ? 'off'
                : s.statusObj.state === 'off'
                    ? 'on'
                    : 'error',
            serverOnline: s => s.api.state === 'online',
            stateClass: s => s.statusObj.state === 'on'
                ? 'highlight'
                : s.statusObj.state === 'off'
                    ? 'highlight-crit'
                    : 'error'
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
