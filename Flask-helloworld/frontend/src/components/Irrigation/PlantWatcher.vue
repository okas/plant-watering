<template>
<section>
    <header>
        <h2>Real-time plant overview</h2>
    </header>
    <article>
        <header>
            <ul class="list-style-none">
                <li class="status-small">
                    Updates: <span v-text="ticker"/>
                    </li>
                <li v-if="status" v-text="status" :class="statusClass"/>
            </ul>
        </header>
        <ul class="plant-list is-clearfix">
            <dl v-for="p in plants" :class="stateOutterClass">
                <dt class="h1" v-text="p.name"></dt>
                <div class="horizontal status">
                    <dt class="is-pulled-left">state:</dt>
                    <dd v-text="p.state" class="is-pulled-aligned-right"></dd>
                </div>
                <div class="horizontal">
                    <dt class="h2 is-pulled-left">Moisture</dt>
                    <dd class="h2 is-pulled-aligned-right">%</dd>
                </div>
                <div>
                    <div class="horizontal status">
                        <dt class="is-pulled-left">required:</dt>
                        <dd v-text="p.moist_level" class="is-pulled-aligned-right"></dd>
                    </div>
                    <div class="horizontal status">
                        <dt class="is-pulled-left">measured:</dt>
                        <dd v-text="p.moist_measured" class="is-pulled-aligned-right"></dd>
                    </div>
                    <div class="horizontal">
                        <a href=""
                            v-if="serviceIsOn"
                            v-text="linkRef"
                            @click.prevent="wsRefreshPlant(p)"/>
                        <span v-text="linkRef" v-else/>
                        <span>&nbsp;|&nbsp;</span>
                        <router-link
                            v-if="serviceIsOn"
                            v-text="linkSta"
                            :to="{name: 'plantstats', params: {name: p.name}}"/>
                        <span v-text="linkSta" v-else/>
                        <span>&nbsp;|&nbsp;</span>
                        <router-link
                            v-if="serviceIsOn"
                            v-text="linkCal"
                            :to="{name: 'plantcalibrate', params: {name: p.name}}"/>
                        <span v-text="linkCal" v-else/>
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
            plants: [],
            ticker: 0,
            linkRef: 'refresh',
            linkSta: 'stats',
            linkCal: 'calibrate'
        }
    },
    sockets: {
        update_plant_status (data) {
            if (!data) {
                this.status = 'server initiated plant status update, but no data was sent.'
                this.statusClass = 'is-danger'
                return
            }
            if (this.plants.length === 0) {
                this.plants.push(data)
            } else {
                this.addOrUpdatePlant(data)
            }
            this.status = ''
            this.ticker++
        }
    },
    computed: {
        serviceIsOn () {
            return this.$store.state.irrigation.state === 'on'
        },
        stateOutterClass () {
            return this.serviceIsOn ? 'plant-block-active' : 'plant-block-inactive'
        },
        statusClass () {
            return this.serviceIsOn ? 'has-text-warning' : ''
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
        wsRefreshPlant (plant) {
            this.$socket.emit('initiate_plant_measuring', plant.name)
        },
        addOrUpdatePlant (plant) {
            var existing = this.plants.find(p => p.name === plant.name)
            if (existing) {
                Object.assign(existing, plant)
            } else {
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
.plant-list {
    padding: 0;
    margin: 0;
}
%plant-block {
    width: 195px;
    display: inline-block;
    margin: 0 25px 50px;
    transition: 0.5s color;
}
.plant-block-active {
    @extend %plant-block;
    box-shadow: 0px 0px 14px 4px $primary;
    color: $default-text-color;
}
.plant-block-inactive {
    @extend %plant-block;
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
.horizontal {
    width: 100%;
    overflow: hidden;
    padding: 0;
    margin: 0;
    > dt, dt {
        width: auto;
        padding: 0;
        margin: 0;
    }
}
.status {
    margin-top:0.1em;
    box-shadow: 1px 1px 2px 0px $grey-light;
}
</style>
