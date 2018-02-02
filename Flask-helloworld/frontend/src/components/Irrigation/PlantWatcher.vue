<template>
<section class="has-text-centered">
    <header>
        <h2>Real-time plant overview</h2>
    </header>
    <article>
        <ul class="plant-list is-clearfix">
            <dl class="plant-block" :class="plantStateCls" v-for="p in plants">
                <dt
                class="h1"
                :class="badgeCls"
                v-text="p.name"
                :data-badge="p._ticker"/>
                <div class="horizontal status">
                    <dt class="is-pulled-left">state:</dt>
                    <dd v-text="p.state" class="is-pulled-aligned-right"/>
                </div>
                <div class="horizontal">
                    <dt class="h2 is-pulled-left">Moisture</dt>
                    <dd class="h2 is-pulled-aligned-right">%</dd>
                </div>
                <div>
                    <div class="horizontal status">
                        <dt class="is-pulled-left">required:</dt>
                        <dd v-text="p.moist_level" class="is-pulled-aligned-right"/>
                    </div>
                    <div class="horizontal status">
                        <dt class="is-pulled-left">measured:</dt>
                        <dd v-text="p.moist_measured" class="is-pulled-aligned-right"/>
                    </div>
                    <div class="horizontal toolbar">
                        <button
                        class="button is-outlined is-small"
                        :class="buttonCls"
                        :disabled="!serviceIsOn"
                        @click="wsRefreshPlant(p, $event)">
                            refresh</button>
                        <router-link
                        class="button is-outlined is-small"
                        :class="buttonCls"
                        :disabled="!serviceIsOn"
                        :to="{name: 'plantstats', params: {name: p.name}}"
                        tag="button">
                            stats</router-link>
                        <router-link
                        class="button is-outlined is-small"
                        :class="buttonCls"
                        :disabled="!serviceIsOn"
                        :to="{name: 'plantcalibrate', params: {name: p.name}}"
                        tag="button">
                            calibrate</router-link>
                    </div>
                </div>
            </dl>
        </ul>
    </article>
</section>
</template>

<script>
export default {
    name: 'plant-watcher',
    head: { title: { inner: 'Plant watcher' } },
    data () {
        return {
            status: '...loading plants from server...',
            creating: false,
            joined: false,
            plants: []
        }
    },
    sockets: {
        update_plant_status (data) {
            if (!data) {
                this.status = 'server initiated plant status update, but no data was sent.'
                this.statusClass = 'is-danger'
                return
            }
            this.addOrUpdatePlant(data)
            this.status = ''
        }
    },
    computed: {
        serviceIsOn () {
            return this.$store.state.irrigation.state === 'on'
        },
        plantStateCls () {
            return this.serviceIsOn ? 'act' : 'inact'
        },
        buttonCls () {
            return this.serviceIsOn ? 'is-link' : ''
        },
        badgeCls () {
            return this.serviceIsOn ? 'badge is-badge-outlined is-badge-small is-badge-default' : ''
        }
    },
    watch: {
        serviceIsOn (s) {
            if (s) {
                this.status = ''
                this.wsJointPlantwatcherRoom()
            } else {
                this.joined = false
                this.status = 'Service is not running, cannot update.'
            }
        }
    },
    methods: {
        wsJointPlantwatcherRoom (isCreator = false) {
            if (this.joined || (this.creating && !isCreator)) {
                return
            }
            this.$socket.emit('join_room_plantwatcher', data => {
                this.joined = true
                console.log(`joined to room [plantwatcher]; status [${data}]`)
                if (this.serviceIsOn) {
                    this.$socket.emit('push_me_all_plants', () => {
                        this.creating = false
                    })
                } else {
                    this.status = 'Service is not running, can\'t render the overview for you.'
                }
            })
        },
        wsRefreshPlant (plant, e) {
            this.$socket.emit('initiate_plant_measuring', plant.name)
            e.target.blur()
        },
        addOrUpdatePlant (plant) {
            if (this.plants.length === 0) {
                plant._ticker = 0
                this.plants.push(plant)
                return
            }
            var existing = this.plants.find(p => p.name === plant.name)
            if (existing) {
                Object.assign(existing, plant)
                existing._ticker++
            } else {
                plant._ticker = 0
                this.plants.push(plant)
            }
        }
    },
    created () {
        this.creating = true
        this.wsJointPlantwatcherRoom(true)
    },
    beforeRouteLeave (to, from, next) {
        this.$socket.emit('leave_room_plantwatcher', data => {
            this.joined = false
            console.log(`leaved from room [plantwatcher]; status [${data}].`)
        })
        next()
    }
}
</script>

<style lang="scss" scoped>
$transition: 0.5s all;

.plant-list {
    padding: 0;
    margin: 0;
    .plant-block {
        width: 195px;
        display: inline-block;
        margin: 0 25px 50px;
        border-radius: 0.33rem;;
        transition: $transition;
        &.act {
            box-shadow: 0px 0px 14px 4px $primary;
            color: $default-text-color;
        }
        &.inact {
            box-shadow: -1px -1px 10px -1px $grey-light;
            color: $grey-light;
        }
        .h1 {
            font-size: 1.5em;
            text-align: center;
        }
        .h2 {
            font-size: 1.25em;
            text-align: left;
        }
        .status {
            margin-top:0.1em;
            box-shadow: 1px 1px 2px 0px $grey-light;
        }
        .horizontal {
            width: 100%;
            overflow: hidden;
            padding: 0 0.15rem;
            margin: 0;
            &.toolbar {
                padding: 0.20rem;
                .button {
                    transition: $transition;
                }
            }
            > dt, > dd {
                width: auto;
                padding: 0;
                margin: 0;
            }
        }
    }
}
</style>
