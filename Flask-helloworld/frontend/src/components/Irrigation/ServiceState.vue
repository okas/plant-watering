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
        <code>TODO: Detect and show offline.</code>
        <ul class="list-style-none" :class="statusClass">
            <li v-if="status" v-text="status"></li>
            <li v-if="specStatus" v-text="specStatus"></li>
        </ul>
    </header>
    <p v-if="state" class="activity">
        <span>
            Service state:</span>
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
export default {
    name: 'IrrigationServiceState',
    props: ['statusObj'],
    data () {
        return {
            status: '..loading from database..',
            specStatus: '',
            state: '',
            configDocumentObject: ''
        }
    },
    computed: {
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
    watch: {
        'statusObj.state' (val) {
            if (['on', 'off'].indexOf(val) !== -1) {
                this.state = val
                this.status = ''
            } else {
                this.state = 'error'
                this.status = `Service is not good right now: '${val}'.`
            }
        }
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
