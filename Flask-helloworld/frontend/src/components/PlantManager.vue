<template>
<plant-layout>
<section>
    <header>
        <h2>Manage irrigation service</h2>
        <ul class="list-inline">
            <li v-if="status" v-text="status"></li>
        </ul>
    </header>
    <article>
        <p>
            You can start or stop irrigation service.
            Restarting service means two things: configuration is
            loaded again and measurements start right away.
            It doesn't consider any state from previous session.
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
                @click="toggleState"
                class="state"/>
            &nbsp;|&nbsp;(
            <a href="#refresh" @click="retreiveState">refresh</a>
            )
        </p>
    </article>
</section>
</plant-layout>
</template>

<script>
import PlantLayout from './PlantLayout'
import axios from 'axios'

export default {
    name: 'PlantManager',
    components: { PlantLayout },
    data () {
        return {
            status: '..loading from database..',
            defaultState: '..loading..',
            state: '..loading..'
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
        retreiveState () {
            axios.get('/api/plant/service-state')
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
        toggleState () {
            // this.state = this.newState
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
            axios.get(`/api/plant/service-${act}`)
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
        this.retreiveState()
    }
}
</script>

<style scoped>
.activity {
    font-weight: 600;
}
.activity::before {
    content: "=>";
}
.state {
    text-transform: uppercase;
}
</style>
