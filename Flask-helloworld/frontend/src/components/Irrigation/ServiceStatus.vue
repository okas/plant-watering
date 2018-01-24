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
        <ul class="list-style-none" :class="status ? 'has-text-danger' : ''">
            <li v-if="status" v-text="status"/>
            <li v-if="specStatus" v-text="specStatus"/>
        </ul>
    </header>
    <div class="activities list-inline has-text-centered">
        <div class="field">
            <input
                type="checkbox"
                class="switch is-rounded is-success has-text-warning"
                id="scv_tog"
                v-model="stateToggler"
                :disabled="disableToggler"
                true-value="on"
                false-value="off"/>
            <label for="scv_tog">
                state</label>
        </div>
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
        stateToggler: {
            get () {
                return ['on', 'off'].includes(this.state) ? this.state : 'off'
            },
            set () { this.wsToggleState() }
        },
        ...mapState({
            state: 'state',
            newState (s) {
                switch (s.state) {
                case 'on': return 'off'
                case 'off': return 'on'
                default: return ''
                }
            },
            status (s) {
                switch (s.state) {
                case 'server-off': return 'Sorry, application server is not reachable!'
                case 'on': case 'off': return ''
                default: return `Service is not good right now: '${s.state}'.`
                }
            },
            disableToggler (s) {
                if (s.apiState !== 'online') {
                    return true
                } else {
                    return !['on', 'off'].includes(this.state)
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

<style lang="scss" scoped>
.activities {
    font-weight: 600;
}
</style>
