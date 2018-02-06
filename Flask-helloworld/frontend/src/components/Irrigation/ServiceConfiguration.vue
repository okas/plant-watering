<template>
<article>
<header>
    <h3>Irrigation service cofiguration</h3>
    <p>
        You can evaluate and change configuration.<br/>
        Service restart will be done only if service is started already.
    </p>
    <code>TODO: do something with json parsing order...</code>
    <ul class="list-inline">
        <li v-if="status" v-text="status" :class="statusClass"/>
    </ul>
</header>
<ul class="list-inline">
    <li>
        <button class="button is-rounded" @click="wsGetServiceConfig">
            <transition name="fade" appear mode="out-in">
                <f-a :icon="loaderIcon" :key="loaderIcon"/>
            </transition>
        </button>
    </li>
    <li v-if="hasConf">
        <transition name="fade" appear>
            <button
            class="button is-rounded"
            :class="stateClass"
            @click="modify=!modify">
                <f-a icon="edit"/>
            </button>
        </transition>
    </li>
    <li v-if="hasConf">
        <transition name="fade" appear>
            <button
            class="button is-rounded"
            :disabled="!modify"
            @click="addPlant">
                <f-a icon="plus"/>&nbsp;
                <span>
                    plant</span>
            </button>
        </transition>
    </li>
    <li v-if="hasConf">
        <div class="dropdown" :class="isActivePlantRemoveCls" :title="plantRemoveTitle">
            <div class="dropdown-trigger">
                <transition name="fade" appear>
                    <button
                    class="button is-rounded"
                    aria-haspopup="true"
                    aria-controls="dropdown_menu"
                    :disabled="disableRemove"
                    @click.passive="togglePlantRemoveMenu">
                        <f-a icon="minus"/>&nbsp;
                        <span>
                            plant</span>
                    </button>
                </transition>
            </div>
            <div class="dropdown-menu" id="dropdown_menu" role="menu">
                <div class="dropdown-content">
                    <div
                    class="dropdown-item"
                    @click="removePlant(p.name)"
                    v-for="p in configData.content.plants_args_list"
                    :key="p.name">
                        <f-a icon="minus"/>&nbsp;
                        <span v-text="p.name"/>
                    </div>
                </div>
            </div>
        </div>
    </li>
    <li v-if="hasConf">
        <transition name="fade" appear>
            <button
            class="button is-rounded"
            @click="wsStoreServiceConfig"
            :disabled="!worthSaving">
                <f-a icon="upload"/>
                <transition name="fade">
                    <span v-if="restartIcon">
                        &nbsp;<f-a icon="cog"/>
                    </span>
                </transition>
            </button>
        </transition>
    </li>
</ul>
<p v-if="hasConf && modify" class="has-text-warning">
    Please, be very careful with changing configuration!
    Saving faulty configuration might prevent to start service!
    False GPIO pin settings most probably disables service or
    it my behave in unexpected way and even burn down hardware.
    You've been warned...
</p>
<tree-view
class="json-conf"
v-if="hasConf"
:data="configData.content"
@change-data="onTreeViewDataChange"
:options="{
    rootObjectKey: configData.filename,
    maxDepth: 3,
    modifiable: this.modify}"/>
</article>
</template>

<script>
import Vue from 'vue'
Vue.use(require('vue-json-tree-view'))

const ns = 'irrigation'
const debug = process.env.NODE_ENV !== 'production'
var counter = 0

const plantTemplate = {
    'name': 'Lill ',
    'valve_pin': -1,
    'led_pin': -1,
    'moist_percent': 65,
    'pour_millilitres': 50,
    'sensor_args': {
        'spi_device': -1,
        'spi_channel': -1,
        'vcc_pin': -1,
        'wet_value': 0.44,
        'dry_value': 0.85
    }
}

export default {
    name: 'service-configuration',
    data () {
        return {
            status: '',
            configData: {},
            modify: false,
            worthSaving: false,
            isActivePlantRemoveCls: ''
        }
    },
    computed: {
        plantRemoveTitle () {
            return this.disableRemove ? 'cannot remove single plant' : ''
        },
        statusClass () {
            return this.status ? 'has-text-danger' : ''
        },
        stateClass () {
            return this.modify ? 'has-text-primary' : 'has-text-warning'
        },
        disableRemove () {
            return !this.hasConf || this.configData.content.plants_args_list.length <= 1
        },
        hasConf () {
            // TODO use schema to verifiy correct config existence
            return this.configData && Object.keys(this.configData).length > 0
        },
        loaderIcon () {
            return !this.hasConf ? 'download' : 'sync'
        },
        restartIcon () {
            return this.$store.state.irrigation.state === 'on'
        }
    },
    socket: {
        namespace: `/${ns}`,
        options: { multiplexNamespace: true }
    },
    methods: {
        wsGetServiceConfig (e) {
            this.modify = this.worthSaving = false
            this.$socket.emit('get_service_config', (data) => {
                this.status = ''
                this.configData = data
            })
        },
        wsStoreServiceConfig () {
            this.modify = false
            if (!this.worthSaving) {
                return
            }
            this.worthSaving = false
            this.$socket.emit('store_service_config_and_restart',
                this.configData, (type, msg) => {
                    this.status = type ? msg : ''
                    if (type !== 'error') {
                        this.configData = null
                    }
                    if (debug && type !== 'info') {
                        console.log(`${type}: ${msg}`)
                    }
                })
        },
        onTreeViewDataChange (updatedDocument) {
            this.worthSaving = true
            this.configData.content = updatedDocument
        },
        addPlant () {
            var plants = this.configData.content.plants_args_list
            if (plants === undefined) {
                this.status = 'can\'t add plant, expected [plants_args_list] key in configuration'
                return
            }
            this.worthSaving = true
            // TODO: automate this schema retreival somehow :)
            var newPlant = Object.assign({}, plantTemplate)
            newPlant.name += ++counter
            plants.push(newPlant)
            this.status = 'please calibrate new plant\'s sensor before usage'
        },
        removePlant (name) {
            if (name === null) {
                return
            }
            this.worthSaving = true
            var plants = this.configData.content.plants_args_list
            const temp = JSON.parse(
                JSON.stringify(
                    plants.filter(
                        p => p.name !== name))
            )
            plants.splice(0)
            this.$nextTick(() => temp.forEach(p => plants.push(p)))
            this.togglePlantRemoveMenu(true)
        },
        togglePlantRemoveMenu (force = false) {
            if (!force && this.disableRemove) {
                return
                // TODO show message here
            }
            this.isActivePlantRemoveCls = this.isActivePlantRemoveCls
                ? ''
                : 'is-active'
        }
    }
}
</script>

<style lang="scss">
.json-conf.tree-view-wrapper > div > div > div.tree-view-item-node
> span.tree-view-item-key {
    font-size: large;
    color: #980303;
}
</style>

<style lang="scss" scoped>
.fade-enter-active, .fade-leave-active {
    transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
    opacity: 0;
}
.button {
    transition: 0.5s all;
}
.dropdown-item {
    cursor: pointer;
}
.tree-view-wrapper {
    text-align: left;
    margin: 1em;
}
hr {
    border-style: ridge;
}
</style>
