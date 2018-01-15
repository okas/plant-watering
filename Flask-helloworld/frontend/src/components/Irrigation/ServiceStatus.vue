<template>
<article>
    <header>
        <h3>
            Service status</h3>
        <p>
            You can start or stop irrigation service. Restarting service
            means two things:<br/>
            configuration is loaded again <i>and</i> measurements start
            right away. It doesn't consider any state from previous session.
            </p>
        <code>
            TODO: intensive state toggling will cause fatal error in
            server, investigate.
            </code>
        <code>
            TODO: also global error data handling should be implemented
            or principles how to show it. Currently service erros are
            not rendered very well to this part. (status, state etc.)
            </code>
        <ul class="list-style-none" :class="status ? 'highlight-crit' : ''">
            <li v-if="status" v-text="status"/>
            <li v-if="specStatus" v-text="specStatus"/>
            </ul>
    </header>
    <div v-if="serverOnline" class="activities list-inline">
        <span>
            Current state:</span>
        <span v-text="state" :class="stateClass" class="state"/>
        <div v-if="newState">
            <span>
                &nbsp;|&nbsp; toggle to</span>
            <a href="" v-text="newState" @click.prevent="wsToggleState" class="state"/>
            </div>
        <span v-else>disabled</span>
        <span>
            &nbsp;|&nbsp;</span>
        <a href="" @click.prevent="$store.dispatch('irrigation/refreshServiceStatus')">
            refresh</a>
    </div>
</article>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
const { mapState } = createNamespacedHelpers('irrigation')

export default {
    name: 'service-status',
    data () {
        return {
            specStatus: ''
        }
    },
    computed: {
        status () {
            switch (this.state) {
            case 'server-off': return 'Sorry, application server is not reachable!'
            case 'on': case 'off': return ''
            default: return `Service is not good right now: '${this.state}'.`
            }
        },
        ...mapState({
            state: 'state',
            newState: s => {
                switch (s.state) {
                case 'on': return 'off'
                case 'off': return 'on'
                default: return ''
                }
            },
            serverOnline: s => s.apiState === 'online',
            stateClass: s => {
                switch (s.state) {
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
                console.log(`Bad value of [${this.newState}] in [this.newState]!
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
.activities {
    font-weight: 600;
}
.state {
    text-transform: uppercase;
}
</style>
