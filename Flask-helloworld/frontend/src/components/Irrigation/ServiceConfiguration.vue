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
    <ul class="list-inline activities">
        <li>
            <a href="" @click.prevent="wsGetServiceConfig" v-text="actionText"/>
        </li>
        <li v-if="hasConf">
            <a href="" @click.prevent="modify=!modify" :class="stateClass">
                modify</a>
        </li>
        <li v-if="hasConf && (worthSaving || modify)">
            <a href="" @click.prevent="wsUpdateServiceConfig">
                save and restart service</a>
        </li>
    </ul>
    <ul v-if="hasConf && modify" class="list-inline activities">
        <li>
            <a href="" @click.prevent="addPlant">
                add new plant</a>
        </li>
        <li>
            <label for="p_r">
                remove plant</label>
            <select id="p_r" v-model="plantToRemove" :disabled="disableRemove" :title="selectTitle">
                <option :value="null">
                    ...chose...</option>
                <option
                    v-for="p in configData.content.plants_args_list"
                    v-text="p.name"
                    :key="p.name"/>
            </select>
        </li>
    </ul>
    <p v-if="hasConf && modify" class="highlight-warn">
        Please, be very careful with changing configuration!
        Saving faulty configuration might prevent to start service!
        False GPIO pin settings most probably disables service or
        it my behave in unexpected way and even burn down hardware.
        You've been warned...
    </p>
    <tree-view
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

const debug = process.env.NODE_ENV !== 'production'
var counter = 0

export default {
    name: 'service-configuration',
    data () {
        return {
            status: '',
            configData: '',
            modify: false,
            worthSaving: false
        }
    },
    computed: {
        selectTitle () {
            return this.disableRemove ? 'cannot remove single plant' : ''
        },
        statusClass () {
            return this.status ? 'highlight-crit' : ''
        },
        stateClass () {
            return this.modify ? 'highlight' : 'highlight-warn'
        },
        disableRemove () {
            return this.configData.content.plants_args_list.length <= 1
        },
        plantToRemove: {
            get () { return null },
            set (name) { this.removePlant(name) }
        },
        hasConf () {
            return this.configData && Object.keys(this.configData).length > 0
        },
        actionText () {
            return !this.hasConf ? 'load from server' : 'reload from server'
        }
    },
    methods: {
        wsGetServiceConfig () {
            this.modify = this.worthSaving = false
            this.$socket.emit('get_service_config', (data) => {
                this.status = ''
                this.configData = data
            })
        },
        wsUpdateServiceConfig () {
            this.modify = false
            if (!this.worthSaving) {
                return
            }
            this.worthSaving = false
            this.$socket.emit('store_service_config_and_restart',
                this.configData, (type, msg) => {
                    this.status = type ? msg : ''
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
            plants.push({
                'name': `Lill ${++counter}`,
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
            })
            this.status = 'please calibrate new plant\'s sensor before usage'
        },
        removePlant (name) {
            if (name === null) {
                return
            }
            this.worthSaving = true
            var plants = this.configData.content.plants_args_list
            const index = plants.findIndex(p => p.name === name)
            if (index !== -1) {
                plants.splice(index, 1)
            } else {
                this.status = 'plant you were trying to remove do not existn in array'
            }
        }
    }
}
</script>

<style>
.tree-view-wrapper > div > div > div.tree-view-item-node > span.tree-view-item-key {
    font-size: large;
    color: #980303;
}
</style>

<style scoped>
.tree-view-wrapper, pre {
    text-align: left;
    margin: 1em;
}
.activities > *:not(:first-child)::before{
    content: " | ";
}
hr {
    border-style: ridge;
}
</style>
